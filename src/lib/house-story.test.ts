import { describe, expect, it, vi } from 'vitest';
import {
  FrameQueue,
  ScrollPlayback,
  followScroll,
  nextMotionFrame,
  chapterAt,
  chapterProgress,
  frameAt,
  frameUrl,
  houseManifest,
  houseScrollLength,
  createScrollTimeline,
  progressAtFrame,
  sourceFrame,
  scrollProgressAtTimeline,
  timelineProgressAtScroll,
} from './house-story';

describe('shared Blender timeline', () => {
  it('uses native chapter boundaries without requiring stationary reading poses', () => {
    houseManifest.chapters.forEach((chapter, index) => {
      expect(chapterAt(chapter.start)).toBe(index);
      expect(chapterAt(chapterProgress(index))).toBe(index);
      if (index > 0) expect(chapterAt(chapter.start - 0.00001)).toBe(index - 1);
    });
  });
  it('clamps edges and maps to exported frames in both render profiles', () => {
    expect(frameAt(-1)).toBe(1);
    expect(frameAt(2)).toBe(1441);
    expect(frameAt(NaN)).toBe(1);
    for (const profile of ['desktop', 'mobile'] as const) {
      const step = houseManifest.profiles[profile].step;
      for (let frame = 1; frame <= 1441; frame++) {
        const sampled = frameAt(progressAtFrame(frame), profile);
        expect((sampled - 1) % step).toBe(0);
        expect(Math.abs(sampled - frame)).toBeLessThanOrEqual(step / 2);
        expect(sampled).toBeGreaterThanOrEqual(1);
        expect(sampled).toBeLessThanOrEqual(1441);
      }
    }
  });
  it('preserves the project base path', () => {
    expect(frameUrl('/elektro-hubmann/', 'mobile', 1)).toBe(
      `/elektro-hubmann/${houseManifest.assetPath}mobile/frame-0001.webp?v=${houseManifest.revision}`,
    );
  });
  it('resolves long reading holds to a single exported image without alias chains', () => {
    for (const profile of ['desktop', 'mobile'] as const) {
      const step = houseManifest.profiles[profile].step;
      for (let frame = 1; frame <= 1441; frame += step) {
        const source = sourceFrame(profile, frame);
        expect(sourceFrame(profile, source)).toBe(source);
        expect((source - 1) % step).toBe(0);
      }
    }
  });
});

