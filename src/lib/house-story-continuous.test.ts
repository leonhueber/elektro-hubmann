import { describe, expect, it, vi } from 'vitest';

// Exercise the future export entirely in memory while production still renders.
vi.mock('../config/house-v4-manifest.json', () => ({
  default: {
    version: 4,
    revision: 'v4-continuous-01',
    frameCount: 1441,
    assetPath: 'images/version-g/house-v4-continuous-r1/',
    profiles: {
      desktop: { width: 960, height: 960, step: 8, cacheFrames: 12 },
      mobile: { width: 720, height: 720, step: 8, cacheFrames: 18 },
    },
    chapters: [
      { id: 'planning', start: 0, rest: 0.035 },
      { id: 'installation', start: 0.12, rest: 0.275 },
      { id: 'smarthome', start: 0.37, rest: 0.535 },
      { id: 'security', start: 0.64, rest: 0.755 },
      { id: 'energy', start: 0.81, rest: 0.95 },
    ],
  },
}));
vi.mock('../config/house-v4-frames.json', () => ({
  default: { desktop: {}, mobile: {} },
}));

import {
  FrameQueue,
  ScrollPlayback,
  chapterAt,
  chapterProgress,
  frameAt,
  frameUrl,
  houseManifest,
  houseScrollLength,
  sourceFrame,
  scrollProgressAtTimeline,
  timelineProgressAtScroll,
} from './house-story';
import { VERSION_G_STORY_CHAPTERS } from '../config/version-g-story-assets';
import { houseSceneCaptionAt } from '../config/house-orientation';

describe('future continuous native export', () => {
  it('uses identity timing and unique assets throughout both render profiles', () => {
    expect(houseManifest.revision).toBe('v4-continuous-01');
    expect(houseScrollLength).toBe(1);
    for (let frame = 1; frame <= 1441; frame += 8) {
      const progress = (frame - 1) / 1440;
      expect(timelineProgressAtScroll(progress)).toBeCloseTo(progress, 12);
      expect(scrollProgressAtTimeline(progress)).toBeCloseTo(progress, 12);
      for (const profile of ['desktop', 'mobile'] as const) {
        expect(frameAt(timelineProgressAtScroll(progress), profile)).toBe(
          frame,
        );
        expect(sourceFrame(profile, frame)).toBe(frame);
      }
    }
    for (const map of [scrollProgressAtTimeline, timelineProgressAtScroll]) {
      expect(map(-1)).toBe(0);
      expect(map(NaN)).toBe(0);
      expect(map(2)).toBe(1);
    }
    expect(frameUrl('/elektro-hubmann/', 'desktop', 769)).toBe(
      '/elektro-hubmann/images/version-g/house-v4-continuous-r1/desktop/frame-0769.webp?v=v4-continuous-01',
    );
  });

  it('lands navigation on the new native poses and selects matching chapter copy', () => {
    const posters = [49, 401, 769, 1089, 1369];
    houseManifest.chapters.forEach((chapter, index) => {
      expect(chapterAt(chapter.start)).toBe(index);
      if (index) expect(chapterAt(chapter.start - 0.00001)).toBe(index - 1);
      const restored = timelineProgressAtScroll(
        scrollProgressAtTimeline(chapterProgress(index)),
      );
      expect(chapterAt(restored)).toBe(index);
      expect(frameAt(restored)).toBe(posters[index]);
      expect(VERSION_G_STORY_CHAPTERS[index]!.id).toBe(chapter.id);
    });
    expect(houseSceneCaptionAt('planning', 0.035)).toBe('');
    expect(houseSceneCaptionAt('smarthome', 0.535)).toBe(
      'Jalousie fährt herunter',
    );
    expect(houseSceneCaptionAt('energy', 0.895)).toBe(
      'Dach und Wallbox verbunden',
    );
    expect(houseSceneCaptionAt('energy', 0.95)).toBe('Solarstrom an der Wallbox');
    expect(VERSION_G_STORY_CHAPTERS[4]!.components).toContain(
      'Wallbox & Überschussladen',
    );
  });

  it('keeps advancing during a steady forward or reverse scroll through every former hold', () => {
    for (const profile of ['desktop', 'mobile'] as const) {
      for (const direction of [1, -1]) {
        const queue = new FrameQueue<ImageBitmap>(
          () => new Promise(() => {}),
          vi.fn(),
          vi.fn(),
          { capacity: 12, concurrency: 3, step: 8, count: 1441 },
        );
        const request = vi.spyOn(queue, 'request');
        const playback = new ScrollPlayback(queue, profile);
        playback.seek(direction === 1 ? 0 : 1);
        let previous = request.mock.lastCall![0];
        let repeatedTicks = 0;
        for (let index = 1; index <= 120; index++) {
          const scroll = direction === 1 ? index / 120 : 1 - index / 120;
          playback.follow(timelineProgressAtScroll(scroll));
          playback.tick((index * 1000) / 60);
          const current = request.mock.lastCall![0];
          const travel = (current - previous) * direction;
          expect(travel).toBeGreaterThanOrEqual(0);
          // A sampled sequence can repeat a frame during startup smoothing;
          // it must not reintroduce stationary chapter-length intervals.
          repeatedTicks = travel === 0 ? repeatedTicks + 1 : 0;
          expect(repeatedTicks).toBeLessThanOrEqual(2);
          previous = current;
        }
        expect(Math.abs(previous - (direction === 1 ? 1 : 1441))).toBeGreaterThan(1300);
        queue.dispose();
      }
    }
  });
});
