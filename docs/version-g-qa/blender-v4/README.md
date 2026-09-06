# Haus V4 – Blender-Prüfung

Stand: 6. September 2026. Native Szene:
`assets/3d/elektro-hubmann-house-v4.blend`.
Referenz: das unveränderte Paket `v4-reference-01`.

[Vorlage und Blender nebeneinander vergleichen](compare.html) ·
[Modell und Blender-Bedienung](../../../blender/house_v4/README.md)

## Ansichten

Die PNGs werden direkt von Blender/Cycles mit 1.200 × 1.200 Pixeln und
40 Samples ausgegeben. Sie sind eigenständige Modellprüfbilder; die V4-Sequenz
ist noch nicht in die Website eingebaut. Modellstand: `v4-build-02`, einschließlich
des vergrößerten PV-Felds, der wärmeren Beleuchtung und der überarbeiteten Türen.

| Bild | Modellzustand |
| --- | --- |
| [01 Planung](01-planung.png) | Geschlossenes Haus mit zwei Vollgeschossen und Satteldach |
| [02 Öffnung](02-oeffnung.png) | Dach und Obergeschoss angehoben, vordere Schnittwände geöffnet |
| [03 Installation](03-installation.png) | Eingerichtetes EG, Verteiler, Netzwerk und Leitungsweg |
| [04 Beleuchtung](04-beleuchtung.png) | Identische EG-Kamera mit verstärkten warmen Raumleuchten |
| [05 Smart Home](05-smart-home.png) | OG mit drei Schlafzimmern, Bad, Treppenöffnung und Beschattung |
| [06 Sicherheit](06-sicherheit.png) | Eingang mit Holztür, Videosprechanlage und Pflanzgefäß |
| [07 Photovoltaik](07-photovoltaik.png) | Dachperspektive auf zehn PV-Module |
| [08 Abschluss](08-abschluss.png) | Gleiche Außenkamera wie 01 mit warmer Innenbeleuchtung |

## Native Prüfung

[`native-validation.json`](native-validation.json) prüft die tatsächlichen
Blender-Objekte und ihre Zugehörigkeit. Alle vierzehn Prüfungen bestanden:
V4-Szene, drei getrennt bewegliche Baugruppen, zehn getrennte dachgebundene
PV-Module innerhalb der Dachfläche,
drei OG-Betten, zwei Treppenläufe mit je neun Steigungen, passende Deckenöffnung,
acht Perspektivkameras, Materialbelegung, neun eingepackte Bilder und die
modellierte Videosprechanlage. Zusätzlich sind die Auflageflächen von Podest,
Terrasse und beiden Pflanzgefäßen sowie der Anschluss der mit dem Dach bewegten
OG-Decke geprüft.

Die Referenzprüfung bestätigt weiterhin 59 unveränderte Dateien, einschließlich
der acht Originalmockups, elf Website-Screenshots und des Kamera-Bewegungsplans.

## Modell und weitere Umsetzung

Die Geometrie wurde über die sichtbare Python-Konsole im geöffneten Blender
aufgebaut. Die Seitenleiste **V4 Haus** schaltet Kamera, Geschosspositionen,
Schnittteile und Lichtzustand um. Die Prüfbilder zeigen dasselbe geometrisch
zusammenhängende Haus in allen Zuständen.

Die AI-Vorlagen weichen bei Treppe, Raum- und Fassadenöffnungen teilweise
voneinander ab. Der Nachbau verwendet eine reale U-Treppe und abgestimmte
Öffnungen über beide Geschosse. Möbelformen, Raumaufteilung und Materialwirkung
orientieren sich an der jeweiligen Vorlage; Pixelgleichheit wird nicht behauptet.

Die kontinuierliche Öffnungsanimation, weiche Kamerafahrten, bewegte Beschattung
sowie Desktop-/Mobilrendering und Web-Export stehen noch aus. Kameramarker allein
stellen diese Übergänge nicht her. Der verbindliche Bewegungsplan bleibt die
Grundlage für diesen nächsten Schritt.

`iterations/` enthält überholte Diagnosebilder aus der Kamerakorrektur und
Materialprüfung. Für den aktuellen Vergleich gelten die acht PNGs direkt in
diesem Verzeichnis.
