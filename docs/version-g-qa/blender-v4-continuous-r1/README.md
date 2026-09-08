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

Auf Wunsch des Nutzers sind der Produktionsrunner und der automatische
Commit-/Push-Abschluss gestoppt. Der alte unvollständige Lauf ist unter
`benchmarks/vehicle-r0-superseded/` lokal archiviert. Er darf nicht mit dem neuen
Modell fortgesetzt werden. Es läuft kein vollständiger Produktionsrender.

`proofs/` enthält zehn neue native Cycles-Kontrollbilder dieses Modellstands,
640 × 640 Pixel, 16 Samples mit Denoising. `states-overview.jpg` zeigt alle fünf
Themen einschließlich der PV-Gesamt- und Detailperspektive.
`motion-overview.jpg` vergleicht die Installation und drei Smart-Home-Zeitpunkte.
Die Einblendungen auf den Übersichtsblättern sind nur Bildunterschriften;
sie sind keine Beschriftungen im 3D-Modell.

`sources.json` dokumentiert Bild-, Modell- und Renderherkunft. Diese Bilder dienen
der Auswahl und Kompositionsprüfung, nicht als endgültiger Schärfenachweis.
Der spätere Webexport bleibt bei 1200 px / 48 Samples. Die Vergleichsbilder in
`quality-profile-review.json` gehören zur vorherigen Modellrevision und sind
lediglich die historische Grundlage für dieses Qualitätsprofil.

`native-build.json` und `native-validation.json` dokumentieren das aktuelle
Modell und 721 geprüfte native Zustände. Die ursprüngliche Blender-Datei bleibt
bytegleich. Bewegungs- und Frontendtests prüfen kontinuierliche Fahrt, sichtbare
Zielpunkte und passende Szenenbeschriftungen. Die Website wird erst nach einem
vollständigen neuen Export umgeschaltet. Vor dessen Start steht die Bildsichtung
mit dem Nutzer aus.
