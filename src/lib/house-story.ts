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
/** Time-based follow, independent of wheel frequency and display refresh rate. */
export function followScroll(
  position: number,
  target: number,
  deltaMs: number,
) {
  const amount = -Math.expm1(-Math.max(0, Math.min(50, deltaMs)) / 150);
  return position + (clampProgress(target) - position) * amount;
}

/** Cross a reading hold freely, but never skip a distinct native motion image. */
export function nextMotionFrame(
  from: number,
  toward: number,
  profile: HouseProfile,
) {
  if (from === toward) return toward;
  const step = manifest.profiles[profile].step * Math.sign(toward - from);
  const source = sourceFrame(profile, from);
  for (
    let frame = from + step;
    step > 0 ? frame <= toward : frame >= toward;
    frame += step
  ) {
    if (sourceFrame(profile, frame) !== source) return frame;
  }
  return toward;
}
export function sourceFrame(profile: HouseProfile, frame: number) {
  return (aliases[profile] as Record<string, number>)[String(frame)] ?? frame;
}
export function frameUrl(base: string, profile: HouseProfile, frame: number) {
  const source = sourceFrame(profile, frame);
  return `${base}${manifest.assetPath}${profile}/frame-${String(source).padStart(4, '0')}.webp?v=${manifest.revision}`;
}
export function posterUrl(
  base: string,
  profile: HouseProfile,
  chapter: number,
) {
  return `${base}${manifest.assetPath}${profile}/${manifest.chapters[chapter]!.id}.webp?v=${manifest.revision}`;
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
  private wanted = new Set<number>();
  private target = 1;
  private direction = 1;
  private requested = false;
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
  has(frame: number) {
    return this.cache.has(this.source(frame));
  }
  request(frame: number) {
    if (this.disposed) return;
    if (this.requested && frame === this.target) return;
    this.requested = true;
    if (frame !== this.target) this.direction = Math.sign(frame - this.target);
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
    // Count distinct images, not aliased timeline positions. Prefetch across
    // long holds so the first camera movement is already decoded when needed.
    const ahead = this.neighbors(frame, this.direction);
    const behind = this.neighbors(frame, -this.direction);
    const wanted = new Set([source]);
    while (
      wanted.size < this.options.capacity &&
      (ahead.length || behind.length)
    ) {
      for (const candidates of [ahead, ahead, behind]) {
        if (wanted.size < this.options.capacity && candidates.length)
          wanted.add(candidates.shift()!);
      }
    }
    this.wanted = wanted;
    this.queue = [...wanted];
    for (const [frame, controller] of this.pending) {
      if (!this.queue.includes(frame)) controller.abort();
    }
    this.pump();
  }
  private neighbors(frame: number, direction: number) {
    const found = new Set<number>();
    const current = this.source(frame);
    const step = direction * this.options.step;
    for (
      let next = frame + step;
      next >= 1 && next <= this.options.count;
      next += step
    ) {
      const source = this.source(next);
      if (source !== current) found.add(source);
      if (found.size >= this.options.capacity) break;
    }
    return [...found];
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
            const keys = [...this.cache.keys()];
            const oldest =
              keys.find((key) => !this.wanted.has(key)) ??
              keys.find((key) => key !== this.source(this.target))!;
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

/** A buffered playhead: scroll chooses the destination, decoded frames set pace. */
export class ScrollPlayback<T extends DecodedFrame> {
  private position = 0;
  private target = 0;
  private lastTime: number | undefined;
  constructor(
    private frames: FrameQueue<T>,
    private profile: HouseProfile,
  ) {}
  seek(progress: number) {
    this.position = this.target = clampProgress(progress);
    this.lastTime = undefined;
    this.frames.request(frameAt(this.position, this.profile));
  }
  follow(progress: number) {
    this.target = clampProgress(progress);
  }
  tick(time: number) {
    const delta =
      this.lastTime === undefined ? 1000 / 60 : time - this.lastTime;
    const proposed =
      Math.abs(this.target - this.position) < 0.00001
        ? this.target
        : followScroll(this.position, this.target, delta);
    const wanted = frameAt(proposed, this.profile);
    const next = nextMotionFrame(
      frameAt(this.position, this.profile),
      wanted,
      this.profile,
    );
    this.frames.request(next);
    // Never run the clock past a missing frame and catch up with a visible jump.
    if (this.frames.has(next))
      this.position = next === wanted ? proposed : progressAtFrame(next);
    const running = this.position !== this.target || !this.frames.has(next);
    this.lastTime = running ? time : undefined;
    return running;
  }
}
