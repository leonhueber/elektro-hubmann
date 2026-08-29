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

export const services = [
  {
    title: 'Elektroinstallationen',
    description:
      'Durchdachte Lösungen für Neubau, Sanierung und laufende Erweiterungen.',
    marker: '01',
  },
  {
    title: 'Smart Home',
    description:
      'Gebäudetechnik, die Komfort, Übersicht und Energieeffizienz verbindet.',
    marker: '02',
  },
  {
    title: 'Photovoltaik',
    description:
      'Planung und Umsetzung passend zu Gebäude, Nutzung und Zukunftsplänen.',
    marker: '03',
  },
  {
    title: 'Fachhandel',
    description:
      'Persönliche Beratung und ausgewählte Produkte für Elektro und Haushalt.',
    marker: '04',
  },
] as const;

export const processSteps = [
  [
    '01',
    'Planung',
    'Anforderungen klären und eine nachvollziehbare Lösung entwickeln.',
  ],
  [
    '02',
    'Umsetzung',
    'Sauber arbeiten, abstimmen und transparent informieren.',
  ],
  ['03', 'Service', 'Auch nach Abschluss persönlich erreichbar bleiben.'],
] as const;
