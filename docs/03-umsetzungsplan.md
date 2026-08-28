# Umsetzungsplan für den Website-Neubau

Stand: 29. August 2026

## 1. Grundsatz

Die alte Website bleibt erreichbar, bis die neue Website vollständig fertig,
geprüft, freigegeben und rückrollbar ist. Design, Entwicklung, Web-Launch,
E-Mail-Migration und Registrartransfer sind getrennte Projekte mit eigenen
Abnahmepunkten.

## 2. Phasen und Qualitäts-Gates

### Phase 0 – Eigentum, Zugänge und Sicherung

**Arbeiten**

- Domaininhaber, Registrar, DNS-Hoster, Webhoster und Microsoft-365-Tenant
  eindeutig identifizieren;
- mindestens zwei kontrollierte Admin-Zugänge mit MFA und sicheren
  Wiederherstellungswegen einrichten;
- vollständiges Website-, Datenbank-, Medien- und DNS-Backup erstellen;
- aktuelle Verträge, Laufzeiten und Kündigungsfristen erfassen;
- vollständige DNS-Zone und vorhandene Mailobjekte exportieren;
- Original-Logo, Fotos und Nutzungsrechte sichern.

**Gate:** Keine weitere Phase beginnt, solange Domain- und Mailadministration
nicht sicher unter Unternehmenskontrolle stehen.

### Phase 1 – Fachliche Klärung und Content-Inventar

**Arbeiten**

- angebotene Leistungen, Einsatzgebiet, Störungsdienst, Öffnungszeiten,
  Kontaktdaten und Qualifikationen bestätigen;
- Zielprioritäten festlegen: Privat/Gewerbe, Projekte/Störung/Fachhandel;
- alte Texte und Bilder mit „behalten, überarbeiten, löschen“ markieren;
- 3–6 belastbare Referenzprojekte auswählen;
- Formular- und Datenschutzbedarf festlegen;
- Rechtsform und Pflichtangaben mit WKO-/Rechtsberatung verifizieren.

**Gate:** Freigegebenes Content-Briefing und keine widersprüchlichen
Unternehmensdaten.

### Phase 2 – Informationsarchitektur und Textkonzept

**Arbeiten**

- finale Sitemap und Leistungscluster beschließen;
- pro Seite Hauptziel, H1, CTA und benötigte Belege definieren;
- finale Texte in natürlicher, regionaler Sprache schreiben;
- Redirect-Matrix der Alt- zu Neu-URLs erstellen;
- Metadaten, strukturierte Daten und interne Verlinkung planen.

**Gate:** Jede geplante Seite hat einen Zweck, Eigentümer und vollständigen
Inhalt. Keine leeren „kommt später“-Seiten.

### Phase 3 – Visuelles Design

**Arbeiten**

- zuerst Startseite und eine Leistungsdetailseite als Desktop- und
  Mobilentwurf gestalten;
- echte Bilder oder klar gekennzeichnete Shooting-Platzhalter verwenden;
- Design-Tokens und Komponenten festlegen;
- Kontakt-, Störungs- und Geschäftswege testen;
- Kontrast, Fokus, Typografie und Bewegungsreduktion mitplanen.

**Gate:** Ein freigegebener visueller Zielentwurf für Desktop und Mobil. Erst
danach beginnt die Entwicklung.

### Phase 4 – Entwicklung

**Arbeiten**

- Astro-Projekt mit statischem Output und TypeScript Strict initialisieren;
- Node.js LTS und pnpm über Versions-/Lockdateien reproduzierbar festlegen;
- Design-Tokens in nativen CSS Custom Properties und komponentennahe Styles
  umsetzen; kein globales UI-Framework ohne neuen Architekturentscheid;
- Inhalte über typisierte Astro Content Collections und Markdown/MDX abbilden;
- Komponenten, Seiten und Inhaltsmodell umsetzen;
- responsive Navigation und erreichbare Telefon-/Mailaktionen bauen;
- Bilder mit Astros Bildpipeline responsive als AVIF/WebP plus Fallback
  ausliefern und lokal benötigte Fonts selbst hosten;
