# R3 Detail – native Modellansichten und Website-Export

Diese Bilder stammen aus der detaillierten Blender-Szene. Die ursprünglichen
ImageGen-Mockups bleiben separate Gestaltungsreferenzen.

| Ansicht | Blender-Rendering |
| --- | --- |
| Geschlossenes Haus | [Planung](proofs/frame-0001.jpg) |
| Dachöffnung | [Übergang](proofs/frame-0031.jpg) |
| Vollständige Einrichtung | [Offene Ansicht](proofs/frame-0049.jpg) |
| Technik und Bad | [Installation](proofs/frame-0061.jpg) |
| Lichtwirkung | [Beleuchtung](proofs/frame-0085.jpg) |
| Schlafzimmer und Beschattung | [Smart Home](proofs/frame-0109.jpg) |
| Eingang und Anschlüsse | [Sicherheit](proofs/frame-0133.jpg) |
| Dach und Module | [Photovoltaik](proofs/frame-0163.jpg) |
| Rückkehr zum geschlossenen Haus | [Abschluss](proofs/frame-0181.jpg) |

Die JPEGs sind die nativen Renderings auf weißem Hintergrund, ohne überlagerte
Website-Beschriftungen. PNG-Originale liegen unter `renders/desktop/` und
`renders/mobile/`. Die Website verwendet daraus erzeugte WebPs und separat
projizierte SVG-Beschriftungen.

- [Modell und reproduzierbarer Ablauf](../../../13-haus-r3-materialien-und-details.md)
- [Detaillierte Blender-Quelle](../../../../assets/3d/elektro-hubmann-house-v3-r3-detail.blend)
- [Separate Web-Animation](../../../../assets/3d/elektro-hubmann-house-v3-r3-detail-web.blend)
- [Geometrieprüfung](../detail/validation.json)
- [Animationsprüfung](animation-validation.json)
- [Ausgabeprofil](manifest.json)
- [Bildanzahl und Datenmenge](export-report.json)
- [Browserprüfung](browser-qa.json)

Alle sechs Kapitel wurden bei 1440 × 1000 und 390 × 844 Pixeln über die echte
Scrollnavigation in beiden Richtungen geprüft. Die kompakte Ansicht bei
375 × 667 Pixeln hält den Kontaktbutton sichtbar; die statische Ansicht bei
844 × 500 verwendet nach frischem Laden alle sechs neuen Kapitelposter.
Screenshots liegen neben diesem Bericht. Die Betriebssystem-Einstellung für
reduzierte Bewegung wurde nicht separat umgeschaltet.

Astro-Prüfung: 20 Dateien ohne Fehler, Warnungen oder Hinweise. Der statische
Build erzeugt sieben Routen erfolgreich; alle 18 Tests in zwei Dateien bestehen.
