# Durchgehende Hausfahrt – Modellvorschau ohne Auto

Die native Datei `assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend`
enthält die gewählten Ansichten und die durchgehende Kamerafahrt. Die ursprüngliche
Smart-Home-B-Datei bleibt die unveränderte Quelle.

## Aktueller Stand

- Planung C: komplettes Haus, Holzfenster, Balkon, Einrichtung, keine Modelltexte.
- Installation: EG, OG und Dach heben sich; schematische Leitungswege wachsen.
- Smart Home A: direkter Schlafzimmerblick, Raumtaster, 30 bewegte Lamellen.
- Sicherheit B: direkte Nahansicht der Türkamera ohne Lupe.
- Photovoltaik: Gesamtperspektive auf Dach und Haus, dann Fahrt an die Wallbox.
  Das Auto ist vollständig entfernt. Das Kabel hängt mit Stecker im Wandhalter;
  der schematische Energiepfad endet an der Statusanzeige der Wallbox.
- Kleine Hausübersicht rechts unten und eine Szenenzeile für das gerade gezeigte
  Motiv sind für den vollständigen neuen Webexport vorbereitet.

## Vorschauen vor dem langen Renderlauf

Der Nutzer hat die Bildvorschau freigegeben und anschließend eine kürzere
Renderzeit verlangt. Der abgebrochene 721-Bilder-Lauf liegt lokal unter
`benchmarks/full-721-superseded/`. Die Webanimation verwendet jetzt 181 native
Positionen (Schrittweite 8) aus derselben unveränderten Blender-Animation.
Die dichte native Zeitleiste und die 640-px-Prüfvorschauen bleiben erhalten.

Blender rendert nur einmal: 960 px, 24 Samples, Denoising. Desktop übernimmt
diese Bilder; mobile WebP-Dateien entstehen durch anschließendes Verkleinern
auf 720 px. Es gibt keinen zweiten Blender-Renderlauf für Mobilgeräte.
Die ersten drei Produktionsbilder dienen gleichzeitig als Qualitätsprobe und
werden beim Fortsetzen übernommen. `web-profile-review.json` hält die Messung fest.

`proofs/` enthält zehn neue native Cycles-Kontrollbilder dieses Modellstands,
640 × 640 Pixel, 16 Samples mit Denoising. `states-overview.jpg` zeigt alle fünf
Themen einschließlich der PV-Gesamt- und Detailperspektive.
`motion-overview.jpg` vergleicht die Installation und drei Smart-Home-Zeitpunkte.
Die Einblendungen auf den Übersichtsblättern sind nur Bildunterschriften;
sie sind keine Beschriftungen im 3D-Modell.

`sources.json` dokumentiert Bild-, Modell- und Renderherkunft. Diese Bilder dienen
der Auswahl und Kompositionsprüfung, nicht als endgültiger Schärfenachweis.
Das gewählte Webprofil nutzt 960 px / 24 Samples. Die Vergleichsbilder in
`quality-profile-review.json` gehören zur vorherigen Modellrevision und sind
lediglich die historische Grundlage für dieses Qualitätsprofil.

`native-build.json` und `native-validation.json` dokumentieren das aktuelle
Modell und 721 geprüfte native Zustände. Die ursprüngliche Blender-Datei bleibt
bytegleich. Bewegungs- und Frontendtests prüfen kontinuierliche Fahrt, sichtbare
Zielpunkte und passende Szenenbeschriftungen. Die Website wird erst nach einem
vollständigen neuen Export umgeschaltet. Nach vollständigem Export folgen Frontendtests, Build und gemeinsamer Push.
Vorbereitende lokale Codecommits werden erst mit dem fertigen Export gepusht.