describe('continuous scroll pacing', () => {
  const distance = (a: number, b: number) =>
    (scrollProgressAtTimeline(b) - scrollProgressAtTimeline(a)) *
    houseScrollLength;

  it('removes every consecutive duplicate hold without shortening a movement transition', () => {
    const step = houseManifest.profiles.desktop.step;
    const continuous = houseManifest.revision.startsWith('v4-continuous-');
    for (let frame = 1; frame < houseManifest.frameCount; frame += step) {
      const same = (['desktop', 'mobile'] as const).every(
        (profile) =>
          sourceFrame(profile, frame) === sourceFrame(profile, frame + step),
      );
      expect(
        distance(progressAtFrame(frame), progressAtFrame(frame + step)),
      ).toBeCloseTo(
        same && !continuous ? 0 : step / (houseManifest.frameCount - 1),
        12,
      );
    }
    if (continuous) expect(houseScrollLength).toBe(1);
    else expect(houseScrollLength).toBeLessThan(0.6);
  });

  it('preserves the visible image through scrolling, reversal and resize restoration', () => {
    let previous = -1;
    for (let frame = 1; frame <= houseManifest.frameCount; frame++) {
      const native = progressAtFrame(frame);
      const scroll = scrollProgressAtTimeline(native);
      expect(scroll).toBeGreaterThanOrEqual(previous);
      const restored = timelineProgressAtScroll(scroll);
      for (const profile of ['desktop', 'mobile'] as const) {
        expect(sourceFrame(profile, frameAt(restored, profile))).toBe(
          sourceFrame(profile, frameAt(native, profile)),
        );
      }
      previous = scroll;
    }
    for (let index = 1000; index >= 0; index--) {
      const scroll = index / 1000;
      expect(
        scrollProgressAtTimeline(timelineProgressAtScroll(scroll)),
      ).toBeCloseTo(scroll, 12);
    }
  });

  it('lands every chapter button on the intended native rest frame', () => {
    houseManifest.chapters.forEach((_, index) => {
      const rest = chapterProgress(index);
      const restored = timelineProgressAtScroll(scrollProgressAtTimeline(rest));
      expect(chapterAt(restored)).toBe(index);
      for (const profile of ['desktop', 'mobile'] as const) {
        expect(sourceFrame(profile, frameAt(restored, profile))).toBe(
          sourceFrame(profile, frameAt(rest, profile)),
        );
      }
    });
  });

  it('clamps scroll endpoints without losing the opening or closing image', () => {
    for (const map of [scrollProgressAtTimeline, timelineProgressAtScroll]) {
      expect(map(-1)).toBe(map(0));
      expect(map(NaN)).toBe(map(0));
      expect(map(1)).toBe(1);
      expect(map(2)).toBe(1);
    }
    expect(sourceFrame('desktop', frameAt(timelineProgressAtScroll(0)))).toBe(
      sourceFrame('desktop', 1),
    );
    expect(sourceFrame('desktop', frameAt(timelineProgressAtScroll(1)))).toBe(
      sourceFrame('desktop', houseManifest.frameCount),
    );
  });

  it('jumps to the end of an identical pose and then interpolates only the next moving interval', () => {
    const sources = [1, 1, 1, 4, 5, 5, 5, 8, 9, 9, 9];
    const map = createScrollTimeline(
      sources.length,
      1,
      (a, b) => sources[a - 1] === sources[b - 1],
    );
    expect(map.length).toBe(0.4);
    expect(map.toTimeline(0)).toBe(0.2);
    expect(map.toTimeline(0.5)).toBe(0.6);
    expect(map.toTimeline(0.525)).toBeCloseTo(0.61);
    expect(map.toScroll(0.4)).toBe(0.5);
    expect(map.toScroll(0.5)).toBe(0.5);
    expect(map.toScroll(0.6)).toBe(0.5);
    expect(
      [0, 0.25, 0.5, 0.75, 1].map(
        (p) => sources[Math.round(map.toTimeline(p) * 10)],
      ),
    ).toEqual([1, 4, 5, 8, 9]);
  });

  it('retains returning images and is an exact identity when every frame moves', () => {
    const returned = [1, 1, 3, 1, 1];
    const returning = createScrollTimeline(
      5,
      1,
      (a, b) => returned[a - 1] === returned[b - 1],
    );
    expect(returning.length).toBe(0.5);
    expect(returning.toTimeline(0.5)).toBe(0.5);
    const continuous = createScrollTimeline(1441, 2, () => false);
    expect(continuous.length).toBe(1);
    for (let index = 0; index <= 1000; index++) {
      expect(continuous.toTimeline(index / 1000)).toBeCloseTo(index / 1000, 12);
      expect(continuous.toScroll(index / 1000)).toBeCloseTo(index / 1000, 12);
    }
  });

  it('handles a completely static or single-frame sequence without a division by zero', () => {
    for (const count of [1, 11]) {
      const map = createScrollTimeline(count, 1, () => true);
      expect(map.length).toBe(0);
      expect(map.toTimeline(0.5)).toBe(0);
      expect(map.toScroll(0.5)).toBe(0);
    }
  });
});

const bitmap = () => ({ width: 100, height: 100, close: vi.fn() });
type Bitmap = ReturnType<typeof bitmap>;
const settle = async () => {
  for (let i = 0; i < 8; i++) await Promise.resolve();
};

