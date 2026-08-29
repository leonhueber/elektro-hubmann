# Deploymentplan für GitHub Pages

Stand: 29. August 2026  
Status: Astro-Grundprojekt und Deployment-Workflow vorhanden; erstes
GitHub-Pages-Deployment wird mit dem Implementierungscommit ausgelöst

## 1. Zielbild

Die statisch gebaute Astro-Website wird aus dem öffentlichen Repository
`leonhueber/elektro-hubmann` per GitHub Actions auf GitHub Pages veröffentlicht.
Die Veröffentlichung erfolgt in zwei bewusst getrennten Stufen:

1. technische Abnahme unter
   `https://leonhueber.github.io/elektro-hubmann/`;
2. erst nach Freigabe Anbindung von `https://elektro-hubmann.at` und `www`.

Innerhalb desselben Deployments werden mehrere Designvarianten unter festen
Unterpfaden veröffentlicht. Es gibt dafür keine getrennten Pages-Sites und
keine voneinander abweichenden Branch-Deployments; ein Commit beschreibt immer
den gemeinsam abgenommenen Stand aller aktiven Varianten.

Die bestehende Domain, DNS-Zone und E-Mail-Konfiguration bleiben während der
Entwicklung unangetastet.

## 2. Aktueller Implementierungsstand

Das Astro-/React-Grundprojekt, `package.json`, `pnpm-lock.yaml` und
`.github/workflows/deploy-pages.yml` sind vorhanden. Der lokale
Produktionsbuild erzeugt die Übersichtsseite und alle fünf Varianten ohne
Typfehler. Jeder Push auf `main` startet den offiziellen Astro-Pages-Workflow.

## Einsatzgrenze von GitHub Pages

GitHub Pages wird in diesem Projekt vorerst als öffentliche Designvorschau und
Abnahmeumgebung verwendet. Die finale kommerzielle Unternehmenswebsite darf
nicht automatisch auf Pages verbleiben: GitHub beschreibt Pages primär als
Projekt-Showcase und schließt kostenloses Hosting für ein Online-Geschäft bzw.
primär auf kommerzielle Transaktionen gerichtete Websites aus. Außerdem werden
bei Pages-Aufrufen Besucher-IP-Adressen zu Sicherheitszwecken protokolliert.

Vor dem Domain-Cutover sind deshalb Nutzungsbedingungen, Datenschutzrollen,
Vertragsgrundlage und der tatsächliche Funktionsumfang zu prüfen. Die
empfohlene Produktionslösung ist ein EU-/AT-tauglicher Hoster mit geklärtem
AVV, Datenstandort, Logs, Backups und Support. Details und Quellen stehen in
[Dokument 09](09-responsive-accessibility-eu-checkliste.md).

Falls das erste Deployment trotz erfolgreichem Build nicht veröffentlicht,
muss einmalig im GitHub-Repository unter **Settings → Pages → Source** die
Option **GitHub Actions** ausgewählt werden.

## 3. Astro-Konfiguration in den zwei Betriebsphasen

### Phase A – GitHub-Projekt-URL

Solange keine Custom Domain aktiv ist:

```js
export default defineConfig({
  site: "https://leonhueber.github.io",
  base: "/elektro-hubmann",
  output: "static",
});
```

Navigation, Bilder, Canonicals, Sitemap und Tests müssen den Basispfad
berücksichtigen. Absolute Pfade wie `/leistungen/` dürfen nicht unkontrolliert
am Repository-Pfad vorbeilaufen.

### Phase B – Custom Domain

Nach fachlicher und technischer Abnahme:

```js
export default defineConfig({
  site: "https://elektro-hubmann.at",
  output: "static",
});
```

Der `base`-Wert wird entfernt. Anschließend werden Canonicals, Sitemap,
Open-Graph-URLs und alle internen Links erneut im Produktionsbuild geprüft.
Die Custom Domain wird in **Settings → Pages** verwaltet; bei einem
Actions-Deployment darf die DNS-Zuordnung nicht nur von einer `CNAME`-Datei
abhängen.

