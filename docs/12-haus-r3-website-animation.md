# Haus R3 – erste Animation in der Website

Die nachfolgende [Detailfassung](13-haus-r3-materialien-und-details.md) verbessert
Einrichtung, Materialien und Bildauflösung. Dieses Dokument beschreibt die erste
integrierte Animation und ihren weiterhin gültigen Kapitelablauf.

Die vollständige R3-Raumaufteilung wird an den vorhandenen Scroll-Player angeschlossen.
Der Entwurf erhält Kapitelkameras für Technik, Licht, Beschattung, Eingang und PV.
Dies ist die erste Animationsfassung zur Beurteilung von Ablauf und Lesbarkeit.

## Quellen und Ausgabe

- Architekturquelle: `assets/3d/elektro-hubmann-house-v3-r3.blend`.
- Separate Animationsdatei: `assets/3d/elektro-hubmann-house-v3-r3-web.blend`.
- Vorbereitung und Rendering: `blender/house_r3/web_preview.py`.
- Web-Export: `blender/house_r3/export_web.py`.
- Renderings und Prüfberichte: `docs/version-g-qa/blender-v3-r3/web-preview/`.
- Website-Bilder: `public/images/version-g/house-r3/`.
- Player: `src/components/variants/g/HouseStory.tsx`.

Die Architekturquelle wird nicht überschrieben. Die zweite `.blend` übernimmt
Geometrie und vorhandene Bauteilanimationen; sie ergänzt Desktop-/Mobilkameras,
passt die Zeit der Beschattung an und hellt die Innenraumphasen etwas auf.
Die frühere zweigeschossige V3-Bildfolge bleibt separat erhalten.

## Ablauf

| Abschnitt | Bild und Bewegung |
| --- | --- |
| Planung | Ruhige Außenansicht des vollständigen Hauses. |
| Öffnung | Dach hebt sich, obere Wandteile blenden aus, die Kamera zeigt den vollständigen Grundriss. |
| Installation | Annäherung an den Technikraum; Verteilung und Netzwerk sind sichtbar. |
| Beleuchtung | Rückkehr zur Gesamtansicht mit Lichtwirkung in den eingerichteten Räumen. |
| Smart Home | Näherer Blick auf Steuerung und Schlafzimmerfenster; die Beschattung fährt herunter. |
| Sicherheit | Nahansicht der Videosprechanlage am Eingang. |
| Photovoltaik | Dach kehrt zurück; erhöhter Blick auf die acht Module. |
| Abschluss | Kamera kehrt zur Außenansicht zurück, das Haus schließt sich. |

Die native Zeitleiste enthält 181 Zustände. Für diese Vorschau werden 91
Desktopbilder mit 960 × 860 Pixeln und 61 Mobilbilder mit 640 × 640 Pixeln
gerendert. Die Kamera verändert sich kontinuierlich zwischen den Kapitelpositionen;
es werden echte Zwischenzustände aus Blender verwendet. Der bestehende Player
wählt das zum Scrollfortschritt passende Bild und hält seinen Bildspeicher begrenzt.

Beschriftungen werden durch die tatsächlichen Kapitelkameras projiziert. Sie
erscheinen nur während fester Kamerapositionen. Desktop zeigt höchstens zwei,
mobil höchstens eine Beschriftung. Der Story-Bereich ist auf Desktop 900 svh und
mobil 750 svh hoch. Damit ist der nutzbare Scrollweg gegenüber der ersten Fassung
ungefähr doppelt so lang; Öffnung, Kamerafahrten und Kapitel lassen sich ruhiger
verfolgen. Die Kapitelnavigation springt weiterhin direkt zur jeweiligen Ruheposition.
Statische Kapitel bleiben für reduzierte
Bewegung, niedrige Bildschirmhöhen und Fehler beim Laden verfügbar.

## Wiederholen

```powershell
# Neue Animationsableitung aus der Architekturquelle erstellen:
blender --background assets/3d/elektro-hubmann-house-v3-r3.blend --python-exit-code 1 --python blender/house_r3/web_preview.py -- --prepare --annotations

# Gespeicherte Ableitung prüfen und beide Sequenzen rendern:
blender --background assets/3d/elektro-hubmann-house-v3-r3-web.blend --python-exit-code 1 --python blender/house_r3/validate_web.py
blender --background assets/3d/elektro-hubmann-house-v3-r3-web.blend --python-exit-code 1 --python blender/house_r3/web_preview.py -- --profile both --all --samples 32

# Erst vollständige Sequenzen prüfen und dann die Website umstellen:
python blender/house_r3/export_web.py
```

`--prepare` erzeugt die separate Web-Datei erneut. Wenn diese Datei manuell
bearbeitet wurde, nur aus der gespeicherten Web-Datei rendern und die Annotationen
mit `--annotations` neu projizieren. `--resume` setzt einen unterbrochenen Renderlauf
fort; nur bei unverändertem Modell, unveränderten Kameras und gleichen Einstellungen
verwenden, damit keine unterschiedlichen Revisionen gemischt werden.

## Qualitätsstufe

Die Vorschau verwendet Eevee mit 32 Samples. Animierte Wandtransparenzen werden
ohne Dithering gerendert, um punktförmige Wandreste beim Öffnen zu vermeiden.
Das Dach verwendet tiefengeprüfte Transparenz, damit sich PV-Module und Dachfläche
in den Übergängen korrekt überlagern.
Transparente Bilder werden für die Website auf Weiß gesetzt und als WebP kodiert.
Cycles-Materialwirkung, Schattenfänger und höhere Bilddichte bleiben Gegenstand
der finalen Ausgabe nach der Beurteilung dieser integrierten Animationsfassung.

## Prüfung

`animation-validation.json` prüft die reproduzierbare Auswertung aller 181
Zustände vorwärts/rückwärts, feste Kameras während der Beschriftungen und die
Rückkehr des Dachs. `export-report.json` dokumentiert Bildanzahl, Auflösung und
Datenmenge beider Profile. Die geometrische Prüfung der Architekturquelle liegt
weiterhin in `docs/version-g-qa/blender-v3-r3/validation.json`.

Die Browserprüfung ist in `web-preview/browser-qa.json` dokumentiert. Alle sechs
Kapitel wurden über die Scrollnavigation in beiden Richtungen aufgerufen,
die Kontaktaktion sowie die statische Ansicht bei geringer Bildschirmhöhe geprüft.
Screenshots liegen neben den Prüfberichten. Die Betriebssystem-Einstellung für
reduzierte Bewegung wurde nicht separat umgeschaltet; ihr gemeinsamer statischer
Darstellungspfad ist über die geringe Bildschirmhöhe geprüft.

Die exportierte Bildfolge enthält 86 unterschiedliche Desktopbilder mit insgesamt
2.760.196 Bytes und 58 unterschiedliche Mobilbilder mit 1.074.624 Bytes.
Identische Ruhephasen werden über die Aliasdatei wiederverwendet. Die Startposter
belegen 19.806 beziehungsweise 11.192 Bytes. Kapitelposter kommen separat hinzu.
