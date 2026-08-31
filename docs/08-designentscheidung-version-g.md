# Designentscheidung: Haus-Story als One-Pager

Stand: 1. September 2026

## Entscheidung

Die frühere Version G ist als einzige Gestaltungsrichtung ausgewählt und wird
als vollständiger One-Pager umgesetzt. Leistungen, Arbeitsbeispiele,
Unternehmen, Fachgeschäft und Kontakt liegen auf der Startseite. Eigene Seiten
bleiben ausschließlich für rechtliche Inhalte bestehen. Ein Kontaktformular
wird nicht angeboten; Kontakt erfolgt direkt per Telefon oder E-Mail.

## Öffentliche URL-Struktur

Die Website beginnt direkt auf der normalen Startseite:

```text
https://leonhueber.github.io/elektro-hubmann/
```

Die fachlichen Bereiche werden über Anker auf der Startseite erreicht:

```text
/#leistungen
/#projekte
/#unternehmen
/#fachhandel
/#kontakt
```

Nur rechtliche Inhalte verwenden eigene Pfade:

```text
/impressum/
/datenschutz/
/agb/
/barrierefreiheit/
/bild-lizenznachweise/
```

Die zuvor veröffentlichten Pfade unter `/varianten/` werden nicht
weitergeführt. Die produktive Struktur beginnt direkt am Website-Root.

## Gestaltungs- und Technikbasis

- reduzierte Architekturästhetik auf weißem Hintergrund;
- sieben aufeinander abgestimmte Motive als visueller roter Faden;
- scrollgesteuerte Story von der Planung bis zum Service;
- React nur für die interaktive Haus-Story;
- GSAP ScrollTrigger für normales, nicht blockierendes Seitenscrolling;
- statische Hauskapitel bei `prefers-reduced-motion` und ohne JavaScript;
- eine statische Astro-Startseite für alle fachlichen Inhalte;
- statische Astro-Unterseiten ausschließlich für Rechtliches;
- gemeinsame Unternehmens- und Arbeitsbereichsdaten in `src/config/site.ts`;
- zentral gepflegte Story-Kapitel in `src/config/version-g-story-assets.ts`.

## Aktueller Veröffentlichungsstatus

Die Website ist technisch öffentlich erreichbar, bleibt aber vorerst mit
`noindex, follow` von der Suchmaschinenindexierung ausgeschlossen. Dieser
Schutz bleibt bestehen, bis mindestens folgende Punkte fachlich freigegeben
sind:

- echte Referenzprojekte und Bilder;
- vollständiges und anwaltlich beziehungsweise fachlich geprüftes Impressum;
- auf Hosting und direkte Kontaktwege abgestimmter Datenschutztext;
- bestätigte Öffnungszeiten und Unternehmensangaben;
- finale visuelle Abnahme der Haussequenz.

## Abnahmekriterien für den finalen Launch

- Startseite und die fünf rechtlichen Unterseiten bauen ohne Fehler;
- Navigation und interne Links funktionieren mit GitHub-Pages-Basispfad und
  später auf der Custom Domain;
- alle fachlichen Navigationsziele führen zu Abschnitten des One-Pagers;
- keine sichtbaren Variantenbezeichnungen oder Variantenumschalter;
- keine horizontalen Überläufe bei 390, 768, 1024 und 1440 Pixel Breite;
- vollständige Bedienbarkeit per Tastatur und sichtbare Fokuszustände;
- reduzierte Bewegung ohne Informationsverlust;
- Kontakt ist ohne Formular direkt über Telefon und E-Mail möglich;
- Produktionsbuild, Typecheck, Linting und Tests sind erfolgreich;
- SEO-Indexierung wird erst nach inhaltlicher und rechtlicher Freigabe
  aktiviert.
