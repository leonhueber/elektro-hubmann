# Hausmodell V3 – Blender-Modell und Scroll-Story

Stand: 5. September 2026

Status: Überholter Erstplan. Das erste V3-Modell wurde umgesetzt, seine Gestaltung
aber am 5. September als nicht ausreichend clean und professionell bewertet.
Der [gestalterische Neustart](11-hausmodell-v3-gestalterischer-neustart.md)
ersetzt die Hausrichtung und Arbeitsreihenfolge dieses Dokuments. Die folgenden
Angaben dokumentieren den ursprünglichen Planungsstand.

## 1. Ziel und Leitentscheidung

Ein zusammenhängendes Haus zeigt, wo die Leistungen von Elektro Hubmann im
Gebäude wirken. Beim Scrollen hebt sich das Dach, ausgewählte Wände verschwinden
und die einzelnen Systeme werden nacheinander sichtbar und aktiviert. Beim
Zurückscrollen läuft derselbe Vorgang rückwärts.

Das Haus wird vollständig in Blender modelliert, beleuchtet und animiert. Für
die Website ist eine daraus gerenderte Bildsequenz vorgesehen. Das ist eine
Darstellungsentscheidung: Die editierbare 3D-Szene bleibt die Quelle aller
Ansichten, Übergänge und statischen Kapitelbilder.

Die wichtigste Änderung gegenüber V2 ist die Arbeitsreihenfolge: **Zuerst
Hausform, sichtbare Technik und Öffnungsbewegung gemeinsam lösen. Danach
Architekturdetails, Einrichtung und Materialien ausarbeiten.**

## 2. Geprüfter Bestand

| Bestand | Bedeutung für V3 |
| --- | --- |
| `assets/3d/elektro-hubmann-house-v2.blend` und `blender/house_v2.py` | Bestehende, separat erzeugte Blender-Szene mit zwei Vollgeschossen, Satteldach, unterirdischer Technikzelle und Animationslogik. |
| `docs/version-g-qa/blender-v2/final-model-v02/01-final-cutaway.png` | Sichtbare V2-Referenz: Einrichtung und Geschossaufbau beanspruchen viel Bildfläche; die Technik ist im Vergleich klein. |
| `src/components/variants/g/HouseStory.tsx` | Der aktuelle Player bewegt und überblendet einzelne Kapitelbilder. Er spielt derzeit keine Blender-Bildsequenz ab. |
| `src/config/version-g-story-assets.ts` | Vier aktuelle Kapitel: Planung, Installation, Beleuchtung und Energiesysteme. Das aktive Planungsmotiv ist ein Pultdachhaus. |
| `StaticHouseChapters.astro` und `VariantG.astro` | Statische Kapitel für reduzierte Bewegung und ohne JavaScript sind bereits vorgesehen. |
| Lokale Blender-Installation | `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe` ist vorhanden. Der V3-Aufbau muss später mit dieser Installation geprüft werden. |

README und ältere Planungsdokumente beschreiben teilweise noch eine andere
Story. Für den aktuellen Web-Anschluss gilt der gelesene Quellcode. V3 erhält
eigene Quelldateien und Ausgaben; vorhandene Modelle und Web-Assets werden bei
der Entwicklung nicht überschrieben.

## 3. Hausform und visuelle Richtung

**Empfohlene Arbeitsannahme:** ein modernes, kompaktes Einfamilienhaus mit zwei
Geschossen und flach geneigtem Pultdach. Das passt zum aktuell ausgewählten
Webmotiv und lässt viel Platz für die geöffneten Räume und das PV-Feld. Diese
Hausform ist ein Vorschlag für V3, keine bereits freigegebene Vorgabe.

- Grundfläche als Ausgangspunkt etwa 10 × 8 Meter; endgültige Proportionen
  werden am groben Modell und in tatsächlicher Website-Größe bestimmt.
- Heller Putz, wenige warme Holzflächen, dunkle Fensterrahmen und ein dunkles
  Dach. Ruhige Materialien und weiche Schatten auf dem weißen Seitenhintergrund.
