import { describe, expect, it } from 'vitest';
import { getStoryState } from './HouseStory';

describe('getStoryState', () => {
  it.each([
    [0, 'planning'],
    [0.249, 'planning'],
    [0.25, 'installation'],
    [0.519, 'installation'],
    [0.52, 'energy'],
    [0.779, 'energy'],
    [0.78, 'service'],
    [1, 'service'],
  ] as const)('maps %s to %s', (progress, expected) => {
    expect(getStoryState(progress)).toBe(expected);
  });
});
