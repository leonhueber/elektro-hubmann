# Hausmodell V3 / R3 – Blender-Renderings

Stand: 5. September 2026. Neu aufgebaut nach dem erweiterten R3-Mockup.

Die Bilder stammen aus derselben [nativen Blender-Szene](../../../assets/3d/elektro-hubmann-house-v3-r3.blend).
Sie zeigen das vollständige Raumprogramm mit Elternschlafzimmer, Kinderzimmer,
Büro/Gast, Wohnküche, Bad/WC, Hauswirtschaft/Technik und durchgehendem Flur.

## Ansichten

| Vorschau | Inhalt |
| --- | --- |
| [Offenes Haus](preview/open.jpg) | Vollständige Raumaufteilung und schematische Strom-/Datenwege. |
| [Geschlossen](preview/closed.jpg) | Fassade, mittiger Eingang, Flachdach und acht PV-Module. |
| [Grundriss](preview/plan.jpg) | Raumzugänge, Möbel und Fenster aus der Draufsicht. |
| [Beleuchtung](preview/lighting.jpg) | Lichtwirkung im Wohnraum, in Küche, Schlafzimmer und Bad. |
| [Technikraum](preview/technical.jpg) | Verteilung, Netzwerk, Wechselrichter und Hauswirtschaft. |
| [Smart Home](preview/smart-home.jpg) | Geänderte Lichtszene und Beschattung am festen Fenster. |
| [Dachöffnung](preview/opening.jpg) | Früher Zwischenzustand der Öffnungsbewegung. |
| [Abschluss](preview/closing.jpg) | Geschlossenes, beleuchtetes Haus. |
| [Übersicht](preview/overview.jpg) | Sechs zentrale Ansichten zusammen. |

Die PNG-Dateien im Hauptordner sind Cycles-Renderings mit Transparenz und
Schattenfänger. Die JPEG-Vorschauen setzen diese auf Weiß und sind für die
Betrachtung auf dem Handy kleiner gespeichert.

## Umsetzung und Prüfung

Die Raumgrenzen folgen den R3-Maßvorgaben: 12,0 × 11,4 m außen, 30 cm Außenwände,
15 cm Innenwände, 1,30 m freier Flur. Alle Räume besitzen eigene Türöffnungen.
Hauptmöbel, Sanitärgegenstände und Geräte sind räumlich angelegt. Die Geräte im
Technikraum wurden für freie Zugänge und sichtbare Fronten innerhalb des Raums
präzisiert. Der vollständige Grundriss bleibt in allen Innenraumkapiteln erhalten.

[validation.json](validation.json) enthält die Prüfung der gespeicherten Szene:
Raumflächen, Flur- und Türbreiten, Möbelgrenzen, Fenster, Dachgruppierung,
Sichtbarkeit, eingepackte Texturen und reversible Timeline-Zustände. Die
Türschwenkbereiche werden in 18 Winkelstellungen gegen die tatsächlichen
Möbelgrenzen geprüft. Eine zunächst gefundene Kollision mit der Duschtasse
wurde durch deren Anpassung auf 1,26 × 1,13 m behoben.
Die Ansichten werden zusätzlich visuell auf Raumfolge, Sichtbarkeit und
Bauteilanschlüsse geprüft. Das Modell ist keine ausführungsreife Bau- oder
Elektroplanung.

Die gestalterische Ausführung ist eine native 3D-Interpretation des Mockups.
Die [Detailfassung](../../13-haus-r3-materialien-und-details.md) ergänzt geformte
Polster, Leinen, Holzmaserung, Steinoberflächen und ausgearbeitete Anschlüsse.
Ihre Prüfberichte liegen separat in `detail/` und `web-detail/`.
Die [erste Website-Animation](../../12-haus-r3-website-animation.md) verwendet
eine separate Ableitung dieser Szene mit Kapitelkameras und projizierten
Beschriftungen. Die Startseite ist lokal auf diese R3-Bildfolge umgestellt.
Details zu Bedienung und ursprünglichen Keyframes stehen im
[Blender-README](../../../blender/house_r3/README.md).
