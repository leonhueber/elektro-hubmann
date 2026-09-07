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
  progressAtFrame,
  sourceFrame,
} from './house-story';

describe('shared Blender timeline', () => {
  it('uses the designed unequal chapter boundaries, including opening and closing', () => {
    expect(
      [0, 0.079, 0.08, 0.389, 0.39, 0.51, 0.67, 0.82, 1].map(chapterAt),
    ).toEqual([0, 0, 1, 1, 2, 3, 4, 5, 5]);
    houseManifest.chapters.forEach((_, index) =>
      expect(chapterAt(chapterProgress(index))).toBe(index),
    );
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
      expect(sourceFrame(profile, 57)).toBe(1);
      expect(sourceFrame(profile, 113)).toBe(1);
      const step = houseManifest.profiles[profile].step;
      for (let frame = 1; frame <= 1441; frame += step) {
        const source = sourceFrame(profile, frame);
        expect(sourceFrame(profile, source)).toBe(source);
        expect((source - 1) % step).toBe(0);
      }
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
  it('recovers when a fast reversal stops on an already cancelled decode', async () => {
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
    expect(firstLoads).toBe(2);
    expect(stale.close).toHaveBeenCalledOnce();
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

describe('buffered scroll playback', () => {
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

  it('visits every native motion image after a large scroll jump, in both directions', async () => {
    const display = vi.fn();
    const queue = createQueue(async () => bitmap(), display);
    const playback = new ScrollPlayback(queue, profile);
    playback.seek(0.08);
    await settle();
    playback.follow(0.3);
    let time = 0;
    for (let i = 0; i < 900; i++) {
      const running = playback.tick((time += 1000 / 60));
      await settle();
      if (!running) break;
    }
    const expected = [
      ...new Set(
        Array.from(
          { length: (frameAt(0.3) - frameAt(0.08)) / step + 1 },
          (_, i) => sourceFrame(profile, frameAt(0.08) + i * step),
        ),
      ),
    ];
    expect([
      ...new Set(
        display.mock.calls.map((call) => sourceFrame(profile, call[1])),
      ),
    ]).toEqual(expected);
    expect(display.mock.lastCall?.[1]).toBe(frameAt(0.3));
    display.mockClear();
    playback.follow(0.08);
    for (let i = 0; i < 900; i++) {
      const running = playback.tick((time += 1000 / 60));
      await settle();
      if (!running) break;
    }
    expect([
      ...new Set(
        display.mock.calls.map((call) => sourceFrame(profile, call[1])),
      ),
    ]).toEqual(expected.slice(0, -1).reverse());
    expect(display.mock.lastCall?.[1]).toBe(frameAt(0.08));
    queue.dispose();
  });

  it('waits for a delayed frame instead of cancelling it or jumping ahead', async () => {
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
    for (let i = 0; i < 60; i++) {
      playback.tick(i * 16);
      await settle();
    }
    expect(display.mock.lastCall?.[1]).toBe(start);
    expect(signal.aborted).toBe(false);
    finish(bitmap());
    await settle();
    expect(display.mock.lastCall?.[1]).toBe(start + step);
    playback.follow(progressAtFrame(start));
    for (let i = 60; i < 160; i++) {
      playback.tick(i * 16);
      await settle();
    }
    expect(display.mock.lastCall?.[1]).toBe(start);
    queue.dispose();
  });
});
