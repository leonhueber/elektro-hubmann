import manifest from '../config/house-v3-manifest.json';
import aliases from '../config/house-v3-frames.json';
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
/** Labels are projected for a fixed camera pose and stay hidden during travel. */
export function annotationsVisible(progress: number) {
  const chapter = manifest.chapters[chapterAt(progress)]!;
  const range = (chapter as { annotationFrames?: number[] }).annotationFrames;
  if (!range) return false;
  const frame = 1 + clampProgress(progress) * (manifest.frameCount - 1);
  return frame >= range[0]! && frame <= range[1]!;
}
export function frameUrl(base: string, profile: HouseProfile, frame: number) {
  const source =
    (aliases[profile] as Record<string, number>)[String(frame)] ?? frame;
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

/** Bounded decoder queue. Only the current target may become visible. */
export class FrameQueue<T extends DecodedFrame> {
  private cache = new Map<number, T>();
  private pending = new Set<number>();
  private failed = new Set<number>();
  private queue: number[] = [];
  private target = 1;
  private disposed = false;
  private controller = new AbortController();
  constructor(
    private load: (frame: number, signal: AbortSignal) => Promise<T>,
    private display: (image: T, frame: number) => void,
    private error: (frame: number) => void,
    private options = { capacity: 18, concurrency: 3, step: 1, count: 181 },
  ) {}
  request(frame: number) {
    if (this.disposed) return;
    const direction = frame >= this.target ? 1 : -1;
    this.target = frame;
    const cached = this.cache.get(frame);
    if (cached) {
      this.cache.delete(frame);
      this.cache.set(frame, cached);
      this.display(cached, frame);
    } else if (this.failed.has(frame)) {
      this.error(frame);
    }
    this.queue = [frame];
    for (let offset = 1; offset <= 5; offset++) {
      this.queue.push(
        frame + offset * direction * this.options.step,
        frame - offset * direction * this.options.step,
      );
    }
    this.queue = this.queue.filter(
      (candidate) => candidate >= 1 && candidate <= this.options.count,
    );
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
      this.pending.add(frame);
      void this.load(frame, this.controller.signal)
        .then((image) => {
          if (this.disposed) {
            image.close();
            return;
          }
          this.cache.set(frame, image);
          if (frame === this.target) this.display(image, frame);
          while (this.cache.size > this.options.capacity) {
            const oldest = [...this.cache.keys()].find(
              (key) => key !== this.target,
            )!;
            this.cache.get(oldest)!.close();
            this.cache.delete(oldest);
          }
        })
        .catch(() => {
          if (this.disposed) return;
          this.failed.add(frame);
          if (frame === this.target) this.error(frame);
        })
        .finally(() => {
          this.pending.delete(frame);
          this.pump();
        });
    }
  }
  dispose() {
    this.disposed = true;
    this.controller.abort();
    for (const image of this.cache.values()) image.close();
    this.cache.clear();
    this.queue = [];
  }
}
