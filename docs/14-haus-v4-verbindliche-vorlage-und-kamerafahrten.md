# Haus V4 – Vorlage für Modell, Frontend und Kamerafahrten

Stand: 6. September 2026. Leon hat die vorhandenen V4-Mockups als Ziel für den
Blender-Nachbau ausgewählt: dieselbe Erscheinung, derselbe Detailgrad und dieselbe
Darstellung im Frontend. Dieser Stand heißt **v4-reference-01**.

Die Auswahl betrifft die gestalterische Vorlage. Eine passende native V4-Szene,
Kamerafahrten und ein Web-Export sind noch zu erstellen und visuell zu prüfen.

## Gesicherte Quelle

- [Acht Originalbilder und beide Grundrisse](mockups/house-v4/README.md).
- [Website-Mockups](mockups/house-v4/website.html) mit vorhandener Typografie,
  Header, Textspalte, Bildfläche, CTA und sechs Kapiteln.
- [Desktop- und Mobilreferenzen](mockups/house-v4/website-mockups/).
- [Kamera- und Bewegungsplan](mockups/house-v4/motion-plan.json).
- [Prüfsummen aller gesicherten Dateien](mockups/house-v4/reference-lock.json).
- [Portables Referenzpaket](../assets/reference/house-v4-reference-01.zip).

Das Paket enthält Original-PNGs, Frontend-Screenshots, SVG-Grundrisse, Prompts,
lokale Schriftdateien, Logo, CSS, HTML und diese Vorgaben. Die ZIP-Struktur erhält
die relativen Projektpfade. Die Vorschau braucht zum Anzeigen keinen Astro-Server.
Die Header- und Kontaktlinks verweisen weiterhin auf die lokale V3-Website.

Die ausgewählten Dateien werden nicht neu generiert oder überschrieben. Änderungen
an V4 werden als neue Revision mit eigenem Ordner und Vergleich zur Referenz geführt.
Die beiden Generatoren für Grundrisse und Vorschau stoppen bei vorhandenem
`reference-lock.json`. Prüfen lässt sich der Stand ohne Änderungen mit:

```powershell
python docs/mockups/house-v4/reference_package.py --verify
```

## Welche Vorlage entscheidet?

| Gegenstand | Maßgebliche Referenz | Für den Nachbau |
| --- | --- | --- |
| Baukörper und Fassade | 01 Planung | Zwei Vollgeschosse, Giebelfront, einfaches Stehfalz-Satteldach, Fensterfolge, Eichen-Eingang, Terrasse. |
| Öffnungsbild | 02 Öffnung | Zwei getrennte, vollständig eingerichtete Etagen; Dach mit Giebel und PV als eigene Gruppe. |
| EG und Möbel | 03 Installation | Wohnküche links, Technik rechts vorne, WC und Büro rechts; echte Zargen, Sockel und Einbauten. |
| Lichtwirkung | 04 Beleuchtung | Gleiche EG-Geometrie und Kamera wie 03; Licht auf Tisch, Arbeitsplatte, Sockel und Polster. |
| OG und Ausstattung | 05 Smart Home | Eltern, zwei Kinderzimmer, Familienbad, Flur, Taster und Beschattung. |
| Eingang und Detailniveau | 06 Sicherheit | Putz, Holz, Steinstufe, Fensterleibung und lesbare Türstation aus der Nähe. |
| Dach und PV | 07 Photovoltaik | Dieselben zehn Module in zwei Reihen zu fünf; sauberer Randabstand, Falze, Traufe und Rinne. |
| Abschluss | 08 Abschluss | Außenkamera von 01 mit warmem Innen- und Eingangslicht. |
| Website-Anordnung | Acht Desktop-Screenshots; zwei Mobilbeispiele | Verhältnis von Text zu Haus, Typografie, Weißraum, CTA und Navigation. |
| Erschließung | Beide SVG-Grundrisse | Alle Zimmer zugänglich; konsistenter Treppenschacht und nachvollziehbare Nassraumzone. |

