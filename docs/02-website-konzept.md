# Website-Konzept für Elektro Hubmann

Stand: 29. August 2026

## 1. Leitidee

**Elektro Hubmann wird als erfahrener, persönlich erreichbarer Fachbetrieb für
Elektrotechnik im Gitschtal positioniert – schnell im Störungsfall, verlässlich
bei Projekten und nahbar im Fachgeschäft.**

Die neue Website soll nicht wie ein beliebiger Technik- oder Baukasten-Auftritt
wirken. Sie soll in wenigen Sekunden drei Fragen beantworten:

1. Kann Elektro Hubmann mein Problem lösen?
2. Ist der Betrieb in meiner Region tätig und vertrauenswürdig?
3. Wie erreiche ich jetzt die richtige Person?

## 2. Ziele und messbare Ergebnisse

### Primäre Ziele

- mehr qualifizierte Telefon- und Projektanfragen;
- schnell erreichbarer Störungsdienst auf Mobilgeräten;
- mehr Orientierung für Besucher des Geschäfts in Weißbriach;
- bessere lokale Auffindbarkeit für tatsächlich angebotene Leistungen;
- professioneller, langfristig pflegbarer Markenauftritt.

### Empfohlene Kennzahlen

- Klicks auf Störungsnummer, Festnetz, E-Mail und Anfahrt;
- abgesendete qualifizierte Projektanfragen;
- organische Zugriffe auf Leistungsseiten;
- Suchanfragen und Sichtbarkeit in der Zielregion;
- Core Web Vitals und Fehlerquote nach Launch;
- keine ungeklärten 404, keine verlorenen E-Mails und keine ungeplanten
  Ausfallzeiten beim Cutover.

Analytics wird nur eingesetzt, wenn ein klarer Nutzen besteht und die
Datenschutz-/Consent-Konfiguration korrekt umgesetzt wird. Server- und
Conversiondaten mit möglichst wenig personenbezogenen Informationen sind zu
bevorzugen.

## 3. Zielgruppen und Nutzerwege

| Zielgruppe | Hauptbedarf | Primäre Aktion |
|---|---|---|
| Privatkund:innen und Eigentümer:innen | Installation, Sanierung, PV, Beleuchtung, Störung | Leistung prüfen, anrufen oder Projekt anfragen |
| Gewerbe, Bau, Hausverwaltung, Gemeinde | Planung, Ausführung, Prüfung, Wartung | qualifizierte Projektanfrage |
| Menschen mit akutem Problem | schnelle Erreichbarkeit und klare Zuständigkeit | Störungsnummer anrufen |
| Kund:innen des Fachhandels | Öffnungszeiten, Sortiment, Bestellung, Anfahrt | Geschäft besuchen oder anrufen |
| potenzielle Mitarbeitende | Betrieb, Arbeitsweise, offene Stellen | optional Karriere/Initiativkontakt |

Eine Karriereseite wird nur gebaut, wenn tatsächlich eingestellt wird oder eine
Initiativbewerbung gewünscht ist. Eine leere oder dauerhaft veraltete
Karriereseite wäre kontraproduktiv.

## 4. Empfohlene Informationsarchitektur

```text
/
├── leistungen/
│   ├── installation-planung/
│   ├── photovoltaik-energie/
│   ├── pruefung-service-stoerung/
│   ├── sicherheit-blitzschutz-brand-alarm/
│   ├── netzwerk-sat-smart-home/
│   └── beleuchtung-heizung-klima/
├── fachhandel/
├── projekte/
├── unternehmen/
├── kontakt/
├── karriere/                 (optional, nur mit echtem Inhalt)
├── impressum/
└── datenschutz/
```

Die sechs Leistungscluster sind ein Startvorschlag. Vor Umsetzung werden sie
mit dem tatsächlichen Umsatz-/Anfragefokus und den vorhandenen Berechtigungen
abgeglichen. Nicht jede einzelne Leistung braucht eine dünne SEO-Seite.

„Aktuelles“ wird nur ergänzt, wenn eine verantwortliche Person und ein realistischer
Pflegeprozess feststehen. Ansonsten sind zeitlose Projekte/Referenzen glaubwürdiger.

## 5. Seitenkonzept

### 5.1 Startseite

1. **Kompakter Header:** Logo, Leistungen, Fachhandel, Projekte, Unternehmen,
   Kontakt; mobile Menüschaltfläche korrekt beschriftet.
2. **Hero ohne Slider:** klare H1, Region, Nutzenversprechen, echtes Motiv.
3. **Drei sofortige Wege:** „Störung anrufen“, „Projekt anfragen“, „Zum
   Fachgeschäft“.
4. **Leistungsübersicht:** sechs Cluster mit je einem klaren Nutzen und Link.
5. **Vertrauensbelege:** seit 1972, über 50 Jahre Erfahrung, regionale
   Erreichbarkeit, Qualifikationen/Zertifizierungen – nur belegbare Angaben.
