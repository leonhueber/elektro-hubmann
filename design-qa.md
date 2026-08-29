# Design QA – Version E

## Vergleichsbasis

- Source visual truth: `docs/version-e-reference/source-design.png`
- Erste Implementierung: `docs/version-e-qa/e-desktop-pass1.png`
- Finale Desktop-Implementierung: `docs/version-e-qa/e-desktop-final.png`
- Tablet: `docs/version-e-qa/e-tablet.png`
- Mobile Hero: `docs/version-e-qa/e-mobile.png`
- Mobile Leistungen: `docs/version-e-qa/e-mobile-services-final.png`
- Mobiles Formular: `docs/version-e-qa/e-mobile-form-final.png`
- Full-view comparison: `docs/version-e-qa/comparison-full.png`
- Focused hero comparison: `docs/version-e-qa/comparison-hero.png`
- Route/state: Version E, Standardzustand, nicht angemeldet

## Viewport und Normalisierung

- Quelle: 1024 × 1536 px, Dichte 1.
- Desktop: 1024 px nutzbare CSS-Breite; Capture 1024 × 1533 px,
  Dichte 1. Für den Vergleich wurde die Implementierung nur vertikal um 3 px
  auf 1536 px normalisiert.
- Tablet: angeforderter Viewport 768 × 1024 CSS-px; nutzbare Breite 753 px.
- Mobile: angeforderter Viewport 390 × 844 CSS-px; nutzbare Breite 375 px.
- Die zusätzliche 44-px-Leiste für den Versionsumschalter ist eine bewusste
  Produktanforderung und fehlt in der Designreferenz.

## Full-view comparison

Die finale Umsetzung übernimmt die wesentliche Komposition der Referenz:

1. vollflächiger dunkler Baustellen-Hero;
2. Informationsleiste und Navigation direkt auf dem Foto;
3. dreizeilige Anton-Headline links und Elektriker am Verteiler rechts;
4. primärer roter CTA und sekundärer unterstrichener Link;
5. dunkle Vertrauensleiste mit drei gleichgewichteten Argumenten;
6. weiße Leistungssektion mit Anton-Überschrift und vier Karten in der ersten
   Reihe.

Der fünfte Leistungsbereich KNX/Netzwerk bleibt erhalten und folgt in einer
zweiten, zentrierten Reihe. Damit bleibt die freigegebene Inhaltsarchitektur
vollständig, ohne die Referenzkomposition der ersten Reihe zu verändern.

## Focused comparison

Der kombinierte Hero-Vergleich bestätigt Motiv, Bildfokus, Kontrast,
Typografie, CTA-Hierarchie und Vertrauensleiste. Das Hero-Foto ist ein
eigenständiges 1586 × 992 px großes WebP-Asset. Text, Logo, Navigation und
Buttons sind echte zugängliche Web-Elemente und nicht Bestandteil des Bildes.

## Fidelity surfaces

- Typografie: Anton 400 bildet die schmale, schwere Display-Schrift der
  Referenz nach. Der Hero läuft auf Desktop in denselben drei Zeilen; Inter
  bleibt für Navigation, Fließtext und Formulare erhalten.
- Spacing/Layout: Inhaltskante, Hero-Höhe, Navigationsabstände,
  Vertrauensleiste und vierteilige erste Service-Reihe folgen der Vorlage.
  Mobile wird die Struktur linearisiert, ohne Inhalte oder CTAs abzuschneiden.
- Farben/Tokens: nahezu schwarzer Hintergrund, Weiß und Hubmann-Rot entsprechen
  der Referenz. Es werden keine dekorativen Verläufe oder Glasflächen benutzt.
- Bildqualität/Assets: Hero und Logo sind lokale optimierte Assets. Die
  Leistungsbilder stammen vorläufig aus den bereits lokal gesicherten
  Website-Motiven; es gibt keine defekten sichtbaren Bilder.
- Copy: Hero-Botschaft, Regionsbezug, CTAs und Leistungsbezeichnungen folgen
  der Designreferenz und der vereinbarten Inhaltsstruktur.

## Findings

- Keine verbleibenden P0-, P1- oder P2-Abweichungen.
- [P3] Die vorhandenen Leistungsbilder treffen nicht alle Motive der Referenz
  exakt. Sie sind bewusst als lokale Platzhalter erhalten, bis echte
  freigegebene Hubmann-Projektfotos vorliegen.
- [P3] Die Versionierungsleiste verschiebt den Hero gegenüber der reinen
  Referenz um 44 px. Das ist beabsichtigt, weil alle fünf Entwürfe live und
  direkt umschaltbar bleiben sollen.

## Comparison history

### Pass 1

- [P2] Die Headline lief auf Desktop über fünf statt drei Zeilen.
- [P2] Bei 1024 px wurden nur drei statt vier Leistungskarten in der ersten
  Reihe angezeigt.
- [P2] Der Hero war dadurch zu hoch und der Leistungsbereich begann zu spät.

### Fixes

- Headlinebreite auf 13 Zeichenbreiten erweitert und die finale Herohöhe auf
  824 px abgestimmt.
- Version E auf ein vierteiliges Desktop-Servicegrid umgestellt; Service &
  Prüfung wird vor KNX/Netzwerk einsortiert.
- Die fünfte Karte bleibt zentriert in der Folgereihe erhalten.

### Mobile Pass

- [P2] Die Desktop-Position der fünften Servicekarte erzeugte auf Mobile eine
  implizite dritte Gridspalte und überlagerte Karten.
- Fix: Unter 820 px wird das Servicegrid explizit zweispaltig; die fünfte Karte
  spannt zentriert über beide Spalten.
- Post-fix evidence: `docs/version-e-qa/e-mobile-services-final.png`.
- Client- und Scrollbreite stimmen auf Mobile mit 375 px überein; keine Karte,
  Schaltfläche oder Formularfläche ragt aus dem Viewport.

## Interaction and runtime checks

- `Projekt starten` springt zu `#projektanfrage`.
- `Referenzen ansehen` und die Navigation verwenden funktionierende Anker.
- Der Versionsumschalter navigiert korrekt zwischen E und D; Version E ist mit
  `aria-current="page"` markiert.
- Keine Browser-Konsolenmeldungen und keine defekten sichtbaren Bilder.
- Astro-, TypeScript- und Produktionsbuild ohne Fehler, Warnungen oder Hinweise.

## Follow-up polish

- Das generierte Hero-Motiv und die Service-Platzhalter vor dem offiziellen
  Firmenlaunch durch rechtlich freigegebene echte Hubmann-Fotos ersetzen.

final result: passed