- Kontaktformular außerhalb von GitHub Pages als getrennten API-Dienst mit
  serverseitiger Schema-Validierung, Honeypot und Rate Limit umsetzen; falls
  Datenschutz, AVV und Zustellung noch nicht freigegeben sind, zunächst nur
  Telefon und E-Mail veröffentlichen;
- Sitemap, robots.txt, Canonicals, Open Graph und strukturierte Daten ergänzen;
- Consent nur für tatsächlich eingesetzte einwilligungspflichtige Dienste;
- sichere Header, HTTPS, Cache und Fehlerseiten konfigurieren;
- GitHub Actions für Format, Lint, `astro check`, Build, Linkprüfung,
  Playwright und Accessibility-Tests einrichten;
- GitHub-Pages-Workflow erst nach vorhandenem Astro-Projekt aktivieren und den
  gebauten Ordner `dist/` als Pages-Artefakt veröffentlichen.

**Gate:** Alle Seiten funktionieren lokal und nach dem ersten Pages-Deployment
unter `https://leonhueber.github.io/elektro-hubmann/`; die Produktionsdomain
wurde noch nicht verändert.

### Phase 5 – Inhaltliche und rechtliche Abnahme

**Arbeiten**

- Namen, Nummern, E-Mail, Adresse, Öffnungszeiten und Leistungszusagen gegen
  Primärquellen prüfen;
- Bilderrechte und Kundenfreigaben dokumentieren;
- Impressum nach tatsächlicher Rechtsform neu erstellen;
- Datenschutzerklärung aus tatsächlichen Datenflüssen ableiten;
- Consent-Konfiguration mit real geladenen Ressourcen abgleichen;
- ODR-Altverweis entfernen und österreichische Pflichten prüfen.

**Gate:** Schriftliche Freigabe durch verantwortliche Person; Rechtstexte
nicht bloß aus dem Altbestand kopiert.

### Phase 6 – Technische QA

**Testmatrix**

| Bereich | Mindestumfang |
|---|---|
| Viewports | 360, 390, 768, 1024, 1280 und 1440 px |
| Browser | aktuelles Chrome, Edge, Firefox und Safari/iOS |
| Eingabe | Maus, Touch und vollständige Tastaturbedienung |
| Zoom/Reflow | 200 % Zoom und schmale Reflow-Ansicht |
| Seiten | jede öffentliche Seite, 404, Weiterleitungen, Formularzustände |
| Kontakt | `tel:`, `mailto:`, Karte/Route und Formular |
| SEO | Titles, Descriptions, H1, Canonical, Sitemap, robots, Schema |
| Sicherheit | HTTPS, Mixed Content, Header, Abhängigkeiten, Secret-Scan |
| Datenschutz | Ablehnen/Akzeptieren/Widerrufen; keine Vorabübertragung |
| Performance | langsames Mobilnetz, Bildgrößen, Fonts, JS und Core Web Vitals |
| CI | sauberer Install aus Lockfile, Typecheck, Build und Tests |

**Performancebudgets**

- LCP im Feldziel <= 2,5 s;
- INP im Feldziel <= 200 ms;
- CLS im Feldziel <= 0,1;
- initiales JavaScript so gering wie möglich, Ziel unter 100 KB komprimiert;
- Hero-Bild responsive, korrekt dimensioniert und ohne Layoutsprung;
- keine externen Fonts oder Tracker ohne fachlichen Grund.

**Barrierefreiheitsziel**

WCAG 2.2 AA als Entwicklungs- und Prüfbasis: Semantik, Tastatur, sichtbarer
Fokus, Alternativtexte, Labels, Kontraste, Fehlerhilfe, Zielgrößen,
Bewegungsreduktion und Reflow. Eine automatische Prüfung allein reicht nicht.

**Gate:** Keine offenen P0/P1-Fehler; dokumentierte Restpunkte nur mit bewusstem
Risikoentscheid.

### Phase 7 – Pre-Launch

**Arbeiten**

- finalen Produktionsbuild und unveränderliche Versionskennung erzeugen;
- Website über GitHub Pages unter der Projekt-URL testen, bevor DNS umgestellt
  wird;
- Repository unter **Settings → Pages** auf „GitHub Actions“ stellen;
- `elektro-hubmann.at` in GitHub als Custom Domain eintragen und verifizieren,
  bevor die öffentlichen DNS-Webrecords geändert werden;