6. **Ausgewählte Projekte:** 3 echte, kurze Referenzen mit Ausgangslage,
   Leistung und Ergebnis.
7. **Unternehmen/Ansprechperson:** persönlicher, lokaler Betrieb statt
   anonymer Anbieter.
8. **Fachgeschäft:** Sortiment, aktuelle Öffnungszeiten, Anfahrt.
9. **Kontaktabschluss:** Telefon, E-Mail, Anfrage und Adresse; kein unklarer
   allgemeiner CTA.

Beispiel für die inhaltliche Richtung der H1, noch nicht als finaler Werbetext:

> Elektrotechnik aus Weißbriach – persönlich geplant, sauber umgesetzt.

Subline:

> Elektroinstallationen, Service, Photovoltaik und Fachhandel für das Gitschtal,
> Hermagor und den Weißensee.

Die Behauptung zu Einsatzgebiet und Leistungsumfang muss vor Veröffentlichung
bestätigt werden.

### 5.2 Leistungen

Die Übersichtsseite erklärt die Leistungscluster und führt gezielt zu
Detailseiten. Jede Detailseite folgt demselben belastbaren Muster:

1. Problem/Nutzen in klarer H1;
2. typische Aufgaben und für wen die Leistung gedacht ist;
3. konkreter Leistungsumfang und bewusste Abgrenzung;
4. Ablauf von Erstkontakt bis Abschluss;
5. echtes Projekt oder Foto;
6. relevante Qualifikation/Hersteller nur mit Beleg;
7. regionaler Bezug;
8. passender CTA: Beratung, Projektanfrage oder Störungsanruf;
9. kurze, echte FAQ.

### 5.3 Fachhandel

- aktuelle Öffnungszeiten einschließlich Nachmittagsregelung;
- Adresse, Park-/Zufahrtsinformation und datenschutzfreundliche Karte;
- Sortimentsgruppen und Marken nur bei aktueller Verfügbarkeit;
- klare Aussage: lagernd, bestellbar, Beratung vor Ort;
- direkte Telefonaktion für Produktanfragen;
- aktuelle Fotos des Geschäfts.

### 5.4 Projekte

Projektkarten statt veralteter News. Pro Projekt:

- Ausgangslage und Kundentyp, ohne vertrauliche Daten;
- erbrachte Leistungen;
- Region/Ort nur mit Freigabe;
- Ergebnis und Besonderheiten;
- 3–6 hochwertige, rechtlich freigegebene Bilder;
- optional Kundenstimme mit dokumentierter Zustimmung.

### 5.5 Unternehmen

- Geschichte 1972 bis heute;
- Inhaber und Team;
- Arbeitsweise und Werte in konkreten Aussagen;
- Qualifikationen, Gewerbeberechtigungen, Partner und Zertifikate;
- Einsatzgebiet;
- optional Karriereblock;
- CTA zur passenden Kontaktart.

### 5.6 Kontakt

Kontakt wird eine eigene Seite, nicht nur ein Startseitenanker:

- Störung: Mobilnummer, Erreichbarkeits-/Leistungsgrenzen klar angeben;
- Projekt: kurzes, datensparsames Formular oder Rückrufweg;
- Fachgeschäft: Festnetz, Öffnungszeiten, Adresse und Route;
- E-Mail: sichtbare Antworterwartung nur nennen, wenn sie eingehalten wird;
- keine sensiblen Details im Freitext anfordern;
- verständliche Fehler-, Erfolgs- und Datenschutzhinweise.

## 6. Marken- und Designsystem

### Gestaltungsprinzipien

- ruhig, präzise, handwerklich und persönlich;
- starke Hierarchie statt Slider, Effekten und langen Leerflächen;
- reale Arbeit statt generischer Stockfotografie;
- ausreichend große Schrift und klare Kontraste;
- mobile Nutzung zuerst, weil Störungs- und Kontaktanfragen häufig mobil starten;
- wenige wiederverwendbare Komponenten statt individueller Seitentricks.

### Verifizierte Logofarben

Die Original-Logo-PNG enthält als Hauptfarben:

| Token | Wert | Verwendung |
|---|---:|---|
| Hubmann Rot | `#E30613` | primäre CTA, aktive Zustände, markante Linien |
| Anthrazit | `#1D1D1B` | Text, Header, dunkle Flächen |
| Signalgelb | `#FFED00` | sehr sparsame Akzente, nie als heller Text auf Weiß |
| Weiß | `#FFFFFF` | Grundfläche und Text auf dunklen Flächen |

`#E30613` erreicht auf Weiß ungefähr 4,88:1 und damit WCAG-AA für normalen
Text. Trotzdem wird Rot primär für Buttons, Icons und kurze Akzente genutzt;
lange Texte bleiben anthrazit. Gelb wird nur mit dunklem Text kombiniert.

### Typografie und Layout

