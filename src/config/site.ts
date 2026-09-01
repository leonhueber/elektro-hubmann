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
    category: 'Wohnbau',
    description:
      'Durchdachte Elektroinstallation für modernes und komfortables Wohnen.',
    image: '/images/version-g/projects/family-home-v1.webp',
    alt: 'Modernes Einfamilienhaus mit sorgfältig geplanter Außenbeleuchtung',
    width: 1280,
    height: 853,
  },
  {
    type: 'Sanierung eines Bestandsgebäudes',
    category: 'Sanierung',
    description:
      'Bestehende Anlagen sicher modernisieren und zukunftsfähig erweitern.',
    image: '/images/version-g/projects/renovation-v1.webp',
    alt: 'Historischer Sicherungskasten in einem Gebäude während der Sanierung',
    width: 1280,
    height: 853,
  },
  {
    type: 'Gewerbeobjekt',
    category: 'Gewerbe',
    description:
      'Zuverlässige Elektrotechnik, abgestimmt auf betriebliche Anforderungen.',
    image: '/images/version-g/projects/commercial-v1.webp',
    alt: 'Professionell ausgeführte Elektroinstallation in einem Gewerbegebäude',
    width: 1280,
    height: 853,
  },
  {
    type: 'Tourismusbetrieb',
    category: 'Hotellerie',
    description:
      'Technik für Komfort, Betriebssicherheit und eine einfache Bedienung.',
    image: '/images/version-g/projects/hospitality-v1.webp',
    alt: 'Stimmungsvoll beleuchteter Restaurantbereich eines Tourismusbetriebs',
    width: 1280,
    height: 853,
  },
  {
    type: 'Photovoltaikanlage',
    category: 'Photovoltaik',
    description:
      'Erzeugung, Speicherung und Verbrauch sinnvoll zusammendenken.',
    image: '/images/version-g/projects/photovoltaics-v1.webp',
    alt: 'Photovoltaikanlage auf einem Dach vor alpiner Landschaft',
    width: 1280,
    height: 853,
  },
  {
    type: 'Gebäudetechnik oder KNX',
    category: 'Gebäudetechnik',
    description:
      'Licht, Beschattung und Gebäudefunktionen intelligent vernetzen.',
    image: '/images/version-g/projects/knx-v1.webp',
    alt: 'KNX Bedienpanel in einem modern ausgestatteten Wohnraum',
    width: 1280,
    height: 853,
  },
] as const;
