# Implementierungsplan: Hausmodell V2

## Ziel

Das Haus wird als neues, unabhaengiges Blender-Modell auf Basis von
`02-technical-axonometric.png` aufgebaut. Entscheidend ist die visuelle
Uebereinstimmung mit dem Mockup: Silhouette, Geschossproportionen, Schnitt,
Raumfolge, Fassadenoeffnungen und sichtbare Technik. Perfekte bauliche
Ausfuehrungsplanung und hochrealistische Innenraeume sind nachrangig.

Das bestehende Modell und seine Web-Sequenz bleiben unangetastet, bis V2 als
Gesamtmodell freigegeben ist.

## Separate V2-Pipeline

- Prozedurale Quelle: `blender/house_v2.py`
- Editierbare Szene: `assets/3d/elektro-hubmann-house-v2.blend`
- QA-Ausgaben: `docs/version-g-qa/blender-v2/`
- Spaetere Web-Sequenz: eigener temporaerer V2-Ausgabeordner; Austausch der
  produktiven 120 Frames erst nach Gesamtfreigabe

`house_v2.py` wird neu und modular aufgebaut. Allgemeine Primitive wie Box,
Material und Kamera duerfen als kleine Hilfsfunktionen neu geschrieben werden;
Geometrie, Objektstruktur und Animation werden nicht aus `house_story.py`
kopiert.

## Verbindliche visuelle Regeln

- Zwei Vollgeschosse mit sichtbaren Betonplatten und klaren Eckstuetzen.
- Durchgehendes dunkles Satteldach mit warmer Holzkonstruktion und PV-Feld.
- Erdgeschoss: Wohnen links, Eingang und gerade Treppe mittig, Verteilung
  mittig rechts, Essen und Kueche rechts.
- Obergeschoss: Schlafen links, Treppe und Flur mittig, Bad mittig rechts,
  schmale Galerie ganz rechts.
- Serverraum als eigene unterirdische Zelle direkt unter dem Technikstrang.
- Rechte Fassade als reale Wand mit Laibungen und Stuerzen; keine ueberlagerten
  Fenster, Lamellen oder Wandflaechen.
- Roter Leitungsweg durchgehend von Serverraum und Verteilung bis Bad und PV.
- Die kanonische 3/4-Kamera zeigt das vollstaendige Haus vom Dach bis zum
  Serverraumboden.

## Phasen und Freigabepunkte

### Phase 0 – Technische Basis

Umfang:

- neue Datei-, Collection- und Namensstruktur
- zentraler Mass- und Hoehendatensatz
- feste Material-Platzhalter
- kanonische Mockup-Kamera und orthografische Plankameras
- selektive Renderbefehle fuer einzelne Ansichten und Bauphasen

Abnahme:

- neue Szene laesst sich reproduzierbar aufbauen und speichern
- V1-Modell und bestehende Sequenz werden nicht veraendert
- keine 120-Frame-Ausgabe ist Teil des Standardbefehls

### Phase 1A – Baukoerper

Umfang:

- Fundament, Terrassen und Eingangsstufen
- Erdgeschoss- und Obergeschossplatte
- Eckstuetzen und tragende Rahmen
- Serverraum-Huelle
- Dachvolumen mit plausibler Neigung, Ueberstand und PV-Platzhalter

Noch nicht enthalten:

- Fensterdetails
- Innenwaende
- Moebel
- Leitungen
- Leuchten

QA pro Iteration:

1. front-rechte 3/4-Ansicht
2. reine rechte Seitenansicht
3. frontale Proportionsansicht

Freigabekriterien:

- Silhouette und Geschosshoehen entsprechen Mockup V2
- Dach, Platten, Stuetzen und Serverraum liegen auf einer gemeinsamen Achse
- nichts schwebt oder schneidet ungewollt durch andere Bauteile

### Phase 1B – Fassade und Grundriss

Umfang:

- vollstaendige Aussenwandflaechen
- echte Oeffnungen fuer Fenster und Tueren
- Holzlamellen als eigener, kollisionsfreier Fassadenlayer
- grobe Raumzonen und Treppenoefnung
- drei lesbare Grundrisse fuer Untergeschoss, Erdgeschoss und Obergeschoss

QA pro Iteration:

1. geschlossene 3/4-Fassade
2. rechte Fassadenkontrolle
3. Grundriss Untergeschoss
4. Grundriss Erdgeschoss
5. Grundriss Obergeschoss

Freigabekriterien:

- rechte Wand, Fenster und Lamellen ueberlappen sich nicht
- Raumzonen entsprechen dem verbindlichen V2-Schema
- Serverraum, Verteilung und Bad liegen vertikal uebereinander
- Treppe und Tueroeffnungen bilden einen nachvollziehbaren Weg

Nach dieser Freigabe werden Baukoerper und Grundrisse eingefroren. Spaetere
Phasen duerfen diese Masse nur nach ausdruecklicher Ruecksprache aendern.

### Phase 2A – Waende, Fenster, Tueren und Treppe

Umfang:

- Innenwaende mit klaren Tueroeffnungen
- gerade Treppe, Podest und Absturzsicherung
- Fensterrahmen, Laibungen, Stuerze und Schwellen
- Aussentueren und vereinfachte Innentueren
- Badabtrennung und schmale Galerie

QA pro Iteration:

1. offener Schnitt ohne Moebel
2. Obergeschoss-Grundriss
3. Blick entlang der rechten Fassade

Freigabekriterien:

- keine Wand endet unbeabsichtigt in einem Fenster
- Tueren blockieren weder Treppe noch Hauptwege
- Bad ist als geschlossener Raum lesbar
- Galerie bleibt schmal und ist kein leerer zweiter Raum

### Phase 2B – Vereinfachte Moebel

Umfang:

