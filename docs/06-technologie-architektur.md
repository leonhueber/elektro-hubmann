# Technologie- und Architekturplan

Stand: 29. August 2026  
Status: empfohlener und für die Planung verbindlicher Zielentscheid

## 1. Entscheidung in einem Satz

Die neue Website wird als **statisch generierte Astro-Website mit TypeScript,
nativem CSS, typisierten Markdown-Inhalten und automatisierten GitHub-Actions-
Prüfungen** gebaut. Im Browser wird standardmäßig kein JavaScript-Framework
geladen. Nur das optionale Kontaktformular benötigt eine kleine getrennte
serverseitige Funktion.

Diese Architektur ist für eine kleine Unternehmenswebsite absichtlich
unspektakulär. Sie minimiert Ausfälle, Angriffsfläche, laufende Wartung und die
Abhängigkeit von einem einzelnen Hostinganbieter.

## 2. Verbindlicher Technologie-Stack

| Bereich | Technologie | Entscheidung |
|---|---|---|
| Laufzeit für Build/Tools | aktuelle Node.js-LTS-Version | in Repository und CI fest an dieselbe Hauptversion binden |
| Paketmanager | pnpm | reproduzierbare Installation mit committed `pnpm-lock.yaml` und `--frozen-lockfile` |
| Web-Framework | Astro, statischer Output | HTML wird zur Build-Zeit erzeugt; kein dauerhafter App-Server für Inhaltsseiten |
| Sprache | TypeScript, `strict: true` | keine untypisierten Datenmodelle oder stillen `any`-Ausnahmen |
| UI | Astro-Komponenten | server-/buildseitige Komponenten; Browser-JavaScript nur als begründete Insel |
| Styling | natives CSS, CSS Custom Properties, Astro-scoped Styles | Design-Tokens zentral, Komponenten lokal; kein Tailwind im Basissetup |
| Inhalte | Astro Content Collections mit Markdown/MDX | Leistungen, Projekte und Unternehmensinhalte mit Schema validieren |
| Datenvalidierung | Zod-Schemas bzw. Astro-Schemafunktion | Build bricht bei fehlenden Pflichtfeldern oder ungültigen Slugs ab |
| Bilder | Astro Image Pipeline | responsive Größen, AVIF/WebP, Fallback, feste Abmessungen gegen Layoutsprünge |
| Schrift | selbst gehostete WOFF2-Dateien | keine Verbindung zu Google Fonts; nur benötigte Schnitte laden |
| Formular | separater API-Dienst in TypeScript | GitHub Pages führt keinen Servercode aus; keine Datenbank, serverseitige Validierung, Honeypot und Rate Limit |
| E-Mail-Versand des Formulars | authentifizierter Transaktions-/SMTP-Dienst | erst nach Provider-, AVV- und Datenschutzentscheidung festlegen |
| Unit-/Logiktests | Vitest, nur für nichttriviale Logik | keine Tests um ihrer selbst willen |
| Browser-/E2E-Tests | Playwright | Chromium, Firefox und WebKit; Mobil- und Desktoppfade |
| Accessibility-Automation | `@axe-core/playwright` | automatisierte WCAG-A/AA-Risiken plus verpflichtende manuelle Prüfung |
| Performanceprüfung | Lighthouse CI plus reale Messung nach Launch | Budgets im Pull Request und Core Web Vitals im Betrieb |
| CI/CD | GitHub Actions | Format, Lint, Typprüfung, Build und Tests vor Merge/Deployment |
| Hosting | GitHub Pages | öffentlicher statischer Betrieb aus `main`; Custom Domain und HTTPS nach Abnahme |
| Monitoring | externer HTTPS-/Seitenmonitor plus Host-Logs | Alarm für Startseite, Kontakt und Zertifikat |

Versionsnummern werden nicht dauerhaft in diesem Konzept festgeschrieben. Beim
Projektstart werden aktuelle, unterstützte Versionen gewählt und in
`package.json`, Lockfile und CI fixiert. Unkontrollierte `latest`-Installationen
im Deployment sind nicht erlaubt.