- Erdgeschoss: Wohnen links, Essen/Küche rechts, Treppe im hinteren Kern und
  ein gut einsehbarer Technikraum nahe der sichtbaren Schnittkante.
- Obergeschoss: Schlafzimmer, Arbeitszimmer und Bad als wenige lesbare Zonen.
  Der Installationsschacht liegt über dem Technikraum.
- Technik im Erdgeschoss statt einer zusätzlichen Kellerzelle. Dadurch bleibt
  das Haus kompakter und Verteilung, Netzwerk und Energiesysteme werden größer
  sichtbar. Diese Raumordnung ersetzt für V3 die bisherige V2-Raumvorgabe.
- Kleine Zufahrt mit Platz für eine optionale Wallbox; Terrasse für Außenlicht
  und Eingang mit Sprechanlage. Ein Auto ist nur nötig, wenn die Wallbox sonst
  nicht verständlich wird.
- Einrichtung erklärt die Nutzung der Räume: Sofa, Esstisch, Küchenzeile, Bett
  und Schreibtisch. Detailmöbel erhalten erst nach der Technik ihren Platz.
- Das Haus ist ein fiktives Anschauungsmodell und wird nicht als ausgeführtes
  Kundenprojekt dargestellt.

Die Hauptkamera zeigt das Haus leicht von oben aus einer festen 3/4-Richtung.
Kurze, kleine Annäherungen sind möglich, der Grundriss bleibt aber während der
gesamten Story nachvollziehbar. Kein Kameraflug durch Wände und keine komplette
Umrundung. Alle Kapitel zeigen dasselbe Haus mit identischen Objektpositionen.

## 4. Scroll-Ablauf

Die Prozentwerte beziehen sich auf den Fortschritt innerhalb der Haus-Story,
nicht auf die gesamte Seite. Sie sind Startwerte für den ersten Bewegungstest.
Die Navigation erhält sechs Kapitel; Öffnung und Abschluss sind Übergänge
innerhalb dieser Kapitel.

| Fortschritt | Kapitel / Zustand | Bewegung und sichtbare Komponenten | Aussage |
| --- | --- | --- | --- |
| 0–10 % | 01 Planung | Vollständiges, geschlossenes Haus. Ein zurückhaltender Grundriss auf der Bodenfläche und wenige Anschlusspunkte führen in die Planung ein. | Gute Elektrotechnik beginnt mit einem abgestimmten Plan. |
| 10–23 % | 02 Installation – Haus öffnen | Das Dach hebt sich als zusammenhängende Baugruppe um zunächst etwa 0,8–1,2 Meter. Vorderfassade und kameranahe Seitenwand blenden sich mit ihren Fenstern und Türen aus. Der Technikraum wird sichtbar. | Sichtbar machen, was gewöhnlich hinter den Wänden liegt. |
| 23–37 % | 02 Installation – Technik zeigen | Der geöffnete Verteiler wird betont. Ein Hauptweg und wenige Abzweige zeichnen sich vom Technikraum zu Steckdosen, Schaltern und Leuchten nach. Separat wird eine Datenverbindung zum Arbeitszimmer sichtbar. | Saubere Installation und strukturierte Vernetzung. |
| 37–51 % | 03 Beleuchtung | Leitungsakzente treten zurück. Esstischpendel, Küchenlicht, Wohnraumlicht und Eingangslicht schalten sich nacheinander ein. Die Umgebung wird etwas dunkler, die Architektur bleibt lesbar. | Licht macht den Nutzen der Installation unmittelbar sichtbar. |
| 51–64 % | 04 Smart Home | Ein Wandtaster beziehungsweise Display wird hervorgehoben. Eine beispielhafte Szene dimmt Licht und bewegt eine Beschattung. Gateway, Bedienelement und Wirkung im Raum sind verbunden. | Vernetzte Steuerung schafft Komfort. |
| 64–76 % | 05 Sicherheit | Fokus nacheinander auf Videosprechanlage am Eingang, Alarmkontakt beziehungsweise Bewegungsmelder und Brandmeldetechnik. Dezente Markierung statt Alarmblinken. | Schutz beginnt an konkreten Punkten im Gebäude. |
| 76–93 % | 06 Photovoltaik & Energie | Das Dach senkt sich wieder auf seinen Sitz, die vordere Schnittöffnung bleibt bestehen. Das PV-Feld wird hervorgehoben. Ein schematischer Pfad führt zum Wechselrichter, zur Hausverteilung und gegebenenfalls zu Speicher und Wallbox. | Energie erzeugen und im Haus nutzen. |
| 93–100 % | Abschluss innerhalb Kapitel 06 | Der Energieakzent klingt ab. Die Fassaden schließen sich ruhig, das vollständig beleuchtete Haus bleibt als Abschluss stehen. Text führt zu Projektanfrage und Betreuung. | Planung, Ausführung und Service aus einer Hand. |

