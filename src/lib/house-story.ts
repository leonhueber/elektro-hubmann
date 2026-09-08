import manifest from '../config/house-v4-manifest.json';
import aliases from '../config/house-v4-frames.json';
export { manifest as houseManifest };
export type HouseProfile = keyof typeof manifest.profiles;
export const clampProgress = (value: number) =>
  Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : 0;

/** Remove only adjacent duplicate images; keep every native movement interval. */
export function createScrollTimeline(
  frameCount: number,
  step: number,
  sameImage: (a: number, b: number) => boolean,
) {
  const extent = Math.max(0, frameCount - 1);
  const intervals: { start: number; end: number; distance: number }[] = [];
  let distance = 0;
  for (let start = 0; start < extent; start += step) {
    const end = Math.min(extent, start + step);
    if (!sameImage(start + 1, end + 1)) {
      intervals.push({ start, end, distance });
      distance += end - start;
    }
  }
  // Search in integer native-frame units. Tolerance only resolves floating-point
  // round trips at an exactly collapsed hold; it is far below one render frame.
  const lastBefore = (value: number, field: 'start' | 'distance') => {
    let low = 0;
    let high = intervals.length;
    while (low < high) {
      const middle = (low + high) >>> 1;
      if (intervals[middle]![field] <= value + 1e-9) low = middle + 1;
      else high = middle;
    }
    return low - 1;
  };
  const within = (value: number, interval: (typeof intervals)[number]) =>
    Math.max(0, Math.min(interval.end - interval.start, value));
  return {
    length: extent ? distance / extent : 0,
    toTimeline(progress: number) {
      if (!distance) return 0;
      const p = clampProgress(progress);
      if (p === 1) return 1;
      const travelled = p * distance;
      const interval =
        intervals[Math.max(0, lastBefore(travelled, 'distance'))]!;
      // Right-continuity jumps to the END of an identical pose. Interpolating
      // across that pose would reintroduce a long hold before the next image.
      return (
        (interval.start + within(travelled - interval.distance, interval)) /
        extent
      );
    },
    toScroll(progress: number) {
      if (!distance) return 0;
      const native = clampProgress(progress) * extent;
      const index = lastBefore(native, 'start');
      if (index < 0) return 0;
      const interval = intervals[index]!;
      return (
        (interval.distance + within(native - interval.start, interval)) /
        distance
      );
    },
  };
}

const profiles = Object.keys(manifest.profiles) as HouseProfile[];
const gcd = (a: number, b: number): number => (b ? gcd(b, a % b) : a);
const timing = createScrollTimeline(
  manifest.frameCount,
  profiles.map((profile) => manifest.profiles[profile].step).reduce(gcd),
  manifest.revision.startsWith('v4-continuous-')
    ? () => false
    : (a, b) =>
        profiles.every(
          (profile) =>
            sourceFrame(profile, frameAt(progressAtFrame(a), profile)) ===
            sourceFrame(profile, frameAt(progressAtFrame(b), profile)),
        ),
);
export const houseScrollLength = timing.length;
export const timelineProgressAtScroll = timing.toTimeline;
export const scrollProgressAtTimeline = timing.toScroll;

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
  const amount = -Math.expm1(-Math.max(0, Math.min(50, deltaMs)) / 100);
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
  private displayed: number | undefined;
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
    this.present();
    if (this.failed.has(source)) this.error(frame);
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
    // Finish the bounded in-flight batch. Repeated cancellation can starve
    // decoding while a wheel or trackpad keeps changing the target.
    this.pump();
  }
  private present() {
    // Only move toward the current scroll target. Late images cannot pull the
    // view backward or overshoot it; an exact decoded target always wins.
    const direction = Math.sign((this.displayed ?? this.target) - this.target);
    const step = direction * this.options.step;
    for (let frame = this.target; ; frame += step) {
      const source = this.source(frame);
      const image = this.cache.get(source);
      if (image) {
        this.cache.delete(source);
        this.cache.set(source, image);
        if (this.displayed !== frame) this.display(image, frame);
        this.displayed = frame;
        return;
      }
      if (!step || frame === this.displayed) return;
    }
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
          this.present();
          if (
            !this.wanted.has(frame) &&
            (this.displayed === undefined ||
              this.source(this.displayed) !== frame)
          ) {
            image.close();
            this.cache.delete(frame);
          }
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

/** Scroll drives elapsed time, even when image downloads are still pending. */
export class ScrollPlayback<T extends DecodedFrame> {
  private position = 0;
  private target = 0;
  private lastTime: number | undefined;
  constructor(
    private frames: FrameQueue<T>,
    private profile: HouseProfile,
  ) {}
  seek(progress: number) {
    this.position = this.target = scrollProgressAtTimeline(progress);
    this.lastTime = undefined;
    this.frames.request(
      frameAt(timelineProgressAtScroll(this.position), this.profile),
    );
  }
  follow(progress: number) {
    this.target = scrollProgressAtTimeline(progress);
  }
  tick(time: number) {
    const delta =
      this.lastTime === undefined ? 1000 / 60 : time - this.lastTime;
    this.position =
      Math.abs(this.target - this.position) < 0.00001
        ? this.target
        : followScroll(this.position, this.target, delta);
    this.frames.request(
      frameAt(timelineProgressAtScroll(this.position), this.profile),
    );
    const running = this.position !== this.target;
    // The decoder can present the final frame without an idle animation loop.
    this.lastTime = running ? time : undefined;
    return running;
  }
}
