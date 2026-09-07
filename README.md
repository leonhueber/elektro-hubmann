# Elektro Hubmann – Website-Neubau und Migration

Stand: 6. September 2026

Dieses Verzeichnis enthält die belastbare Planungsgrundlage für den Neubau von
<https://elektro-hubmann.at/> und die spätere Migration von Domain, DNS und
E-Mail. Die ausgewählte Haus-Story-Website ist als Astro-/React-Projekt
umgesetzt; Inhalte, Referenzprojekte und Rechtstexte sind noch nicht final
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
`/elektro-hubmann/`. Die Website beginnt direkt auf
`/elektro-hubmann/`; einen Variantenumschalter gibt es nicht mehr.

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
8. [Designentscheidung Haus-Story](docs/08-designentscheidung-version-g.md) –
   Auswahl der früheren Version G als einzige Website, URL-Struktur,
   technische Basis und Launch-Gates.
9. [Responsiveness, Barrierefreiheit und EU-/AT-Checkliste](docs/09-responsive-accessibility-eu-checkliste.md)
   – umgesetzte Responsive-Matrix sowie verbindliche spätere Accessibility-,
   Datenschutz-, Rechts- und Hosting-Gates.
10. [Hausmodell V3](docs/10-hausmodell-v3-plan.md) – Blender-Aufbau,
    Öffnungsanimation, Leistungsstationen und Anschluss an die Scroll-Story.
11. [Hausmodell V3 – gestalterischer Neustart](docs/11-hausmodell-v3-gestalterischer-neustart.md)
    – aktueller Vorschlag für Hausform, Bildgestaltung und die nächste Modellrunde.
12. [Haus R3 – Website-Animation](docs/12-haus-r3-website-animation.md)
    – separate Animationsszene, Kapitelkameras, Desktop-/Mobilsequenz und Web-Export.
13. [Haus R3 – Materialien und Einrichtung](docs/13-haus-r3-materialien-und-details.md)
    – detaillierte Möbel, Textilien, Oberflächen und die höher aufgelöste Web-Ausgabe.
14. [Haus V4 – ausgewählte Vorlage und Kamerafahrten](docs/14-haus-v4-verbindliche-vorlage-und-kamerafahrten.md)
    – gesicherte Mockups für zwei Geschosse mit Satteldach, Detailgrad, Frontend
    und Bewegungsplan für den nächsten Blender-Nachbau.
15. [Haus V4 – Website-Animation](docs/15-haus-v4-website-animation.md)
    – native Kamerafahrten, acht Ansichten in sechs Kapiteln, responsive
    Bildfolge, Ladeverhalten und reproduzierbarer Export.
16. [Haus V4 – Balkon und Außendetails](docs/16-haus-v4-aussendetails.md)
    – neueste Blender-Modellrevision: Variante B mit Metallgeländer,
    Holzfenstern, größerer Terrasse und detaillierter Fassade.

Das [native V4-Blender-Modell](blender/house_v4/README.md) enthält zwei
eingerichtete Geschosse, Satteldach und acht Prüfansichten. Die Startseite
verwendet die separate V4-Animation mit angehobenem Dach und Obergeschoss,
offenen Innenräumen, warmem Licht und einer durchgehenden Kamera.

## Ausgewähltes Design

Die Website verwendet die reduzierte Haus-Story: Ein vorgerendertes Blender-Haus
führt auf der Startseite scrollgesteuert durch Planung, Installation,
Beleuchtung, Smart Home, Sicherheit und Photovoltaik. Frühere Designvarianten
und ihre Vorschau-Assets wurden entfernt.

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