- eine selbst gehostete Sans-Serif-Familie, bevorzugt **Inter**, in 400/600/700;
- Fließtext mindestens 16 px, bevorzugt 18 px bei längeren Inhalten;
- klare H1–H3-Hierarchie ohne visuelle Überschriftenattrappen;
- Inhalt maximal ca. 1.200 px breit, Textzeilen 60–75 Zeichen;
- 8-px-Abstandssystem, konsistente 8-px-Ecken, sichtbare Fokusrahmen;
- Buttons mindestens 44 × 44 px große Trefferfläche;
- Animationen sparsam und unter `prefers-reduced-motion` deaktivierbar.

### Kernkomponenten

- Header und zugängliche Mobile Navigation;
- Notfall-/Störungsleiste;
- Hero mit statischem Bild und zwei klaren Aktionen;
- Leistungs- und Projektkarten;
- Vertrauenskennzahlen;
- Öffnungszeitenblock;
- Ansprechpartnerblock;
- datensparsames Anfrageformular;
- Karte erst nach Zustimmung oder zunächst statischer Link;
- kompakter Footer mit NAP, Öffnungszeiten und Rechtstexten.

## 7. Bildkonzept und benötigtes Shooting

Vor dem Design-Freeze sollte ein kompaktes professionelles Shooting geplant
werden. Benötigt werden:

- Inhaber und Team, einzeln und bei echter Arbeit;
- Firmengebäude/Fachgeschäft außen und innen;
- Fahrzeug/Markenauftritt;
- Installations-, Prüf-, PV-, Netzwerk- und Service-Situationen;
- 3–5 abgeschlossene Projekte;
- Querformat für Hero und 4:3/1:1 für Karten;
- dokumentierte Nutzungsrechte und Einwilligungen.

Alte Bilder werden nur weiterverwendet, wenn sie aktuell, ausreichend groß und
rechtlich freigegeben sind. Das Original-Logo sollte zusätzlich als saubere
Vektor- oder hochauflösende Masterdatei beschafft werden.

## 8. SEO- und lokale Sichtbarkeitsstrategie

1. Jede Seite erhält genau ein klares Hauptthema, eine H1, einen individuellen
   Title und eine individuelle Description.
2. NAP-Daten (Name, Adresse, Telefon) werden auf Website, WKO, Google
   Unternehmensprofil und relevanten Verzeichnissen identisch gehalten.
3. `LocalBusiness`/passenderer Schema.org-Typ, `Service`, `BreadcrumbList` und
   echte Projekte werden strukturiert ausgezeichnet.
4. Ein Open-Graph-Bild, Favicon-Set und Social-Metadaten werden gepflegt.
5. Alte URLs erhalten eine explizite 301-Zuordnung; keine pauschale Umleitung
   aller Seiten auf die Startseite.
6. XML-Sitemap, robots.txt, Canonicals und Google Search Console werden geprüft.
7. Alte News werden nur übernommen, wenn Inhalt/Produkte weiterhin aktuell
   sind; andernfalls 301 auf die fachlich passendste Seite oder kontrolliert 410.
8. Keine künstlich aufgeblähten Ortsseiten. Regionale Seiten nur mit eigenem,
   hilfreichem Inhalt und tatsächlicher Leistungserbringung.

## 9. Technische Empfehlung

### Festgelegte Zielrichtung: Astro und TypeScript

Für den aktuellen Umfang ist eine mit **Astro** statisch generierte Website und
**TypeScript im Strict-Modus** die robusteste Basis:

- sehr wenig Angriffs- und Wartungsfläche;
- schnelle Ladezeiten und einfache Cache-Verteilung;
- versionierte Änderungen und reproduzierbare Deployments;
- Inhalte als Markdown/strukturierte Daten;
- kein öffentliches WordPress-Backend.

Die UI wird primär mit Astro-Komponenten und nativem CSS umgesetzt. React oder
ein anderes Client-Framework wird nicht global eingebunden. Interaktive
JavaScript-Inseln werden nur verwendet, wenn eine Funktion sie tatsächlich
benötigt. Inhalte liegen typisiert in Astro Content Collections und
Markdown/MDX. Der vollständige, verbindliche Technologieentscheid ist in
[Technologie und Architektur](06-technologie-architektur.md) dokumentiert.

Wenn der Betrieb Inhalte regelmäßig selbst ohne Git pflegen muss, wird vor
Baubeginn entweder ein kleines Headless-CMS ergänzt oder WordPress bewusst als
Alternative gewählt. WordPress ist nur sinnvoll, wenn redaktionelle
Selbstverwaltung den zusätzlichen Patch-, Backup- und Sicherheitsaufwand
wirklich rechtfertigt.

### Nicht an einen Komplettprovider koppeln

Die Architektur bleibt portabel:

- Domain beim Registrar;
- DNS separat und exportierbar;
- Website auf managed Hosting/CDN;
- E-Mail bei einem spezialisierten Mailanbieter;
- Quellcode und Assets im eigenen Repository;
- Zugang und Abrechnung im Namen des Unternehmens.

Damit kann später ein Teil gewechselt werden, ohne alle anderen Dienste zu
gefährden.