- wahrscheinlichen Wildcard-A-Record bestätigen und vor dem Pages-Cutover
  entfernen; Wildcards erhöhen bei GitHub Pages das Übernahmerisiko;
- Altwebsite und DNS erneut sichern;
- TTL der Webrecords mehrere Tage vorher von 86.400 auf 300 Sekunden senken;
- Monitoring für HTTPS, Erreichbarkeit und wichtige Seiten einrichten;
- Search Console vorbereiten und Redirect-Matrix maschinell testen;
- Rollback-Ziel und verantwortliche Person festlegen.

**Gate:** Go/No-Go mit schriftlicher Checkliste und getesteter Rückkehr zur alten
Web-IP.

### Phase 8 – Website-Launch

**Arbeiten**

1. Wartungsfenster bestätigen; keine gleichzeitige E-Mail-/Registraränderung.
2. Nur die Webrecords auf die in GitHub Pages angezeigten Ziele ändern: Apex
   mittels der zum Cutover gültigen A/AAAA- oder ALIAS/ANAME-Werte, `www` per
   CNAME direkt auf `leonhueber.github.io` – ohne Repository-Pfad.
3. MX, SPF, DKIM, DMARC und Autodiscover unverändert lassen.
4. DNS-Auflösung, TLS, Startseite, Unterseiten, Redirects und Formular testen.
5. Logs und Monitoring beobachten.
6. Bei kritischem Fehler Webrecord auf die alte IP `152.53.64.181`
   zurückstellen.

**Gate:** 24 Stunden fehlerfrei, anschließend weitere 7–14 Tage engmaschig
beobachten.

### Phase 9 – Nacharbeiten

- 404-/Redirect-Berichte prüfen;
- Indexierung und Core Web Vitals beobachten;
- echte Suchanfragen und Kontaktwege auswerten;
- Inhalte korrigieren, ohne URL-Struktur leichtfertig zu ändern;
- TTL nach Stabilisierung auf einen normalen Wert, z. B. 3.600–14.400 Sekunden,
  erhöhen;
- Altwebsite mindestens 30 Tage als nicht öffentliches Rollback-Backup halten;
- erst dann separaten Mail-/Registrar-Cutover planen.

## 3. Verbindliche Redirect-Matrix

Die endgültige Matrix wird nach finaler Sitemap erstellt. Mindestzuordnung:

| Alte URL | Vorläufiges neues Ziel |
|---|---|
| `/` | `/` |
| `/unternehmen/` | `/unternehmen/` |
| `/dienstleistungen/` | `/leistungen/` |
| `/handel/` | `/fachhandel/` |
| `/news/` | `/projekte/` oder kontrolliert entfernen |
| `/easytherm-infrarotheizung/` | fachlich passende Leistungsseite, falls aktuell |
| `/my-home-bticino/` | Smart-Home-Leistungsseite, falls aktuell |
| `/impressum/` | `/impressum/` |
| `/datenschutz/` und `/datenschutzerklaerung/` | eine kanonische `/datenschutz/` |
| `http://...` und `www` | einheitlich per 301 auf HTTPS-Kanonical |

Weiterleitungen werden nur gesetzt, wenn das Ziel inhaltlich passt. Veraltete
Inhalte ohne Ersatz erhalten nach SEO-Abwägung 410 statt einer irreführenden
Umleitung auf die Startseite.

## 4. Definition of Done

Die Website ist erst fertig, wenn:

- alle freigegebenen Seiten und Inhalte produktiv vorhanden sind;
- keine Platzhalter, toten Links oder `#`-Social-Links existieren;
- Mobilnavigation und alle Kernwege tastatur- und touchbedienbar sind;
- Kontaktdaten, Öffnungszeiten und Leistungen schriftlich bestätigt sind;
- Formulare Erfolg, Fehler, Spam und Datenschutz korrekt behandeln;
- Consent den realen Datenflüssen entspricht;
- Impressum/Datenschutz fachlich freigegeben sind;
- alle Alt-URLs entschieden und getestet sind;
- Backup, Monitoring, Admin-Zugänge und Rollback dokumentiert sind;
- Website-Launch ohne Veränderung der Mailzustellung erfolgt ist.
