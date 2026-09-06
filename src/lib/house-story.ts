import manifest from '../config/house-v4-manifest.json';
import aliases from '../config/house-v4-frames.json';
export { manifest as houseManifest };
export type HouseProfile = keyof typeof manifest.profiles;
export const clampProgress = (value: number) =>
  Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : 0;
export function chapterAt(progress: number) {
  const p = clampProgress(progress);
  return Math.max(
    0,
    manifest.chapters.findLastIndex((chapter) => p >= chapter.start),
  );
}
export function chapterProgress(index: number) {
  return manifest.chapters[
    Math.max(0, Math.min(manifest.chapters.length - 1, index))
  ]!.rest;
}
export function frameAt(progress: number, profile: HouseProfile = 'desktop') {
  const { step } = manifest.profiles[profile];
  return (
    1 +
    Math.round((clampProgress(progress) * (manifest.frameCount - 1)) / step) *
      step
  );
}
export function progressAtFrame(frame: number) {
  return clampProgress((frame - 1) / (manifest.frameCount - 1));
}
export function sourceFrame(profile: HouseProfile, frame: number) {
  return (aliases[profile] as Record<string, number>)[String(frame)] ?? frame;
}
export function frameUrl(base: string, profile: HouseProfile, frame: number) {
  const source = sourceFrame(profile, frame);
  return `${base}${manifest.assetPath}${profile}/frame-${String(source).padStart(4, '0')}.webp`;
}
export function posterUrl(
  base: string,
  profile: HouseProfile,
  chapter: number,
) {
  return `${base}${manifest.assetPath}${profile}/${manifest.chapters[chapter]!.id}.webp`;
}
export type DecodedFrame = { width: number; height: number; close(): void };
type QueueOptions = {
  capacity: number;
  concurrency: number;
  step: number;
  count: number;
  resolveFrame?: (frame: number) => number;
};

/** Bounded decoder queue. Only the current target may become visible. */
export class FrameQueue<T extends DecodedFrame> {
  private cache = new Map<number, T>();
  private pending = new Map<number, AbortController>();
  private failed = new Set<number>();
  private queue: number[] = [];
  private target = 1;
  private disposed = false;
  constructor(
    private load: (frame: number, signal: AbortSignal) => Promise<T>,
    private display: (image: T, frame: number) => void,
    private error: (frame: number) => void,
    private options: QueueOptions = {
      capacity: 6,
      concurrency: 3,
      step: 4,
      count: 1441,
    },
  ) {}
  private source(frame: number) {
    return this.options.resolveFrame?.(frame) ?? frame;
  }
  request(frame: number) {
    if (this.disposed) return;
    const direction = frame >= this.target ? 1 : -1;
    this.target = frame;
    const source = this.source(frame);
    const cached = this.cache.get(source);
    if (cached) {
      this.cache.delete(source);
      this.cache.set(source, cached);
      this.display(cached, frame);
    } else if (this.failed.has(source)) {
      this.error(frame);
    }
    this.queue = [frame];
    for (let offset = 1; offset <= 5; offset++) {
      this.queue.push(
        frame + offset * direction * this.options.step,
        frame - offset * direction * this.options.step,
      );
    }
    this.queue = [
      ...new Set(
        this.queue
          .filter(
            (candidate) => candidate >= 1 && candidate <= this.options.count,
          )
          .map((candidate) => this.source(candidate)),
      ),
    ];
    for (const [frame, controller] of this.pending) {
      if (!this.queue.includes(frame)) controller.abort();
    }
    this.pump();
  }
  private pump() {
    if (this.disposed) return;
    while (this.pending.size < this.options.concurrency && this.queue.length) {
      const frame = this.queue.shift()!;
      if (
        this.pending.has(frame) ||
        this.cache.has(frame) ||
        this.failed.has(frame)
      )
        continue;
      const controller = new AbortController();
      this.pending.set(frame, controller);
      void this.load(frame, controller.signal)
        .then((image) => {
          if (this.disposed || controller.signal.aborted) {
            image.close();
            return;
          }
          this.cache.set(frame, image);
          if (frame === this.source(this.target))
            this.display(image, this.target);
          while (this.cache.size > this.options.capacity) {
            const oldest = [...this.cache.keys()].find(
              (key) => key !== this.source(this.target),
            )!;
            this.cache.get(oldest)!.close();
            this.cache.delete(oldest);
          }
        })
        .catch(() => {
          if (this.disposed || controller.signal.aborted) return;
          this.failed.add(frame);
          if (frame === this.source(this.target)) this.error(this.target);
        })
        .finally(() => {
          this.pending.delete(frame);
          // A fast reversal may target a decode that was already cancelled.
          // It must be retried even if the pointer stops on this exact frame.
          if (controller.signal.aborted && frame === this.source(this.target)) {
            this.queue.unshift(frame);
          }
          this.pump();
        });
    }
  }
  dispose() {
    this.disposed = true;
    for (const controller of this.pending.values()) controller.abort();
    for (const image of this.cache.values()) image.close();
    this.cache.clear();
    this.queue = [];
  }
}