## 3. Warum Astro

Die Website besteht überwiegend aus strukturierten Inhaltsseiten und wenigen
kleinen Interaktionen. Astro erzeugt daraus fertiges HTML und liefert
standardmäßig nur das JavaScript aus, das eine ausdrücklich interaktive
Komponente benötigt.

Das passt besser als ein vollständiges React-/Next.js-System:

- Suchmaschinen und Besucher erhalten direkt vollständiges HTML;
- Navigation, Inhalte, Telefonlinks und SEO benötigen kein JavaScript;
- weniger Client-JavaScript reduziert Fehler- und Performancefläche;
- der Build kann als statischer Ordner bei vielen Hostern betrieben werden;
- ein Hostingwechsel erfordert keine proprietäre Serverplattform;
- Vorschau, Rollback und Versionierung bleiben einfach.

Astro Content Collections bieten einen typisierten Weg für Markdown-/MDX-
Inhalte. Dadurch kann beispielsweise kein Projekt ohne Titel, Beschreibung,
Bild-Alttext, Veröffentlichungsstatus und zulässigen Slug gebaut werden.

Offizielle Grundlagen:

- [Astro: Inhalte und Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Astro: Bilder](https://docs.astro.build/en/guides/images/)

## 4. Bewusst kein React als Grundvoraussetzung

React ist nicht verboten, aber für die geplante Website kein Basisteil. Ein
React-/Vue-/Svelte-Island darf nur ergänzt werden, wenn eine klar benannte
Funktion mit Astro/HTML nicht sinnvoll umsetzbar ist. Beispiele könnten ein
komplexer Konfigurator oder ein mehrstufiges interaktives Werkzeug sein.

Mobile Navigation, Akkordeons, Formularzustände und einfache Filter rechtfertigen
kein globales SPA. Sie werden mit semantischem HTML, CSS und sehr kleinem
TypeScript umgesetzt.

## 5. Styling-Entscheid

### Natives CSS statt Tailwind

Für den kleinen, individuellen Markenauftritt wird natives CSS verwendet:

- Design-Tokens in `src/styles/tokens.css`;
- Reset und globale Typografie in `src/styles/global.css`;
- komponentennahe Styles direkt in `.astro`-Komponenten;
- wenige explizite Utilities für wiederkehrende Layoutmuster;
- keine dynamisch zusammengesetzten Klassennamen.

Tailwind würde die Umsetzung nicht grundsätzlich verschlechtern, bringt hier
aber ein zusätzliches Abstraktions- und Upgrade-Layer ohne ausreichenden Nutzen.
Ein späterer Wechsel erfolgt nur über einen dokumentierten Architekturentscheid.

Beispiel für die Token-Struktur:

```css
:root {
  --color-brand: #e30613;
  --color-ink: #1d1d1b;
  --color-signal: #ffed00;
  --color-surface: #ffffff;
  --space-1: 0.5rem;
  --space-2: 1rem;
  --space-3: 1.5rem;
  --radius-control: 0.5rem;
  --content-max: 75rem;
}
```

Die tatsächlichen Komponentenwerte werden im Design festgelegt und nicht
unkontrolliert direkt in Seiten dupliziert.

## 6. Inhaltsmodell

Inhalte werden nicht als frei verteilte HTML-Fragmente gepflegt. Vorgesehen
sind mindestens folgende Collections:

### `services`

- `title`, `slug`, `summary`, `seoTitle`, `seoDescription`;
- `heroImage`, `heroAlt`;
- `audiences`, `benefits`, `includedServices`;
- `serviceArea`, `ctaType`;
- `draft`, `updatedAt`.

### `projects`

- `title`, `slug`, `summary`;
- `challenge`, `solution`, `result`;
- `services`, optional freigegebener Ort;
- Bilder jeweils mit Alttext und Rechte-/Freigabevermerk;
- `publishedAt`, `updatedAt`, `draft`.

### `settings`

- bestätigter Firmenname und NAP-Daten;
- Festnetz, Störungsnummer, E-Mail;
- Öffnungszeiten;
- Einsatzgebiet;
- Social-Links nur bei echten Zielen.

Zentrale Unternehmensdaten werden nur einmal gespeichert und in Header,
Footer, Kontaktseite sowie strukturierten Daten wiederverwendet. So entstehen
keine widersprüchlichen Telefonnummern oder Öffnungszeiten.

## 7. Kontaktformular

### Zielarchitektur

Das Formular ist kein Grund, die ganze Website serverseitig zu rendern. Es wird
als isolierte Funktion umgesetzt:

```text
Browser
  -> POST /api/contact
  -> Schema-Validierung
  -> Größen-/Rate-Limit und Honeypot
  -> authentifizierter Mailversand
  -> neutrale Erfolgs- oder Fehlermeldung
```

### Sicherheits- und Datenschutzregeln

- nur Name, Rückkanal, Anliegenkategorie und Nachricht abfragen;
- keine Uploads in Version 1;
- keine sensiblen Daten anfordern;
- maximale Feld- und Requestgrößen festlegen;
- serverseitig validieren und normalisieren;
- keine Fehlermeldung mit internen Details ausgeben;
- IP-Adressen nicht dauerhaft in einer eigenen Datenbank speichern;
- Logs minimieren und mit definierter Frist löschen;
- kein Google reCAPTCHA; zunächst Honeypot, zeitbasierte Prüfung und Rate Limit;
- Versanddienst, Datenregion, AVV und Unterauftragsverarbeiter vor Aktivierung
  prüfen;
- Formular erst aktivieren, wenn Zustellung und Datenschutzerklärung abgenommen
  sind.

Wenn diese Voraussetzungen nicht rechtzeitig erfüllt sind, startet die Website
bewusst nur mit Telefon- und E-Mail-Kontakt. Ein unsicheres Formular ist kein
Launch-Kriterium.

## 8. Datenschutzfreundlicher Grundzustand

Version 1 soll ohne nicht notwendige Cookies auskommen:

- keine Werbe- oder Retargeting-Tags;
- keine extern geladenen Webfonts;
- keine eingebetteten Social Feeds;
- keine automatisch geladene Google Map;
- zunächst keine clientseitige Analytics-Bibliothek;
- Route über einen normalen externen Kartenlink öffnen;
- lokale/serverseitige Betriebsmetriken nur datensparsam verwenden.

Ohne einwilligungspflichtige Dienste ist voraussichtlich kein großer
Consent-Dialog erforderlich. Die finale Bewertung erfolgt jedoch anhand der
tatsächlich gebauten Seite und der österreichischen Rechtslage – nicht anhand
dieser technischen Annahme.

## 9. Repository-Struktur

```text
/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy-pages.yml
│   └── dependabot.yml
├── docs/
├── public/
│   ├── favicon/
│   ├── fonts/
│   └── static/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   ├── navigation/
│   │   ├── sections/
│   │   └── ui/
│   ├── content/
│   │   ├── services/
│   │   └── projects/
│   ├── layouts/
│   ├── pages/
│   ├── styles/
│   └── utils/
├── tests/
│   ├── e2e/
│   └── accessibility/
├── astro.config.mjs
├── package.json
├── pnpm-lock.yaml
├── playwright.config.ts
└── tsconfig.json
```

Eine Formularfunktion kann nicht in GitHub Pages laufen. Eine `functions/`- oder
providerbezogene Adapterstruktur wird erst ergänzt, wenn ein getrenntes
Formular-Backend freigegeben ist. Fachliche Inhalte dürfen nicht in
providergebundene Funktionen wandern.

## 10. CI/CD und Branch-Regeln

### Pull Request

Jeder Pull Request muss automatisch bestehen:

1. Installation exakt aus `pnpm-lock.yaml`;
2. Formatprüfung;
3. ESLint;
4. `astro check` und TypeScript-Strict-Prüfung;
5. Produktionsbuild;
6. interner Link- und Asset-Check;
7. Playwright-Smoke-Tests;
8. automatisierter axe-Scan;
9. Lighthouse-Budget für die Kernseiten.

GitHub empfiehlt für Node-Projekte eine fest konfigurierte Node-Version und
reproduzierbare Build-/Testschritte in GitHub Actions:
[GitHub Actions für Node.js](https://docs.github.com/en/actions/tutorials/build-and-test-code/nodejs).

### Deployment

- Pull Requests werden vollständig gebaut und getestet. GitHub Pages stellt für
  dieses Repository keine isolierte Vorschau-URL pro Pull Request bereit;
- die öffentliche Vorabnahme erfolgt auf der Pages-Projekt-URL, bevor die
  Custom Domain umgestellt wird;
- `main` ist geschützt und erfordert erfolgreiche Checks;
- Produktion wird aus einem eindeutig identifizierbaren Commit gebaut;
- kein direktes Bearbeiten von Dateien auf dem Produktionsserver;
- der Pages-Deploy-Job benötigt nur `pages: write` und `id-token: write` und
  verwendet die geschützte Umgebung `github-pages`;
- Rollback erfolgt durch erneutes Deployment eines bekannten guten Commits;
- Secrets liegen ausschließlich im geschützten Secret Store des Hosters/GitHub,
  nie in `.env`-Dateien im Repository;
- Produktionsdeployment erhält vor dem DNS-Launch eine manuelle Freigabe.

## 11. Teststrategie

### Automatisch

- Build- und Schemafehler;
- interne Links, Canonicals und erwartete Redirects;
- Navigation, Mobile-Menü und Kern-CTAs;
- Formular Erfolg, Fehler, Rate Limit und Spam-Honeypot;
- wichtige Seiten in Chromium, Firefox und WebKit;
- axe-Prüfung der Startseite, Leistungsseite, Kontaktseite und geöffneten
  Navigation;
- visuelle Screenshots der zentralen Viewports;
- Performancebudgets.

Playwright unterstützt Chromium, Firefox und WebKit. Die offizielle
Accessibility-Anleitung empfiehlt `@axe-core/playwright`, weist aber ausdrücklich
darauf hin, dass automatisierte Tests nur einen Teil der Barrieren erkennen:
[Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing).

### Manuell vor Launch

- vollständige Tastaturnavigation;
- sichtbarer Fokus und sinnvolle Fokusreihenfolge;
- Screenreader-Stichprobe;
- 200-%-Zoom und Reflow;
- echte iOS-/Android-Geräte;
- Telefon-, Mail-, Karte- und Formularwege;
- Ablehnen/Akzeptieren/Widerrufen, falls Consent erforderlich ist;
- Inhalt, Rechtstexte und Kontaktdaten gegen Primärquellen.

## 12. Sicherheitsbasis

- ausschließlich HTTPS und automatische Zertifikatserneuerung;
- HSTS erst nach erfolgreichem HTTPS-Betrieb und Prüfung aller Subdomains;
- Content Security Policy zunächst im Report-Only-Modus entwickeln, dann
  erzwingen;
- `X-Content-Type-Options: nosniff`;
- strenge `Referrer-Policy`;
- minimale `Permissions-Policy`;
- keine Inline-Skripte ohne Nonce/Hash, wenn CSP aktiv ist;
- Abhängigkeiten mit Lockfile, Dependabot und regelmäßiger Review;
- keine Secrets im Client-Bundle oder Repository;
- Formularfunktion mit Größen-, Zeit- und Rate-Limits;
- Fehlerseiten und Logs ohne personenbezogene oder interne Details.

DNSSEC, CAA, DKIM und DMARC gehören zum Infrastruktur-/Mailplan und werden
koordiniert aktiviert, nicht unkontrolliert durch den Website-Build.

## 13. GitHub Pages als Zielhosting

Die Website wird über GitHub Pages veröffentlicht. Das passt zum statischen
Astro-Build, hält Hosting und E-Mail getrennt und ermöglicht reproduzierbare
Deployments direkt aus dem Repository.

Verbindliche Grenzen:

- GitHub Pages führt ausschließlich statische Dateien aus; Formularlogik läuft
  bei einem separaten, noch auszuwählenden API-Dienst;
- es gibt keine native, isolierte Pages-URL je Pull Request; PRs werden in CI
  gebaut und getestet, die Abnahme erfolgt lokal bzw. auf der Projekt-URL;
- Security Header sind auf Pages nur eingeschränkt steuerbar. Kritische
  Anforderungen werden vor Launch gegen die ausgelieferten Header geprüft;
- Hosting-Logs sind begrenzt; Verfügbarkeit und Kernseiten werden extern
  überwacht;
- da das Repository öffentlich ist, dürfen keine Secrets, Kundendaten,
  unveröffentlichten personenbezogenen Inhalte oder internen Dokumente
  eingecheckt werden;
- CAA muss, falls später gesetzt, `letsencrypt.org` für das Pages-Zertifikat
  zulassen.

Bis zum Domain-Cutover gilt die Projekt-URL
`https://leonhueber.github.io/elektro-hubmann/`. Dafür setzt Astro
`site: "https://leonhueber.github.io"` und `base: "/elektro-hubmann"`. Beim
Wechsel auf `https://elektro-hubmann.at` wird `site` auf die Custom Domain
gesetzt und `base` entfernt. Die Details und Reihenfolge stehen im
[GitHub-Pages-Deploymentplan](07-github-pages-deployment.md).

## 14. Wartung und Updates

- monatlicher automatisierter Abhängigkeitsbericht;
- Sicherheitsupdates zeitnah nach Test im Preview;
- normale Framework-Upgrades gebündelt und mit vollständiger CI;
- halbjährliche manuelle Prüfung von Formular, Backups, Kontakten, Öffnungszeiten,
  Rechtstext-Datenflüssen und externen Links;
- jährliche Restore-/Rollback-Übung;
- veraltete Inhalte über `updatedAt` sichtbar machen und redaktionell prüfen;
- kein automatisches Major-Upgrade direkt in Produktion.

## 15. Bewusst nicht gewählt

| Alternative | Warum nicht als Standard |
|---|---|
| WordPress/Divi | unnötiger öffentlicher Adminbereich, Plugin-/Patchlast und höhere Angriffsfläche bei geringem Redaktionsbedarf |
| Next.js/React-App | mehr Client-/Serverkomplexität als die statische Inhaltswebsite benötigt |
| reine React-SPA | schlechtere Grundrobustheit und unnötige JavaScript-Abhängigkeit für Navigation und Inhalte |
| Tailwind als Basis | zusätzliche Abstraktion ohne ausreichenden Nutzen für das kleine individuelle Designsystem |
| schweres Headless-CMS | Kosten, Konten und Betriebsaufwand vor nachgewiesenem Selbstpflegebedarf |
| Kontaktformular-Drittanbieter per Embed | zusätzliche Datenflüsse, Branding-/Consent-Abhängigkeit und geringere Kontrolle |
| Google Fonts/Maps direkt eingebettet | vermeidbare Drittanbieteraufrufe; Fonts lokal, Karte zunächst als Link |
| Website, Domain und Mail im selben Paket | erhöht Lock-in und koppelt unabhängige Ausfall-/Migrationsrisiken |

## 16. Bedingungen für eine spätere Architekturänderung

Astro/static wird nur neu bewertet, wenn mindestens eine dieser Anforderungen
real bestätigt wird:

- Mitarbeitende müssen häufig und ohne Git Inhalte selbst veröffentlichen;
- geschützte Benutzerkonten oder personalisierte Daten werden benötigt;
- komplexe Echtzeitfunktionen oder ein Kundenportal kommen hinzu;
- umfangreiche Produkt-/Lagerdaten müssen integriert werden;
- mehrere Redaktionen benötigen Freigabe-Workflows und Rollen;
- ein Konfigurator rechtfertigt ein eigenes interaktives Frontend.

Dann wird ein separates Architecture Decision Record erstellt. Die bestehende
statische Website darf nicht schleichend zu einer unübersichtlichen App
umgebaut werden.