Die Rasterbilder sind keine maßhaltigen Ansichten desselben 3D-Modells. Bei einem
Widerspruch wird die sichtbare Hausidentität erhalten und die Konstruktion dahinter
korrigiert. Die Außenansicht bestimmt die Fenstermaße; 06 ist eine Detail- und
Materialvorlage. Die U-Treppe wird einmal korrekt von EG zu OG konstruiert; das
Treppenauge in 02 zeigt ihre Öffnung nach unten. WC-Zugang und Kinderschreibtisch
werden nach den SVGs ergänzt. Das ist kein Anlass für eine neue Hausrichtung oder
eine vereinfachte Einrichtung. Unvermeidbare sichtbare Änderungen werden anhand
eines direkten Vergleichs mit der ausgewählten Ansicht kenntlich gemacht.

## Detailgrad des Modells

| Bereich | Erforderliche sichtbare Ausführung |
| --- | --- |
| Architektur | Wandstärke und Leibung, Fensterrahmen mit Profil, zurückgesetztes Glas, Zargen, Türblatt und Griff, Sockelleisten, saubere Schnittkanten. |
| Dach | Zwei zusammenhängende Dachflächen, Falze, Ortgänge, Dachkante, Rinnen/Fallrohre, PV-Rahmen und geringe reale Montageabstände. |
| Böden | Eichenplanken mit richtiger Maserungsrichtung und dezenten Unterschieden; Stein/Fliesen mit maßstäblichen Fugen und Schwellen. |
| Polstermöbel | Geformte Sitz- und Rückenkissen, sichtbare Trennung der Polster, Nähte, weiche Kanten, Stoffstruktur und Bodenkontakt. |
| Betten | Rahmen, Matratze, einzelne Kissen, Decke mit Falten und Überstand, zurückhaltende Leinenstruktur und Nachttische. |
| Küche | Frontfugen, Griffe/Griffmulden, Arbeitsplattenstärke, echtes Spülbecken mit Ausschnitt, Armatur, Kochfeld, Geräte und Schrankabschlüsse. |
| Bad und WC | Hohle Becken, Armaturen, Duschglas und Beschläge, Wanne, WC, Spiegel, Schrankfronten und plausible Abstände. |
| Technik | Verteilung mit erkennbaren Reihen und Anschlüssen, Rack/Netzwerk, Gerätefronten, Waschmaschine/Trockner und zurückhaltende Kabelwege. |
| Kleine Ausstattung | Tische/Stühle mit echten Querschnitten, Teppichkante, wenige Bücher, Keramik und Pflanzen entsprechend der Vorlage. |
| Materialien und Licht | Warmer heller Putz, Eiche, Leinen, heller Stein, Anthrazit; feine Rauheit, weiche Kontaktschatten und kontrolliertes Glas. |

Details werden in den jeweiligen Website-Ausschnitten beurteilt. Vereinfachte
Möbelklötze, flächige Ersatzmaterialien oder überstrahlte weiße Flächen erreichen
diese Vorlage nicht. Die native Szene bekommt genug Geometrie für die Nahansicht;
die Website-Leistung wird über Bildformat, Auflösung, Nachladen und Bildspeicher
optimiert. Der Browser lädt weiterhin Bilder, nicht sämtliche Möbel-Meshes.

## Kamerafahrten als eigenes Qualitätsziel

Die Mockups zeigen Zielbilder, keine vorhandenen Fahrten. Im aktuellen R3-Code
wechselt die Kamera von OPEN bei Frame 51 zu TECH bei Frame 59. Das Desktopprofil
verwendet Schrittweite 2: 51 → 53 → 55 → 57 → 59, also vier Bildschritte. Bei einem
großen Positions- und Maßstabswechsel bleibt das sichtbar, auch auf längerem
Scrollweg. V4 übernimmt diese kurze Kamerasequenz nicht ungeprüft.

**Eine zusammenhängende Szene und Kamerabahn pro Ausgabeprofil.** Die Kamera
verwendet Perspektive, einen festen Horizont ohne Rollbewegung und einen separat
geführten Zielpunkt. Ein längeres Objektiv um 70 mm ist ein Startwert für den
Bildabgleich, kein bereits ermittelter Kamerawert. Reale Dolly-Bewegung und
gezielte Höhenänderung ersetzen laufendes Brennweiten-Pumpen. Position und Ziel
werden gemeinsam geplant; sie müssen aus den gültigen Zwischenpositionen auf
die Referenzansichten zufahren. Exakte Weltkoordinaten entstehen erst am Modell.

