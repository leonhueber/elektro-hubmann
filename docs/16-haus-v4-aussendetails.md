# Haus V4 – Balkon und Außendetails

Stand: 7. September 2026. Revision `v4-exterior-01`.

Leon hat **Variante B mit Fensterrahmen in Holzoptik** gewählt. Grundlage sind
das Architekturmodell `v4-build-02` und die zuletzt gespeicherte Animation
`v4-scroll-02`. Die Außenüberarbeitung liegt in eigenen nativen Blender-Dateien:

- `assets/3d/elektro-hubmann-house-v4-exterior-r1.blend`
- `assets/3d/elektro-hubmann-house-v4-exterior-r1-web.blend`

## Außenbereich

- 4,5 × 1,9 m großer Balkon über dem Wohnbereich, mit Betonplatte,
  einzelnen Bodenplatten, Abtropfkante und Entwässerungsrinne.
- Schlankes anthrazitfarbenes Stabgeländer mit Handlauf, unterem Rahmen,
  Pfosten, Fußplatten und Befestigungen; zwei Stützen bis zur Terrasse.
- Das linke OG-Fenster wird zur bodentiefen verglasten Balkontür.
  Die bisherige Fensterbrüstung ist aus der Wandgeometrie entfernt.
  Zweiflügeliger Rahmen, Türgriffe und längere Vorhänge ergänzen den Zugang.
- Fensterprofile auf allen vier Fassaden in Eichenholzoptik. Metallfensterbänke
  bleiben anthrazit. Zusätzliche Leibungen, Abdeckungen und Endkappen geben Tiefe.
- Größere Holzterrasse mit einzelnen Dielen und Schrauben, zwei gepolsterten
  Sesseln, Dreibeintisch, Tasse und bepflanztem Betontrog.
- Separates Eingangsvordach mit Holzuntersicht, Tragarmen und zwei warmen
  Einbauleuchten; Trittplatten, Fußmatte und schmale Holzflächen am Eingang.
- Geschossfuge, umlaufende Sockeldetails, Kiesstreifen mit einzelnen Steinen,
  Regenrohrhalter, Rinnenhalter, Dachuntersichten und Giebellüftung.

Hausabmessungen, Satteldach, zehn PV-Module, Raumprogramm, Möbel und U-Treppe
bleiben Grundlage des Modells. Die Fenstertextur stammt aus dem vorhandenen,
eingepackten Eichenmaterial. Alle ergänzten Bauteile sind native Blender-Geometrie.

## Animation und Bildausschnitt

Die Überarbeitung der Web-Datei beginnt direkt mit der zuletzt gespeicherten
Animationsdatei. Kamerapfade, Geschossbewegungen und bestehende Licht-Keyframes
werden übernommen. Die Brennweiten werden gleichmäßig auf 90 % skaliert, damit
Terrasse und Balkon im Bild bleiben; die Fahrt bleibt kontinuierlich.

Der Balkon einschließlich Geländer und Möbeln folgt dem OG. Die Stützen gehören
zum EG und verschwinden mit dessen Schnittwänden. Terrasse und Sockel folgen
der vorhandenen EG-Sichtbarkeit. Neue Fensterprofile und Fassadenteile verwenden
die vorhandenen Sichtbarkeitsgruppen. Die niedrige Balkonbrüstung bleibt in den
offenen Geschossansichten sichtbar.

## Frontend-Render

Der vollständige Neurender der freigegebenen Variante B wurde am 7. September 2026
als lokaler Hintergrundprozess gestartet. Aktueller Zustand und abgeschlossene
Schritte stehen in `version-g-qa/blender-v4-exterior-r1/frontend/pipeline-status.json`;
der Fortschritt je Bild steht in `render-progress.json` im selben Verzeichnis.
Die [Render-Vorschau](version-g-qa/blender-v4-exterior-r1/frontend/index.html) zeigt
sieben geprüfte Kontrollpositionen. Mit dem lokalen HTTP-Server auf Port 4323 zeigt
sie auch den laufenden Fortschritt.

- Cycles, 1.200 × 1.200 px, bis 64 Samples, adaptiver Schwellwert 0,04,
  mindestens 8 Samples, Denoising, fester Zufallsseed, 12 CPU-Threads.
- Weißer Kamerahintergrund wird in Cycles mitgerendert. Die animierte
  `film_transparent`-Kurve wird nur für den Render im Arbeitsspeicher stummgeschaltet,
  damit Geländer und andere feine Kanten sauber gegen Weiß aufgelöst werden.
- Alle 373 unterschiedlichen Kamerabilder werden nativ gerendert. Die 721
  Abspielpositionen und bestehenden Standbild-Aliase bleiben erhalten.
- WebP in 1.200 px für Desktop und 720 px für Mobil, Qualität 90, einschließlich
  der sechs Kapitelposter. Der Cache bleibt auf 12 beziehungsweise 18 Bilder begrenzt.
- SHA-256 und vollständige Bildprüfung vor der Aktivierung. Unterbrechungen können
  fortgesetzt werden; nur nachweislich passende Bilder werden wiederverwendet.

`deliver_exterior.py` führt Render, Export, sämtliche Frontend-Tests, Astro-Prüfung
und Produktionsbuild nacheinander aus. Erst wenn sämtliche WebP-Dateien vorliegen,
wechselt das Manifest auf `v4-scroll-02-exterior-01` und den separaten Asset-Pfad
`images/version-g/house-v4-exterior-r1/`. Bis dahin bleibt die bisherige Bildfolge
aktiv. `phase: complete` im Status bestätigt den erfolgreichen Abschluss inklusive
Build; bei Fehlern steht dort die betroffene Stufe und das zugehörige Log.
Es erfolgt kein Deployment.

Start beziehungsweise Wiederaufnahme (Python benötigt Pillow, Node muss im PATH sein):

```powershell
python blender/house_v4/deliver_exterior.py --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
```

Der Prozess verhindert für seine Laufzeit automatischen Systemruhezustand;
der Bildschirm darf weiterhin ausgeschaltet werden. Ein Prozess-Lock verhindert
zwei gleichzeitige Renderaufträge für dieselbe Ausgabe.

## Prüfung und Reproduktion

[Vorher, Mockup und Blender vergleichen](version-g-qa/blender-v4-exterior-r1/review.html).
Die Prüfbilder und die native Prüfung liegen in
`docs/version-g-qa/blender-v4-exterior-r1/`.

```powershell
blender -b assets/3d/elektro-hubmann-house-v4.blend --python-exit-code 1 --python blender/house_v4/exterior.py -- --apply --variant B --views plan,detail,rear --size 1200 --samples 40
blender -b assets/3d/elektro-hubmann-house-v4-web.blend --python-exit-code 1 --python blender/house_v4/exterior.py -- --apply --variant B --frames 1,289,505,909,1139,1311 --size 800 --samples 24
```

`--apply` erwartet die ursprüngliche V4-Datei und überschreibt ausschließlich
die entsprechende Außenrevision. Ohne `--apply` wird eine geladene Außenrevision
geprüft und optional gerendert. Die ursprünglichen V4-Dateien und das gesicherte
Referenzpaket `v4-reference-01` bleiben erhalten.

Die Dateien enthalten das ausgewählte Mockup und einen Text `V4_EXTERIOR_README`.
Die acht bekannten Modellansichten sind weiterhin über **V4 Haus** verfügbar.
Das Haus bleibt ein fiktives Anschauungsmodell.
