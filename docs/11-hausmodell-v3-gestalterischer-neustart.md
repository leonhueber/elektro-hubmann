# Hausmodell V3 – gestalterischer Neustart

Stand: 5. September 2026

Status: Der erweiterte R3-Entwurf wurde vom Nutzer zur Modellierung ausgewählt
und als neue native Blender-Szene aufgebaut. Dieser Plan ersetzt die
gestalterischen Vorgaben und die Arbeitsreihenfolge aus Dokument 10.

Modell: [elektro-hubmann-house-v3-r3.blend](../assets/3d/elektro-hubmann-house-v3-r3.blend).
[Bedienung und Modellumfang](../blender/house_r3/README.md),
[gerenderte Ansichten](version-g-qa/blender-v3-r3/README.md).

Die [Grundrisskorrektur R3](mockups/house-v3-r3/index.html) zeigt ein vollständiges
Raumprogramm und eine neue offene Frontendansicht. Die vorherige
[Mockup-Galerie R2](mockups/house-v3-r2/index.html) enthält acht Desktopzustände
und zwei mobile Beispiele, aber kein vollständiges Wohnhaus: Schlafzimmer,
Bad und schlüssige Raumzugänge fehlten. Ihre Raumaufteilung ist überholt.
Die Mockup-Galerien enthalten Bildentwürfe. Die neue R3-Szene und ihre echten
Renderings liegen separat. Die [erste R3-Website-Animation](12-haus-r3-website-animation.md)
verwendet eine separate Animationsdatei und ersetzt die ältere Bildfolge im lokalen Player.

## 1. Befund und Ziel

Geprüft wurden die geschlossene Ansicht, der offene Installationszustand und
das [Storyboard des ersten V3-Modells](version-g-qa/blender-v3/storyboard.jpg).

- Gleichartige große Fenster und durchlaufende Geschossbänder erzeugen die
  Anmutung eines kleinen Bürogebäudes. Eingang und Wohnnutzung sind zu schwach.
- Das Obergeschoss verdeckt Teile des Erdgeschosses. Dach, Deckenränder und
  Stützen beanspruchen viel Bildfläche in jedem Leistungskapitel.
- Möbel, Geräte und Leitungen haben keine ausreichend klare Gewichtung.
  Verteilung und Netzwerkschrank wirken in den Wohnbereich hineingestellt.
- Die Kapitelbilder unterscheiden sich zu wenig. Insbesondere Licht,
  Smart Home und Sicherheit sind auf den ersten Blick kaum unterscheidbar.
- Helle Materialien und breite Reflexe schwächen die Form. Mehr Details oder
  höhere Renderqualität allein beheben die Probleme nicht.

Ziel ist ein eigenständig gestaltetes Wohnhaus mit der Ruhe einer sorgfältigen
Architekturvisualisierung. Das geschlossene Haus muss als Einzelbild überzeugen.
Das geöffnete Haus muss verständliche Räume und klar platzierte Technik zeigen.
Beide Zustände bestimmen den Entwurf von Anfang an.

## 2. Empfohlene Hausrichtung

**Ein kompakter, eingeschossiger Wohnpavillon mit flachem Dach.** Die Hausform
wurde mit dem Auftrag zur Umsetzung des erweiterten R3-Mockups ausgewählt.

Ein Geschoss gibt den Blick auf Installation, Licht und Steuerung frei. Die
Kamera muss keine Decke umgehen; die Technik kann im Bild größer werden.
Der Nachteil ist eine geringere Gebäudehöhe und damit eine andere Silhouette
als beim bisherigen Familienhaus. Ein kompakter Grundriss verhindert, dass das
Modell auf dem Handy zu einem schmalen horizontalen Streifen wird.

### Architektur

- Ausgangsgröße ungefähr 12,0 × 11,4 m für das vollständige Raumprogramm,
  ein Hauptvolumen, mittiger Eingang und Terrassenanschluss am Wohnbereich.
  Die frühere Größe von 9,5 × 8,5 m wird verworfen. Maße sind Entwurfswerte.
- Flaches Dach mit sauberer Attika und einer ruhigen, dünn lesbaren Dachkante.
  Das PV-Feld erhält einen klaren Platz und Abstand zum Dachrand.
- Eine größere Verglasung für Wohnen und Essen; kleinere, gezielt gesetzte
  Öffnungen für Nebenräume. Fenstergrößen ergeben sich aus den Räumen.
- Heller mineralischer Baukörper, zurückgesetzte dunkle Rahmen, warmer
  Holzakzent am Eingang. Wandstärken, Leibungen und Anschlüsse bleiben sichtbar.
- Schmale Bodenplatte mit weichem Kontaktschatten. Wenige Außenflächen genügen,
  um Eingang und Wohnen verständlich zu machen.

### Innenraum und Technik

- Wohnen, Essen und Küche liegen links vorne. Dahinter befindet sich das
  Elternschlafzimmer mit Doppelbett und Schrankzone.
