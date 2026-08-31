import { describe, expect, it } from 'vitest';
import { getSceneMotion, getStoryState } from './HouseStory';

describe('getStoryState', () => {
  it.each([
    [0, 'planning'],
    [0.249, 'planning'],
    [0.25, 'installation'],
    [0.499, 'installation'],
    [0.5, 'photovoltaic'],
    [0.749, 'photovoltaic'],
    [0.75, 'service'],
    [1, 'service'],
    [2, 'service'],
    [-1, 'planning'],
  ] as const)('maps %s to %s', (progress, expected) => {
    expect(getStoryState(progress)).toBe(expected);
  });
});

describe('getSceneMotion', () => {
  it('keeps one scene fully visible in the middle of a chapter', () => {
    expect(getSceneMotion(0.125, 0).opacity).toBe(1);
    expect(getSceneMotion(0.125, 1).opacity).toBe(0);
  });

  it.each([0.25, 0.5, 0.75])(
    'crossfades evenly at chapter boundary %s',
    (progress) => {
      const nextScene = Math.round(progress * 4);
      const previousOpacity = getSceneMotion(progress, nextScene - 1).opacity;
      const nextOpacity = getSceneMotion(progress, nextScene).opacity;
      expect(previousOpacity).toBeCloseTo(0.5, 5);
      expect(nextOpacity).toBeCloseTo(0.5, 5);
      expect(previousOpacity + nextOpacity).toBeCloseTo(1, 5);
    },
  );

  it('clamps progress before calculating the image motion', () => {
    expect(getSceneMotion(-1, 0).opacity).toBe(1);
    expect(getSceneMotion(2, 3).opacity).toBe(1);
  });
});
