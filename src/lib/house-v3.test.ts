import { describe, expect, it, vi } from 'vitest';
import {
  FrameQueue,
  annotationsVisible,
  chapterAt,
  chapterProgress,
  frameAt,
  frameUrl,
  houseManifest,
  progressAtFrame,
} from './house-v3';

describe('shared Blender timeline', () => {
  it('uses the designed unequal chapter boundaries, including opening and closing', () => {
    expect(
      [0, 0.099, 0.1, 0.369, 0.37, 0.51, 0.64, 0.76, 1].map(chapterAt),
    ).toEqual([0, 0, 1, 1, 2, 3, 4, 5, 5]);
    houseManifest.chapters.forEach((_, index) =>
      expect(chapterAt(chapterProgress(index))).toBe(index),
    );
  });
  it('clamps edges and maps to exported frames in both render profiles', () => {
    expect(frameAt(-1)).toBe(1);
    expect(frameAt(2)).toBe(181);
    expect(frameAt(NaN)).toBe(1);
    for (const profile of ['desktop', 'mobile'] as const) {
      const step = houseManifest.profiles[profile].step;
      for (let frame = 1; frame <= 181; frame++) {
        const sampled = frameAt(progressAtFrame(frame), profile);
        expect((sampled - 1) % step).toBe(0);
        expect(Math.abs(sampled - frame)).toBeLessThanOrEqual(step / 2);
        expect(sampled).toBeGreaterThanOrEqual(1);
        expect(sampled).toBeLessThanOrEqual(181);
      }
    }
  });
  it('preserves the project base path', () => {
    expect(frameUrl('/elektro-hubmann/', 'mobile', 1)).toMatch(
      /^\/elektro-hubmann\/images\/version-g\/[^/]+\/mobile\/frame-\d{4}\.webp$/,
    );
  });
  it('keeps fixed labels hidden during camera travel and visible at chapter stops', () => {
    for (const frame of [1, 31, 51, 73, 99, 121, 145, 177, 181]) {
      expect(annotationsVisible(progressAtFrame(frame))).toBe(false);
    }
    for (const frame of [61, 85, 109, 133, 163]) {
      expect(annotationsVisible(progressAtFrame(frame))).toBe(true);
    }
  });
});

const bitmap = () => ({ width: 100, height: 100, close: vi.fn() });
type Bitmap = ReturnType<typeof bitmap>;
const settle = async () => {
  for (let i = 0; i < 8; i++) await Promise.resolve();
};

describe('frame loading during scrubbing', () => {
  it('ignores an old decode after a jump, and revisits cached frames in reverse', async () => {
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
    loads.get(1)!(bitmap());
    await settle();
    expect(display).not.toHaveBeenCalled();
    const target = bitmap();
    loads.get(100)!(target);
    await settle();
    expect(display).toHaveBeenLastCalledWith(target, 100);
    queue.request(1);
    expect(display.mock.lastCall?.[1]).toBe(1);
    queue.dispose();
    expect(target.close).toHaveBeenCalledOnce();
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
