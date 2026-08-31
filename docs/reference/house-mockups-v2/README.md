# Haus-Arbeitsmockups V2

Diese drei Bilder ersetzen die bisherigen Screenshots als primaere visuelle
Arbeitsreferenzen fuer das prozedurale Hausmodell. Sie zeigen bewusst dasselbe
Haus und unterscheiden sich nur in ihrem Einsatzzweck.

## Verwendung

1. `01-master-cutaway.png` ist die primaere 3D-Referenz fuer Baukoerper,
   Raumfolge, Materialien und Moeblierung.
2. `02-technical-axonometric.png` ist die Referenz fuer Wandstaerken,
   Oeffnungen, Deckenplatten, Technikschacht und den durchgehenden roten
   Installationsweg.
3. `03-animation-exploded.png` ist die Referenz fuer die Scroll-Animation.
   Dach und Fassaden bewegen sich als wenige vollstaendige, gerade und
   ausgerichtete Baugruppen. Die dargestellten Abstaende sind eine visuelle
   Richtung und keine exakten Animationsmasse.

## Verbindliche Raumlogik

- Erdgeschoss: Wohnen links, Eingang und gerade Treppe mittig,
  Elektroverteilung mittig rechts, Essen und Kueche rechts.
- Obergeschoss: Schlafen links, Treppe und Flur mittig, vollstaendiges Bad
  mittig rechts, nur eine schmale Galerie an der aeussersten rechten Fassade.
- Untergeschoss: eigener Server- und Netzwerkraum direkt unter dem
  Installationskern, Rack links, USV und Sicherheit rechts, Kuehlung und
  nachvollziehbarer Zugang.
- Die rechte Hauswand besitzt echte Oeffnungen mit Laibung und Sturz. Wand,
  Fenster und Holzlamellen duerfen sich nicht ueberlagern.
- Der rote Installationsweg bleibt vom Serverraum ueber die Verteilung und das
  Obergeschoss bis zur PV-Anlage physisch durchgehend.

## Genauigkeit

Die orthografischen Grundrisse in `docs/version-g-qa/blender/floorplans/`
bleiben fuer exakte Raumgrenzen und Objektpositionen verbindlich. Bei einem
Konflikt gilt: Grundriss vor Master-Cutaway, Master-Cutaway vor technischer
Axonometrie, technische Axonometrie vor Explosionsdarstellung.

Die Bilder wurden mit dem integrierten ImageGen-Workflow erzeugt. Die finalen
Prompt-Spezifikationen liegen in `PROMPTS.md`.

## Umgesetztes V2-Modell

Das abgeschlossene, editierbare Modell liegt unter
`assets/3d/elektro-hubmann-house-v2.blend`. Seine prozedurale Quelle ist
`blender/house_v2.py`; die Detailmoebel werden aus
`blender/furniture_v2_detailed.py` aufgebaut.

Verbindliche Abschluss-Proofs nach der Grundriss- und Moebelkorrektur:

- `docs/version-g-qa/blender-v2/final-model-v02/`

Weitere lokal generierbare Animations-QA:

- `docs/version-g-qa/blender-v2/phase-04-animation-keyframes-v01/`

Der Standard-Build speichert nur die Szene. Renderausgaben werden bewusst ueber
explizite Proof-Argumente angefordert, damit kleine Modellkorrekturen niemals
ungewollt die komplette 120-Frame-Sequenz neu berechnen.
