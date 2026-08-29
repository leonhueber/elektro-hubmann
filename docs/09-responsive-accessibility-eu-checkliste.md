# Responsiveness, Barrierefreiheit und EU-/AT-Launch-Checkliste

Stand: 29. August 2026  
Status: Responsiveness im Designprototyp umgesetzt; Barrierefreiheit und
Rechts-/Datenschutzumsetzung für das finale Design vorgemerkt

## 1. Klare Abgrenzung

In der aktuellen Iteration wurde ausschließlich die responsive Darstellung der
fünf Designvarianten umgesetzt. Die vorhandenen rechtlichen Seiten, Texte und
das Anfrageformular sind weiterhin Entwürfe und dürfen nicht als fachlich oder
rechtlich freigegeben verstanden werden.

Diese Checkliste ist eine technische Planungsgrundlage, keine Rechtsberatung.
Welche Pflichten tatsächlich greifen, hängt insbesondere von Rechtsform,
Unternehmensgröße, Zielgruppen, eingesetzten Diensten und davon ab, ob online
Verträge abgeschlossen oder Termine verbindlich gebucht werden können.

| Bereich | Aktueller Status | Zeitpunkt der Umsetzung |
|---|---|---|
| Responsiveness A–E | umgesetzt und lokal geprüft | jetzt |
| Accessibility/WCAG | Ziel und Prüfumfang definiert | nach Auswahl des finalen Designs |
| Impressum/Offenlegung | Altbestand als ungeeignet erkannt | vor Produktionslaunch |
| Datenschutz/Consent | Datenflussprüfung ausständig | vor Aktivierung von Formularen oder Drittanbietern |
| BaFG-Anwendbarkeit | fachlich/rechtlich zu klären | vor Freigabe des Funktionsumfangs |
| Produktionshosting | noch nicht freigegeben | vor Domain-Cutover |

## 2. Umgesetzte Responsiveness

Die gemeinsame responsive Basis gilt für Version A bis E:

- eigenständige Mobile-Navigation bis einschließlich 820 px;
- Desktop-Navigation ab 821 px;
- kompakte Versionsleiste bis 700 px, ohne abgeschnittene Varianten;
- verkürzte Header-Aktion und kleinere Logos auf schmalen Smartphones;
- responsive Hero-, Trust-, Leistungs-, Projekt-, Unternehmens-, Formular-
  und Footer-Layouts;
- einspaltiges Formular und einspaltige Projektkarten auf Smartphones;
- zwei Leistungsspalten auf Smartphones, variantenabhängig zwei oder drei auf
  Tablets und größere Raster auf Desktop;
- umbrechende Aktionsgruppen, skalierende Typografie und kontrollierte
  Bildausschnitte;
- kein horizontaler Seitenüberlauf in der geprüften Matrix;
- mobiles Menü schließt nach Auswahl eines Sprungziels und nach Klick außerhalb.

### Geprüfte Matrix

Am 29. August 2026 wurden alle fünf Varianten bei folgenden sichtbaren
Layoutbreiten geprüft:

| Breiten | Versionen | Ergebnis |
|---|---|---|
| 320, 360 und 390 px | A–E | kein horizontaler Überlauf; Mobile-Menü und Kernlayouts nutzbar |
| 620, 621 und 685 px | A–E | Versionsleiste und Header wechseln ohne Zwischenbereichsfehler |
| 768, 805 und 820 px | A–E | Tablet-Raster und Mobile-Navigation stabil |
| 900 und 1024 px | A–E | Desktop-Navigation und Zwischenraster stabil |
| 1280 und 1440 px | A–E | Desktop-Layout ohne Überlauf |

Zusätzlich wurden in A–E die vier Mobile-Menüziele geöffnet und der Sprung zu
`#projekte` geprüft. Der Astro-Typecheck und Produktionsbuild laufen ohne
Diagnosen durch.

### Erneut zu prüfen, sobald das finale Design gewählt ist

- reale iOS-/Safari- und Android-/Chrome-Geräte;
- Querformat und sehr niedrige Viewports;
- 200 % Zoom, 320-px-Reflow und vergrößerte Systemschrift;
- lange reale Projekt-, Leistungs- und Fehlermeldungstexte;
- Bilder mit den finalen Seitenverhältnissen;
- Formularzustände mit echten Validierungs- und Uploadmeldungen;
- langsames Mobilnetz und Core Web Vitals.

## 3. Accessibility-Arbeitspaket für das finale Design

