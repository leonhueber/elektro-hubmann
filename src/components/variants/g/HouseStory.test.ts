import { describe, expect, it } from 'vitest';
import { getLayerMotion, getStoryState } from './HouseStory';

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

  it('moves image layers continuously between story chapters', () => {
    expect(getLayerMotion(0, 0).opacity).toBe(1);
    expect(getLayerMotion(0, 0.3).opacity).toBe(0);
    expect(getLayerMotion(1, 0.3).opacity).toBe(1);
    expect(getLayerMotion(2, 0.62).opacity).toBe(1);
    expect(getLayerMotion(3, 0.92).opacity).toBe(1);
  });
});