## 4. GitHub-Actions-Deployment

Beim Projektstart wird `.github/workflows/deploy-pages.yml` angelegt. Der
Workflow:

1. startet bei einem freigegebenen Push auf `main` sowie manuell;
2. checkt den exakten Commit aus;
3. installiert die festgelegte Node.js-LTS-Version und pnpm;
4. installiert ausschließlich aus `pnpm-lock.yaml`;
5. führt Format-, Lint-, Typ-, Link-, Accessibility- und Build-Prüfungen aus;
6. konfiguriert GitHub Pages;
7. lädt ausschließlich `dist/` als Pages-Artefakt hoch;
8. deployt in die geschützte Umgebung `github-pages`.

Minimale Workflow-Berechtigungen:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

Gleichzeitige Deployments werden über eine Concurrency-Gruppe serialisiert.
Action-Versionen werden beim Anlegen gegen die offizielle Dokumentation geprüft
und auf konkrete Major-Versionen festgelegt. GitHub nennt derzeit insbesondere
`actions/configure-pages`, `actions/upload-pages-artifact` und
`actions/deploy-pages` für benutzerdefinierte Pages-Workflows.

## 5. Repository- und Sicherheitseinstellungen

- Repository bleibt bewusst öffentlich; damit sind Code, Commit-Historie und
  eingecheckte Inhalte weltweit sichtbar.
- GitHub-Konto mit MFA und sicher verwahrtem Recovery-Zugang schützen.
- **Settings → Pages → Source:** GitHub Actions.
- `main` schützen: Pull Request, erfolgreiche CI und kein Force-Push.
- Produktionsumgebung `github-pages` mit erforderlichen Reviewern schützen,
  solange die alte Domain noch umgestellt wird.
- Keine Zugangsdaten, SMTP-Passwörter, AuthInfo, Kundendaten oder vertraulichen
  Entwürfe committen; Git-Historie ist kein geeigneter Secret Store.
- Dependabot und regelmäßige Action-/Dependency-Updates aktivieren.

## 6. Einschränkung des Kontaktformulars

GitHub Pages kann keinen Servercode und keine Serverless-Funktion ausführen.
Das Formular benötigt deshalb einen getrennten HTTPS-API-Endpunkt. Dieser darf
erst gewählt und aktiviert werden, wenn mindestens AVV, Datenregion,
Aufbewahrung, Spam-Schutz, Rate Limit, Zustellung und Datenschutzerklärung
geprüft sind.

Für den ersten Launch ist eine Website mit gut sichtbaren `tel:`- und
`mailto:`-Kontakten besser als ein ungeprüfter Formulardienst. Ein API-Schlüssel
oder SMTP-Passwort darf niemals im Browserbundle liegen.

## 7. Custom-Domain- und DNS-Reihenfolge

Diese Reihenfolge ist verbindlich:

1. vollständigen DNS-Zonenexport erstellen;
2. Domaininhaber und GitHub-Konto absichern;
3. Domain über den von GitHub angezeigten TXT-Record verifizieren und diesen
   Record beibehalten;
4. `elektro-hubmann.at` in **Settings → Pages** als Custom Domain eintragen;
5. wahrscheinlichen Wildcard-A-Record bestätigen und entfernen;
6. TTL der aktuellen Webrecords mindestens eine alte TTL-Periode vorher auf
   300 Sekunden senken;
7. Apex-Domain auf die zum Cutover-Zeitpunkt von GitHub veröffentlichten
   A/AAAA-Ziele oder auf unterstützte ALIAS/ANAME-Ziele setzen;
8. `www` per CNAME direkt auf `leonhueber.github.io` setzen – ohne Protokoll
   und ohne `/elektro-hubmann`;
9. MX, SPF, Microsoft-Verifikation und Autodiscover unverändert lassen;
10. DNS, GitHub-Zuordnung und Zertifikat abwarten und danach **Enforce HTTPS**
    aktivieren;
