# Konzept für mehrere gleichzeitig öffentliche Website-Versionen

Stand: 29. August 2026  
Status: fünf Varianten umgesetzt und öffentlich bereitgestellt; finales Design
noch nicht gewählt

## 1. Ziel

Mehrere unterschiedliche Designversionen der neuen Elektro-Hubmann-Website
werden gleichzeitig öffentlich bereitgestellt. Besucher und Entscheider können
oben auf jeder Seite zwischen ihnen wechseln und jede Version über eine feste
URL teilen.

Das sind Designvarianten derselben Website, keine historischen Software-Releases
und keine voneinander getrennten Inhaltskopien.

## 2. Empfohlener Umfang

Aktuell sind fünf Varianten vorhanden. Weitere Varianten werden erst ergänzt,
wenn sie eine neue Designhypothese prüfen; jede zusätzliche Variante erhöht
Responsive-, Browser-, Accessibility-, Performance- und Abnahmeaufwand.

Verbindliche Bezeichnungen:

- Version A – ruhig, hochwertig und architekturorientiert;
- Version B – technisch, präzise und leistungsorientiert;
- Version C – regional, persönlich und handwerksnah;
- Version D – klare Basis aus A mit bildstarken, kreativen Elementen;
- Version E – kontrastreich, direkt und baustellenorientiert.

Die endgültigen Richtungen werden erst nach Bild-, Marken- und Inhaltsbriefing
ausgestaltet. Die Namen dürfen nicht als Qualitätsrangfolge verstanden werden.

## 3. URL-Modell

Während der Entwicklung unter der GitHub-Projekt-URL:

```text
https://leonhueber.github.io/elektro-hubmann/varianten/a/
https://leonhueber.github.io/elektro-hubmann/varianten/b/
https://leonhueber.github.io/elektro-hubmann/varianten/c/
https://leonhueber.github.io/elektro-hubmann/varianten/d/
https://leonhueber.github.io/elektro-hubmann/varianten/e/
```

Unterseiten bleiben logisch parallel:

```text
/varianten/a/leistungen/elektroinstallationen/
/varianten/b/leistungen/elektroinstallationen/
/varianten/c/leistungen/elektroinstallationen/
/varianten/d/leistungen/elektroinstallationen/
/varianten/e/leistungen/elektroinstallationen/
```

Nach dem Domain-Cutover liegt die gewählte Hauptversion auf den normalen URLs:

```text
https://elektro-hubmann.at/
https://elektro-hubmann.at/leistungen/elektroinstallationen/
```

Die Alternativen können – sofern bewusst gewünscht – unter ihren
`/varianten/.../`-Pfaden live bleiben. Die Hauptversion wird nicht zusätzlich
unter einem Variantenpfad dupliziert, sobald die Produktionsdomain aktiv ist.

## 4. Versionsleiste oberhalb des Headers

Die Versionsauswahl ist eine eigene schmale Leiste vor dem normalen
Website-Header. Sie darf nicht wie die Kundennavigation wirken.

Vorgesehener Inhalt:

```text
Designvorschau    Version A    Version B    Version C    Version D    Version E
```

Verbindliche UX-Regeln:

- sichtbare Bezeichnung „Designvorschau“ oder „Website-Version“;
- aktuelle Version mit Text, Kontrast und `aria-current="page"` kennzeichnen;
- normale Links verwenden, damit Wechsel ohne JavaScript, per Tastatur und in
  neuen Tabs funktionieren;
- beim Wechsel dieselbe logische Unterseite öffnen, sofern sie in der
  Zielversion existiert;
- fehlt die Unterseite, kontrolliert auf die Startseite der Zielversion führen;
- auf Mobilgeräten umbrechen oder horizontal kompakt bleiben, ohne Inhalte
  abzuschneiden;
- mindestens 44 × 44 CSS-Pixel große Touch-Ziele;
- kein Zustand ausschließlich in Local Storage oder Cookies; die URL ist die
  eindeutige Version;
- Leiste in jeder Variante an derselben Position und mit derselben Bedienlogik.

Die Leiste gehört nicht in Ausdrucke und kann nach der finalen Auswahl aus der
Hauptversion entfernt werden. Ob sie bei öffentlich bleibenden Alternativen
weiter angezeigt wird, entscheidet die Abnahme.

## 5. Technische Struktur

Inhalte und Darstellung werden strikt getrennt:

```text
gemeinsame Content Collections
        │
        ├── Layout/Komponenten Version A
        ├── Layout/Komponenten Version B
        ├── Layout/Komponenten Version C
        ├── Layout/Komponenten Version D
        └── Layout/Komponenten Version E
                 │
                 └── ein gemeinsamer statischer Astro-Build
                         └── ein GitHub-Pages-Artefakt
```

`src/config/variants.ts` enthält die einzige Liste aktiver Varianten. Pro
Variante werden mindestens ID, öffentlicher Name, Pfad, Status und Layout
typisiert definiert. Astro erzeugt alle bekannten Routen beim Build statisch;
unbekannte Varianten dürfen keine beliebigen Seiten erzeugen.

Gemeinsam bleiben:

- Firmendaten und Kontaktdaten;
- Leistungs- und Projektinhalte;
- Rechtstexte;
- Bilder und Freigabemetadaten;
- SEO-Grunddaten;
- Formular-/Kontaktlogik;
- Tests und Qualitätsbudgets.

Variantenspezifisch dürfen sein:

- Layout und Reihenfolge von Inhaltsblöcken;
- Typografie innerhalb des freigegebenen Font-Sets;
- Farbgewichtung und Oberflächen;
- Bildinszenierung;
- Komponentenform und Mikrointeraktionen;
- CTA-Platzierung, solange der Kontaktweg semantisch gleich bleibt.

