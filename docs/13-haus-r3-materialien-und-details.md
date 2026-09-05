# Haus R3 – Materialien und Einrichtung

Die Detailfassung entwickelt das eingerichtete R3-Haus anhand der R3-Mockups
weiter. Raumaufteilung, Fenster, Gerätepositionen und Scrollkameras bleiben erhalten.
Alle Ansichten stammen weiterhin aus derselben editierbaren Blender-Geometrie.

## Aktuelle Dateien

- Detailliertes Modell: `assets/3d/elektro-hubmann-house-v3-r3-detail.blend`.
- Ableitung mit Website-Kameras: `assets/3d/elektro-hubmann-house-v3-r3-detail-web.blend`.
- Reproduzierbare Verfeinerung: `blender/house_r3/refine.py`.
- Geometrieprüfung: `docs/version-g-qa/blender-v3-r3/detail/validation.json`.
- Website-Ausgabe und Prüfberichte: `docs/version-g-qa/blender-v3-r3/web-detail/`.
- Bildfolge: `public/images/version-g/house-r3-detail/`.

Die ursprüngliche Architekturdatei und die erste Web-Bildfolge bleiben erhalten.
`refine.py` lädt ausdrücklich diese Architekturquelle und speichert eine separate
Detailfassung. Nach manuellen Änderungen direkt aus der Detaildatei weiterarbeiten;
ein erneuter Verfeinerungslauf ersetzt deren manuelle Änderungen.

## Gestalterische Änderungen

| Bereich | Änderung |
| --- | --- |
| Sofa und Stühle | Geformte Polster, umlaufende Nähte, weichere Armlehnen und gebogene Stuhlrücken. |
| Schlafzimmer | Separate Bettdecken mit Falten, Saum, umgeschlagenem Leinen und strukturierter Tagesdecke. |
| Holz | Eichenmaserung in passenden Maßstäben, dezente Unterschiede zwischen Dielen, sichtbare Holzstruktur an Fronten und Tischplatten. |
| Textilien | Gewebte Oberflächen, abgestimmte Leinenfarben, eingefasste Teppichränder. |
| Wände | Heller warmer Putz, feinere Oberflächenstruktur, Sockelleisten mit freien Türöffnungen und bündige animierte Schnittkanten. |
| Küche und Bad | Vertiefte Spüle mit Arbeitsplattenausschnitt, hohle Waschbecken, Abläufe, Spiegel, Fliesenfugen und Beschläge. |
| Stauraum und Geräte | Griffmulden, Frontteilungen, Gerätegriffe, dunkle Türgläser und wenige gefaltete Handtücher. |
| Kleine Ausstattung | Geformte Pflanzenblätter, Keramik, Bücher und ein zurückhaltender grüner Textilakzent. |

Die Detailfassung verwendet vorhandene eingepackte Holztexturen und prozedurale
Materialien. Es sind keine externen Add-ons oder zusätzlichen Asset-Downloads nötig.
Die Szene bleibt ein anschauliches Hausmodell, kein Ausführungsplan.

## Website

Die Bildfolge wird mit Eevee, 48 Samples, genauerer indirekter Beleuchtung und
verfeinerten Schatten gerendert. Desktop erhält 1200 × 1075 Pixel, mobil 720 × 720.
WebP-Qualität 88 erhält mehr Materialdetails. Die native Architekturdatei bleibt
auch für Cycles-Renderings eingerichtet.
Die Web-Ausgabe verwendet dünne getönte Glasflächen, damit die animierten
Fensterhälften durchgehend aussehen. Die native Szene behält ihre physikalische
Glastransmission für Cycles. Türhälften teilen sich die Holzkoordinaten ihres
Scharniers; die künstliche Schnittkante erhält keine sichtbare Fase.

Die Kapitel und ihre Ruhepositionen ändern sich nicht. Der langsamere Scrollweg
bleibt bei 900 svh auf Desktop und 750 svh auf Mobilgeräten. Beschriftungen skalieren
unabhängig von der höheren Bildauflösung; ihre sichtbare Größe bleibt gleich.
Der Bildspeicher enthält höchstens zwölf Desktopbilder (rund 59 MiB Rohpixel) oder
14 Mobilbilder (rund 28 MiB), zuzüglich Canvas und laufender Bilddekodierungen.

## Wiederholen

```powershell
# Detailfassung bewusst aus der unveränderten Architekturquelle ableiten:
blender --background assets/3d/elektro-hubmann-house-v3-r3.blend --python-exit-code 1 --python blender/house_r3/refine.py

# Geometrie der gespeicherten Detailfassung prüfen:
blender --background assets/3d/elektro-hubmann-house-v3-r3-detail.blend --python-exit-code 1 --python blender/house_r3/validate.py -- --detail

# Separate Web-Kameras vorbereiten und Beschriftungen projizieren:
blender --background assets/3d/elektro-hubmann-house-v3-r3-detail.blend --python-exit-code 1 --python blender/house_r3/web_preview.py -- --detail --prepare --annotations

# Beide vollständigen Profile rendern:
blender --background assets/3d/elektro-hubmann-house-v3-r3-detail-web.blend --python-exit-code 1 --python blender/house_r3/web_preview.py -- --detail --profile both --all --samples 48

# Animation prüfen und erst nach vollständigem Export die Website umstellen:
blender --background assets/3d/elektro-hubmann-house-v3-r3-detail-web.blend --python-exit-code 1 --python blender/house_r3/validate_web.py -- --detail
python blender/house_r3/export_web.py --detail
```

`--resume` nur bei derselben unveränderten Szenendatei, Auflösung und Renderqualität
verwenden. Nach Material- oder Modelländerungen die gesamte Bildfolge neu rendern.

## Prüfung

Die Geometrieprüfung kontrolliert Raumgrenzen, freie Türschwenkbereiche und Flur,
Möbelpositionen, unveränderte Türblätter und die beiden modellierten Bettdecken.
Die Animationsprüfung wertet alle 181 Zustände in beiden Richtungen aus und prüft
die festen Kamerapositionen der Beschriftungen sowie die Dachbewegung.
Der Export prüft alle Bilder beider Profile vor dem Wechsel der aktiven Konfiguration.

Die vollständige Ausgabe enthält 91 Desktop- und 61 Mobilzustände. Nach dem
Zusammenfassen identischer Bilder bleiben 87 Desktopbilder mit 5.503.518 Bytes
und 59 Mobilbilder mit 1.805.264 Bytes. Die Startposter belegen 36.996 bzw.
18.280 Bytes; Kapitelposter kommen separat hinzu. Der Player lädt nur Bilder
in der Nähe der aktuellen Scrollposition nach.