WCAG 2.2 AA bleibt das verbindliche technische Qualitätsziel – unabhängig
davon, ob im Einzelfall eine gesetzliche Ausnahme greift. Zu prüfen und
umzusetzen sind mindestens:

- vollständige Bedienung per Tastatur, logisch sichtbarer Fokus und sinnvolle
  Fokusreihenfolge;
- korrekte Landmarken, Überschriftenhierarchie, Link- und Button-Semantik;
- ausreichende Kontraste in Normal-, Hover-, Fokus-, Fehler- und
  Deaktiviert-Zuständen;
- Reflow ohne Informationsverlust, Textabstände, Zoom und ausreichend große
  Touch-Ziele;
- aussagekräftige Alternativtexte; dekorative Bilder bleiben für assistive
  Technik stumm;
- reduzierte Bewegung entsprechend `prefers-reduced-motion`;
- verständliche Formularlabels, Pflichtfeldhinweise, Fehlermeldungen,
  Fehlerzusammenfassung und Erfolgsbestätigung;
- Statusmeldungen für Screenreader und keine ausschließlich farbliche
  Bedeutung;
- manuelle Prüfung mit Tastatur und Screenreader zusätzlich zu automatisierten
  Axe-/Playwright-Tests.

Das österreichische BaFG gilt seit 28. Juni 2025 für die im Gesetz genannten
B2C-Produkte und -Dienstleistungen, darunter bestimmte E-Commerce-Dienste.
Kleinstunternehmen, die Dienstleistungen anbieten oder erbringen, sind nach
§ 6 BaFG von diesen Dienstleistungsverpflichtungen ausgenommen. Ob Elektro
Hubmann, die konkrete Website und ein späteres Online-Buchungs- oder
Vertragssystem darunterfallen, muss anhand der tatsächlichen Unternehmensdaten
und Funktionen geklärt und dokumentiert werden. Eine mögliche Ausnahme ist
kein Grund, das WCAG-Ziel zu streichen; außerdem bleibt das
Bundes-Behindertengleichstellungsrecht gesondert zu beachten.

## 4. Rechts- und Datenschutzarbeitspaket vor dem Produktionslaunch

### Anbieterkennzeichnung und Inhalte

- tatsächliche Rechtsform, Firmenbuch-/GISA-Daten, Gewerbebehörde,
  Vertretungsbefugnis, UID und Kammerzugehörigkeit verifizieren;
- Impressum und Offenlegung passend zu ECG, GewO oder UGB sowie MedienG
  erstellen; DLG-Pflichten bei Anwendbarkeit ergänzen;
- keine deutschen TMG-/UStG-Verweise und keinen eingestellten EU-ODR-Link
  übernehmen;
- Urheber-, Nutzungs- und Persönlichkeitsrechte für Logo, Baustellen-, Team-,
  Kunden- und Projektbilder dokumentieren.

### DSGVO und Formulare

- tatsächliches Datenfluss-Inventar für Hosting, Formulare, E-Mail, Karten,
  Videos, Schriftarten, Analyse, Logs und Backups erstellen;
- Informationspflichten insbesondere nach Art. 13 DSGVO aus den realen
  Verarbeitungen ableiten: Verantwortlicher, Zwecke, Rechtsgrundlagen,
  Empfänger, Drittlandtransfer, Speicherdauer und Betroffenenrechte;
- Datenminimierung, Löschfristen, Zugriffsschutz, Auftragsverarbeiter und AVV
  festlegen;
- Rechtsgrundlage der Projektanfrage fachlich bestimmen. Eine erzwungene
  „Datenschutz-Einwilligung“ ist nicht automatisch die richtige Grundlage für
  vorvertragliche Anfragen;
- Datei-Upload erst nach Malwareprüfung, Größen-/Typgrenzen, Löschkonzept und
  sicherer serverseitiger Verarbeitung aktivieren;
- das aktuelle Formular bleibt bis dahin ausdrücklich eine nicht sendende
  Vorschau.

### Cookies, Tracking und externe Einbindungen

- nicht notwendige Speicherung oder Zugriffe auf Endgeräte erst nach aktiver,
  informierter Einwilligung gemäß § 165 Abs. 3 TKG 2021;
- Ablehnen so einfach wie Akzeptieren, Einwilligungen nachweisbar und jederzeit
  widerrufbar gestalten;
- keine Drittanbieter vor Zustimmung laden;
- wenn ausschließlich technisch notwendige Funktionen ohne Tracking verwendet
  werden, keinen unnötigen Cookie-Banner bauen;
- Datenschutzerklärung und Consent-Oberfläche immer gegen einen technischen
  Scan der tatsächlich geladenen Ressourcen abgleichen.

