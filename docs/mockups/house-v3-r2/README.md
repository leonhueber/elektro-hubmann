# Haus V3 – Mockups der Scrollzustände

Stand: 5. September 2026. Acht Desktop-Bildzustände und zwei mobile Beispiele.
Die [Galerie](index.html) zeigt die ausgewählten Entwürfe in Scrollreihenfolge.

**Architektur überholt:** In diesen Bildern fehlen Schlafzimmer, Bad und eine
vollständige Erschließung. Die [Grundrisskorrektur R3](../house-v3-r3/README.md)
ersetzt die Raumaufteilung mit einem vollständigen Wohnhaus und einer neuen
offenen Frontendansicht. Die übrigen R2-Bilder dienen noch als Referenzen für
die Leistungsfolge; sie sind keine gültigen Geometrievorlagen.

## Grundlage

Das lokale Frontend wurde im Browser aufgerufen und im Desktop- und Mobilformat
angesehen. Die Referenzbilder liegen in `references/`. Der zunächst auftretende
React-Fehler war nach dem Neustart der Entwicklungsvorschau mit erneuertem
Vite-Cache nicht mehr in der Desktopansicht vorhanden. Der Wechsel zur mobilen
Installation hing bei einem Prüflauf; eine frisch geöffnete mobile Planungsansicht
war darstellbar. Dies ist keine vollständige Funktionsprüfung des Players.

Die Mockups übernehmen Logoanordnung, Weißraum, Inter-/Inter-Tight-Hierarchie,
rote Akzente, Textspalte, umrandete Kontaktaktion und Kapitelnavigation aus dem
Frontend. Die Hausgestaltung folgt dem
[Vorschlag für den gestalterischen Neustart](../../11-hausmodell-v3-gestalterischer-neustart.md).
Die Planung ist der Bildanker; die weiteren Zustände wurden daraus mit
ImageGen und zusätzlichen Zustandreferenzen entwickelt.

## Zustände

| Bild | Kapitel im Frontend | Vorgeschlagener Bereich | Schwerpunkt |
| --- | --- | --- | --- |
| [01 Planung](states/01-planung.png) | 01 Planung | 0–10 % | Geschlossenes Wohnhaus. |
| [02 Öffnung](states/02-oeffnung.png) | 02 Installation | 10–23 % | Dach hebt sich, vordere Hülle öffnet sich. |
| [03 Installation](states/03-installation.png) | 02 Installation | 23–37 % | Offener Schnitt, Verteilung, Strom und Daten. |
| [04 Beleuchtung](states/04-beleuchtung.png) | 03 Beleuchtung | 37–51 % | Lichtwirkung auf Raum und Oberflächen. |
| [05 Smart Home](states/05-smart-home.png) | 04 Smart Home | 51–64 % | Taster, Beschattung und Lichtszene. |
| [06 Sicherheit](states/06-sicherheit.png) | 05 Sicherheit | 64–76 % | Näherer Blick auf den Eingangsbereich. |
| [07 Photovoltaik](states/07-photovoltaik-r2.png) | 06 Photovoltaik | 76–93 % | Dach und lokale Öffnung zur Energietechnik. |
| [08 Abschluss](states/08-abschluss.png) | 06 Abschluss | 93–100 % | Vollständig geschlossenes, beleuchtetes Haus. |

Öffnung und Abschluss ergänzen die sechs bestehenden Kapitel um beurteilbare
Übergangsbilder. Die Zeitbereiche sind noch keine festgelegte Animation.

Mobil: [Installation](mobile/03-installation.png) und
[Sicherheit](mobile/06-sicherheit-r2.png). Beide verwenden die mobile Reihenfolge
Kopfzeile → Fortschritt → Bild → Text → Aktion sowie eine einzelne Beschriftung.

## Einordnung für die Modellierung

Die Bilder sind generierte Gestaltungsentwürfe, keine Renderings eines bereits
gebauten neuen Blender-Modells. Sie legen Bildsprache, Funktion, Komposition und
Kameraabsicht fest. Pixelgenaue Identität von Raummaßen, Mobiliar, Geräten und
Bauteilen über alle Bilder ist damit nicht nachgewiesen.

Bei der Umsetzung wird eine einzige 3D-Szene verbindlich: gleicher Grundriss,
identische Fenster, acht PV-Module, fest positionierte Geräte und ruhende Möbel.
Die Gerätedarstellung und insbesondere die genaue Zuordnung der Beschriftungen
werden in Blender geprüft. Im PV-Mockup ist die Trennung zwischen Wechselrichter
und Hausverteilung noch zu präzisieren. Die Linien zeigen schematische Zusammenhänge.
Speicher und Wallbox sind nicht Teil dieser Entwürfe.

Die originale Logo-Datei, die echten Webfonts und die HTML-Texte bleiben bei der
späteren Umsetzung die Quelle der Benutzeroberfläche. Generierte Schrift und
Logos werden nicht als Produktionsassets übernommen. Die Abschlussüberschrift
und ihr Absatz sind neue Textvorschläge; die übrigen Kapitel beruhen auf
`src/config/version-g-story-assets.ts`.

## Dateien und Prüfung

- `states/`: acht ausgewählte Desktopzustände; die erste PV-Fassung bleibt
  zusätzlich erhalten. Die Galerie verwendet die korrigierte `-r2`-Datei.
- `mobile/`: zwei ausgewählte mobile Beispiele; die erste Sicherheitsfassung
  bleibt erhalten. Die Galerie verwendet die korrigierte Fortschrittsmarkierung.
- `references/`: echte Frontend-Aufnahmen als Gestaltungsgrundlage.
- `index.html`: lokale Bildgalerie mit Einzelansicht, Übersicht und Mobilansicht.

Desktop-Zielverhältnis: 1440 × 1024. Mobile-Zielverhältnis: 390 × 844.
Die PNGs wurden von ImageGen in höherer Auflösung mit entsprechendem
Seitenverhältnis ausgegeben und in der Galerie ohne Verzerrung eingebunden.
Alle Bilder wurden visuell angesehen. Modulzahl und mobile Fortschrittsmarkierung
wurden nach dem Vergleich korrigiert. Die Galerie ersetzt keine Prüfung der
späteren Scrollbewegung.

Die lokale Galerie wurde im Browser geprüft: acht Einträge in der Desktopübersicht,
korrekte Bildzuordnung beim Zustandswechsel, mobile Sicherheitsansicht mit der
korrigierten Fassung und kein horizontaler Seitenüberlauf im geprüften Fenster.

Die Galerie lässt sich auch direkt als `index.html` öffnen. Für eine lokale
Browser-Vorschau aus dem Projektverzeichnis:

```sh
python -m http.server 4323 --bind 127.0.0.1 --directory docs/mockups/house-v3-r2
```

Nächster Gestaltungsschritt: Hausform, offene Raumaufteilung und die Nähe der
Sicherheitsansicht anhand dieser Bilder festlegen; danach in Blender modellieren.
