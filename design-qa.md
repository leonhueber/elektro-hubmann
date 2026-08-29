# Design QA – Version D

## Vergleichsbasis

- Source visual truth: `docs/version-d-ideation/selected-option-3.png`
- Desktop implementation: `docs/version-d-qa/d-desktop-v2.png`
- Tablet implementation: `docs/version-d-qa/d-tablet-final.png`
- Mobile implementation: `docs/version-d-qa/d-mobile-v2.png`
- Mobile Detailaufnahmen: `docs/version-d-qa/d-mobile-services.png` und
  `docs/version-d-qa/d-mobile-form-final.png`
- Full-view comparison: `docs/version-d-qa/comparison-full.png`
- Focused hero comparison: `docs/version-d-qa/comparison-hero.png`
- Route/state: Version D, Standardzustand, nicht angemeldet

## Viewport und Normalisierung

- Quelle: 1511 × 1041 px, Dichte 1.
- Desktop: angeforderter Viewport 1440 × 1000 CSS-px; nutzbare Fläche und
  Capture 1425 × 990 px durch Browser-Chrome und Scrollbar, Dichte 1.
- Tablet: angeforderter Viewport 768 × 1024 CSS-px; Capture 753 × 1004 px,
  Dichte 1.
- Mobile: angeforderter Viewport 390 × 844 CSS-px; Capture 375 × 812 px,
  Dichte 1.
- Für den kombinierten Desktopvergleich wurde die Quelle proportional in einen
  1425 × 1000 px großen weißen Rahmen gesetzt. Die Implementierung wurde auf
  dieselbe Vergleichsfläche normalisiert.

## Full-view comparison

Quelle und Implementierung verwenden dieselbe sichtbare Reihenfolge:

1. dunkler Versionsumschalter;
2. kompakte Informationsleiste;
3. weiße Navigation mit Hubmann-Logo;
4. zentrierter, zweizeiliger Hero mit zwei klaren CTAs;
5. breites regionales Projektfoto mit asymmetrischer Rundung;
6. überlagerte Vertrauenskarte;
7. helle Vertrauens- und Leistungsbereiche.

Die Implementierung übernimmt das Layout des ausgewählten Entwurfs, verwendet
aber die fünf bereits freigegebenen Vertrauenspunkte statt der drei verkürzten
Mockup-Punkte. Das ist eine beabsichtigte inhaltliche Abweichung.

## Focused comparison

Der fokussierte Hero-Vergleich bestätigt die maßgeblichen Details: zentrierte
Typografie, roter Eyebrow-Text, gleichgewichtete Button-Gruppe, großflächige
Architekturfotografie und die links unten liegende Vertrauenskarte. Das finale
Foto ist als eigenständiges WebP-Asset eingebunden; keine UI-Fläche wurde aus
dem Mockup ausgeschnitten oder als CSS-Grafik nachgebaut.

## Fidelity surfaces

- Typografie: Inter und die bestehende Hubmann-Gewichtsskala bleiben erhalten.
  Die Desktop-Hauptbotschaft läuft wie in der Quelle über zwei Zeilen; Tablet
  und Mobile brechen kontrolliert und ohne abgeschnittene Wörter um.
- Spacing/Layout: Navigation, Hero-Abstände, Bildbreite, asymmetrische Radien
  und Badge-Position folgen dem Mockup. Die mobile Badge-Karte wird aus dem
  Bild heraus in den Dokumentfluss überführt, damit sie nichts verdeckt.
- Farben/Tokens: Weiß, Anthrazit, Hubmann-Rot und warmes Elfenbein entsprechen
  der ausgewählten Mischung aus Version A und C. Es gibt keine Verläufe oder
  Glasflächen im Seitenlayout.
- Bildqualität/Assets: Das Hero-Motiv liegt als 1920 × 800 px großes, 203 KB
  starkes WebP vor. Es ist scharf, passend beschnitten und zeigt keine
  fehlerhaften Ressourcen. Logo und UI-Icons bleiben echte Assets bzw. Icons
  aus `@tabler/icons-react`.
- Copy: Hauptbotschaft, Region, CTAs und Vertrauensargumente entsprechen der
  vereinbarten Inhaltsstruktur.

## Findings

- Keine verbleibenden P0-, P1- oder P2-Abweichungen.
- [P3] Die exakte Zeilenbreite schwankt gegenüber dem generierten Mockup leicht,
  weil die produktive Seite die bestehende Inter-Schrift und reale
  Browserbreiten verwendet. Die Hierarchie und der Zweizeilen-Umbruch bleiben
  erhalten.
- [P3] Unterhalb des Hero werden fünf statt drei Vertrauenspunkte gezeigt. Das
  ist bewusst, weil die freigegebene Inhaltsarchitektur alle fünf Punkte
  verlangt.

## Comparison history

### Pass 1

- [P2] Der Desktop-Hero war zu hoch; die Überschrift lief über drei Zeilen und
  das Projektfoto begann deutlich zu tief.
- [P2] Die D-spezifischen Buttons übernahmen den großen Kartenradius und wirkten
  runder als im ausgewählten Entwurf.

### Fixes

- Headline-Breite und Schriftgröße angepasst, vertikale Abstände reduziert und
  die Headerhöhe für Version D auf 78 px verdichtet.
- D-spezifische Buttons auf einen 2-px-Radius gesetzt; Bild-, Projekt- und
  Form-Radien bleiben davon unabhängig.

### Pass 2

- Post-fix evidence: `docs/version-d-qa/d-desktop-v2.png` und
  `docs/version-d-qa/comparison-hero.png`.
- Die Überschrift läuft auf Desktop über zwei Zeilen und das Bild beginnt
  innerhalb des beabsichtigten Above-the-fold-Bereichs.
- Tablet und Mobile zeigen keinen horizontalen Overflow: Client- und
  Scrollbreite stimmen mit 753 px bzw. 375 px überein.
- Servicekarten ordnen sich auf Mobile zweispaltig an; das fünfte Element wird
  zentriert. Formularfelder bleiben vollständig innerhalb des Viewports.

## Interaction and runtime checks

- `Leistungen ansehen` springt zu `#leistungen`.
- Der Versionsumschalter navigiert von D korrekt zu A; Version D ist mit
  `aria-current="page"` markiert.
- Keine Browser-Konsolenmeldungen und keine defekten Bilder.
- Astro-, TypeScript- und Produktionsbuild ohne Fehler, Warnungen oder Hinweise.

## Follow-up polish

- Vor dem finalen Firmenlaunch das generierte Hero-Motiv durch ein rechtlich
  freigegebenes, echtes Hubmann-Projektfoto ersetzen, sobald passendes Material
  vorliegt.

final result: passed
