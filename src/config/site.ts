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

export const projects = [
  {
    type: 'Einfamilienhaus-Neubau',
    description:
      'Durchdachte Elektroinstallation für modernes und komfortables Wohnen.',
    image: '/images/legacy-placeholders/hubmann-slider-4.jpg',
    alt: 'Elektriker bei Arbeiten an einem Verteilerkasten',
    width: 1920,
    height: 1277,
  },
  {
    type: 'Sanierung eines Bestandsgebäudes',
    description:
      'Bestehende Anlagen sicher modernisieren und zukunftsfähig erweitern.',
    image: '/images/legacy-placeholders/hubmann-slider-1.jpg',
    alt: 'Detailaufnahme eines elektrischen Verteilers',
    width: 1920,
    height: 1277,
  },
  {
    type: 'Gewerbeobjekt',
    description:
      'Zuverlässige Elektrotechnik, abgestimmt auf betriebliche Anforderungen.',
    image: '/images/legacy-placeholders/wire.jpg',
    alt: 'Verdrahtete elektrische Anschlussklemmen',
    width: 1920,
    height: 1080,
  },
  {
    type: 'Tourismusbetrieb',
    description:
      'Technik für Komfort, Betriebssicherheit und eine einfache Bedienung.',
    image: '/images/legacy-placeholders/elektriker.jpg',
    alt: 'Elektroinstallateur bei der Arbeit',
    width: 446,
    height: 618,
  },
  {
    type: 'Photovoltaikanlage',
    description:
      'Erzeugung, Speicherung und Verbrauch sinnvoll zusammendenken.',
    image: '/images/legacy-placeholders/hubmann-slider-1.jpg',
    alt: 'Detailaufnahme einer Elektroinstallation',
    width: 1920,
    height: 1277,
  },
  {
    type: 'Gebäudetechnik oder KNX',
    description:
      'Licht, Beschattung und Gebäudefunktionen intelligent vernetzen.',
    image: '/images/legacy-placeholders/wire.jpg',
    alt: 'Verdrahtung in einer technischen Anlage',
    width: 1920,
    height: 1080,
  },
] as const;
