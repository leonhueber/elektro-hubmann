# Haus V4 – zwei Geschosse und Satteldach

Stand: 6. September 2026. Acht ImageGen-Mockups und zwei schematische Grundrisse
als Vorlage für einen späteren Blender-Neubau. Die aktive V3-Website wurde nicht
umgestellt; V4 besitzt noch keine native Blender-Szene oder berechnete Animation.

Leon hat diese Bildserie als **v4-reference-01** für den Nachbau ausgewählt.
Haus, Einrichtung, Materialdetails und Frontend-Anordnung sind die feste Vorlage.
Die Originaldateien bleiben unverändert; Weiterentwicklungen erhalten einen eigenen
Revisionsordner. Die Bildgeneratoren für Grundrisse und Vorschau stoppen bei
vorhandenem `reference-lock.json`.

- [Verbindlicher Nachbau- und Kameraplan](../../14-haus-v4-verbindliche-vorlage-und-kamerafahrten.md).
- [Bewegungsablauf mit Ruhepositionen](motion-plan.json) – geplant, noch nicht animiert.
- [Referenzpaket als ZIP](../../../assets/reference/house-v4-reference-01.zip)
  und [SHA-256-Prüfsummen](reference-lock.json).

Integrität aus dem Projektverzeichnis prüfen:

```powershell
python docs/mockups/house-v4/reference_package.py --verify
```

## Ansehen

- [Ansichten im bestehenden Website-Layout](website.html): acht Zustände über die
  untere Navigation oder die Pfeiltasten durchschalten. Die rechte Navigation
  bildet die sechs Leistungskapitel ab. Auf schmalen Bildschirmen wird sie horizontal.
- [Alle Bilder vergleichen](review-board.html): acht Szenen plus beide Grundrisse.
- [Erdgeschoss](09-grundriss-eg.svg) und [Obergeschoss](10-grundriss-og.svg).
- [Gemeinsamer Bildbrief](brief.md) mit Hausidentität und Raumprogramm.
- [Exakte Bildprompts](prompts/) – eingebautes ImageGen, kein API-/CLI-Fallback.
- [Desktop- und Mobilansichten der Website-Mockups](website-mockups/).

Lokal: `http://127.0.0.1:4325/website.html`. Der Vorschau-Server benötigt nur Python:

```powershell
python -m http.server 4325 --bind 127.0.0.1 --directory docs/mockups/house-v4
```

Die Bilddateien und die Website-Attrappe funktionieren auch ohne den laufenden
Astro-Server. Die Kontakt- und Headerlinks führen zur vorhandenen lokalen Website.
Die Mockup-Steuerung ist ein Ansichtswechsler, noch kein animierter Scroll-Player.

## Die acht Zustände

| Bild | Kapitel / Zweck | Bildidee |
| --- | --- | --- |
| [01 Planung](states/01-planung.png) | 01 Planung | Geschlossene Architektur, zwei Vollgeschosse, ruhiges Satteldach. |
| [02 Öffnung](states/02-oeffnung.png) | Übergang zu 02 | Dach und OG separat angehoben; beide eingerichteten Etagen sichtbar. |
| [03 Installation](states/03-installation.png) | 02 Installation | EG-Schnitt mit Verteilung, Netzwerk und Hauswirtschaft rechts vorne. |
| [04 Beleuchtung](states/04-beleuchtung.png) | 03 Beleuchtung | Derselbe EG-Blick mit warmem Arbeits-, Essplatz- und Wohnlicht. |
| [05 Smart Home](states/05-smart-home.png) | 04 Smart Home | OG mit drei Schlafzimmern, Familienbad, Taster und Beschattung. |
| [06 Sicherheit](states/06-sicherheit.png) | 05 Sicherheit | Nähere Ansicht des Eichen-Eingangs mit Videosprechanlage. |
| [07 Photovoltaik](states/07-photovoltaik.png) | 06 Photovoltaik | Höherer Blick auf das bekannte Dach mit zehn Modulen in zwei Reihen. |
| [08 Abschluss](states/08-abschluss.png) | Abschluss | Gleiche Außenperspektive mit warmem Innen- und Eingangslicht. |

## Gestalterische Entscheidung

Das Haus erhält zwei vollwertige Wohngeschosse unter einem einfachen Satteldach.
Die klare Giebelfassade, ein zurückgesetzter Eichen-Eingang, warme Putzflächen
und dunkle Fensterprofile bilden die gemeinsame Identität. EG und OG erhalten
unterschiedliche Aufgaben: Wohnen, Arbeiten und Technik unten; Schlafen und Bad oben.
Das vermeidet den Charakter eines Bürogebäudes und erhält ein vollständiges Wohnhaus.

