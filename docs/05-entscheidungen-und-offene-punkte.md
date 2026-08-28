# Entscheidungen und offene Punkte

Stand: 29. August 2026

Diese Liste ist das Eingangstor für Design, Entwicklung und Migration. Fehlende
Angaben dürfen nicht durch Annahmen ersetzt werden, wenn sie Inhalt, Recht,
E-Mail oder Domainbetrieb beeinflussen.

## 1. Unternehmens- und Rechtsdaten

- [ ] Exakter Firmenwortlaut und Rechtsform bestätigt.
- [ ] Firmenbucheintragung, Firmenbuchnummer und Gericht geklärt.
- [ ] Standort der Gewerbeberechtigung bestätigt.
- [ ] Unternehmensgegenstand und Gewerbe exakt benannt.
- [ ] WKO-/Fachgruppen-/Innungsmitgliedschaften bestätigt.
- [ ] Berufsbezeichnung, Verleihungsstaat und relevante Befähigungen bestätigt.
- [ ] UID `ATU51880004` aus Primärquelle bestätigt.
- [ ] Aufsichts-/Gewerbebehörde bestätigt.
- [ ] Medieninhaber/Herausgeber und erforderliche Blattlinie geklärt.
- [ ] Rechtstexte fachlich geprüft; alte deutsche TMG-/UStG-Verweise entfernt.

Empfehlung: Das WKO-Impressumsservice passend zur tatsächlichen Rechtsform als
Ausgangspunkt verwenden und bei Unsicherheit juristisch prüfen.

## 2. Angebot und Positionierung

- [ ] Welche Leistungen sind 2026 tatsächlich aktiv?
- [ ] Welche drei Leistungen sollen die meisten neuen Anfragen erzeugen?
- [ ] Privatkundschaft, Gewerbe oder beide – mit welcher Priorität?
- [ ] Exaktes Einsatzgebiet und eventuelle Anfahrtsgrenzen?
- [ ] Was bedeutet „Störungsdienst“ konkret: Zeiten, Region, Kundengruppen,
  Kosten-/Leistungsgrenzen?
- [ ] Sind Photovoltaik, KNX, Alarm/Brand, Blitzschutz, Prüfungen, Klima,
  Infrarot und Fachhandel weiterhin aktiv und rechtlich/technisch abgedeckt?
- [ ] Welche Marken/Partner dürfen genannt und bebildert werden?
- [ ] Welche Leistungen sollen ausdrücklich nicht angefragt werden?

## 3. Kontakt und Fachgeschäft

- [ ] Festnetz `+43 4286 240` bestätigt.
- [ ] Mobil-/Störungsnummer `+43 664 4343187` bestätigt.
- [ ] `office@elektro-hubmann.at` bestätigt und überwacht.
- [ ] Adresse `Weißbriach 94, 9622 Weißbriach, Österreich` bestätigt.
- [ ] Öffnungszeiten bestätigt, besonders Mittwoch- und Freitagnachmittag.
- [ ] Antwortverantwortung und realistische Antwortzeit für Webanfragen definiert.
- [ ] Kontaktformular ja/nein; benötigte Felder und Aufbewahrung festgelegt.
- [ ] Kartendienst oder nur datenschutzfreundlicher Routenlink entschieden.
- [ ] Echte Social-Profile vorhanden oder Social-Symbole vollständig entfernen.

## 4. Inhalte und Medien

- [ ] Original-Logo als SVG/EPS/PDF oder hochauflösende Masterdatei beschafft.
- [ ] Nutzungsrechte für alle alten Fotos dokumentiert.
- [ ] Alte Fotos auf Aktualität und dargestellte Personen geprüft.
- [ ] Shooting-Termin und Shotlist festgelegt.
- [ ] Mindestens drei geeignete Referenzprojekte mit Freigabe ausgewählt.
- [ ] Kundenzitate nur mit dokumentierter Zustimmung.
- [ ] Unternehmensgeschichte und Jahreszahlen bestätigt.
- [ ] Team, Rollen, Qualifikationen und Zertifikate bestätigt.
- [ ] Entscheidung: Projekte, Aktuelles oder beides?
- [ ] Karriere nur bei realem Bedarf und klarem Bewerbungsprozess.

## 5. Design- und Produktentscheidungen

- [ ] Hauptziel der Startseite priorisiert: Störung, Projekt oder Fachhandel.
- [ ] Finale Navigation und Leistungscluster freigegeben.
- [ ] Stilrichtung anhand echter visueller Entwürfe ausgewählt.
- [ ] Logofarben `#E30613`, `#1D1D1B`, `#FFED00` als Markenbasis bestätigt.
- [ ] Sprache nur Deutsch oder später weitere Sprache?
- [ ] CMS-Selbstpflege wirklich erforderlich?
- [ ] Wer ist nach Launch für Inhalte verantwortlich?
- [ ] Analytics nötig; wenn ja, welche Entscheidungen werden damit getroffen?

## 6. Technische Architektur

