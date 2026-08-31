export type VersionGStoryState =
  'planning' | 'installation' | 'photovoltaic' | 'service';

export type VersionGStoryAsset = {
  src: string;
  alt: string;
  width: number;
  height: number;
};

const objectAssets = {
  planning: {
    src: 'planning-house.webp',
    alt: 'Architektonischer Schnitt eines modernen Hauses auf einem Bauplan',
    width: 1448,
    height: 1086,
  },
  installation: {
    src: 'installation-cabinet.webp',
    alt: 'Geöffneter, sauber verdrahteter elektrischer Verteilerschrank',
    width: 1536,
    height: 1024,
  },
  photovoltaic: {
    src: 'photovoltaic-storage.webp',
    alt: 'Photovoltaikmodul mit kompaktem, weißem Stromspeicher',
    width: 1448,
    height: 1086,
  },
  service: {
    src: 'service-wallbox.webp',
    alt: 'Moderne Wallbox mit ordentlich aufgewickeltem Ladekabel',
    width: 1448,
    height: 1086,
  },
} satisfies Record<VersionGStoryState, VersionGStoryAsset>;

/**
 * Keep every visual direction as a named set. A set may reuse assets from
 * another set, so testing a single replacement never duplicates image files.
 */
export const VERSION_G_STORY_ASSET_SETS = {
  objects: objectAssets,
  integratedEnergyHouse: {
    ...objectAssets,
    photovoltaic: {
      src: 'alternatives/energy-house-integrated-v1.png',
      alt: 'Modernes Wohnhaus mit Photovoltaikanlage, Stromspeicher und Wallbox',
      width: 1448,
      height: 1086,
    },
  },
  technicalPlanningHouse: {
    ...objectAssets,
    planning: {
      src: 'alternatives/planning-house-technical-v1.png',
      alt: 'Technischer Schnitt eines modernen Wohnhauses mit sichtbarer Elektroplanung',
      width: 1448,
      height: 1086,
    },
  },
  shedRoofPlanningHouse: {
    ...objectAssets,
    planning: {
      src: 'alternatives/planning-house-shed-roof-v1.png',
      alt: 'Modernes Pultdachhaus mit realistisch dargestellter Elektro-Haustechnik',
      width: 1448,
      height: 1086,
    },
  },
} satisfies Record<string, Record<VersionGStoryState, VersionGStoryAsset>>;

// Change only this value to switch the complete visual direction.
export const ACTIVE_VERSION_G_STORY_ASSET_SET: keyof typeof VERSION_G_STORY_ASSET_SETS =
  'objects';

export const VERSION_G_STORY_ASSETS =
  VERSION_G_STORY_ASSET_SETS[ACTIVE_VERSION_G_STORY_ASSET_SET];

/**
 * Optional chapters that are not part of the active four-step story yet.
 * Keeping them in the same catalog makes a later five- or six-step direction
 * possible without rediscovering paths, dimensions, or accessible labels.
 */
export const VERSION_G_OPTIONAL_STORY_ASSETS = {
  smarthome: {
    src: 'optional/smarthome-controls-v1.png',
    alt: 'Ungebrandete SmartHome-Bediengeräte vor einem modernen Wohnbereich',
    width: 1448,
    height: 1086,
  },
  lighting: {
    src: 'optional/lighting-systems-v1.png',
    alt: 'Architekturmodul mit Pendel-, Einbau-, Wand- und Sicherheitsbeleuchtung',
    width: 1402,
    height: 1122,
  },
  security: {
    src: 'optional/security-systems-v1.png',
    alt: 'Ungebrandete Alarm-, Brandmelde- und Kameraausstattung an einem Hauseingang',
    width: 1448,
    height: 1086,
  },
} satisfies Record<string, VersionGStoryAsset>;

export function versionGStoryAssetUrl(
  baseUrl: string,
  asset: VersionGStoryAsset,
) {
  return `${baseUrl}images/version-g/story/${asset.src}`;
}
