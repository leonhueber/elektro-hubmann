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
} satisfies Record<string, Record<VersionGStoryState, VersionGStoryAsset>>;

// Change only this value to switch the complete visual direction.
export const ACTIVE_VERSION_G_STORY_ASSET_SET: keyof typeof VERSION_G_STORY_ASSET_SETS =
  'objects';

export const VERSION_G_STORY_ASSETS =
  VERSION_G_STORY_ASSET_SETS[ACTIVE_VERSION_G_STORY_ASSET_SET];

export function versionGStoryAssetUrl(
  baseUrl: string,
  asset: VersionGStoryAsset,
) {
  return `${baseUrl}images/version-g/story/${asset.src}`;
}