### Ablauf und Ruhepositionen

Die Prozentwerte sind ein konkreter erster Bewegungsentwurf. Die Bildziele und
die Trennung der Bewegungsschritte sind fest; Zeiten werden nach dem Testfilm
abgestimmt. Der zugehörige JSON-Plan liegt außerhalb der aktiven Website-Konfiguration.

| Scrollweg | Bewegung / Bild | Zweck |
| --- | --- | --- |
| 0–8 % | 01 geschlossen halten | Einstieg lesen; Navigation ruht bei 4 %. |
| 8–14 % | Dach zuerst anheben; Kamera fährt etwas zurück und höher | Platz schaffen, statt das Dach an den Bildrand zu schneiden. |
| 14–20 % | OG mit Bodenplatte anheben; Kamera erreicht 02 | Zusammenhang der beiden Etagen erklären. |
| 20–23 % | 02 kurz halten | Explosionsansicht lesbar machen. |
| 23–30 % | Kamera kontrolliert nach unten zum EG; angehobenes OG/Dach aus dem Sichtkegel führen | Keine Fahrt durch Decken; Ziel 03. |
| 30–39 % | 03 halten | Technik lesen; Ruheposition 35 %. |
| 39–43 % | Kamera bleibt stehen; Leitungsakzente aus, warmes Licht an | 03 und 04 durch Wirkung verbinden. |
| 43–51 % | 04 halten | Lichtwirkung lesen; Ruheposition 47 %. |
| 51–57 % | Zuerst Abstand gewinnen, dann außen am Haus zur offenen OG-Ebene steigen | Etagenwechsel nachvollziehbar halten; Ziel 05. |
| 57–60 % | Kamera steht; Beschattung und Lichtszene ändern sich | Bedienung und Wirkung zeigen. |
| 60–67 % | 05 halten | Smart Home lesen; Ruheposition 63 %. |
| 67–71 % | Kamera fährt außerhalb des Hauses zurück; OG und Dach schließen sich räumlich korrekt | Vor dem Eingangsausschnitt wieder ein zusammenhängendes Haus. |
| 71–76 % | Ruhiger Dolly zum Eingang | 06 erreichen, Türstation früh im Bild halten. |
| 76–82 % | 06 halten | Sicherheit lesen; Ruheposition 79 %. |
| 82–88 % | Kamera zieht zurück und steigt in einem flachen Bogen zur Dachfläche | Kein abrupter Sprung von Türgriffgröße zur Gesamtansicht. |
| 88–94 % | 07 halten | PV lesen; Ruheposition 91 %. |
| 94–98 % | Zur exakten Außenkamera von 01 zurück; Innen-/Eingangslicht wärmer | Abschluss 08. |
| 98–100 % | 08 halten | Ruhig in den folgenden Website-Bereich übergehen. |

An Ruhepositionen gehen Geschwindigkeit und Beschleunigung weich auf null.
Innere Wegpunkte einer längeren Fahrt werden ohne Zwischenstopp durchfahren.
Ein mögliches Profil für eine vollständige Fahrt ist `6t⁵ − 15t⁴ + 10t³`; es wird
auf den Wegfortschritt angewendet, nicht als unabhängiges Easing jeder XYZ-Achse.
Kurve, Zielpunkt und Dach-/Geschossbewegung werden auf Kollisionen, Überschwingen
und den ganzen Sichtkegel geprüft. Die Reihenfolge lässt sich vollständig umkehren.

### Zwischenbilder und Web-Player

- Erster Vorschau-Takt: 1.441 Timeline-Positionen für einen 24-s-Test bei 60 fps;
  Desktop-Schritt 2, Mobil-Schritt 3 als Ausgangspunkt. Das ergibt in einer Fahrt
  von 6 % etwa 43 bzw. 29 Bildschritte statt vier. Es ist eine Testbasis, kein
  ungeprüftes Renderbudget für die finale Ausgabe.