describe('frame loading during scrubbing', () => {
  it('does not evict and decode upcoming frames again during a forward run', async () => {
    const load = vi.fn(async (_frame: number, _signal: AbortSignal) =>
      bitmap(),
    );
    const queue = new FrameQueue(load, vi.fn(), vi.fn(), {
      capacity: 6,
      concurrency: 3,
      count: 100,
      step: 1,
    });
    for (let frame = 1; frame <= 40; frame++) {
      queue.request(frame);
      for (let i = 0; i < 5; i++) await settle();
      expect(queue.has(frame)).toBe(true);
    }
    const decoded = load.mock.calls.map((call) => call[0]);
    expect(new Set(decoded).size).toBe(decoded.length);
    queue.dispose();
  });

  it('decodes aliases once and still displays the latest timeline position', async () => {
    let finish!: (image: Bitmap) => void;
    const load = vi.fn(
      () =>
        new Promise<Bitmap>((resolve) => {
          finish = resolve;
        }),
    );
    const display = vi.fn();
    const queue = new FrameQueue(load, display, vi.fn(), {
      capacity: 2,
      concurrency: 3,
      count: 7,
      step: 1,
      resolveFrame: () => 1,
    });
    queue.request(1);
    queue.request(5);
    const image = bitmap();
    finish(image);
    await settle();
    expect(load).toHaveBeenCalledTimes(1);
    expect(display).toHaveBeenLastCalledWith(image, 5);
    queue.request(7);
    expect(load).toHaveBeenCalledTimes(1);
    expect(display).toHaveBeenLastCalledWith(image, 7);
    queue.request(1);
    expect(display).toHaveBeenLastCalledWith(image, 1);
    expect(load).toHaveBeenCalledTimes(1);
    queue.dispose();
    expect(image.close).toHaveBeenCalledOnce();
  });
  it('discards a late decode after a jump and keeps the current bitmap cached', async () => {
    const loads = new Map<number, (image: Bitmap) => void>();
    const display = vi.fn();
    const queue = new FrameQueue<Bitmap>(
      (frame) => new Promise((resolve) => loads.set(frame, resolve)),
      display,
      vi.fn(),
      { capacity: 3, concurrency: 2, step: 1, count: 181 },
    );
    queue.request(1);
    queue.request(100);
    const stale = bitmap();
    loads.get(1)!(stale);
    await settle();
    expect(display).not.toHaveBeenCalled();
    expect(stale.close).toHaveBeenCalledOnce();
    const target = bitmap();
    loads.get(100)!(target);
    await settle();
    expect(display).toHaveBeenLastCalledWith(target, 100);
    queue.request(100);
    expect(display).toHaveBeenLastCalledWith(target, 100);
    queue.dispose();
    expect(target.close).toHaveBeenCalledOnce();
  });
  it('keeps an in-flight decode useful through a fast reversal', async () => {
    let first!: (image: Bitmap) => void;
    let far!: (image: Bitmap) => void;
    let firstLoads = 0;
    const display = vi.fn();
    const error = vi.fn();
    const load = (frame: number): Promise<Bitmap> => {
      if (frame === 1 && ++firstLoads === 1)
        return new Promise((resolve) => {
          first = resolve;
        });
      if (frame === 100)
        return new Promise((resolve) => {
          far = resolve;
        });
      return Promise.resolve(bitmap());
    };
    const queue = new FrameQueue(load, display, error, {
      capacity: 24,
      concurrency: 3,
      step: 1,
      count: 181,
    });
    queue.request(1);
    for (let i = 0; i < 8; i++) await settle();
    queue.request(100);
    for (let i = 0; i < 8; i++) await settle();
    queue.request(1);
    const stale = bitmap();
    first(stale);
    for (let i = 0; i < 8; i++) await settle();
    expect(firstLoads).toBe(1);
    expect(stale.close).not.toHaveBeenCalled();
    expect(display.mock.lastCall?.[1]).toBe(1);
    expect(error).not.toHaveBeenCalled();
    queue.dispose();
    far(bitmap());
    await settle();
  });
  it('reports only a current failure and does not retry it on every scroll event', async () => {
    const load = vi.fn().mockRejectedValue(new Error('404'));
    const error = vi.fn();
    const queue = new FrameQueue(load, vi.fn(), error, {
      capacity: 2,
      concurrency: 1,
      step: 1,
      count: 1,
    });
    queue.request(1);
    await settle();
    queue.request(1);
    await settle();
    expect(load).toHaveBeenCalledTimes(1);
    expect(error).toHaveBeenCalledWith(1);
    queue.dispose();
  });
  it('frees decoded images on eviction and even when a decode finishes after disposal', async () => {
    const images: Bitmap[] = [];
    const queue = new FrameQueue(
      async () => {
        const image = bitmap();
        images.push(image);
        return image;
      },
      vi.fn(),
      vi.fn(),
      { capacity: 2, concurrency: 1, step: 1, count: 4 },
    );
    queue.request(1);
    for (let i = 0; i < 4; i++) await settle();
    expect(
      images.filter((image) => !image.close.mock.calls.length),
    ).toHaveLength(2);
    queue.dispose();
    expect(images.every((image) => image.close.mock.calls.length === 1)).toBe(
      true,
    );
    let finish!: (image: Bitmap) => void;
    const display = vi.fn();
    const lateQueue = new FrameQueue<Bitmap>(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
      display,
      vi.fn(),
      { capacity: 1, concurrency: 1, step: 1, count: 1 },
    );
    lateQueue.request(1);
    lateQueue.dispose();
    const late = bitmap();
    finish(late);
    await settle();
    expect(late.close).toHaveBeenCalledOnce();
    expect(display).not.toHaveBeenCalled();
  });
});

