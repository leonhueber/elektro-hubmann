# Designentscheidung: Haus-Story als einzige Website

Stand: 30. August 2026

## Entscheidung

Die frühere Version G ist als einzige Gestaltungsrichtung ausgewählt. Sie ist
keine Vorschauvariante mehr, sondern die Grundlage der künftigen Website von
Elektro Hubmann. Die Varianten A bis F, der Variantenumschalter und die
Variantenübersicht wurden aus dem produktiven Code entfernt.

## Öffentliche URL-Struktur

Die Website beginnt direkt auf der normalen Startseite:

```text
https://leonhueber.github.io/elektro-hubmann/
```

Unterseiten verwenden ebenfalls normale, dauerhaft verständliche Pfade:

```text
/leistungen/
/leistungen/photovoltaik-energie/
/projekte/
/unternehmen/
/kontakt/
/fachhandel/
/impressum/
/datenschutz/
```

Die zuvor veröffentlichten Pfade unter `/varianten/` werden nicht
weitergeführt. Die produktive Struktur beginnt direkt am Website-Root.

## Gestaltungs- und Technikbasis

- reduzierte Architekturästhetik auf weißem Hintergrund;
- ein Haus als visueller roter Faden der Startseite;
- scrollgesteuerte Sequenz aus 120 vorgerenderten Blender-Bildern;
- React nur für die interaktive Haus-Story;
- GSAP ScrollTrigger für normales, nicht blockierendes Seitenscrolling;
- statische Hauskapitel bei `prefers-reduced-motion` und ohne JavaScript;
- statische Astro-Unterseiten für Leistungen, Projekte, Unternehmen, Kontakt,
  Fachhandel und Rechtliches;
- gemeinsame Unternehmens-, Leistungs- und Projektdaten in
  `src/config/site.ts`.

## Aktueller Veröffentlichungsstatus

Die Website ist technisch öffentlich erreichbar, bleibt aber vorerst mit
`noindex, follow` von der Suchmaschinenindexierung ausgeschlossen. Dieser
Schutz bleibt bestehen, bis mindestens folgende Punkte fachlich freigegeben
sind:

- echte Referenzprojekte und Bilder;
- vollständiges und anwaltlich beziehungsweise fachlich geprüftes Impressum;
- auf Hosting und Formulardienst abgestimmter Datenschutztext;
- bestätigte Öffnungszeiten und Unternehmensangaben;
- funktionsfähige, datenschutzkonforme Formularanbindung;
- finale visuelle Abnahme der Haussequenz.

## Abnahmekriterien für den finalen Launch

- Startseite und alle 18 Unterseiten beziehungsweise Detailseiten bauen ohne
  Fehler;
- Navigation und interne Links funktionieren mit GitHub-Pages-Basispfad und
  später auf der Custom Domain;
- keine sichtbaren Variantenbezeichnungen oder Variantenumschalter;
- keine horizontalen Überläufe bei 390, 768, 1024 und 1440 Pixel Breite;
- vollständige Bedienbarkeit per Tastatur und sichtbare Fokuszustände;
- reduzierte Bewegung ohne Informationsverlust;
- Formular überträgt ohne aktivierte Backend-Anbindung keine Daten;
- Produktionsbuild, Typecheck, Linting und Tests sind erfolgreich;
- SEO-Indexierung wird erst nach inhaltlicher und rechtlicher Freigabe
  aktiviert.