- Bewegte Abschnitte erhalten genügend echte Blender-Zwischenbilder. Gleichartige
  Ruhephasen werden über Aliase wiederverwendet. Erst eine schnelle Vorschau
  rendern, dann problematische Fahrten verdichten und die finale Menge festlegen.
- Im Zielausschnitt dürfen Kanten weder versetzen noch flackern. Ein langsamer
  Scrolltest prüft Bildschritte; normales Scrollen prüft Rhythmus; schnelles
  Vor-/Zurückscrollen prüft Laden und Aktualität des angezeigten Frames.
- Scrollfortschritt wird direkt und monoton auf die geprüfte Timeline abgebildet.
  Keine zweite lange Verzögerung im Player; kein nachlaufendes Abarbeiten veralteter
  Frames. Kapiteltext, Beschriftung und Kamerapose müssen zum sichtbaren Bild passen.
- Ausgangspunkt bleibt der bewusst langsamere Weg von 900 svh am Desktop und
  750 svh mobil. Erst am V4-Prototyp prüfen, ob die Leseruhe pro Kapitel ausreicht.
- Höhere Renderauflösung erhält Materialdetails. Startwerte: Desktop 1600², mobil
  900², anschließend bei tatsächlicher Bildfläche/DPR und komprimiertem WebP prüfen.
  Cache z. B. sechs bzw. neun dekodierte Bilder (ca. 59 bzw. 28 MiB reine Bilddaten);
  Canvas und laufende Dekodierungen kommen hinzu. Nicht alle Frames vorab laden.

## Frontend-Abgleich

Die gespeicherten Website-Screenshots sind das Layoutziel. Header, Typografie,
Weißraum, linke Textspalte, Bildgröße, rote Akzente und sechs Kapitel bleiben
zusammenhängend. Acht Bilder bedeuten keine acht Leistungsnummern: Öffnung und
Abschluss sind Übergänge innerhalb der sechs Kapitel.

Die Modellgrafik enthält keine eingebrannten UI-Texte. An der gewählten ruhigen
Bildgestaltung orientieren; zusätzliche Beschriftungen nur dort verwenden, wo die
Komponente sonst nicht verständlich wäre. Mobile Ansichten werden eigens komponiert,
mit vollständig lesbarem Hauptgegenstand und erreichbarem CTA. Reduzierte Bewegung,
kleine Höhen, fehlendes JavaScript und Ladefehler erhalten vollständige statische
Kapitel. Das V4-Assetpaket wird erst nach erfolgreicher Prüfung umgestellt.

## Reihenfolge und visuelle Abnahme

1. **Modell:** EG/OG, Treppe, Fassade und Dach geschlossen sowie geöffnet abgleichen.
2. **Materialien und Ausstattung:** 01, 03, 05 und 06 als vollwertige Detailbilder
   aus derselben Szene rendern. Direkter Vergleich neben der unveränderten Vorlage.
3. **Kamera:** Alle Fahrten als günstigen 24-s-Vorschaufilm vorwärts und rückwärts
   prüfen, besonders Explosionsansicht → EG, EG → OG und Eingang → Dach.
4. **Frontend-Probe:** Diese Vorschau im echten Scroll-Player bei Desktop-, Tablet-
   und Handybreite ansehen. Frame-Dichte, Leseruhe und Bildausschnitt dort entscheiden.
5. **Finale Ausgabe:** Erst die abgestimmte Szene hochauflösend rendern; danach
   Bildkompression, begrenzten Speicher und statische Rückfälle prüfen.

Akzeptiert ist die Umsetzung, wenn Hausidentität, Möbel, Materialstruktur, Licht
und Frontend-Anordnung im direkten Vergleich denselben Eindruck erreichen und
die Bewegung ohne Sprünge, Decken-Durchfahrten, Rollbewegungen oder Flackern lesbar
bleibt. Ein bestandener Build oder eine technisch korrekte Animation allein
erfüllt diese visuelle Anforderung nicht. Die native Szene wird danach als
`assets/3d/elektro-hubmann-house-v4.blend` separat gespeichert.
