# Haus V4 – natives Blender-Modell

**Neueste Modellrevision: Außenrevision 01.** Balkon mit Metallgeländer,
Fensterrahmen in Holzoptik, Vordach, größere Terrasse und Fassadendetails liegen
in `assets/3d/elektro-hubmann-house-v4-exterior-r1.blend`. Die entsprechend
ergänzte neueste Animationsszene trägt den Zusatz `-web.blend`.
[Änderungen, Prüfung und Reproduktion](../../docs/16-haus-v4-aussendetails.md).
Die folgenden Angaben beschreiben die erhaltene V4-Grundlage.

Die Szene in `assets/3d/elektro-hubmann-house-v4.blend` baut die ausgewählte
Referenz `v4-reference-01` als zusammenhängendes Haus nach. Sie wurde in
Blender 5.2.1 über dessen sichtbare Python-Konsole aufgebaut und mit Cycles
kontrolliert. Die Website verwendet den separaten
[V4-Animations- und Web-Export](../../docs/15-haus-v4-website-animation.md).
Die Architekturdatei bleibt dabei unverändert.

## Modell

- Zwei Vollgeschosse, Grundkörper 9,6 × 10,8 m und 35°-Satteldach.
- EG: Wohnküche mit sechs Essplätzen, Technik/Hauswirtschaft, Gäste-WC,
  Büro und zentrale U-Treppe.
- OG: Elternschlafzimmer, zwei Kinderzimmer, Familienbad und Treppenflur.
- Echte Fenster- und Türöffnungen, Fensterprofile, Leibungen, Sockelleisten,
  einzelne Parkettdielen und Fliesen sowie eine durchbrochene OG-Decke.
- Möbel mit einzelnen Fronten, Griffen, Polstern, Nähten und gefalteter
  Bettwäsche; hohle Sanitärkeramik, Armaturen, Glas, Pflanzen und Leuchten.
- Verteiler und Netzwerkschrank, Leitungswege, Taster/Beschattung,
  Videosprechanlage sowie zehn PV-Module mit Zellen, Rahmen und Schienen.

Stand `v4-build-02`: Das PV-Feld ist auf der Dachfläche zentriert und gegenüber
dem ersten Aufbau vergrößert. Die Raumleuchten haben einen warmen Farbton;
das Studio-Tageslicht bleibt neutral. Der Wohn-/Essbereich hat einen breiten,
türlosen Durchgang. Im EG bleiben Türen für HWR, Gäste-WC und Büro, jeweils
mit Öffnung in den Raum und zurückhaltenden weißen Türblättern.

Erdgeschoss, Obergeschoss und Dach haben eigene übergeordnete Objekte.
Die für Schnittansichten abnehmbaren Wand- und Fensterteile sind getrennt
modelliert. Regenrohre folgen den jeweiligen Geschossen.
In Schnittansichten werden die inneren Türblätter samt Beschlägen zusammen
mit den oberen Wänden ausgeblendet. Niedrige Zargen bleiben als Einfassung
der tatsächlichen Durchgänge sichtbar.
Die OG-Decke folgt dem Dach. Deckenleuchten ergänzen die Tisch-, Steh- und
Pendelleuchten; die Innenräume bleiben dadurch auch durch die geschlossene
Fassade sichtbar. In der isolierten OG-Ansicht bleibt ein begrenzter Ausschnitt
des tatsächlichen Treppenhauses darunter erhalten.

## Direkt in Blender bedienen

Im 3D-Viewport die Seitenleiste mit `N` öffnen und **V4 Haus** wählen.
Acht Schaltflächen wechseln Modellzustand, Kamera und Beleuchtung. Der
Render-Knopf berechnet die gewählte Ansicht mit Cycles.

Nach einem Blender-Neustart ist die Python-Erweiterung eventuell noch nicht
registriert. Im Text-Editor den in der Datei gespeicherten Text
`RUN_V4_SIDEBAR` wählen und **Run Script** ausführen. Die Startdatei erwartet
das Repository an seinem bisherigen Ort. Bei einem Umzug den dortigen Pfad
zum `blender`-Verzeichnis anpassen. Das Modell und seine Materialien selbst
benötigen die Erweiterung nicht; Textur und Referenzbilder sind eingepackt.

Die acht Kameramarker sind **einzelne Prüfpositionen**. Das Abspielen der
Timeline ist noch keine fertige Öffnungsanimation. Die kontinuierlichen
Kamerafahrten, Übergänge und Desktop-/Mobilsequenzen folgen auf dieser Szene
gemäß dem gespeicherten V4-Bewegungsplan.

## Reproduzierbarer Aufbau

In Blenders Python-Konsole:

```python
import sys
sys.path.insert(0, 'C:/Users/hueberl/Private_Projects/elektro-bubmann/blender')
import build_house_v4 as v4
v4.build()
```

`build()` ersetzt die als V4 generierten Objekte und speichert die V4-Datei.
Manuelle Änderungen an diesen Objekten vorher in einer eigenen Datei sichern.
Die Module trennen Geometrie/Materialien, Architektur, Möbel, Raumausstattung
und die Blender-Seitenleiste.

```python
v4.set_view('smart-home')
v4.render(list(v4.POSES), size=1200, samples=40)
from house_v4 import validate
validate.run()
```

Die native Prüfung liest Raumzuordnung, Geschossgruppen, Betten, PV-Module,
Treppenstufen, Deckenöffnung, Kameras und eingepackte Bilder aus der Szene.
Die Prüfbilder und das Ergebnis liegen in
`docs/version-g-qa/blender-v4/`.

## Referenztreue

Die unveränderten Mockups liegen in `docs/mockups/house-v4/`. Außenansicht,
EG und OG dienen jeweils als gestalterische Referenz. Die Modellgeometrie
löst die kleinen Widersprüche der generierten Bilder konstruktiv auf:
durchgehende Geschosse, eine reale U-Treppe mit passender Deckenöffnung,
zusammengehörige Fassadenöffnungen und nutzbare Sanitärobjekte. Das Ergebnis
ist ein editierbares gemeinsames Modell; kein pixelidentischer Ersatz der
einzeln generierten Bilder.

Die verwendete Eichenholz-Textur ist die bereits im Projekt vorhandene
CC0-Textur `oak_veneer_01` von Poly Haven. Alle Haus- und Möbelgeometrien
dieser Szene sind native Blender-Geometrie.