- einfache, saubere Silhouetten statt hochdetaillierter Einzelmodelle
- Wohnen: Sofa, Sessel, Tisch und TV
- Kueche/Essen: Kuechenzeile, Tisch und Stuehle
- Schlafen: Bett, Nachtkaestchen und Schrank
- Bad: Waschtisch, Dusche, WC und Wanne entsprechend Grundriss
- Technik: Verteiler, Rack, USV/Sicherheit und Kuehlung als Blockout

QA pro Iteration:

1. kanonischer Cutaway
2. Erdgeschoss-Grundriss
3. Obergeschoss-Grundriss
4. Serverraum-Grundriss

Freigabekriterien:

- Moebel erzeugen im Mockup-Blick die richtigen Raum-Silhouetten
- Verkehrswege bleiben frei
- kein Objekt schwebt, dupliziert sich oder schneidet durch Waende
- Detailrealismus wird nicht auf Kosten der Gesamtkomposition erhoeht

### Phase 3A – Materialien und Architekturdetails

Umfang:

- Beton, weisser Putz, helle Eiche, dunkle Fenster und Dachziegel
- Dachstuhl, Rinnen, wenige konstruktive Fugen und Schattenkanten
- saubere Sockel-, Decken- und Wandanschluesse
- PV-Module als zusammenhaengendes Dachsystem

QA pro Iteration:

1. geschlossene Energieansicht
2. offener Cutaway
3. Material-Nahansicht rechte Fassade

### Phase 3B – Technik und Licht

Umfang:

- geoeffneter Verteilerschrank mit klarer Geraetehierarchie
- Serverrack, USV/Sicherheit, Gateway und Kuehlung
- ein sauberer roter Hauptpfad mit wenigen nachvollziehbaren Abzweigen
- Pendelleuchten, Downlights und indirektes Kuechen-/Badlicht
- Lichtwerte auf Lesbarkeit des Mockups statt physikalische Simulation trimmen

QA pro Iteration:

1. Installationsschnitt
2. Detail Verteilerschrank
3. Detail Serverraum
4. beleuchteter Cutaway

Freigabekriterien:

- Technikpfad ist durchgehend und ohne visuelles Kabelchaos
- Verteilung und Serverraum sind auf Website-Groesse erkennbar
- Licht trennt Raeume, ueberstrahlt aber keine weissen Flaechen

### Phase 4 – Animation und Kamera

Umfang:

- Dach als eine starre Baugruppe
- Front- und rechte Fassade als wenige vollstaendige Paneelgruppen
- Innenkern, Moebel und Technik bleiben waehrend der Explosion stabil
- Kamera-Keyframes werden erst nach Freigabe der statischen Ansichten gesetzt
- Serverraum bleibt im Installationszustand im Bild

QA pro Iteration:

- nur die Schluesselframes `1`, `28`, `40`, `52`, `70`, `82`, `92`, `104`
  und `120`
- bei Kameraaenderungen zunaechst nur der direkt betroffene Frame plus seine
  beiden Nachbarn
- keine vollstaendige Sequenz waehrend der Modelliteration

Freigabekriterien:

- jede Scrollphase besitzt eine klar unterscheidbare Kamerafuehrung
- Dach und Fassaden bewegen sich ruhig, vollstaendig und nachvollziehbar
- keine Geometrie springt, driftet oder skaliert sichtbar aus dem Ursprung
- die 120 Frames werden genau einmal nach Gesamtfreigabe gerendert

## Iterationsregel

Jede Runde veraendert nur eine Kategorie, beispielsweise nur Dachproportion,
nur rechte Fensteroeffnungen oder nur Badmoebel. Der Ablauf bleibt immer:

1. kleine Aenderung implementieren
2. V2-Blend reproduzierbar neu aufbauen
3. nur die vereinbarten QA-Bilder rendern
4. gegen Mockup und letzten freigegebenen Stand vergleichen
5. Aenderung freigeben oder gezielt korrigieren
6. freigegebenen Meilenstein separat committen

QA-Ordner werden nach Phase und Version benannt, zum Beispiel
`phase-01b-facade-v03/`. Dadurch bleiben Vergleiche nachvollziehbar und ein
spaeteres Detail kann keinen bereits freigegebenen Grundriss unbemerkt
veraendern.

## Bewusste Nicht-Ziele

- keine exakte Ausfuehrungs- oder Genehmigungsplanung
- keine vollstaendige Elektro- oder Sanitaerberechnung
- keine hochaufgeloesten Einzelmoebel, wenn einfache Formen im Mockup genuegen
- keine Mikrodetails vor Freigabe von Silhouette, Fassade und Raumaufteilung
- kein erneutes Rendern aller 120 Frames nach kleinen Aenderungen

## Aktueller Stand – Phase 2B

Umgesetzt und reproduzierbar in `house_v2.py`:

- Phase 0: separate V2-Szene, Collections, Kameras und selektive Proofs
- Phase 1A: Baukoerper, korrekt geneigtes Satteldach und Serverraum-Huelle
- Phase 1B: segmentierte Fassaden, kollisionsfreie rechte Fensterwand,
  Lamellen und drei beschriftete Grundrisse
- Phase 2A: reale Treppenoeffnung, gerade Treppe, Innenwaende, Tueren,
  Fensterrahmen und offene Absturzsicherung
- Phase 2B: vereinfachte Moebel fuer alle Raeume sowie Verteiler-, Rack-,
  USV- und Kuehlungs-Blockouts

Freigegebener Review-Kandidat:
`docs/version-g-qa/blender-v2/phase-02b-furniture-v03/`

Naechster bewusster Stopp ist Phase 3A. Materialien, Dachdetails, Leuchten,
rote Leitungswege und finale Technikdetails wurden noch nicht vorgezogen.
