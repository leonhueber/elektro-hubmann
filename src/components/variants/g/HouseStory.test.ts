import { describe, expect, it } from 'vitest';
import {
  getFrameIndex,
  getMobileFrameIndex,
  getStoryState,
} from './HouseStory';

describe('getStoryState', () => {
  it.each([
    [0, 'planning'],
    [0.219, 'planning'],
    [0.22, 'installation'],
    [0.559, 'installation'],
    [0.56, 'energy'],
    [0.819, 'energy'],
    [0.82, 'service'],
    [1, 'service'],
  ] as const)('maps %s to %s', (progress, expected) => {
    expect(getStoryState(progress)).toBe(expected);
  });

  it('maps scroll progress to the rendered Blender sequence', () => {
    expect(getFrameIndex(-1)).toBe(0);
    expect(getFrameIndex(0)).toBe(0);
    expect(getFrameIndex(0.1)).toBe(19);
    expect(getFrameIndex(0.3)).toBe(34);
    expect(getFrameIndex(0.5)).toBe(49);
    expect(getFrameIndex(0.58)).toBe(67);
    expect(getFrameIndex(0.82)).toBe(91);
    expect(getFrameIndex(1)).toBe(119);
    expect(getFrameIndex(2)).toBe(119);
  });

  it('uses a lighter but complete mobile sequence', () => {
    expect(getMobileFrameIndex(0)).toBe(0);
    expect(getMobileFrameIndex(0.3) % 2).toBe(0);
    expect(getMobileFrameIndex(1)).toBe(119);
  });
});
