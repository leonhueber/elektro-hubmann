# Haus V4 – Website und native Scroll-Animation

Die Startseite verwendet das eingerichtete zweigeschossige V4-Haus mit
Satteldach. Dach, Obergeschoss, Wände und Beschattung bewegen sich zusammen
mit einer durchgehenden perspektivischen Blender-Kamera. Alle 19 Innenleuchten
bleiben über die gesamte Animation warm und auf ihrer normalen Lichtleistung.
Die aktive Bewegungsrevision ist `v4-scroll-02`.

## Quellen und Reproduktion

- Architektur: `assets/3d/elektro-hubmann-house-v4.blend`, Revision `v4-build-02`.
- Separate native Animation: `assets/3d/elektro-hubmann-house-v4-web.blend`.
- Bewegung und Export: `blender/house_v4/{motion,web,export_web}.py`.
- Aktiver Player: `src/components/variants/g/HouseStory.tsx`.
- Konfiguration: `src/config/house-v4-{manifest,frames}.json`.

Die ausgewählte Vorlage `v4-reference-01` bleibt unverändert. Die Animation
baut auf dem fertigen nativen Modell auf und überschreibt dessen Quelldatei
nicht. Kamerafahrten werden als native Transformationen gespeichert;
die Website lädt vorgerenderte Bilder.

```powershell
blender -b assets/3d/elektro-hubmann-house-v4.blend --python-exit-code 1 --python blender/house_v4/web.py -- --prepare
blender -b assets/3d/elektro-hubmann-house-v4-web.blend --python-exit-code 1 --python blender/house_v4/web.py -- --all --resume
python blender/house_v4/export_web.py
blender -b assets/3d/elektro-hubmann-house-v4-web.blend --python-exit-code 1 --python blender/house_v4/validate_web.py
```

`--resume` nur verwenden, wenn Modell, Animation und Rendereinstellungen seit
den vorhandenen Bildern unverändert sind. Jede Revision besitzt einen eigenen Renderordner. Der Export prüft vor dem
Schreiben der Website-Konfiguration alle benötigten Renderdateien.
Für Revision 02 wurden 42 bereits vorhandene Bilder mit exakt gleichem
Kamera-, Geometrie-, Sichtbarkeits- und Lichtzustand übernommen;
`scroll-02-reused-frames.json` dokumentiert die Quellen und Prüfsummen.

## Sechs Kapitel, acht Ansichten

| Kapitel | Bild und Bewegung | Ruheposition |
| --- | --- | --- |
| Planung | Geschlossenes Haus | 4 % |
| Installation | Dach anheben, OG anheben, Explosionsansicht, dann offenes EG | 35 % |
| Beleuchtung | Gleiche EG-Kamera, Leitungsdarstellung aus; warmes Licht bleibt an | 47 % |
| Smart Home | Außen zurückziehen, zum OG wechseln, Beschattung absenken | 63 % |
| Sicherheit | Haus schließen, zum Eingang und zur Türstation fahren | 79 % |
| Photovoltaik | Dachansicht, anschließend warme Außenansicht wie bei Planung | 91 % |

Die 18 Bewegungs- und Ruheabschnitte der Vorlage bleiben erhalten. Die
Kamera folgt Bezier-Bahnen mit getrenntem Blickziel und ohne Rollen.
Quintische Beschleunigung wirkt auf die Bogenlänge der gesamten Fahrt;
interne Kontrollpunkte sind keine zusätzlichen Haltepunkte. Installation
und Beleuchtung sowie Planung und Abschluss besitzen jeweils dieselbe Kamera.

## Web-Ausgabe

Die native Zeitleiste umfasst 1441 Positionen. Jeder zweite Frame wird
abgetastet: 721 Scroll-Positionen mit 373 unterschiedlichen Szenenbildern.
Die Bewegungen sind damit doppelt so dicht abgetastet wie in Revision 01.
Identische Ruhephasen teilen sich eine Datei. Bewegte Zwischenbilder stammen
aus Blender; der Browser überblendet keine isolierten Ansichten.

- Cycles mit 12 Samples, Denoising und festem Zufallsstartwert.
- Während die Fassade transparent wird, berechnet Cycles den weißen
  Studiohintergrund direkt. So kann der Denoiser auch die Übergangskanten
  glätten; die Beleuchtung und die übrigen Ansichten bleiben unverändert.
