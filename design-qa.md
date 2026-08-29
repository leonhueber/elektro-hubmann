# Design QA – Leistungsübersicht

## Vergleichsbasis

- Source visual truth:
  `docs/references/service-cards-reference.png`
- Desktop implementation:
  `docs/design-qa/service-showcase-desktop.png`
- Mobile implementation:
  `docs/design-qa/service-showcase-mobile.png`
- Combined comparison:
  `docs/design-qa/service-showcase-comparison.png`
- Route/state: Version A, Leistungsübersicht, Standardzustand

## Viewport und Normalisierung

- Quelle: 449 × 186 px.
- Desktop-Browser: 1265 px CSS-Viewport; Komponentenrechteck ca.
  1217 × 374 CSS-px; Capture 1216 × 374 px.
- Mobile-Browser: 375 px CSS-Viewport; kein horizontaler Overflow;
  Komponentenrechteck ca. 347 × 956 CSS-px.
- Für den kombinierten Vergleich wurde die Quelle proportional auf 374 px Höhe
  skaliert. Die unterschiedliche Spaltenzahl ist beabsichtigt: Die Referenz
  zeigt vier Leistungen, die freigegebene Hubmann-Struktur benötigt fünf.
- Browser-Capture und CSS-Pixel wurden mit Dichte 1 verglichen.

## Full-view comparison

Der kombinierte Vergleich bestätigt dieselbe visuelle Hierarchie:

1. feine obere Begrenzung;
2. gleichmäßige, vertikal getrennte Spalten;
3. rotes Line-Icon;
4. kurze, schwarze Leistungsbezeichnung;
5. kurzer roter Akzent;
6. hochformatiges Foto über nahezu die gesamte Spaltenbreite.

Die Implementierung ist bewusst etwas großzügiger, da fünf statt vier
Leistungsgruppen dargestellt werden.

## Focused comparison

Ein zusätzlicher Detailausschnitt war nicht erforderlich, weil der
Desktop-Capture bereits ausschließlich die Komponente und alle relevanten
Details zeigt. Die separate Mobile-Aufnahme prüft Umbruch, Spaltenwechsel und
die ungerade Anzahl von fünf Einträgen.

## Fidelity surfaces

- Typografie: Gewicht, kompakte Größe, zweizeilige Titel und Zeilenhöhe folgen
  der Referenz. Lange Hubmann-Bezeichnungen bleiben vollständig lesbar.
- Spacing/Layout: Spaltenbreite, Innenabstand, vertikale Trennlinien,
  Akzentabstand und Bildproportion entsprechen der Referenzsprache.
- Farben/Tokens: Hubmann-Rot, Anthrazit, Weiß und feine graue Linien verwenden
  das bestehende Markensystem.
- Bildqualität/Assets: lokal gespeicherte Bilder der bestehenden Website
  ersetzen die Referenzmotive vorläufig. Keine CSS- oder Platzhaltergrafiken
  werden als Fotos verwendet.
- Copy: Die fünf vereinbarten Leistungsgruppen wurden für die kompakte Ansicht
  sinnvoll gekürzt, ohne die fachliche Zuordnung zu verändern.

## Findings

- [P3] Die Platzhalterbilder zeigen noch nicht für jede Karte den exakten
  Leistungsbereich, insbesondere Photovoltaik.
  Fix nach Inhaltsfreigabe: durch echte, rechtlich freigegebene Aufnahmen je
  Leistungsbereich ersetzen.
- [P3] Die Tabler-Line-Icons treffen Strichstärke und Farbe, sind aber nicht
  exakt dieselben Piktogramme wie in der Referenz.
  Akzeptiert: Sie bilden ein konsistentes, frei verfügbares Icon-System.

## Comparison history

### Pass 1

- [P2] Auf Mobile stand die fünfte Karte allein links und erzeugte eine
  unausgewogene letzte Zeile.
- Fix: Die letzte Karte spannt auf kleinen Viewports über beide Grid-Spalten
  und wird mit halber Breite zentriert.

### Pass 2

- Post-fix evidence:
  `docs/design-qa/service-showcase-mobile.png`.
- Die fünfte Karte ist zentriert; der Browser meldet 375 px Clientbreite und
  375 px Scrollbreite, also keinen horizontalen Overflow.
- Keine verbleibenden P0-, P1- oder P2-Abweichungen.

## Interaction and runtime checks

- Fünf Kartenlinks vorhanden.
- Klick auf eine Leistung führt zum Projektanfrage-Abschnitt.
- Keine Browser-Konsolenfehler.
- Astro- und TypeScript-Prüfung ohne Fehler, Warnungen oder Hinweise.

## Follow-up polish

- Echte Motive für Photovoltaik, Gebäudetechnik, KNX/Netzwerk und Prüfung
  einsetzen.
- Optional ein eigenes Hubmann-Iconset auf Basis der finalen Markenunterlagen
  erstellen.

final result: passed