- Rechts folgen vom Eingang zur Rückseite Hauswirtschaft/Technik, Bad mit WC,
  Kinderzimmer sowie Büro/Gästezimmer. Bad und Hauswirtschaft teilen eine
  Installationswand. Verteilung und Netzwerk gehören in den Technikraum.
- Ein durchgehender Flur mit ungefähr 1,30 m lichter Breite erschließt jeden
  Raum direkt. Türen, Schwenkbereiche und freie Laufwege werden vor der
  Möblierung geprüft. Jeder Aufenthaltsraum bekommt ein Außenfenster.
- Eine feste Funktionswand trägt Taster, Innenstation und Installationswege.
  Sie bleibt beim Öffnen stehen. Ein festes Fenster zeigt die Beschattung.
- Schlafzimmer, Kinderzimmer und Bad werden vollständig angelegt. Doppelbett,
  Einzelbett, Schränke, Dusche, WC und Waschtisch machen die Nutzung erkennbar.
  Büro/Gast erhält Arbeitsplatz und Schlafsofa. Private Räume werden auch in
  den Leistungskapiteln weder entfernt noch zu einer offenen Halle zusammengelegt.
- Einrichtung bleibt zurückhaltend und bekommt weniger Kontrast als das
  jeweils aktive System. Niedrige Schnittwände erhalten die Raumgrenzen.
- Elektro- und Datenwege bleiben unterscheidbar. Im Installationskapitel
  erscheinen ein Hauptweg und wenige nachvollziehbare Anschlüsse. Die Linien
  bleiben schematische Erklärung, keine ausführungsreife Leitungsplanung.

Die [R3-Modellvorgaben](mockups/house-v3-r3/README.md) enthalten Raumflächen,
lichte Maße und die geometrische Aufteilung. Die geplanten Raumflächen ergeben
zusammen ungefähr 117 m²; dies ist keine normativ ermittelte Wohnfläche.

## 3. Bildgestaltung

- Architektur überwiegend in warmem Weiß und hellen neutralen Tönen.
  Dunkle Rahmen und Technik schaffen gezielte Kontraste; Holz bleibt Akzent.
- Dezente Materialstruktur, maßstäbliche Kanten und erkennbare Wandtiefe.
  Glas erhält kontrollierte Transparenz und Reflexion; PV bleibt dunkel lesbar.
- Eine große weiche Hauptlichtquelle und zurückhaltende Aufhellung modellieren
  das Volumen. Schatten müssen Wand, Boden und Gerät voneinander trennen.
- Hubmann-Rot markiert die gerade erklärte Verbindung oder Komponente.
  Inaktive Systeme treten zurück. Beleuchtung zeigt ihre Wirkung auf realen
  Oberflächen mit warmem Licht.
- Ausgangskamera in ruhiger Dreiviertelansicht mit leichter Perspektive.
  Die offene Gesamtansicht wird deutlich steiler, damit auch Schlafräume und
  Bad lesbar bleiben. Es folgen nähere Einstellungen für einzelne Geräte.
  Keine vollständige Umrundung.
- Kleine Geräte bekommen eine geplante Annäherung der Kamera. Ein Verteiler
  oder Wandtaster muss nicht aus einer unveränderten Gesamtansicht erklärt werden.
- Maximal ein zentraler visueller Fokus und zwei kurze Beschriftungen pro Bild;
  mobil eine Beschriftung. Labels ergänzen erkennbare Objekte.

## 4. Öffnung und Leistungsfolge

Das Dach muss während der Innenraumkapitel keine Bildfläche beanspruchen.
Es hebt sich sichtbar ab und blendet anschließend aus. Die kameranahen Fassaden
gehen in einem kurzen, abgestimmten Übergang einschließlich ihrer Fenster
und Türen in einen niedrigen Schnitt über. Verdeckende Innenwände werden ebenfalls
auf ungefähr 0,85–1,10 m reduziert; Zimmergrenzen und Türöffnungen bleiben lesbar.
Feste Funktionswände und ihre Geräte behalten einen sichtbaren Halt.
Zur PV-Erklärung kehrt das Dach an seinen Sitz zurück.

| Abschnitt | Bild und Bewegung | Erkennbarer Schwerpunkt |
| --- | --- | --- |
| Haus / Planung | Geschlossenes Haus, ruhiges Tageslicht, klarer Eingang. | Architektur und Zusammenhang des Projekts. |
| Öffnen / Installation | Dach hebt sich und verschwindet; vordere Hülle öffnet sich. Kamera nähert sich der Technikzone. | Verteilung und wenige nachvollziehbare Leitungswege. |
| Beleuchtung | Leitungsakzente treten zurück. Ein etwas weiterer Blick zeigt den Wohnbereich. Licht verändert sichtbar Tisch, Wand und Raum. | Die Lichtwirkung statt ausschließlich leuchtender Lampenkörper. |
| Smart Home | Fokus auf festes Bedienelement und das zugehörige Fenster. Beschattung bewegt sich, eine Lichtszene verändert den Raum. | Bedienung und unmittelbar erkennbare Wirkung. |
| Sicherheit | Ruhige Annäherung an den Eingangsbereich mit Türstation und einer passenden Sensorik. | Ein konkreter Anwendungsfall; weitere Leistungen können im Text stehen. |
| Photovoltaik | Kamera kehrt zur Hausansicht zurück, Dach sitzt wieder auf. PV-Feld und Verbindung zum Wechselrichter werden lesbar. | Erzeugung und Anschluss an das Haus. |
| Abschluss | Fassade schließt, Haus bleibt mit zurückhaltender Beleuchtung stehen. | Das zusammenhängende Ergebnis. |