11. Apex, `www`, HTTP/HTTPS, Canonicals, Sitemap, 404, alte URLs und E-Mail
    testen.

Die konkreten GitHub-A/AAAA-Adressen werden nicht dauerhaft in diesem Plan
festgeschrieben. Sie werden beim Cutover aus der aktuellen offiziellen
GitHub-Dokumentation bzw. Pages-Oberfläche übernommen und gegengeprüft.

## 8. Redirects und bekannte Pages-Grenzen

GitHub Pages bietet keine frei programmierbare Server-Redirect-Konfiguration.
Darum muss vor der Umsetzung jede alte URL bewertet werden. Wo echte HTTP-301-
Redirects mit GitHub Pages nicht zuverlässig möglich sind, wird entweder:

- die alte URL als statische Seite am identischen Pfad erhalten;
- eine statische Fallback-Seite mit Canonical und sofortigem Link zum Ziel
  verwendet; oder
- vor dem Domain-Cutover ein vorgeschalteter DNS/CDN-Dienst bewusst ergänzt.

Für wichtige alte URLs ist ein clientseitiger Redirect allein keine
gleichwertige SEO-Lösung. Diese Einschränkung ist vor der finalen Hosting-
Abnahme gegen die Redirect-Matrix zu prüfen.

## 9. Rollback

### Fehler im neuen Build

Bekannten guten Git-Commit erneut deployen. Der Commit-Hash und der zugehörige
erfolgreiche Actions-Lauf werden im Launch-Protokoll festgehalten.

### Fehler beim Domain-Cutover

Nur die Web-A/AAAA/CNAME-Records auf die dokumentierten Altwerte
`152.53.64.181` zurückstellen. Mailrecords bleiben unangetastet. Der alte
Webhost wird mindestens 30 Tage weiterbetrieben.

### GitHub-Ausfall

Der statische `dist/`-Build ist portabel und wird als Release-Artefakt bzw.
lokal reproduzierbar gehalten. Ein Notfall-Deployment auf einen alternativen
statischen Hoster ist möglich, ohne Domain, Mail oder Inhaltsmodell umzubauen.

## 10. Aktivierungs- und Abnahmecheckliste

- [ ] Astro-Projekt, `package.json` und `pnpm-lock.yaml` vorhanden.
- [ ] Lokaler Produktionsbuild erzeugt reproduzierbar `dist/`.
- [ ] CI und Tests bestehen auf `main`.
- [ ] Pages-Workflow mit minimalen Berechtigungen eingecheckt.
- [ ] Repository-Quelle in Settings auf GitHub Actions gestellt.
- [ ] Projekt-URL ist öffentlich erreichbar und alle Assets laden.
- [ ] Basispfad, Canonicals und Sitemap sind korrekt.
- [ ] Alle aktiven Varianten und ihre Versionsleiste sind erreichbar.
- [ ] Nur die Hauptversion ist in Sitemap und Suchindex vorgesehen.
- [ ] 404 und Redirect-Matrix sind geprüft.
- [ ] Externer Uptime-Monitor ist vorbereitet.
- [ ] Custom Domain ist vor DNS-Änderung verifiziert und eingetragen.
- [ ] Wildcard-DNS ist entfernt.
- [ ] MX/SPF/Autodiscover bleiben nachweislich unverändert.
- [ ] HTTPS ist aktiv und Zertifikat wird überwacht.
- [ ] Rollback auf guten Commit und alte Web-IP wurde getestet.

## 11. Offizielle Referenzen

- [Astro auf GitHub Pages deployen](https://docs.astro.build/en/guides/deploy/github/)
- [GitHub Pages mit benutzerdefiniertem Workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Publishing Source konfigurieren](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Custom Domain verwalten](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Custom Domain verifizieren](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
- [DNS-Probleme und Wildcard-Risiko](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages)