Jedes Leistungskapitel erhält eine kurze Überschrift, einen Nutzenabsatz und
höchstens zwei bis drei gleichzeitig sichtbare Bauteilbeschriftungen.
Beschriftungen und Kontaktaktionen werden als HTML angelegt, damit sie auf
Mobilgeräten lesbar und zugänglich bleiben.

Eine Bewegung läuft nur über einen Teil ihres Kapitels. Anschließend bleibt
ein klarer Zustand stehen, während der Text gelesen wird. Der Scrollfortschritt
bestimmt den Zustand vollständig; es gibt keine zeitabhängigen Nachläufe oder
automatisch weiterlaufenden Licht- und Energieeffekte.

## 5. Leistungen und Modellkomponenten

Die bisherige
[Leistungsseite von Elektro Hubmann](https://elektro-hubmann.at/dienstleistungen/)
nennt Installation, Netzwerktechnik, Beleuchtung, KNX-EIB, Sprechanlagen,
Alarmanlagen, Brandmeldeanlagen, Blitzschutz, SAT, Photovoltaik, Anlagenprüfung
und Kundendienst. Daraus ergibt sich folgende Auswahl für die Hausdarstellung.
Die Veröffentlichung auf dieser Seite ersetzt keine spätere fachliche
Bestätigung des endgültigen Angebots.

| Bereich | Zu modellieren | Darstellung und Umfang |
| --- | --- | --- |
| Installation | Hausanschluss als vereinfachter Übergabepunkt, Verteilung, Installationsschacht, Leitungswege, Dosen und Schalter | Ein gut lesbarer Hauptstrang mit wenigen Abzweigen. Keine Darstellung einer ausführungsreifen Elektroplanung. |
| Netzwerk | Kompakter Netzwerkschrank mit Patchpanel und Switch, Anschluss im Arbeitszimmer, Access Point | Eigene Datenwege; elektrische Energie fließt in der Darstellung nicht durch das Netzwerkrack. |
| Beleuchtung | Pendelleuchte, Downlights, indirektes Licht, Außenleuchte | Unterschiedliche Lichtwirkungen im selben Haus. Sicherheitsbeleuchtung nur in einem fachlich passenden Anwendungsbeispiel ergänzen. |
| Smart Home | KNX-Steuerung als generische Geräte, Taster, Display, Beschattung | Eine verständliche Steuerungsszene. Keine unbestätigten Produktmarken oder Integrationsversprechen. |
| Sicherheit | Video-Türstation, Innenstation, Alarmkontakt oder Bewegungsmelder, Komponente der Brandmeldetechnik | Systeme unterscheidbar zeigen. Ein einzelner Rauchwarnmelder wird nicht als vollständige Brandmeldeanlage bezeichnet. |
| Photovoltaik | Dachmodule, Unterkonstruktion, Leitungsabgang, Wechselrichter und Anschluss an die Verteilung | PV bleibt räumlich mit dem Haus verbunden. Energiepfade dienen der Erklärung, nicht einer elektrischen Simulation. |
| Speicher und Laden | Modular zuschaltbarer Batteriespeicher und Wallbox | Im aktuellen Website-Text vorgesehen, auf der bisherigen Leistungsseite nicht ausdrücklich belegt. Vor endgültiger Leistungsdarstellung bestätigen; PV funktioniert im Modell auch ohne diese Ergänzungen. |
| Weitere Leistungen | Bei Bedarf SAT-Schüssel und Blitzschutz als dezente Dachdetails | Kein zusätzliches langes Scrollkapitel. Nur nach fachlicher Auswahl sichtbar machen. |
| Prüfung und Service | Betreuter Gesamtzustand des Hauses und passender Kontakttext | Keine erfundene Prüfplakette oder Zertifizierung. Fachgeschäft bleibt im vorhandenen Abschnitt außerhalb der Haus-Story. |

Aktive Komponenten erhalten einen zurückhaltenden Akzent in Hubmann-Rot.
Technik bleibt auch über Position, Form und Beschriftung verständlich;
Farbe allein darf die Systeme nicht unterscheiden. Leitungsfarben sind eine
schematische Hervorhebung und keine Aussage über reale Leiterkennzeichnungen.

## 6. Blender-Aufbau und Animationsregeln

### Szenenstruktur

| Collection | Inhalt / Steuerung |
| --- | --- |
| `V3_STRUCTURE` | Bodenplatten, Rückwände, Treppenkern, bleibende Stützen und Schnittkanten. |
| `V3_SHELL_FRONT` / `V3_SHELL_SIDE` | Ausblendbare Fassaden einschließlich zugehöriger Fenster, Türen und Laibungen. |
| `V3_ROOF` | Dachhaut, Unterkonstruktion, PV und dachgebundene Details unter einem gemeinsamen Steuerobjekt. |
| `V3_INTERIOR` | Innenwände, Einrichtung und separat steuerbare Deckenbereiche, die den Einblick verdecken könnten. |
| `V3_ELECTRICAL` / `V3_NETWORK` | Verteilung, Geräte und getrennte Strom- beziehungsweise Datenwege. |
| `V3_LIGHTING` / `V3_SMARTHOME` / `V3_SECURITY` | Leuchten, Lichtquellen und die Geräte der jeweiligen Kapitel. |
| `V3_ENERGY` | Stationärer Wechselrichter sowie optionale Speicher- und Ladekomponenten. PV-Module gehören zur bewegten Dachgruppe. |
| `V3_RIG` / `V3_CAMERAS` / `V3_STAGE` | Steuerobjekte, Desktop- und Mobilkamera, Präsentationslicht und Hintergrund. |

Collections organisieren die Szene. Bewegungen werden über eindeutig benannte
Steuerobjekte mit korrekt zugeordneten Unterobjekten gesteuert. Maße,
Materialparameter und Kapitelmarken liegen zentral; V3 übernimmt keine
ungeprüften Geometrie- und Animationsblöcke aus dem großen V2-Skript.

### Regeln für das Öffnen

1. Das Dach bewegt sich starr und senkrecht. PV-Module und Dachdetails folgen
   derselben Bewegung; ihre Einzelteile driften nicht auseinander.
2. Vordere und seitliche Hülle verschwinden kontrolliert über animierte
   Materialien. Auch Schatten und Reflexionen der entfernten Hülle müssen
   plausibel verschwinden. Kein plötzlicher Sichtbarkeitsschalter mitten im
   Übergang und kein Schrumpfen der Wände auf einen Punkt.
3. Rückwände, Böden und der innere Kern bleiben erhalten. Geschosse fliegen
   nicht auseinander. Verdeckt eine Decke wichtige Technik, erhält nur ihr
   kameranaher Bereich eine geplante Schnittöffnung.
4. Innenraumleuchten behalten erkennbare Befestigungen an bleibenden Bauteilen.
   Kein Lampenschirm bleibt nach dem Ausblenden seiner Decke unerklärt hängen.
5. Strom- und Datenwege behalten feste Raumkoordinaten. Ein Dachanschluss wird
   im offenen Zustand als schematische Verbindung dargestellt und kehrt beim
   Schließen exakt auf seine ursprüngliche Position zurück.
6. Glas, Fassadenmaterial und Leitungsakzente werden früh in kurzen Testsequenzen
   geprüft: doppelte Konturen, Transparenzrauschen und flackernde Schatten
   sind typische Fehler dieses Übergangs.
7. Alle Zustände sind direkt ansteuerbar. Dieselbe Fortschrittsposition muss
   vorwärts, rückwärts und nach einem Kapitelsprung dasselbe Bild ergeben.

## 7. Web-Ausgabe und Anschluss

### Empfohlener Ausgabepfad

Blender rendert Einzelbilder; daraus entstehen optimierte WebP-Dateien und
statische Kapitelbilder. Separate Frames erlauben gezielte Nachberechnung und
Wiederaufnahme abgebrochener Renderläufe. Dieser Workflow ist auch im
[Blender-Handbuch zur Animationsausgabe](https://docs.blender.org/manual/en/2.80/render/output/animation.html)
beschrieben; konkrete Einstellungen werden mit der vorhandenen Blender-Version
geprüft.

Für den ersten Webversuch genügen 24–36 grobe Vorschaubilder. Für die finale
Desktop-Sequenz gelten zunächst etwa 160–200 unterschiedliche Bilder als
Planungsrahmen. Die notwendige Dichte wird an Dachbewegung, Fassadenübergang
und schnellem Scrollen gemessen. Haltephasen brauchen keine mehrfach
gespeicherten identischen Bilder. Die vorhandenen 120 Frames sind keine
verbindliche Vorgabe für V3.

Live-3D mit GLB und WebGL wäre bei späterer freier Drehung oder direkt
anklickbaren 3D-Objekten neu zu bewerten. Für den jetzt gewünschten festen
Scroll-Ablauf ist die gerenderte Sequenz der empfohlene Startpunkt.

### Änderungen an der Website

- `HouseStory.tsx` erhält eine zusammenhängende Sequenzdarstellung im Canvas.
  Text, Navigation und Kontaktaktionen bleiben im HTML.
- Ein zentrales V3-Manifest beschreibt Kapitelgrenzen, Ruhepositionen,
  Bildzuordnung, Auflösungen und Poster. Blender-Export und Webplayer nutzen
  dieselbe Zeitbasis; Kapitel dürfen nicht unabhängig vom Bild umspringen.
- Der bestehende
  [GSAP ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
  liefert den normalisierten Fortschritt. Frame, Text und Markierungen werden
  aus demselben angezeigten Fortschritt abgeleitet.
- Framewechsel erfolgen über `requestAnimationFrame` und direkte Canvas-Ausgabe.
  React aktualisiert Kapitelwechsel, nicht jeden Animationsschritt.
- Erstes Poster sofort anzeigen; anschließend Frames um die aktuelle Position
  und in Scrollrichtung priorisiert laden. Bei einem Kapitelsprung den
  Zielzustand bevorzugen. Eine ausstehende alte Ladeantwort darf den aktuellen
  Zustand nicht überschreiben.
- Decodierte Bilder in einem begrenzten Cache halten und verworfene Ressourcen
  freigeben. Nicht sämtliche hochaufgelösten Frames gleichzeitig im Speicher
  halten. Bei Ladefehlern bleibt ein sinnvolles Kapitelposter sichtbar.
- Sechs Kapitel mit Sprungnavigation; normales Seitenscrolling bleibt erhalten.
  Startwert für den Storybereich: etwa 450–550 `svh` auf Desktop. Die Länge wird
  anhand von Lesbarkeit und Bedienung geprüft, nicht aus der Framezahl abgeleitet.
- Der Anschluss berücksichtigt `BASE_URL` und den vorhandenen GitHub-Pages-Pfad
  `/elektro-hubmann/`.

### Mobilgeräte und reduzierte Bewegung

Mobil wird eine eigene Kamera aus derselben Blender-Szene verwendet. Nur das
Desktopbild schmal zuzuschneiden würde Technik oder Dach verlieren. Texte
stehen außerhalb der Modellfläche, die Beschriftungen werden reduziert.

Als Startwert gelten 220–280 `svh` für die mobile Story und eine kleinere
Bildsequenz. Reicht die Lesbarkeit in niedrigen oder schmalen Viewports nicht,
werden die sechs Kapitel als normale Bild-Text-Abschnitte dargestellt.
Reduced Motion, deaktiviertes JavaScript und fehlgeschlagene Initialisierung
erhalten immer vollständige statische Kapitel mit erreichbaren Kontaktaktionen.
Auch ein Wechsel der Bewegungseinstellung während der Sitzung wird berücksichtigt.

Vorläufige Budgets für die Pilotmessung: erstes Hausposter höchstens 250 KB,
initiale Story-Medien höchstens 1 MB, vollständige Desktop-Sequenz höchstens
12 MB, mobile Sequenz höchstens 5 MB. Das sind Zielwerte, keine gemessenen
Ergebnisse. Bei Überschreitung zuerst Auflösung, Kompression und Frameauswahl
anpassen. Ladeverhalten und decodierten Speicher getrennt messen.

## 8. Umsetzung in sechs Phasen

| Phase | Arbeiten | Konkretes Ergebnis und Prüfkriterium |
| --- | --- | --- |
| 1. Grobmodell und Bewegung | Hausform, Kameras, Fassadengruppen, Dach, Technikraum und Platzhaltergeräte aufbauen. Den vollständigen Öffnungs- und Schließvorgang sofort animieren. | Editierbare `.blend`, sechs Kapitelansichten und kurze Vorschausequenz. Dach bleibt im Bild, Räume und Technik sind erkennbar, beide Scrollrichtungen funktionieren. |
| 2. Technische Machbarkeit im Browser | Grobe Frames in einen isolierten V3-Versuch einbinden; Scrollen, Laden, Mobilformat und Fassadenübergang testen. | Früher Nachweis, dass Komposition und Ausgabeweg funktionieren. Noch kein Austausch der bestehenden Startseiten-Story. |
| 3. Architektur und Technik | Öffnungen, Wandstärken, Raumanschlüsse, Verteilung, getrennte Leitungsnetze, Leuchten, PV und weitere Kapitelgeräte ausarbeiten. | Geschlossenes Haus, offener Schnitt, EG-/OG-Grundriss und Technikdetails sind widerspruchsfrei. Jedes Kapitel hat erkennbare Komponenten. |
| 4. Materialien und Erzählung | Wenige passende Möbel, Oberflächen, weiches Licht, Kapitelakzente und abgestimmte Bewegungsverläufe ergänzen. | Alle sechs Kapitel sind auch in tatsächlicher Website-Größe verständlich. Technik bleibt der visuelle Schwerpunkt. |
| 5. Finale Ausgabe und Integration | Nach stabiler Geometrie und Kamera vollständige Bilder ausgeben, optimieren, Manifest und Kapitelposter erzeugen, Player und statische Kapitel anschließen. | Desktop, Mobil und Reduced Motion erzählen dieselben Leistungen. Lade- und Speicherbudgets werden gemessen. |
| 6. Abnahme | Zwischenzustände, Rückwärtsscrollen, Kapitelsprünge, Tastatur, langsames Netz, Bildfehler und Größenwechsel prüfen. Fachliche Leistungsangaben abgleichen. | Dokumentierte QA, geprüfte editierbare Szene und lokal funktionierende V3-Story. Öffentliche Veröffentlichung bleibt ein eigener Schritt. |

Die Phasen sind fachliche Prüfpunkte. Normale Korrekturen erfolgen selbstständig;
Rücksprache ist nur für Änderungen an der vereinbarten Hausrichtung oder für
offene Leistungsangaben nötig. Die vollständige Sequenz wird erst nach stabilen
Modell-, Kamera- und Materialentscheidungen berechnet. Danach werden nur
betroffene Bereiche neu gerendert.

Eine belastbare Renderzeit wird nach den ersten repräsentativen Bildern aus
der tatsächlichen lokalen Laufzeit hochgerechnet. Vorher wird keine feste
Fertigstellungsdauer behauptet.

## 9. Geplante Dateien

```text
blender/house_v3.py                         Einstieg für Aufbau und selektive Ausgabe
blender/house_v3/                           Geometrie, Systeme, Materialien, Rig, Export
assets/3d/elektro-hubmann-house-v3.blend     editierbare Hauptszene
docs/version-g-qa/blender-v3/               Kapitelbilder, Grundrisse, Übergänge und QA
public/images/version-g/house-v3/           optimierte Desktop-/Mobilframes und Poster
src/config/house-v3-manifest.json            gemeinsamer Exportvertrag für die Web-Story
```

Diese Dateien sind Zielpfade und noch nicht implementiert. Der Aufbaubefehl
soll standardmäßig nur die Szene speichern. Einzelbilder, ausgewählte
Framebereiche und finale Ausgaben werden ausdrücklich angefordert. Manuelle
Blender-Anpassungen müssen in der reproduzierbaren Quelle oder als eingebundene
Assets gesichert werden, bevor ein Neuaufbau erfolgt.

## 10. Abnahmekriterien

- Ein und dasselbe Haus ist vom geschlossenen Einstieg über den offenen Schnitt
  bis zum Abschluss wiederzuerkennen.
- Dach, PV, Fassaden, Fenster und Türen bewegen oder blenden sich als
  zusammengehörige Bauteile. Es gibt keine Kollisionen oder verlorenen Einzelteile.
- Stromverteilung, Datenvernetzung und PV-Anschluss sind räumlich schlüssig und
  werden nicht zu einem fachlich irreführenden gemeinsamen Leitungssystem vermischt.
- Installation, Licht, Smart Home, Sicherheit und PV sind nacheinander klar
  erkennbar. Speicher und Wallbox erscheinen als Leistungsangebot erst nach
  Bestätigung; die PV-Story ist nicht von ihnen abhängig.
- Zwischenbilder an jedem Kapitelübergang werden ebenso geprüft wie die
  repräsentativen Standbilder. Ausblendungen erzeugen keine Geisterwände,
  zurückbleibenden Fenster, flackernden Schatten oder sichtbare Materialsprünge.
- Vorwärts- und Rückwärtsscrollen sowie direkte Sprünge liefern denselben Zustand.
  Fehlende Frames erzeugen weder eine leere Bildfläche noch unpassende Kapiteltexte.
- Desktop und Mobil zeigen vollständige Kompositionen; Dach, Technik und
  Beschriftungen bleiben bei 390, 768, 1024 und 1440 Pixel Breite nutzbar.
  Zusätzlich wird ein niedriger beziehungsweise querformatiger Viewport geprüft.
- Ohne Animation bleiben sämtliche Kapitel, Leistungsinformationen und
  Kontaktwege verfügbar. Inaktive Aktionen sind nicht per Tastatur fokussierbar.
- Die Website wird mit gezielten Player-Tests für Kapitel-/Framezuordnung,
  Rückwärtssprünge und Ladefehler geprüft. Bestehende Tests für das Überblenden
  getrennter Motive werden entsprechend der neuen Funktion ersetzt.
- Formatprüfung, Linting, Typecheck, Tests und Produktionsbuild laufen nach der
  Web-Integration erfolgreich. Die Blender-Szene lässt sich erneut öffnen und
  aus der dokumentierten Quelle reproduzieren.

**Erster konkreter Umsetzungsschritt:** V3 als grobes Blender-Haus mit bereits
animiertem Dach und ausblendbaren Fassaden aufbauen. Daran werden die sechs
Kapitelansichten und ein kurzer Scrollversuch geprüft, bevor die Detailarbeit
beginnt.
