import type { VersionGStoryState } from './version-g-story-assets';
import projectedRegions from './house-v4-orientation.json';

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
        ? 'Haus und Auto verbunden'
        : 'Laden an der Wallbox';
  }
}

type HouseRegion = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type HouseOrientation = {
  location: string;
  subject: string;
  regions: HouseRegion[];
};

// Bounds are projected from the native scene onto its square planning poster,
// including white margins; normalized coordinates keep both profiles aligned.
export const HOUSE_ORIENTATION: Record<VersionGStoryState, HouseOrientation> = {
  planning: {
    location: 'Das Haus im Überblick',
    subject: 'Elektrotechnik von Anfang an',
    regions: projectedRegions.planning.regions,
  },
  installation: {
    location: 'Drei Ebenen',
    subject: 'Leitungswege im Haus',
    regions: projectedRegions.installation.regions,
  },
  smarthome: {
    location: 'Schlafzimmer · Obergeschoss',
    subject: 'Beschattung auf Knopfdruck',
    regions: projectedRegions.smarthome.regions,
  },
  security: {
    location: 'Am Hauseingang',
    subject: 'Kamera und Zutritt',
    regions: projectedRegions.security.regions,
  },
  energy: {
    location: 'Dach & Stellplatz',
    subject: 'Solarstrom für Haus und Auto',
    regions: projectedRegions.energy.regions,
  },
};