describe('responsive native scroll playback', () => {
  const profile = 'desktop';
  const step = houseManifest.profiles[profile].step;
  const createQueue = (
    load: (frame: number, signal: AbortSignal) => Promise<Bitmap>,
    display = vi.fn(),
  ) =>
    new FrameQueue(load, display, vi.fn(), {
      capacity: 12,
      concurrency: 3,
      step,
      count: houseManifest.frameCount,
      resolveFrame: (frame) => sourceFrame(profile, frame),
    });

  it('follows equally over time at 30, 60 and 120 Hz and reverses without overshoot', () => {
    const positions = [30, 60, 120].map((hz) => {
      let position = 0;
      for (let i = 0; i < hz; i++)
        position = followScroll(position, 1, 1000 / hz);
      return position;
    });
    expect(positions[0]).toBeCloseTo(positions[1]!, 10);
    expect(positions[1]).toBeCloseTo(positions[2]!, 10);
    const reversed = followScroll(0.4, 0.1, 16);
    expect(reversed).toBeLessThan(0.4);
    expect(reversed).toBeGreaterThan(0.1);
  });

  it('loads distinct upcoming frames even while parked on a long reading hold', async () => {
    const load = vi.fn(async () => bitmap());
    const queue = createQueue(load);
    queue.request(1);
    for (let i = 0; i < 20; i++) await settle();
    expect(load.mock.calls.length).toBe(12);
    expect(queue.has(nextMotionFrame(1, frameAt(0.2), profile))).toBe(true);
    queue.dispose();
  });

  it('catches up within one second at 30, 60 and 120 Hz without a native-frame backlog', async () => {
    for (const hz of [30, 60, 120]) {
      const display = vi.fn();
      const queue = createQueue(async () => bitmap(), display);
      const playback = new ScrollPlayback(queue, profile);
      playback.seek(0.08);
      await settle();
      playback.follow(0.91);
      for (let i = 0; i < hz; i++) {
        playback.tick(((i + 1) * 1000) / hz);
        await settle();
      }
      expect(sourceFrame(profile, display.mock.lastCall![1])).toBe(
        sourceFrame(profile, frameAt(0.91)),
      );
      const forward = display.mock.calls.map((call) => call[1] as number);
      expect(forward).toEqual([...forward].sort((a, b) => a - b));
      display.mockClear();
      playback.follow(0.08);
      for (let i = 0; i < hz; i++) {
        playback.tick(1000 + ((i + 1) * 1000) / hz);
        await settle();
      }
      expect(
        Math.abs(display.mock.lastCall![1] - frameAt(0.08)),
      ).toBeLessThanOrEqual(step);
      const backward = display.mock.calls.map((call) => call[1] as number);
      expect(backward).toEqual([...backward].sort((a, b) => b - a));
      queue.dispose();
    }
  });

  it('does not wait for an obsolete missing frame or display its late decode', async () => {
    const start = frameAt(0.12);
    const blocked = sourceFrame(profile, start + step);
    let finish!: (image: Bitmap) => void;
    let signal!: AbortSignal;
    const display = vi.fn();
    const queue = createQueue(async (frame, pendingSignal) => {
      if (frame === blocked) {
        signal = pendingSignal;
        return new Promise<Bitmap>((resolve) => {
          finish = resolve;
        });
      }
      return bitmap();
    }, display);
    const playback = new ScrollPlayback(queue, profile);
    playback.seek(progressAtFrame(start));
    await settle();
    playback.follow(0.3);
    for (let i = 0; i < 70; i++) {
      playback.tick((i * 1000) / 60);
      await settle();
    }
    expect(sourceFrame(profile, display.mock.lastCall![1])).toBe(
      sourceFrame(profile, frameAt(0.3)),
    );
    expect(signal.aborted).toBe(false);
    const late = bitmap();
    finish(late);
    await settle();
    expect(sourceFrame(profile, display.mock.lastCall![1])).toBe(
      sourceFrame(profile, frameAt(0.3)),
    );
    expect(late.close).toHaveBeenCalledOnce();
    queue.dispose();
  });

  it('stops requesting animation ticks once time settles, even if downloads are pending', async () => {
    const queue = createQueue(() => new Promise<Bitmap>(() => {}));
    const request = vi.spyOn(queue, 'request');
    const playback = new ScrollPlayback(queue, profile);
    playback.seek(0);
    playback.follow(0.63);
    let running = true;
    for (let i = 0; i < 90 && running; i++)
      running = playback.tick((i * 1000) / 60);
    expect(running).toBe(false);
    expect(sourceFrame(profile, request.mock.lastCall![0])).toBe(
      sourceFrame(profile, frameAt(0.63)),
    );
    queue.dispose();
  });

  it('smooths across a collapsed installation hold in scroll space without waiting inside it', () => {
    const queue = createQueue(() => new Promise<Bitmap>(() => {}));
    const request = vi.spyOn(queue, 'request');
    const playback = new ScrollPlayback(queue, profile);
    playback.seek(0.35);
    const initial = sourceFrame(profile, request.mock.lastCall![0]);
    playback.follow(0.395);
    playback.tick(0);
    expect(sourceFrame(profile, request.mock.lastCall![0])).not.toBe(initial);
    queue.dispose();
  });

  it('uses decoded intermediate poses without being pulled backward by a late image', async () => {
    const loads = new Map<number, (image: Bitmap) => void>();
    const display = vi.fn();
    const queue = new FrameQueue<Bitmap>(
      (frame) => new Promise((resolve) => loads.set(frame, resolve)),
      display,
      vi.fn(),
      { capacity: 5, concurrency: 3, step: 1, count: 7 },
    );
    queue.request(1);
    loads.get(1)!(bitmap());
    await settle();
    queue.request(5);
    loads.get(3)!(bitmap());
    await settle();
    expect(display.mock.lastCall?.[1]).toBe(3);
    const late = bitmap();
    loads.get(2)!(late);
    await settle();
    expect(display.mock.lastCall?.[1]).toBe(3);
    loads.get(5)!(bitmap());
    await settle();
    expect(display.mock.calls.map((call) => call[1])).toEqual([1, 3, 5]);
    queue.dispose();
  });
});
