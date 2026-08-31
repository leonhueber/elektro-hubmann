import { describe, expect, it } from 'vitest';
import { VERSION_G_STORY_CHAPTERS } from '../../../config/version-g-story-assets';
import { getSceneMotion, getStoryState } from './HouseStory';

describe('getStoryState', () => {
  it('maps every chapter center to its state', () => {
    VERSION_G_STORY_CHAPTERS.forEach((chapter, index) => {
      const center = (index + 0.5) / VERSION_G_STORY_CHAPTERS.length;
      expect(getStoryState(center)).toBe(chapter.id);
    });
  });

  it('clamps progress to the first and final state', () => {
    expect(getStoryState(-1)).toBe('planning');
    expect(getStoryState(2)).toBe('service');
  });
});

describe('getSceneMotion', () => {
  it('keeps one scene fully visible in the middle of a chapter', () => {
    const center = 0.5 / VERSION_G_STORY_CHAPTERS.length;
    expect(getSceneMotion(center, 0).opacity).toBe(1);
    expect(getSceneMotion(center, 1).opacity).toBe(0);
  });

  it.each(VERSION_G_STORY_CHAPTERS.slice(1).map((_, index) => index + 1))(
    'crossfades evenly at chapter boundary %s',
    (nextScene) => {
      const progress = nextScene / VERSION_G_STORY_CHAPTERS.length;
      const previousOpacity = getSceneMotion(progress, nextScene - 1).opacity;
      const nextOpacity = getSceneMotion(progress, nextScene).opacity;
      expect(previousOpacity).toBeCloseTo(0.5, 5);
      expect(nextOpacity).toBeCloseTo(0.5, 5);
      expect(previousOpacity + nextOpacity).toBeCloseTo(1, 5);
    },
  );

  it('clamps progress before calculating the image motion', () => {
    expect(getSceneMotion(-1, 0).opacity).toBe(1);
    expect(getSceneMotion(2, VERSION_G_STORY_CHAPTERS.length - 1).opacity).toBe(
      1,
    );
  });

  it('uses a restrained motion profile on compact screens', () => {
    const progress = 0.5 / VERSION_G_STORY_CHAPTERS.length;
    const standard = getSceneMotion(progress, 1, 'standard');
    const compact = getSceneMotion(progress, 1, 'compact');

    expect(Math.abs(compact.x)).toBeLessThan(Math.abs(standard.x));
    expect(Math.abs(compact.y)).toBeLessThan(Math.abs(standard.y));
    expect(Math.abs(1 - compact.scale)).toBeLessThan(
      Math.abs(1 - standard.scale),
    );
  });

  it('keeps compact crossfades balanced at chapter boundaries', () => {
    const nextScene = 1;
    const progress = nextScene / VERSION_G_STORY_CHAPTERS.length;
    const previous = getSceneMotion(progress, nextScene - 1, 'compact');
    const next = getSceneMotion(progress, nextScene, 'compact');

    expect(previous.opacity).toBeCloseTo(0.5, 5);
    expect(next.opacity).toBeCloseTo(0.5, 5);
  });
});
