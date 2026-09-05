# Haus V3 / R3 – Blender-Modell

**Aktuelle Detailfassung:** `assets/3d/elektro-hubmann-house-v3-r3-detail.blend`.
Sie verfeinert Möbel, Textilien, Holz, Stein und Wandanschlüsse auf Grundlage der
hier beschriebenen Architektur. Vorgehen und Web-Export stehen in
[Materialien und Einrichtung](../../docs/13-haus-r3-materialien-und-details.md).
Die folgende Beschreibung dokumentiert weiterhin die erhaltene Architekturquelle.

Die native Szene setzt den erweiterten R3-Grundriss um. Sie enthält sechs
eingerichtete Räume und einen durchgehenden Flur. Alle Ansichten stammen aus
derselben editierbaren Geometrie.

- Modell: `assets/3d/elektro-hubmann-house-v3-r3.blend`
- Bilder und Prüfbericht: `docs/version-g-qa/blender-v3-r3/`
- Kleine Vorschauen auf Weiß: Unterordner `preview/`
- Referenz: `docs/mockups/house-v3-r3/`

Die [erste Website-Animation](../../docs/12-haus-r3-website-animation.md) wird
aus `assets/3d/elektro-hubmann-house-v3-r3-web.blend` exportiert. Diese separate
Ableitung enthält die neuen Kapitelkameras; die hier beschriebene Architekturquelle
bleibt erhalten. Die Web-Ausgabe liegt unter `public/images/version-g/house-r3/`.

## Raumaufteilung

Außenmaß 12,0 × 11,4 m, Außenwände 30 cm, Innenwände 15 cm, Geschosshöhe
2,75 m. Der mittige Flur hat 1,30 m lichte Breite. Die Raumgrenzen entsprechen
den Koordinaten aus dem R3-Entwurf; die Summe der lichten Raumflächen beträgt
rund 117 m². Dies ist ein Anschauungsmodell, kein Ausführungsplan.

Links liegen Wohnküche und Elternschlafzimmer. Rechts folgen vom Eingang aus
Hauswirtschaft/Technik, Bad mit WC, Kinderzimmer und Büro/Gästezimmer. Alle
Räume sind direkt vom Flur erreichbar. Jeder Aufenthaltsraum hat Außenfenster.

Das Modell enthält Doppelbett, Einzelbett, Schlafsofa, Schränke, Arbeitsplätze,
L-Küche, Esstisch, Wohnsofa, Dusche, Doppelwaschtisch, WC, Waschmaschine und
Trockner. Verteilung, Netzwerkschrank und Wechselrichter stehen im Technikraum.

Die Geräteanordnung im Technikraum wurde gegenüber der freien Bildvorlage
präzisiert: Waschmaschine und Trockner stehen an der hinteren Wand und zeigen
in den Raum. Die Verteilung sitzt rechts daneben; Netzwerk und Wechselrichter
liegen an der rechten Außenwand. Gerätefronten und Schranktüren bleiben sichtbar.
Die Duschtasse misst 1,26 × 1,13 m; ihre Vorderkante lässt den geprüften
Schwenkbereich der Badezimmertür frei.

## Öffnen und Bearbeiten

Die Datei öffnet bei Frame 62 in der Kamera `Camera | Open R3`. Alle Bauteile
sind normale Blender-Meshes, Kurven oder Lichter. Collections ordnen Architektur,
Räume, Technik, Dach, Kameras und schematische Verbindungen. Die Holztextur ist
eingepackt; zum Öffnen werden keine Add-ons oder externen Skripte benötigt.

Die `.blend` ist die Quelle für weitere gestalterische Bearbeitung. **Nach
manuellen Änderungen mit `--existing` rendern.** Ein absichtlicher Neuaufbau
erfordert `--rebuild`; dabei gehen manuelle Änderungen dieser Datei verloren.
Ältere V3-Dateien und Website-Bildfolgen werden von diesen Befehlen nicht ersetzt.

```powershell
# Gespeicherte Szene rendern, ohne sie neu aufzubauen:
blender --background assets/3d/elektro-hubmann-house-v3-r3.blend --python-exit-code 1 --python blender/build_house_r3.py -- --existing --views open,closed,lighting --samples 48

# Gespeicherte Szene prüfen:
blender --background assets/3d/elektro-hubmann-house-v3-r3.blend --python-exit-code 1 --python blender/house_r3/validate.py

# Nur bei beabsichtigtem Neuaufbau:
blender --background --python-exit-code 1 --python blender/build_house_r3.py -- --rebuild
```

## Native Zeitleiste

| Frame | Zustand |
| --- | --- |
| 1 | Geschlossenes Haus / Planung |
| 28 | Dach hebt sich; Fassaden beginnen sich zu öffnen |
| 62 | Vollständige Schnittansicht, Strom- und Datenwege |
| 86 | Wohn-, Küchen-, Schlaf- und Badlicht |
| 113 | Lichtszene und abgesenkte Beschattung |
| 129 | Eingangsbereich und Sicherheit |
| 161 | Dach mit PV zurück am Haus |
| 181 | Geschlossenes, beleuchtetes Haus |

`Camera | Scroll` enthält die Kameraübergänge. Die zusätzlichen festen Kameras
dienen Grundriss, Außenansicht, offenem Haus, Technikraum und Eingang.
Das Dach mit allen acht PV-Modulen bewegt sich gemeinsam. Oberhalb von 97 cm
werden verdeckende Wandteile samt Fenster- und Türteilen ausgeblendet. Die
unteren Wände und Türöffnungen erhalten den Grundriss. Die Schnittränder erscheinen
nur während der Öffnung. Gerätewände und ein Fenster für die Beschattung bleiben
vollständig stehen; der Deckenmelder ist am Dach befestigt.

Die Sichtbarkeit wird mit Materialien und nativen Keyframes gesteuert.
Vollständig transparente Haltephasen deaktivieren die betreffenden Meshes
zusätzlich für den Renderer. Es gibt keine Python-Frame-Handler.

Strom und Daten sind getrennte schematische Erklärungslinien. Die Bildfolge
enthält noch keine ausführungsreife Elektroplanung oder Gerätebeschriftungen
für die Website. Die Beschriftungen der separaten Web-Ableitung werden beim
Export durch deren Kapitelkameras projiziert; sie gehören nicht zu dieser
ursprünglichen Architekturdatei.

## Ausgabe

Blender rendert mit Cycles auf transparentem Hintergrund und Schattenfänger.
`preview.py` setzt die exportierten Bilder für die Betrachtung auf Weiß und
erstellt kleine JPEG-Dateien sowie eine Übersicht. Es verändert keine Modell-
oder Bildinhalte. `--width` und `--samples` steuern die Vorschauqualität.

Die Validierung prüft Raumgrenzen, Flurbreite, Türbreiten, Möbelpositionen,
Raumzugänge, Dachgruppierung, Sichtbarkeit und reproduzierbare Timeline-Zustände.
Die gerenderten Ansichten ergänzen die geometrische Prüfung um eine Sichtkontrolle.