- [ ] Empfohlene statische Architektur akzeptiert oder CMS-Anforderung belegt.
- [ ] Quellcode-Repository gehört dem Unternehmen.
- [x] GitHub Pages als öffentliches Website-Hosting gewählt.
- [x] Repository ist öffentlich; Quellcode und eingecheckte Inhalte sind damit
  bewusst weltweit lesbar.
- [ ] GitHub-Konto mit MFA, Recovery und mindestens einem dokumentierten
  Notfallweg abgesichert.
- [ ] Deployment, Backups, Monitoring und Patchverantwortung vereinbart.
- [ ] Formularversand und Spam-Schutz entschieden.
- [ ] Datenstandort und Auftragsverarbeitung der Dienstleister geprüft.
- [ ] Repository-Export und Wiederaufbau von `dist/` als Hosting-Exit getestet.

## 7. Domain- und DNS-Zugänge

- [ ] Registrar über nic.at-Whois bzw. Vertrag verifiziert.
- [ ] Domaininhaber und Kontaktadresse stimmen.
- [ ] Telefonnummer für NISG 2026 hinterlegt bzw. vorbereitet.
- [ ] AuthInfo kann vom Domaininhaber angefordert werden.
- [ ] Registrar-MFA, Recovery und Verlängerungszahlung getestet.
- [ ] DNS-Adminzugang zu `ns1/ns2.antagus.de` bzw. zuständigem Portal vorhanden.
- [ ] Vollständige DNS-Zone exportiert.
- [ ] Wildcard-A-Record bestätigt oder widerlegt.
- [ ] Wildcard-DNS vor GitHub-Pages-Cutover entfernt.
- [ ] GitHub-Domainverifikation per TXT abgeschlossen und Record beibehalten.
- [ ] DNSSEC-Status über Registrar/nic.at bestätigt.
- [ ] Aktueller Webhosting-Vertrag und Eigentümer geklärt.
- [ ] Widerspruch zwischen „IONOS“ im Datenschutztext und aktuellem Hosting geklärt.

## 8. E-Mail-Inventar

- [ ] Microsoft-365-Tenant-Admin und Vertragsinhaber bekannt.
- [ ] Alle Benutzer-Mailboxen exportiert.
- [ ] Shared Mailboxes, Gruppen, Aliase und Weiterleitungen exportiert.
- [ ] Kalender, Kontakte, Delegationen, Regeln und Archive inventarisiert.
- [ ] Mailboxgrößen und Datenmengen bekannt.
- [ ] Scanner, Drucker, Website und Fachsoftware als SMTP-Sender erfasst.
- [ ] Entscheidung: Microsoft 365 behalten oder wirklich migrieren?
- [ ] Falls Migration: Zielprovider nach Anforderungen, nicht nur Preis gewählt.
- [ ] Backup/Restore einer Stichprobe erfolgreich.
- [ ] DKIM im Microsoft-365-Tenant geprüft.
- [ ] DMARC-Einführung mit Reporting-Adresse geplant.

## 9. Kriterien für verbleibende Provider

GitHub Pages ist für das statische Website-Hosting gewählt. Registrar, DNS,
E-Mail, Formular-API und Monitoring bleiben getrennte Entscheidungen. Dafür
gelten mindestens diese Kriterien:

| Bereich | Prüffrage |
|---|---|
| Eigentum | Läuft Konto, Domain und Abrechnung auf das Unternehmen? |
| Support | Gibt es deutschsprachigen Support und klaren Eskalationsweg? |
| Verfügbarkeit | SLA, Statusseite, Backups und Restore-Zeit? |
| Sicherheit | MFA, Rollen, Logs, Verschlüsselung, DNSSEC, Security-Lock? |
| Datenschutz | Datenstandort, AVV, Unterauftragsverarbeiter, Löschung? |
| Portabilität | Vollständiger Export von DNS, Website und Mail möglich? |
| E-Mail | DKIM, DMARC, Shared Mailboxes, Kalender, Mobilgeräte, Migration? |
| Website | Pages-Status, Actions-Historie, HTTPS und externer Uptime-Monitor geprüft? |
| Kosten | Gesamtpreis inklusive Mailboxen, Speicher, Backups und Support? |
| Kündigung | Datenexport, Parallelbetrieb und sauberes Offboarding möglich? |

## 10. Go/No-Go vor jeder produktiven Änderung

- [ ] Änderung ist auf genau eine Ebene begrenzt: Web, Mail, DNS oder Registrar.
- [ ] Backup und Zonenexport sind aktuell und lesbar.
- [ ] Ziel wurde produktionsnah getestet.
- [ ] TTL wurde rechtzeitig gesenkt.
- [ ] Monitoring und Testfälle sind bereit.
- [ ] Verantwortliche und Rollback-Entscheider sind erreichbar.
- [ ] Alte Werte und konkrete Rückkehrschritte sind dokumentiert.
- [ ] Keine Kündigung oder irreversible Änderung im selben Fenster.