### Online-Vertrag, Terminbuchung und Verbraucherrecht

Der aktuelle Anfrageentwurf schließt keinen Vertrag online. Werden später
verbindliche Terminbuchung, Angebotserteilung, Bestellung oder Zahlung ergänzt,
müssen vor Umsetzung zusätzlich BaFG-/E-Commerce-Anwendbarkeit,
Verbraucherinformationen, Preisangaben, Bestellablauf, Widerruf und
Bestätigungsprozesse fachlich geprüft werden.

## 5. Hosting-Entscheidung

GitHub Pages bleibt für die öffentliche Designvorschau und technische Abnahme
nutzbar. Für die finale kommerzielle Unternehmenswebsite ist es derzeit keine
freigegebene Hostingentscheidung:

- GitHub beschreibt Pages primär als Showcase für Projekte und schließt die
  Nutzung als kostenloses Hosting für ein Online-Geschäft bzw. primär auf
  kommerzielle Transaktionen gerichtete Websites aus;
- GitHub protokolliert beim Abruf einer Pages-Site Besucher-IP-Adressen zu
  Sicherheitszwecken;
- Vertragslage, Datenschutzrollen, Datenübermittlung, Support, Logging und
  Wiederherstellung müssen vor einem Domain-Cutover belastbar bewertet werden.

Empfehlung: Varianten weiter über die GitHub-Projekt-URL abnehmen, die finale
Website anschließend bei einem für den kommerziellen EU-/AT-Betrieb geeigneten
Provider mit geklärtem AVV, Datenstandort, Logs, Backups und Support betreiben.
Die Domain- und E-Mail-Migration bleibt davon getrennt.

## 6. Verbindliche Launch-Gates

Die Produktionsdomain wird erst umgestellt, wenn:

- das finale responsive Design auf realen Geräten abgenommen ist;
- der WCAG-2.2-AA-Prüfumfang abgeschlossen und Restabweichungen dokumentiert
  sind;
- BaFG-Anwendbarkeit und eine mögliche Ausnahme schriftlich geklärt sind;
- Impressum, Offenlegung und Datenschutz fachlich freigegeben sind;
- Consent exakt den realen Diensten entspricht;
- Hostingvertrag und Datenschutzprüfung abgeschlossen sind;
- Formular und Upload entweder sicher produktiv funktionieren oder vollständig
  deaktiviert sind.

## 7. Maßgebliche Quellen

- [RIS: Barrierefreiheitsgesetz – Geltungsbereich (§ 2)](https://ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Anlage=&Artikel=&Gesetzesnummer=20012316&Paragraf=2&ShowPrintPreview=True&Uebergangsrecht=)
- [RIS: BaFG – Ausnahme für Kleinstunternehmen (§ 6)](https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Anlage=&Artikel=&Gesetzesnummer=20012316&Paragraf=6&Uebergangsrecht=)
- [EUR-Lex: Europäischer Rechtsakt zur Barrierefreiheit, RL (EU) 2019/882](https://eur-lex.europa.eu/eli/dir/2019/882/oj/deu)
- [EUR-Lex: Datenschutz-Grundverordnung (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/deu)
- [RIS: Telekommunikationsgesetz 2021 – § 165](https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Anlage=&Artikel=&Gesetzesnummer=20011678&Paragraf=165&Uebergangsrecht=)
- [WKO: Informationspflichten nach dem ECG](https://www.wko.at/internetrecht/informationspflichten-nach-dem-e-commerce-gesetz--dem-unte)
- [WKO: Informationspflichten nach dem Mediengesetz](https://www.wko.at/internetrecht/informationspflichten-nach-dem-mediengesetz-fuer-websites)
- [WKO: Barrierefreiheitsgesetz im E-Commerce](https://www.wko.at/internetrecht/barrierefreiheitsgesetz-e-commerce)
- [GitHub: Terms for Additional Products and Features – Pages](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#pages)
- [GitHub: IP-Protokollierung bei Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection)
# Ergänzung Version G

- Desktop: sticky 3D-Haus-Story mit normalem Seitenscrolling.
- Mobile, reduzierte Bewegung und WebGL-Fallback: vier statische, vertikale Kapitel.
- Canvas ist dekorativ; sämtliche Informationen liegen als semantisches HTML vor.
- Rechtsseiten sind Entwürfe und müssen vor dem Produktivstart österreichisch-rechtlich und datenschutzrechtlich geprüft werden.
- Das Kontaktformular simuliert keinen erfolgreichen Versand.
