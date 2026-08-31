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
});