- Desktop: 1000 × 1000 px; Mobil: 720 × 720 px, aus demselben Bildausschnitt.
- WebP, Qualität 88. Maße und Abtastung wurden gegenüber dem ersten
  1600/900-px-Entwurf an die tatsächliche Darstellungsgröße angepasst.
- Maximal 12 Desktop- bzw. 18 Mobilbilder im decodierten Cache
  (48 MB bzw. rund 37,3 MB Bilddaten), sechs gleichzeitige Ladevorgänge.
- Das Vorladen zählt unterschiedliche Szenenbilder und reicht über identische
  Ruhepositionen hinweg. Bevorstehende Bilder bleiben im Cache; zuerst werden
  Bilder außerhalb des benötigten Bereichs freigegeben.
- Revisionskennungen an Bild-URLs erlauben die Wiederverwendung bereits
  geladener Dateien, ohne nach einem Update alte Beleuchtungsbilder zu zeigen.
- Scroll-Strecke: 1200 svh am Desktop, 1000 svh mobil; längere Lese- und Fahrstrecken für die acht Ansichten.

Der Player nähert seine Position zeitbasiert mit einer Zeitkonstante von 150 ms
der Scroll-Position an. Solange das Haus sichtbar ist, überspringt er dabei
keine unterschiedlichen Bewegungsbilder. Auf ein noch fehlendes Bild wartet er, statt die Uhr weiterlaufen
zu lassen und anschließend sichtbar vorzuspringen. Identische Ruhepositionen
können direkt durchlaufen werden. Damit hängt die Fahrtdauer bei großen Sprüngen
auch von der verfügbaren Lade- und Decodiergeschwindigkeit ab.
Verlässt ein Sprung zum Kontaktbereich die gesamte Haussektion, wird die
Bildfolge außerhalb des sichtbaren Bereichs direkt an die Scroll-Position
angepasst. Sie läuft dort nicht unnötig vollständig weiter.

Text und Kapitelanzeige folgen dem tatsächlich gezeichneten Bild. Die Texte
blenden beim Kapitelwechsel weich ein. Veraltete Ladevorgänge werden abgebrochen;
späte Decodes werden freigegeben. Ein schneller Richtungswechsel kann auch auf
einem zuvor abgebrochenen Frame wieder anhalten. Fehlende Einzelbilder wechseln
zu den vollständigen statischen Leistungsabschnitten. Bei fehlendem JavaScript,
Initialisierungsfehlern, reduzierter Bewegung oder sehr niedrigen Viewports
bleiben alle sechs Leistungen als statische Abschnitte erreichbar.
Ein Wechsel zwischen Desktop, Hochformat und der statischen Querformatansicht
erhält das aktuelle Kapitel.

Die alten R3-Markierungen wurden entfernt: Ihre Projektionspunkte gehören
zum früheren Modell. Leistungsbezeichnungen und Komponenten bleiben als
HTML-Text zugänglich. Alt-Texte beschreiben jetzt beide Geschosse und zehn
PV-Module auf dem Satteldach.

## Prüfartefakte

`docs/version-g-qa/blender-v4/web/review.html` zeigt die endgültige Bildfolge vorwärts, rückwärts und mit frei wählbarer Position.
`motion-samples.json` enthält die gebackenen Positionen, Blickziele und
Szenenzustände. `export-report.json` dokumentiert Bildanzahl, Dateigrößen und
SHA-256-Prüfsummen der endgültigen Website-Bilder sowie beider Blender-Dateien.
`sequence-overview.jpg` zeigt 24 Positionen aus dem finalen Export;
`website-qa.json` dokumentiert die Prüfungen des Players und des Produktionsbuilds.

Die aktuelle Ausgabe umfasst 758 Web-Dateien. Die vollständige Desktop-Folge
belegt 16,7 MB, die Mobilfolge 10,8 MB; beim Einstieg werden nur das Startbild
und der begrenzte Vorladebereich geladen. Größen und Prüfsummen stehen im
Exportbericht. `native-lighting-validation.json` prüft die tatsächlichen
Licht-Keyframes in der gespeicherten Blender-Datei. Die Browser-Prüfung erfasst
auch die gezeichneten Zwischenbilder während einer Fahrt, zusätzlich zu den
Kapitelansichten und den Wechseln zwischen Desktop, Mobil- und Querformat.

Die ursprünglichen acht Modellprüfbilder und ihre Provenienz bleiben in
`docs/version-g-qa/blender-v4/` erhalten. Das Haus ist ein fiktives
Anschauungsmodell und kein ausgeführtes Referenzprojekt von Elektro Hubmann.
