# Hausmodell V3 / R3 – vollständiges Raumprogramm

Stand: 5. September 2026. Grundrissstudie und überarbeiteter offener Desktopzustand.

**In Blender umgesetzt:** Die nach diesem Entwurf neu gebaute
[R3-Szene](../../../assets/3d/elektro-hubmann-house-v3-r3.blend) und ihre
[echten Renderings](../../version-g-qa/blender-v3-r3/README.md) liegen separat.
Die folgenden PNGs bleiben die ursprünglichen Gestaltungsreferenzen.

Die R2-Mockups zeigten im Wesentlichen Wohnen, Küche und Technik. Schlafzimmer,
Bad und eine nachvollziehbare Erschließung fehlten. R3 korrigiert diese Grundlage.
Die Bilder sind **ImageGen-Entwürfe, keine Renderings eines neuen Blender-Modells**.
Die [erste Website-Animation](../../12-haus-r3-website-animation.md) wird inzwischen
aus einer separaten Blender-Ableitung exportiert und ist lokal in die Startseite
integriert. Die folgenden Bilder bleiben reine Gestaltungsreferenzen.

## Ansichten

- [Grundriss](01-grundriss.png): vollständige Raumaufteilung mit Möbeln, Fenstern und Türen.
- [Offenes Haus im Frontend](02-installation.png): dieselbe Raumorganisation im Installationskapitel.
- [Galerie](index.html): beide Ansichten mit Raumprogramm und Hinweisen zur Scrollbewegung.
- [Prompts](prompts.md): verwendete Texte, Generierungsmodus und Bildreferenzen.

Die Zwischenfassung `02-installation-entwurf.png` bleibt erhalten. Ihre beiden
Gerätebeschriftungen waren nicht eindeutig zugeordnet; die gewählte Fassung
verzichtet auf diese Beschriftungen. Die späteren Gerätenahansichten bekommen
an den tatsächlichen Blender-Objekten verankerte Labels.

## Grundriss als Modellvorgabe

Vorgeschlagen ist weiterhin ein eingeschossiges Haus mit Flachdach. Das vollständige
Raumprogramm benötigt einen größeren Baukörper als der vorherige Entwurf:
ungefähr **12,0 × 11,4 m außen**, mit 30 cm Außenwänden und 15 cm Innenwänden.
Die folgende Maßaufteilung ist eine schematische Modellvorgabe. Bildproportionen
aus ImageGen sind nicht maßhaltig und dürfen nicht als Bauzeichnung vermessen werden.

| Raum | Lage vom Eingang aus | Geplante lichte Fläche | Erkennbare Einrichtung |
| --- | --- | ---: | --- |
| Wohnen / Essen / Küche | Links vorne | 37,1 m² | Sofa, Esstisch, L-Küche |
| Elternschlafzimmer | Links hinten | 21,0 m² | Doppelbett, Nachttische, Schrankzone |
| Hauswirtschaft / Technik | Rechts vorne | 7,8 m² | Waschmaschine, Trockner, Verteilung, Netzwerk |
| Bad mit WC | Rechts, hinter der Technik | 10,0 m² | Dusche, WC, Waschtisch |
| Kinderzimmer | Rechts, hinter dem Bad | 13,5 m² | Einzelbett, Schreibtisch, Schrank |
| Büro / Gästezimmer | Rechts hinten | 13,7 m² | Arbeitsplatz, Schlafsofa, Schrank |
| Flur / Eingang | Mittig, gerade | 14,0 m² | Eingang und direkte Raumzugänge |

Summe der geplanten lichten Raumflächen: ca. 117 m². Dies ist keine normativ
ermittelte Wohnflächenangabe. Das generierte Bild rundet Büro/Gast auf ca. 13,5 m².

### Geometrische Aufteilung

Koordinaten beziehen sich auf die lichte Innenfläche 11,4 × 10,8 m;
X läuft von links nach rechts, Y vom Eingang zur Rückseite.

- Linker Raumstreifen: X = 0 bis 5,45 m.
- Linke Flurwand: X = 5,45 bis 5,60 m.
- Flur: X = 5,60 bis 6,90 m; durchgehend 1,30 m lichte Breite.
- Rechte Flurwand: X = 6,90 bis 7,05 m.
- Rechter Raumstreifen: X = 7,05 bis 11,40 m.
- Links: Wohnen Y = 0 bis 6,80 m; Trennwand bis 6,95 m;
  Eltern Y = 6,95 bis 10,80 m.
