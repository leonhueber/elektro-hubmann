# Elektro Hubmann – Website-Neubau und Migration

Stand: 29. August 2026

Dieses Verzeichnis enthält die belastbare Planungsgrundlage für den Neubau von
<https://elektro-hubmann.at/> und die spätere Migration von Domain, DNS und
E-Mail. Ein erstes lauffähiges Astro-/React-Grundprojekt mit fünf öffentlichen
Designvarianten ist vorhanden; Inhalte und Rechtstexte sind noch nicht final
freigegeben.

## Lokale Entwicklung

Voraussetzungen: Node.js 24 und pnpm 11.

```bash
pnpm install --frozen-lockfile
pnpm dev
```

Qualitätsprüfung und Produktionsbuild:

```bash
pnpm format:check
pnpm build
```

Der lokale Entwicklungsserver verwendet denselben Basispfad wie GitHub Pages:
`/elektro-hubmann/`. Die fünf Versionen liegen unter `/varianten/a/` bis
`/varianten/e/`.

## Dokumente

1. [Bestandsanalyse](docs/01-bestandsanalyse.md) – Ist-Zustand, Audit-Evidenz,
   Technik, SEO, Barrierefreiheit und priorisierte Risiken.
2. [Website-Konzept](docs/02-website-konzept.md) – Ziele, Zielgruppen,
   Informationsarchitektur, Seitenkonzept, Designsystem, Inhalte und SEO.
3. [Umsetzungsplan](docs/03-umsetzungsplan.md) – Phasen, Qualitäts-Gates,
   Testmatrix, Abnahmekriterien und Launch-Ablauf.
4. [Domain- und E-Mail-Migration](docs/04-domain-email-migration.md) –
   risikoarmer, rückrollbarer Migrationsplan mit aktuellem DNS-Bestand.
5. [Entscheidungen und offene Punkte](docs/05-entscheidungen-und-offene-punkte.md)
   – Angaben und Zugänge, die vor Design, Entwicklung oder Migration geklärt
   werden müssen.
6. [Technologie und Architektur](docs/06-technologie-architektur.md) – konkrete
   Zieltechnologie, Repository-Struktur, Formularlösung, CI/CD, Tests,
   Datenschutz, Sicherheit und bewusst verworfene Alternativen.
7. [GitHub-Pages-Deployment](docs/07-github-pages-deployment.md) – öffentlicher
   Betrieb, GitHub Actions, Projekt-URL, Custom Domain, DNS-Reihenfolge und
   Rollback.
8. [Live-Versionen](docs/08-live-versionen.md) – mehrere gleichzeitig
   erreichbare Designvarianten, URL-Schema, Versionsleiste, SEO-Regeln und
   Abnahme.
9. [Responsiveness, Barrierefreiheit und EU-/AT-Checkliste](docs/09-responsive-accessibility-eu-checkliste.md)
   – umgesetzte Responsive-Matrix sowie verbindliche spätere Accessibility-,
   Datenschutz-, Rechts- und Hosting-Gates.

## Design-Mockups

- [Version A – Architektur](docs/mockups/version-a-architektur.png)
- [Version B – Technisch](docs/mockups/version-b-technisch.png)
- [Version C – Regional](docs/mockups/version-c-regional.png)

Version D und E wurden direkt als lauffähige Varianten umgesetzt und besitzen
deshalb kein separates statisches Mockup in diesem Ordner.

Die Bilder sind visuelle Konzepte. Texte, Bilder, Projekte, Personen und
Kontaktdaten darin sind nicht als freigegebene Unternehmensangaben zu verwenden.

## Leitentscheidung

Website, DNS, Domain-Registrar und E-Mail werden als vier getrennte Systeme
behandelt. Sie werden nicht gleichzeitig migriert. Die neue Website wird zuerst
über GitHub Pages unter der GitHub-Projekt-URL fertiggestellt und vollständig
abgenommen. Danach wird nur der Web-Traffic der Domain auf GitHub Pages
umgestellt. E-Mail und Registrar folgen – sofern weiterhin gewünscht – in
eigenen Wartungsfenstern.

## Noch nicht durchführen

- keine bestehende Website abschalten;
- keinen aktuellen Hosting-, Domain- oder Mail-Vertrag kündigen;
- keine Nameserver, MX-, SPF- oder Autodiscover-Einträge verändern;
- keine Zugangsdaten oder Wiederherstellungscodes in diesem Repository speichern;
- keine Rechtstexte ungeprüft aus der alten Website übernehmen.
