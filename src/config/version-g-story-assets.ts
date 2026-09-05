import { houseManifest } from '../lib/house-v3';
export type VersionGStoryState =
  | 'planning'
  | 'installation'
  | 'lighting'
  | 'smarthome'
  | 'security'
  | 'energy';
export type VersionGStoryAsset = {
  src: string;
  alt: string;
  width: number;
  height: number;
};
const copy: Record<
  VersionGStoryState,
  {
    label: string;
    title: string[];
    description: string;
    cta: string;
    hint: string;
    alt: string;
    components: string[];
  }
> = {
  planning: {
    label: 'Planung',
    title: ['Ein gutes Haus', 'beginnt mit', 'einem klaren Plan.'],
    description:
      'Wir planen Elektrotechnik für Neubau, Sanierung und Gewerbe – abgestimmt auf Ihr Gebäude und Ihren Alltag.',
    cta: 'Projekt besprechen',
    hint: 'Scrollen und das Haus entdecken',
    alt: 'Eingeschossiges Wohnhaus mit Flachdach und Photovoltaik als Anschauungsmodell für die Elektroplanung.',
    components: ['Gebäudeplanung', 'Anschlüsse'],
  },
  installation: {
    label: 'Installation',
    title: ['Was hinter den', 'Wänden steckt.'],
    description:
      'Von der Verteilung bis zur Steckdose: Wir installieren Elektrotechnik und strukturierte Netzwerke sauber und vorausschauend.',
    cta: 'Installation anfragen',
    hint: 'Weiter zur Beleuchtung',
    alt: 'Nahansicht des Technikraums im geöffneten Wohnhaus mit Elektroverteilung, Netzwerkschrank und getrennten Strom- und Datenwegen.',
    components: ['Elektroverteilung', 'Strom & Netzwerk'],
  },
  lighting: {
    label: 'Beleuchtung',
    title: ['Licht macht', 'Räume lebendig.'],
    description:
      'Gezieltes Arbeitslicht, eine angenehme Wohnatmosphäre und Licht am Eingang: Wir planen die passende Beleuchtung.',
    cta: 'Lichtplanung besprechen',
    hint: 'Weiter zum Smart Home',
    alt: 'Geöffnetes Haus mit warm beleuchtetem Wohnbereich, Esstisch, Arbeitsplatz und Eingang.',
    components: ['Wohnraumlicht', 'Arbeits- & Außenlicht'],
  },
  smarthome: {
    label: 'Smart Home',
    title: ['Ein Tastendruck.', 'Alles passt.'],
    description:
      'Mit vernetzter Gebäudesteuerung stimmen Sie Licht und Beschattung auf Ihren Alltag ab – einfach und komfortabel.',
    cta: 'Smart Home besprechen',
    hint: 'Weiter zur Sicherheit',
    alt: 'Smart-Home-Ansicht mit KNX-Steuerung und abgesenkter Beschattung am Schlafzimmerfenster.',
    components: ['KNX-Steuerung', 'Licht & Beschattung'],
  },
  security: {
    label: 'Sicherheit',
    title: ['Ein gutes Gefühl.', 'Auch unterwegs.'],
    description:
      'Von der Videosprechanlage bis zur Alarm- und Brandmeldetechnik: Wir planen Schutz passend zu Ihrem Gebäude.',
    cta: 'Sicherheit besprechen',
    hint: 'Weiter zur Photovoltaik',
    alt: 'Nahansicht des Hauseingangs mit Videosprechanlage.',
    components: ['Videosprechanlage', 'Alarm- & Brandmeldetechnik'],
  },
  energy: {
    label: 'Photovoltaik',
    title: ['Auf dem Dach', 'beginnt die', 'eigene Energie.'],
    description:
      'Wir planen und installieren Ihre Photovoltaikanlage – vom Dachmodul über den Wechselrichter bis zum Anschluss im Haus.',
    cta: 'Photovoltaik anfragen',
    hint: 'Weiter zu unseren Projekten',
    alt: 'Erhöhte Ansicht des Wohnhauses mit acht Photovoltaikmodulen auf dem wieder aufgesetzten Flachdach.',
    components: ['PV-Module', 'Wechselrichter'],
  },
};
export const VERSION_G_STORY_CHAPTERS = houseManifest.chapters.map(
  (chapter, index) => {
    const id = chapter.id as VersionGStoryState;
    const content = copy[id];
    return {
      ...chapter,
      ...content,
      id,
      number: String(index + 1).padStart(2, '0'),
      href: '#kontakt',
      asset: {
        src: `${houseManifest.assetPath.replace('images/version-g/', '')}desktop/${id}.webp`,
        alt: content.alt,
        width: houseManifest.profiles.desktop.width,
        height: houseManifest.profiles.desktop.height,
      },
    };
  },
);
export const VERSION_G_STORY_ASSETS = Object.fromEntries(
  VERSION_G_STORY_CHAPTERS.map((chapter) => [chapter.id, chapter.asset]),
) as Record<VersionGStoryState, VersionGStoryAsset>;
export function versionGStoryAssetUrl(
  baseUrl: string,
  asset: VersionGStoryAsset,
) {
  return `${baseUrl}images/version-g/${asset.src}`;
}
