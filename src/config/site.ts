export const variants = [
  {
    id: 'a',
    name: 'Version A',
    direction: 'Architektur',
    summary: 'Ruhig, hochwertig und großzügig.',
  },
  {
    id: 'b',
    name: 'Version B',
    direction: 'Technisch',
    summary: 'Präzise, modular und leistungsorientiert.',
  },
  {
    id: 'c',
    name: 'Version C',
    direction: 'Regional',
    summary: 'Persönlich, warm und handwerksnah.',
  },
] as const;

export type VariantId = (typeof variants)[number]['id'];

export const company = {
  name: 'Elektro Hubmann',
  proprietor: 'Ing. Peter Hubmann',
  address: 'Weißbriach 94, 9622 Weißbriach',
  phone: '04286 / 240',
  phoneHref: 'tel:+434286240',
  emergency: '0664 4343187',
  emergencyHref: 'tel:+436644343187',
  email: 'office@elektro-hubmann.at',
  emailHref: 'mailto:office@elektro-hubmann.at',
  shopHours:
    'Mo–Fr 09:00–12:00 und 15:00–17:30 · Mi & Fr nachmittags geschlossen',
} as const;

export const trustItems = [
  ['Seit 1972', 'Familienbetrieb'],
  ['50+ Jahre', 'Erfahrung'],
  ['Regional', 'Vor Ort'],
  ['Komplett', 'Planung & Ausführung'],
  ['Persönlich', 'Ein Ansprechpartner'],
] as const;

export const services = [
  {
    title: 'Elektroinstallation und Sanierung',
    description:
      'Elektroanlagen für Neubau, Umbau und die fachgerechte Modernisierung bestehender Gebäude.',
    details: 'Planung · Installation · Erweiterung · Sanierung',
    marker: '01',
  },
  {
    title: 'Photovoltaik und Energie',
    description:
      'Energielösungen, die auf Gebäude, Verbrauch und zukünftige Anforderungen abgestimmt sind.',
    details: 'Photovoltaik · Elektroheizung · Energiemanagement',
    marker: '02',
  },
  {
    title: 'Gebäudetechnik und Sicherheit',
    description:
      'Technik für Komfort und Schutz – sorgfältig geplant und nachvollziehbar umgesetzt.',
    details: 'Blitzschutz · Alarmanlagen · Gebäudetechnik',
    marker: '03',
  },
  {
    title: 'KNX, Netzwerk und Medien',
    description:
      'Vernetzte Infrastruktur für moderne Wohngebäude, Betriebe und touristische Objekte.',
    details: 'KNX · PC-Netzwerke · SAT-Anlagen · Medien',
    marker: '04',
  },
  {
    title: 'Prüfung, Service und Störungsbehebung',
    description:
      'Persönlicher Service für bestehende Anlagen und rasche Hilfe, wenn Technik ausfällt.',
    details: 'Prüfung · Wartung · Service · Störungsdienst',
    marker: '05',
  },
] as const;

export const projects = [
  {
    type: 'Einfamilienhaus-Neubau',
    image: '/images/legacy-placeholders/hubmann-slider-4.jpg',
    alt: 'Elektriker bei Arbeiten an einem Verteilerkasten',
    width: 1920,
    height: 1277,
  },
  {
    type: 'Sanierung eines Bestandsgebäudes',
    image: '/images/legacy-placeholders/hubmann-slider-1.jpg',
    alt: 'Detailaufnahme eines elektrischen Verteilers',
    width: 1920,
    height: 1277,
  },
  {
    type: 'Gewerbeobjekt',
    image: '/images/legacy-placeholders/wire.jpg',
    alt: 'Verdrahtete elektrische Anschlussklemmen',
    width: 1920,
    height: 1080,
  },
  {
    type: 'Tourismusbetrieb',
    image: '/images/legacy-placeholders/elektriker.jpg',
    alt: 'Elektroinstallateur bei der Arbeit',
    width: 446,
    height: 618,
  },
  {
    type: 'Photovoltaikanlage',
    image: '/images/legacy-placeholders/hubmann-slider-1.jpg',
    alt: 'Detailaufnahme einer Elektroinstallation',
    width: 1920,
    height: 1277,
  },
  {
    type: 'Gebäudetechnik oder KNX',
    image: '/images/legacy-placeholders/wire.jpg',
    alt: 'Verdrahtung in einer technischen Anlage',
    width: 1920,
    height: 1080,
  },
] as const;

export const processSteps = [
  [
    '01',
    'Projekt anfragen',
    'Vorhaben, Baustellenort und Zeitrahmen übermitteln.',
  ],
  [
    '02',
    'Besichtigung und Beratung',
    'Situation vor Ort prüfen und Anforderungen gemeinsam klären.',
  ],
  [
    '03',
    'Planung und Angebot',
    'Eine nachvollziehbare Lösung mit transparentem Angebot erstellen.',
  ],
  [
    '04',
    'Umsetzung',
    'Die Arbeiten koordiniert und fachgerecht auf der Baustelle ausführen.',
  ],
  [
    '05',
    'Prüfung und Übergabe',
    'Anlage prüfen, dokumentieren und persönlich übergeben.',
  ],
] as const;
