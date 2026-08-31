export type VersionGPrimaryStoryState =
  'planning' | 'installation' | 'photovoltaic' | 'service';

export type VersionGStoryState =
  VersionGPrimaryStoryState | 'smarthome' | 'lighting' | 'security';

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
} satisfies Record<VersionGPrimaryStoryState, VersionGStoryAsset>;

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
} satisfies Record<
  string,
  Record<VersionGPrimaryStoryState, VersionGStoryAsset>
>;

// Change only this value to switch the complete visual direction.
export const ACTIVE_VERSION_G_STORY_ASSET_SET: keyof typeof VERSION_G_STORY_ASSET_SETS =
  'objects';

export const VERSION_G_STORY_ASSETS =
  VERSION_G_STORY_ASSET_SETS[ACTIVE_VERSION_G_STORY_ASSET_SET];

export const VERSION_G_EXTENDED_STORY_ASSETS = {
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

export type VersionGStoryChapter = {
  id: VersionGStoryState;
  number: string;
  label: string;
  title: readonly string[];
  description: string;
  cta: string;
  href: string;
  hint: string;
  asset: VersionGStoryAsset;
};

/**
 * Shared by the animated desktop story and the static mobile fallback so every
 * chapter remains visible and consistently numbered in both experiences.
 */
export const VERSION_G_STORY_CHAPTERS = [
  {
    id: 'planning',
    number: '01',
    label: 'Planung',
    title: ['Ein gutes Haus', 'beginnt mit', 'einem klaren Plan.'],
    description:
      'Wir planen Elektrotechnik für Neubau, Sanierung und Gewerbe – durchdacht, präzise und zukunftssicher.',
    cta: 'Projekt besprechen',
    href: 'kontakt/#projektanfrage',
    hint: 'Scrollen, um die Planung weiterzuführen',
    asset: VERSION_G_STORY_ASSETS.planning,
  },
  {
    id: 'installation',
    number: '02',
    label: 'Installation',
    title: ['Saubere Installation.', 'Präzise umgesetzt.'],
    description:
      'Von Elektroinstallationen bis zur Netzwerktechnik setzen wir Technik sauber, sicher und zuverlässig um.',
    cta: 'Leistungen ansehen',
    href: 'leistungen/elektroinstallation-sanierung/',
    hint: 'Weiter zu SmartHome und KNX',
    asset: VERSION_G_STORY_ASSETS.installation,
  },
  {
    id: 'smarthome',
    number: '03',
    label: 'SmartHome',
    title: ['Smarte Technik.', 'Komfortabel gesteuert.'],
    description:
      'Mit SmartHome, KNX und intelligenter Steuerung vernetzen wir Licht, Beschattung, Heizung und Sicherheit.',
    cta: 'SmartHome entdecken',
    href: 'leistungen/knx-netzwerk-medien/',
    hint: 'Weiter zur Beleuchtung',
    asset: VERSION_G_EXTENDED_STORY_ASSETS.smarthome,
  },
  {
    id: 'lighting',
    number: '04',
    label: 'Beleuchtung',
    title: ['Licht, das Räume', 'und Sicherheit', 'schafft.'],
    description:
      'Von Wohnraumlicht bis zur Sicherheits- und Notbeleuchtung planen wir funktionale und ästhetische Lösungen.',
    cta: 'Beleuchtung ansehen',
    href: 'leistungen/elektroinstallation-sanierung/',
    hint: 'Weiter zur Sicherheitstechnik',
    asset: VERSION_G_EXTENDED_STORY_ASSETS.lighting,
  },
  {
    id: 'security',
    number: '05',
    label: 'Sicherheit',
    title: ['Sicherheit,', 'auf die Sie sich', 'verlassen können.'],
    description:
      'Mit Alarmanlagen, Blitzschutz und moderner Gebäudetechnik schützen wir Haus, Betrieb und Menschen.',
    cta: 'Sicherheit entdecken',
    href: 'leistungen/gebaeudetechnik-sicherheit/',
    hint: 'Weiter zur Photovoltaik',
    asset: VERSION_G_EXTENDED_STORY_ASSETS.security,
  },
  {
    id: 'photovoltaic',
    number: '06',
    label: 'Photovoltaik',
    title: ['Energie smart', 'nutzen.', 'Zukunft sicher', 'denken.'],
    description:
      'Mit Photovoltaik, Speicher und intelligenten Lösungen schaffen wir nachhaltige Energiekonzepte.',
    cta: 'Energie entdecken',
    href: 'leistungen/photovoltaik-energie/',
    hint: 'Weiter zu Service und Wartung',
    asset: VERSION_G_STORY_ASSETS.photovoltaic,
  },
  {
    id: 'service',
    number: '07',
    label: 'Service',
    title: ['Auch nach dem', 'Projekt verlässlich', 'an Ihrer Seite.'],
    description:
      'Kundendienst, Wartung und Erweiterungen begleiten Ihre Anlage langfristig und unkompliziert.',
    cta: 'Service anfragen',
    href: 'kontakt/#projektanfrage',
    hint: 'Weiter zu unseren Referenzprojekten',
    asset: VERSION_G_STORY_ASSETS.service,
  },
] as const satisfies readonly VersionGStoryChapter[];

export function versionGStoryAssetUrl(
  baseUrl: string,
  asset: VersionGStoryAsset,
) {
  return `${baseUrl}images/version-g/story/${asset.src}`;
}