- Rechts: Technik Y = 0 bis 1,80 m; Bad Y = 1,95 bis 4,25 m;
  Kind Y = 4,40 bis 7,50 m; Büro/Gast Y = 7,65 bis 10,80 m.
  Zwischen den Räumen jeweils 0,15 m Trennwand.

Alle sechs Räume erhalten einen eigenen Zugang vom Flur. Schlafzimmer und Bad
sind keine Durchgangsräume. Türöffnungen von ungefähr 0,85–0,90 m und ihre
Schwenkbereiche werden vor der Möblierung in Blender angelegt. Die lichte
Flurbreite bleibt frei. Bad und Hauswirtschaft liegen an einer gemeinsamen
Installationswand. Jeder Aufenthaltsraum bekommt ein Außenfenster; das Bad eine
passende kleinere Öffnung. Fensterpositionen folgen dem Grundriss.

## Auswirkung auf die acht Scrollzustände

| Zustand | Vorgabe für die neue Szene |
| --- | --- |
| 01 Planung | Größeres geschlossenes Haus; mittiger Eingang; Fenster passend zu allen Räumen. |
| 02 Öffnung | Dach hebt sich und blendet aus. Kamera wird steiler. Fassaden und verdeckende Innenwände gehen in einen niedrigen Schnitt über. |
| 03 Installation | Zuerst vollständigen Grundriss zeigen, dann näher an Technik und Flur. Wenige Strom- und Datenwege von dort in reale Räume führen. |
| 04 Beleuchtung | Wohnlicht, Leselicht im Schlafzimmer und Licht am Badspiegel erhalten konkrete Orte. Eine Lichtwirkung bildet jeweils den Fokus. |
| 05 Smart Home | Taster und zugehörige Beschattung an feststehenden Bauteilen zeigen. Grundriss, Fenster und Möbel bleiben identisch. |
| 06 Sicherheit | Eingang und Türstation in einer Nahansicht zeigen. Der Eingang führt weiterhin in den Flur. |
| 07 Photovoltaik | Dach kehrt zurück; PV sitzt auf derselben größeren Dachfläche. Anschluss führt in den echten Technikraum. |
| 08 Abschluss | Dasselbe Haus schließt sich vollständig. Keine Änderung von Raumaufteilung, Fenstern oder Eingang. |

Niedrige Schnittwände von ungefähr 0,85–1,10 m erhalten Zimmergrenzen und
Türöffnungen. Nur verdeckende Teile werden reduziert. Es werden keine Privaträume
entfernt, um Platz für Technik zu schaffen. Für kleine Geräte braucht es gezielte
Nahansichten; die vollständige Draufsicht allein reicht besonders mobil nicht aus.

## Nächste Modellprüfung

Vor einer neuen kompletten Bildserie wird der Grundriss in einer einzigen Blender-Szene
maßhaltig aufgebaut und in Draufsicht sowie aus der offenen Website-Kamera geprüft:
Raumzugänge, Türschwenkbereiche, Möbeltiefen, Fenster, Sanitäranordnung und Wartungsraum
vor der Verteilung. Anschließend folgen geschlossene Ansicht und Beleuchtung.
Die übrigen R2-Zustände sind weiterhin Bildreferenzen für die Erzählung, jedoch
keine gültige Architekturvorlage für R3.

Die beiden R3-Bilder wurden visuell auf Raumanzahl, Raumfolge, Flurzugänge,
Schlafmöbel und Sanitärgegenstände geprüft. Exakte Maße, Elektroplanung und
Identität aller Details über mehrere Renderings sind erst im 3D-Modell prüfbar.

Die Galerie wurde im Browser geöffnet: Beide Bilder laden vollständig, die
Sprungnavigation funktioniert und bei 390 px Viewportbreite entsteht kein
horizontaler Seitenüberlauf. Dies prüft die Bildgalerie, nicht den Website-Player.

Lokale Galerie: `python -m http.server 4324 --bind 127.0.0.1 --directory docs/mockups/house-v3-r3`.
