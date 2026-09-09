import type { VersionGStoryState } from './version-g-story-assets';

export const CONTINUOUS_HOUSE_REVISION = 'v4-continuous-01';

/** Describes the native pose currently drawn, using its original timeline. */
export function houseSceneCaptionAt(
  chapter: VersionGStoryState,
  progress: number,
) {
  switch (chapter) {
    case 'planning':
      return '';
    case 'installation':
      return progress < 0.24
        ? 'Drei Ebenen öffnen sich'
        : 'Leitungswege werden sichtbar';
    case 'smarthome':
      if (progress < 0.445) return 'Raumsteuerung';
      return progress < 0.55
        ? 'Jalousie fährt herunter'
        : 'Lamellen lenken Tageslicht';
    case 'security':
      return 'Kamera und Türzugang';
    case 'energy':
      if (progress < 0.885) return 'Solarstrom vom Dach';
      return progress < 0.93
        ? 'Dach und Wallbox verbunden'
        : 'Solarstrom an der Wallbox';
  }
}