Die Übergänge folgen dem Scrollfortschritt und funktionieren rückwärts.
Jedes Kapitel hat einen ruhigen Zustand zum Lesen. Kameras und Kapitelzeiten
werden erst nach den überzeugenden Einzelbildern festgelegt. Speicher und
Wallbox bleiben bis zur Klärung des Angebots optionale Komponenten.

## 5. Vorgehen in Blender

1. **Neue Szene und vollständiger Grundriss.** Kein Import der alten Hausgeometrie,
   Raumaufteilung, Möbel oder Materialien. Die R3-Maßaufteilung mit allen sechs
   Räumen und Flur aufbauen. In der Draufsicht Türöffnungen, Schwenkbereiche,
   Möbeltiefen, Sanitäranordnung, Fenster und Wartungsraum an Geräten prüfen.
   Erst danach Baukörper und Dach geschlossen und geöffnet darstellen.
2. **Eine Variante gestalterisch ausarbeiten.** Fassadenrhythmus, Öffnungen,
   Wandtiefe, Dachkante und Grundriss im Blender-Viewport kontrollieren.
   Gegenprobe in Front-, Seiten- und Draufsicht sowie mit der Website-Kamera.
   Danach Materialien und Beleuchtung an drei Einzelbildern entwickeln.
3. **Drei belastbare Ansichten zur Gestaltungskontrolle.** Geschlossenes Haus,
   offener Technikblick und Lichtszene aus derselben editierbaren Szene.
   Jeweils in Desktopgröße und ungefähr 350 px Darstellungsbreite prüfen.
   Diese Bilder sind der nächste wesentliche Liefergegenstand.
4. **Systeme und Bewegung ergänzen.** Bauteile gezielt ausarbeiten, Kameras
   abstimmen und einen kurzen Test der Öffnung sowie der schwierigsten
   Übergänge rendern. Auch Zwischenbilder und Rückwärtsbewegung prüfen.
5. **Web-Ausgabe anschließen.** Erst nach der gemeinsamen Beurteilung der
   drei Ansichten und einem überzeugenden Bewegungstest die gesamte Sequenz
   rendern. Bestehenden Player weiterverwenden; neue Bilder, Kameraprojektionen
   und Kapitelzuordnung daran anpassen.

Blender wird für Gestaltung und visuelle Kontrolle direkt bedient, sofern der
App-Zugriff verfügbar ist. Skripte unterstützen wiederholte Bauteile, konsistente
Benennung, Exporte und Prüfungen. Die visuell bearbeitete `.blend` ist danach
die maßgebliche Modellquelle; ein Generator darf diese Änderungen nicht durch
einen vollständigen Neuaufbau überschreiben. Revisionen werden separat gesichert.

Der direkte Öffnungsversuch am 5. September endete mit
`Computer Use app approval timed out`; ein Blender-Fenster stand dabei nicht
zur Verfügung. Die jetzige Bewertung beruht auf den gespeicherten Renderbildern.

## 6. Kriterien für die nächste Modellrunde

- Die geschlossene Ansicht wirkt als Wohnhaus: erkennbarer Eingang,
  differenzierte Öffnungen und nachvollziehbare Proportionen.
- Elternschlafzimmer, Kinderzimmer, Büro/Gast, Bad mit WC, Hauswirtschaft und
  Wohnküche sind eingerichtet und direkt vom Flur erreichbar. Die offene
  Ansicht erhält diese Raumaufteilung sichtbar in jedem Leistungskapitel.
- Die offene Ansicht besitzt eine klare Blickführung. Technik ist räumlich
  zugeordnet und wird von Dach, Stützen oder Einrichtung nicht verdeckt.
- Licht-, Smart-Home- und Sicherheitsbild unterscheiden sich bereits ohne
  Kapitelüberschrift durch Fokus oder sichtbare Wirkung.
- Bei etwa 350 px Bildbreite bleibt der jeweilige Hauptgegenstand erkennbar;
  nötige Details bekommen eine nähere Einstellung.
- Kein dekoratives Detail wird ergänzt, solange Hausform, Schnittansicht,
  Lichtführung oder Materialkontrast unbefriedigend sind.
- Die Beurteilung der drei Ansichten erfolgt vor der vollständigen
  Animationsproduktion. Technisch bestandene Prüfungen ersetzen sie nicht.

Die erste V3-Szene und ihre Exporte bleiben als Zwischenstand erhalten.
Die neue R3-Szene enthält den vollständigen Grundriss, Einrichtung, Technik
und native Keyframes. Nach der Beurteilung der Renderings können die Kameras
und Bewegungszeiten für die Website abgestimmt und die Bildfolge exportiert werden.