Texte werden nicht in Varianten-Komponenten kopiert. Sonst entstehen bereits
nach der ersten Korrektur widersprüchliche Telefonnummern, Leistungen oder
Rechtstexte.

## 6. Suchmaschinenregeln

Mehrere Seiten mit weitgehend gleichem Inhalt unter verschiedenen URLs können
von Suchmaschinen als Duplikate zusammengefasst werden. Deshalb gilt:

- nur die festgelegte Hauptversion erhält selbstreferenzierende Canonicals;
- nur Hauptversions-URLs stehen in `sitemap.xml`;
- alternative Varianten erhalten `meta name="robots"` mit
  `content="noindex, follow"`;
- Varianten-URLs werden nicht in strukturierten Daten als Unternehmens-URL
  ausgegeben;
- vor Launch wird der ausgelieferte HTML-Head jeder Variante automatisiert
  geprüft;
- die Versionsleiste darf Alternativen verlinken, obwohl sie nicht indexiert
  werden sollen;
- `robots.txt` blockiert die Varianten nicht, weil Suchmaschinen die
  `noindex`-Anweisung sonst unter Umständen nicht lesen können.

Wenn die Alternativen später entfernt werden, verweisen ihre URLs kontrolliert
auf die inhaltlich entsprechende Hauptseite oder liefern eine bewusst
gestaltete Auslaufseite. GitHub Pages kann serverseitige 301-Regeln nur sehr
eingeschränkt abbilden; dieser Punkt bleibt Teil der Redirect-Entscheidung.

## 7. Veröffentlichung und Versionierung

Alle aktiven Varianten werden gemeinsam aus `main` gebaut und in einem
GitHub-Pages-Artefakt veröffentlicht. Das verhindert, dass Version A andere
Firmendaten oder einen anderen Rechtsstand als Version B zeigt.

Ein Pull Request gilt nur als bestanden, wenn:

- jede aktive Variante gebaut werden kann;
- die Versionslinks keine 404 erzeugen;
- der Wechsel auf derselben Kernseite funktioniert;
- die aktuelle Version korrekt markiert ist;
- alle Varianten Tastatur-, Kontrast- und Reflow-Mindestanforderungen erfüllen;
- die Hauptversion indexierbar und alle Alternativen `noindex` sind;
- nur Hauptversions-URLs in der Sitemap stehen;
- Screenshots der definierten Desktop- und Mobil-Viewports erzeugt wurden.

## 8. Entscheidungs- und Aufräumprozess

Die Varianten sind ein Entscheidungsinstrument, kein dauerhafter Selbstzweck.
Vor Veröffentlichung werden Bewertungskriterien festgelegt:

- Vertrauen und Professionalität;
- Verständlichkeit des Leistungsangebots;
- Geschwindigkeit bis zum passenden Kontaktweg;
- mobile Bedienbarkeit;
- Wiedererkennbarkeit der Marke;
- Barrierefreiheit und Performance;
- Aufwand für spätere Inhaltspflege.

Nach der Entscheidung wird eine Version als `primary` markiert. Danach wird
explizit entschieden:

1. Alternativen öffentlich mit Versionsleiste und `noindex` behalten;
2. nur über die GitHub-Projekt-URL als Archiv zugänglich halten; oder
3. Alternativen entfernen und ihre Pfade kontrolliert behandeln.

Ohne diese Entscheidung bleiben Alternativen nicht unbegrenzt als vermeintlich
gleichwertige Unternehmenswebsites online.

## 9. Aktueller Responsive-Stand

Alle fünf Varianten besitzen dieselbe responsive Grundlogik und eine
bedienbare Mobile-Navigation. Geprüft wurden Layoutbreiten von 320 bis 1440 px,
einschließlich der Übergänge 620/621 und 820/821 px. Dabei trat in keiner
Variante horizontaler Seitenüberlauf auf. Die Detailmatrix steht in
[Dokument 09](09-responsive-accessibility-eu-checkliste.md).

Accessibility-, Performance- und rechtliche Endabnahme folgen erst auf dem
final ausgewählten Design; sie sind durch den Responsive-Status nicht ersetzt.

## 10. Abnahmekriterien

- [x] Fünf Varianten sind benannt und fachlich abgegrenzt.
- [x] Jede Variante hat eine feste, direkt teilbare URL.
- [x] Versionsleiste steht über dem Header und ist auf allen geprüften Viewports nutzbar.
- [x] Jede Variante besitzt eine bedienbare Mobile-Navigation.
- [x] Keine Variante erzeugt in der definierten Breitenmatrix horizontalen Überlauf.
- [ ] Wechsel erhält Start-, Leistungs- und Kontaktseite korrekt.
- [ ] Alle Varianten lesen denselben freigegebenen Inhaltsbestand.
- [ ] Hauptversion ist eindeutig in Konfiguration und Dokumentation markiert.
- [ ] Nur Hauptversion steht in Sitemap und Suchindex.
- [ ] Alternative Varianten liefern `noindex, follow`.
- [ ] Kein Secret oder vertraulicher Entwurf liegt im öffentlichen Repository.
- [ ] Jede Variante besteht die definierte Browser-, Accessibility- und
  Performanceprüfung.

## 11. Technische Referenzen

- [Astro-Routing und statische Routen](https://docs.astro.build/en/guides/routing/)
- [Google: Indexierung mit `noindex` verhindern](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [Google: doppelte URLs und Canonicals](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