Bei der Öffnung heben sich zuerst das Dach und dann die OG-Gruppe mit Bodenplatte.
Für die Leistungskapitel fährt die Kamera zur benötigten Etage oder zum Eingang.
Die hohe Explosionsansicht dient als kurzer erklärender Übergang. Für Photovoltaik
schließt sich das Haus wieder. Möbel, Fenster und Geräte müssen in der späteren
Blender-Szene an denselben Stellen bleiben; eine Ansicht darf den Grundriss nicht ändern.

## Verbindliche Grundlage für den Blender-Neubau

1. Außenmaß 9,60 × 10,80 m, zwei Vollgeschosse, Satteldach ca. 35°, First von vorne
   nach hinten. Diese Maße sind Entwurfswerte und nicht aus Rasterbildern messbar.
2. Beide SVG-Grundrisse gemeinsam in 3D prüfen. Derselbe Treppenschacht verbindet
   EG und OG; das OG besitzt keine weitere Treppe in den unbewohnten Dachraum.
3. Möbel, Türen und Sanitärgegenstände aus den jeweiligen EG-/OG-Ansichten
   übertragen. Die SVG-Schemata legen Raumfolge und Erschließung fest; erst die
   geprüfte native Szene legt Türanschläge, Treppenlauf und endgültige Maße fest.
4. Collections für EG, OG/Bodenplatte, Dach/Giebel/PV, Schnittwände, Einrichtung
   und technische Systeme anlegen. Die zehn PV-Module bewegen sich mit dem Dach.
5. Geschlossen, Öffnung, EG, OG und Eingang aus derselben Szene als Kontrollbilder
   rendern. Erst danach Kamerafahrten und eine vollständige Scrollsequenz erzeugen.

## Bei der Sichtprüfung erkannte Abweichungen

ImageGen liefert hier die gestalterische Richtung, keine identischen geometrischen
Renderings. Die Originale wurden nicht nachträglich durch Bildmontage vereinheitlicht.

- Die Eingangslage wirkt in der Außenansicht weiter rechts als der Entwurfswert.
  Für Blender wird eine einzige Lage passend zum Flur festgelegt.
- In 03/04 ist nur ein Treppenlauf eindeutig sichtbar. In 05 liest sich ein Teil
  der Treppe aufwärts. Die korrigierte Öffnung 02 zeigt das OG-Treppenauge nach unten;
  der echte U-Treppenlauf muss anhand beider Grundrisse konstruiert werden.
- Der WC-Zugang im EG und einzelne Raumproportionen der Explosionsansicht sind
  nicht zuverlässig aus dem Bild ableitbar. Die Raumorganisation aus 03 und dem
  EG-Grundriss ist maßgeblich, nicht die perspektivische Überlagerung in 02.
- Im hinteren Kinderzimmer der OG-Ansicht fehlt ein sichtbarer Schreibtisch.
  Im Grundriss ist er eingeplant und wird beim Modellieren ergänzt.
- In der Sicherheitsnahansicht wirkt das Technikfenster etwas größer. Fenstermaße,
  Türstation, Leuchte und Pflanzgefäße werden in Blender aus einer festen Quelle verwendet.

## Dateien und Wiederholbarkeit

`states/` enthält die acht unveränderten Originalausgaben des eingebauten ImageGen.
`prompts/` enthält die vollständigen Anweisungen; nur die Öffnung benötigte eine
zweite Generierung für das Treppenauge und den Weißrand. Die anderen Zustände
wurden jeweils einmal erzeugt, mit der Außenansicht bzw. dem EG als Bildreferenz.

`floorplans.py` erzeugt beide SVGs. `build_preview.py` verwendet den vorhandenen
Produktionsbuild für Header und Typografie sowie die vorhandenen Haus-Styles für
die Website-Attrappe. Referenz-CSS, Logo und Schriftdateien sind lokal gespeichert.
Die Galerie wird aus `review-manifest.json` und `review-options.json` mit dem
gemeinsamen Creative-Production-Renderer erzeugt; sie ist die lokale Prüfoberfläche.

Alle acht Desktopzustände wurden bei 1440 × 1000 Pixeln geladen und ohne horizontalen
Überlauf geprüft. Öffnung und Smart Home wurden zusätzlich bei 390 × 844 Pixeln
kontrolliert. Die acht Desktop-Screenshots und zwei mobilen Ganzseitenbilder liegen
in `website-mockups/`. Beide SVGs wurden im Browser auf Lesbarkeit geprüft.
