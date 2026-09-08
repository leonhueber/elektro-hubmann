import { houseManifest } from '../lib/house-story';
import { CONTINUOUS_HOUSE_REVISION } from './house-orientation';
export type VersionGStoryState =
  'planning' | 'installation' | 'smarthome' | 'security' | 'energy';
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
    alt: 'Zweigeschossiges Wohnhaus mit Satteldach, Photovoltaik und großen Fenstern als Anschauungsmodell für die Elektroplanung.',
    components: ['Gebäudeplanung', 'Anschlüsse'],
  },
  installation: {
    label: 'Installation',
    title: ['Was hinter den', 'Wänden steckt.'],
    description:
      'Von der Verteilung bis zur Steckdose: Wir installieren Elektrotechnik und strukturierte Netzwerke sauber und vorausschauend.',
    cta: 'Installation anfragen',
    hint: 'Weiter zum Smart Home',
    alt: 'Geöffnetes Erdgeschoss mit Wohnküche, Essbereich, Büro, Gäste-WC und Technikraum; Elektroverteilung, Netzwerk und Leitungswege sind sichtbar.',
    components: ['Elektroverteilung', 'Strom & Netzwerk'],
  },
  smarthome: {
    label: 'Smart Home',
    title: ['Ein Tastendruck.', 'Alles passt.'],
    description:
      'Licht, Beschattung und Raumtemperatur passend zu Ihrem Alltag: Mit vernetzter Gebäudesteuerung schaffen Sie Komfort auf Knopfdruck.',
    cta: 'Smart Home besprechen',
    hint: 'Weiter zur Sicherheit',
    alt: houseManifest.revision.endsWith('-smart-01')
      ? 'Nahansicht des Elternschlafzimmers mit Raumregler neben dem Eichenschrank und verstellbaren Lamellen vor der Holz-Balkontür; das Stabgeländer und die Balkonmöbel bleiben sichtbar.'
      : 'Geöffnetes Obergeschoss mit Elternschlafzimmer, zwei Kinderzimmern und Familienbad; die Beschattung am Schlafzimmerfenster ist abgesenkt.',
    components: ['KNX-Raumsteuerung', 'Beschattung & Raumklima'],
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
    alt: 'Erhöhte Ansicht des zweigeschossigen Wohnhauses mit zehn Photovoltaikmodulen in zwei Reihen auf dem Satteldach.',
    components: ['PV-Module', 'Wechselrichter'],
  },
};
if (houseManifest.revision === CONTINUOUS_HOUSE_REVISION) {
  copy.planning.alt =
    'Detailliertes Wohnhaus mit Holztüren und Holzfenstern, Balkon, Photovoltaik und einer Wallbox an der Seitenfassade.';
  copy.installation.alt =
    'Das Haus öffnet sich in drei angehobene Ebenen; die groben Leitungswege durch die Geschosse werden sichtbar.';
  copy.smarthome.description =
    'Ein Tastendruck, spürbar mehr Komfort: Die Jalousie im Schlafzimmer fährt herunter und lenkt das Tageslicht. Wir vernetzen Beschattung, Licht und Raumtemperatur für Ihren Alltag.';
  copy.smarthome.alt =
    'Direkte Nahansicht des Schlafzimmers mit Raumtaster neben dem Eichenschrank und abgesenkter Außenjalousie vor der Holz-Balkontür. Die Lamellen filtern das Tageslicht, die Raumbeleuchtung bleibt eingeschaltet.';
  copy.smarthome.components = ['Raumsteuerung', 'Automatische Beschattung'];
  copy.security.alt =
    'Nahansicht des Hauseingangs mit sichtbarer Kamera, Videosprechanlage und Türzugang.';
  copy.security.components = [
    'Kamera & Videosprechanlage',
    'Zutrittskontrolle',
  ];
  copy.energy.title = ['Vom eigenen Dach', 'bis zur Wallbox.'];
  copy.energy.description =
    'Photovoltaik, Haus und Wallbox gemeinsam geplant: Nutzen Sie Ihren Solarstrom auch zum Laden Ihres Elektroautos – mit einer Ladeleistung, die sich an den verfügbaren Überschuss anpasst.';
  copy.energy.alt =
    'Photovoltaik auf dem Hausdach und eine Wallbox mit ordentlich eingehängtem Ladekabel an der Seitenfassade. Eine schematische Energielinie verbindet das Dach mit der Ladestation; die Statusanzeige leuchtet auf.';
  copy.energy.components = ['Photovoltaik', 'Wallbox & Überschussladen'];
}
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
  return `${baseUrl}images/version-g/${asset.src}?v=${houseManifest.revision}`;
}
