# Durchgehende Hausfahrt – gewählte Ansichten

Die native Datei `assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend`
enthält den Modellumbau und die durchgehende Kamerafahrt. Die ursprüngliche
Smart-Home-B-Datei bleibt die unveränderte Quelle. Das aktive Webmanifest wird
erst nach dem vollständigen geprüften Renderexport umgeschaltet.

## Umsetzung

- Planung C ohne Modellbeschriftung; Holzfenster, Balkon und eingerichtetes Haus.
- Erdgeschoss, Obergeschoss und Dach heben sich zu einer Explosionsansicht.
  Schematische Leitungen wachsen durch beide bewohnten Ebenen.
- Smart Home A mit seitlichem Blick auf Bett, Balkon, Holz-Balkontür und
  Raumtaster. 30 Lamellen fahren auseinander und kippen; das Innenlicht bleibt an.
- Sicherheit B ohne Lupe: direkte Fahrt an die detaillierte Türkamera.
- Photovoltaik mit einer verbindenden Gesamtperspektive auf Dach und Auto,
  anschließend Wallbox, angeschlossener Stecker und animierter Energiepfad.
- Kleine Hausübersicht rechts unten und eine einzelne Szenenzeile, die dem
  tatsächlich gezeichneten Bild folgt. Keine Einblendung bei der Planung.

## Prüfungen und Grenzen

`native-build.json` dokumentiert Quellen und Prüfsummen. `native-validation.json`
prüft 721 gespeicherte Zustände, darunter Bewegungen, Ebenenabstände, konstantes
Innenlicht, Jalousiehub und Ladeanzeige. Die technischen Prüfungen ersetzen keine
Sichtprüfung der Renderbilder.

Die ersten Proberender deckten eine angeschnittene Dachspitze, verdecktes Bett,
ausgeblendete Türrahmen und eine fehlende Gesamtperspektive bei Photovoltaik auf.
Kamera und Modell wurden daraufhin korrigiert. Die Überarbeitung wurde anhand
neuer nativer Bilder geprüft, ohne die Webkonfiguration vorzeitig zu wechseln.

Die geprüften Ansichten liegen unter `proofs/`: Planung, Installation,
Smart Home, Sicherheit, Photovoltaik und deren verbindende Gesamtperspektive.
Die ersten beiden Bilder stammen aus dem 96-Sample-Referenzlauf, die drei
Detailansichten aus dem gewählten 48-Sample-Profil, jeweils bei 1200 px.
Die PV-Gesamtperspektive dokumentiert zusätzlich den 640-px-Kompositionscheck.
`sources.json` hält die genaue Herkunft fest; diese Einzelbilder aktivieren
keine unvollständige Webanimation.

`quality-profile-review.json` dokumentiert den Vergleich der Renderprofile.
Die 48-Sample-Probe bewahrt die sichtbare Schärfe und verkürzt die Renderzeit.
Die abschließende technische Prüfung besteht aus 29 nativen Prüfungen,
20 Bewegungstests und 9 Tests der Render-/Exportpipeline.

Die bestehende Website überspringt jetzt alle identischen Standbilder ihrer
bisherigen Folge. 38 Frontendtests bestehen, einschließlich isolierter Tests
der künftigen kontinuierlichen Konfiguration. Die Desktopfahrt vorwärts wurde
im echten Browser geprüft; weitere Browserprüfungen scheiterten an wiederholten
Debuggerabbrüchen. Eine vollständige Browserfreigabe der neuen Bildrevision steht
bis zu deren vollständigem Export aus.

`frontend/runner-status.json` und `frontend/pipeline-status.json` zeigen den
lokalen Produktionsfortschritt. Proberender liegen getrennt unter
`frontend/preview/`; sie werden niemals als vollständige Websitefolge aktiviert.

Der ausdrücklich gestartete `finalize_continuous.py` wartet einmalig auf den
laufenden Export. Danach prüft er die Exportdateien, Vitest, Astro Check und
Produktionsbuild, committet ausschließlich die neuen Webbilder und deren
Konfiguration und pusht normal nach `main`. Er ist an Codecommit, Modell-SHA,
Runner und den verifizierten GitHub-Remote gebunden. Ein veränderter Branch,
neue fremde Änderungen, gestagte Dateien oder ein vorgerückter Remote stoppen
den Abschluss. Der bestehende fremde Arbeitsstand wird erhalten. Sein Status
steht in `frontend/finalizer-status.json`; es gibt keine zeitgesteuerte Wiederholung.
