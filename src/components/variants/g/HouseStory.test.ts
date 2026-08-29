import { describe, expect, it } from 'vitest';
import { getFrameIndex, getStoryState } from './HouseStory';

describe('getStoryState', () => {
  it.each([
    [0, 'planning'],
    [0.239, 'planning'],
    [0.24, 'installation'],
    [0.509, 'installation'],
    [0.51, 'energy'],
    [0.779, 'energy'],
    [0.78, 'service'],
    [1, 'service'],
  ] as const)('maps %s to %s', (progress, expected) => {
    expect(getStoryState(progress)).toBe(expected);
  });

  it('maps scroll progress to the rendered Blender sequence', () => {
    expect(getFrameIndex(-1)).toBe(0);
    expect(getFrameIndex(0)).toBe(0);
    expect(getFrameIndex(0.5)).toBe(60);
    expect(getFrameIndex(1)).toBe(119);
    expect(getFrameIndex(2)).toBe(119);
  });
});
