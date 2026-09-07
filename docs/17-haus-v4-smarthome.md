# Haus V4 – Smart Home A

Leon hat die Nahansicht von Elternschlafzimmer und Balkon aus Mockup A gewählt.
Die Umsetzung baut auf dem B-Außenmodell mit Holzfenstern auf. Die Architektur
liegt in `assets/3d/elektro-hubmann-house-v4-smarthome-r1.blend`, die native
Animation in `assets/3d/elektro-hubmann-house-v4-smarthome-r1-web.blend`.
Revision: `v4-scroll-02-exterior-01-smart-01`.

## Verhalten

- Die vorhandene Fahrt öffnet das Haus und wechselt vom EG ins OG.
- Zwischen 57 und 60,5 % rückt dieselbe perspektivische Kamera näher an
  Elternschlafzimmer, Holz-Balkontür und Geländer heran. Der vorhandene
  Eichenschrank, das Bett und die anschließende Erschließung bleiben erhalten.
- Ein nativer 17 × 17 cm großer Raumregler sitzt auf der vorhandenen Rückwand
  neben dem Schrank, 1,22 m über dem OG-Boden. Die Anzeige „21°“ ist eine
  illustrative Modellanzeige. Es werden keine Live-Daten dargestellt.
- Die 15 vorhandenen Metalllamellen fahren weiter herunter, drehen sich
  zunächst bis 55° und öffnen sich für die Ruheansicht auf −35°, sodass
  auch aus der erhöhten Kameraposition Durchblick zwischen den Lamellen bleibt.
  Führungsschienen und oberer Kasten ergänzen die Beschattung.
- Zwischen 64,5 und 67 % fährt die Kamera zurück in die vorhandene OG-Ansicht.
  Anschließend schließen sich die Geschosse und die Fahrt zur Türstation
  setzt sich fort. Alle Bewegungen sind native Blender-Keyframes und laufen
  beim Zurückscrollen rückwärts. Die Leuchten behalten ihre Lichtleistung.

Im Architekturmodell sind die neuen Bauteile dauerhaft vorhanden. Die
Animationsdatei blendet die ergänzten Details während der Nahaufnahme ein;
außerhalb dieses Abschnitts bleibt die Außenrevision bildgleich. Die übrigen
Kamerafahrten und Geschossbewegungen werden nicht neu aufgebaut.

## Prüfung und Render-Ausgabe

`docs/version-g-qa/blender-v4-smarthome-r1/web-validation.json` prüft die
tatsächlich gespeicherten Kamera-, Lamellen- und Lichtzustände an allen 649
abgetasteten Positionen außerhalb des neuen Abschnitts. Dort sind keine
Änderungen erlaubt; neue Objekte müssen vollständig ausgeblendet sein.
Der Bericht bindet Original und Ergebnis mit SHA-256 an die native Quelle.
`frame-schedule.json` enthält die neue Folge: 408 unterschiedliche native
Bilder, davon 57 neue Smart-Home-Bilder und 351 unveränderte B-Bilder.

Die neuen Bilder werden in Cycles mit 1.200 × 1.200 px und bis zu 64 Samples
gerendert. Vier CPU-Threads ergänzen den bereits laufenden Außenrender;
nach dessen Abschluss werden zwölf Threads genutzt. Sobald
beide Folgen fertig sind, werden die unveränderten Bilder anhand der nativen
Prüfung und ihrer PNG-Prüfsummen übernommen. Erst nach vollständiger Prüfung
schaltet der Export die Website auf `images/version-g/house-v4-smarthome-r1/`
um. Desktop erhält 1.200 px, Mobil 720 px; die fünf Kapitel bleiben erhalten.
Tests, Astro-Prüfung und Produktionsbuild gehören zum Lieferlauf.

Der Lauf ist fortsetzbar. Der Status liegt in
`docs/version-g-qa/blender-v4-smarthome-r1/frontend/pipeline-status.json`.
`phase: complete` bestätigt Export, Tests und Build. Standardmäßig führt der
Prozess keine Git-Operationen aus. Der explizite Parameter `--publish-from SHA`
erlaubt anschließend den von Leon beauftragten Commit und Push der fertigen
Bilder, des Exportberichts und der beiden Website-Konfigurationen. Der Lauf
prüft zuvor den unveränderten Ausgangscommit auf `main`, ein leeres Staging,
das festgelegte Repository und sämtliche Bildprüfsummen. Andere Änderungen
werden nicht aufgenommen. `publishedCommit` bestätigt den auf GitHub geprüften
Commit; bei einem veränderten Checkout bleiben die Bilder zur Prüfung lokal.

## Reproduktion

```powershell
blender -b assets/3d/elektro-hubmann-house-v4-exterior-r1.blend --python-exit-code 1 --python blender/house_v4/smarthome.py -- --apply
blender -b assets/3d/elektro-hubmann-house-v4-exterior-r1-web.blend --python-exit-code 1 --python blender/house_v4/smarthome.py -- --apply --frames 909 --size 1200 --samples 64
python blender/house_v4/deliver_smarthome.py --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python -m unittest discover -s blender/house_v4 -p "test_*.py" -v
```

Die ursprünglichen B-Dateien bleiben Quellen der Außenrevision. Ein Render
darf nur wiederaufgenommen werden, solange Quelldateien, Qualität und
Frame-Plan zu den gespeicherten Prüfsummen passen.
