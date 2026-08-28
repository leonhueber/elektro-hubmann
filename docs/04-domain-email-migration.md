# Plan für Domain-, DNS- und E-Mail-Migration

Stand: 29. August 2026

## 1. Wichtigste Sicherheitsentscheidung

Die Begriffe „Providerwechsel“ und „Domainumzug“ dürfen nicht als ein einzelner
Schritt behandelt werden. Es gibt vier getrennte Ebenen:

| Ebene | Aktueller öffentlicher Hinweis | Eigenes Risiko |
|---|---|---|
| Domainregistrierung | Registrar öffentlich noch nicht verifiziert | Inhaberschaft, AuthInfo, Vertrag |
| DNS | `ns1.antagus.de`, `ns2.antagus.de` | alle Web- und Mailrecords |
| Website | A-Record `152.53.64.181` | Erreichbarkeit, TLS, SEO |
| E-Mail | Microsoft 365 laut MX/SPF/Autodiscover | Mailboxdaten, Zustellung, Identitäten |

**Empfohlene Reihenfolge:** neue Website bauen → Web-DNS umstellen → stabilisieren
→ Mailbedarf entscheiden und gegebenenfalls migrieren → stabilisieren →
Registrartransfer zuletzt.

Wenn Microsoft 365 fachlich und wirtschaftlich beibehalten wird, ist keine
Mailboxmigration erforderlich. Bei einem reinen Registrar-/DNS-Wechsel werden
MX, SPF, Autodiscover und Microsoft-Verifikation exakt übernommen.

## 2. Vorbedingungen

Vor jeder Änderung müssen folgende Punkte erfüllt sein:

- Domaininhaber und Rechtsform sind korrekt dokumentiert;
- Registrar und Vertragskonto sind bekannt;
- AuthInfo kann vom Domaininhaber angefordert werden;
- Adminzugriff auf DNS, Webhosting und Microsoft 365 ist getestet;
- mindestens zwei vertrauenswürdige Admins bzw. ein Notfallzugang existieren;
- MFA und Wiederherstellungscodes liegen in einem Unternehmens-Passwortmanager;
- vollständige DNS-Zone ist exportiert;
- alle Mailboxen und mailfähigen Objekte sind inventarisiert;
- alte Verträge werden bis nach erfolgreicher Migration weitergeführt;
- Rollback-Verantwortung und Kommunikationsweg sind festgelegt.

Zugangsdaten, AuthInfo, Passwörter und Recovery-Codes gehören nicht in dieses
Repository.

## 3. Besondere .at-Anforderung 2026

Ab 1. Oktober 2026 verlangt das österreichische NISG 2026 vollständige und
gegebenenfalls verifizierbare Inhaberdaten für .at-Domains; zu den bestehenden
Angaben kommt eine Telefonnummer hinzu. Bei Aufforderung muss der Domaininhaber
mitwirken. Vor einem späteren Transfer müssen die beim Registrar hinterlegten
Daten deshalb kontrolliert und aktuell sein.

Quelle: [nic.at – NISG 2026 für .at-Domains](https://www.nic.at/de/news/nic-at/nisg-2026-was-sich-fur-at-domains-andert)

## 4. Aktueller DNS-Snapshot

Momentaufnahme vom 29. August 2026:

```text
@            A      152.53.64.181                         TTL ~86400
www          A      152.53.64.181                         TTL 86400
@            NS     ns1.antagus.de, ns2.antagus.de        TTL 86400
@            MX 0   elektrohubmann-at01i.mail.protection.outlook.com
@            TXT    v=spf1 include:spf.protection.outlook.com -all
@            TXT    MS=ms21158600
autodiscover CNAME  autodiscover.outlook.com
_dmarc       TXT    nicht gefunden
selector1._domainkey CNAME nicht gefunden
selector2._domainkey CNAME nicht gefunden
DS/DNSSEC           nicht gefunden
CAA                  nicht gefunden
```

Die vollständige Zone kann zusätzliche Records enthalten und muss aus dem
DNS-Portal exportiert werden. Mehrere Hostnamen lösen auf die Web-IP auf; ein
Wildcard-A-Record ist wahrscheinlich, aber noch zu bestätigen.

## 5. Website-Cutover – ohne E-Mail-Risiko

### Vorbereitung, mindestens 7 Tage vorher

1. Neue Website unter `https://leonhueber.github.io/elektro-hubmann/`
   vollständig testen.
2. Repository unter **Settings → Pages** auf „GitHub Actions“ stellen.
3. Domain per GitHub-TXT-Challenge verifizieren und den TXT-Record dauerhaft
   belassen.
4. `elektro-hubmann.at` zuerst in den GitHub-Pages-Einstellungen als Custom
   Domain hinterlegen; DNS erst danach umstellen. Das reduziert das Risiko
   einer Domainübernahme.
5. Vollständigen DNS-Export und Screenshot/Export der aktuellen Zone sichern.
6. Wahrscheinlichen Wildcard-A-Record eindeutig prüfen und entfernen. GitHub
   warnt bei Pages ausdrücklich vor Wildcard-DNS-Records.
7. Web-A/AAAA/CNAME-TTL von 86.400 auf 300 Sekunden senken. Die Änderung muss
   mindestens eine alte TTL-Periode vor dem Cutover aktiv sein.
8. MX, SPF, Microsoft-TXT und Autodiscover als „nicht anfassen“ markieren.
9. Rollback auf `152.53.64.181` testen und dokumentieren.

### Cutover

1. Nur Webrecords ändern. Für die Apex-Domain ausschließlich die zum
   Cutover-Zeitpunkt in der offiziellen GitHub-Dokumentation bzw. Pages-Oberfläche
   angegebenen A/AAAA- oder ALIAS/ANAME-Ziele verwenden.
2. `www` als CNAME direkt auf `leonhueber.github.io` setzen. Weder
   `https://` noch `/elektro-hubmann` gehören in den CNAME-Wert.
3. DNS über mehrere Resolver prüfen.
4. Nach ausgestelltem Zertifikat „Enforce HTTPS“ in GitHub Pages aktivieren.
5. Canonical-Domain und HTTP→HTTPS/www-Redirect testen.
6. Startseite, Kernseiten, 404, Formulare und alte URL-Redirects testen.
7. Eingehende und ausgehende E-Mail testen, obwohl Mailrecords unverändert sind.

### Stabilisierung

- 24 Stunden engmaschig, mindestens 7 Tage normal überwachen;
- 404, TLS, Formularfehler und Indexierung prüfen;
- TTL nach 48–72 stabilen Stunden schrittweise auf 3.600–14.400 erhöhen;
- alten Webhost erst nach mindestens 30 Tagen und geprüftem Backup kündigen.

## 6. E-Mail-Migration – nur nach eigenem Go/No-Go

### 6.1 Entscheiden, ob eine Migration wirklich nötig ist

Vor Anbieterwahl klären:

- Anzahl und Größe aller Benutzer- und Shared Mailboxes;
- Kalender, Kontakte, Aufgaben, Regeln, Kategorien und Delegationen;
- Aliase, Verteiler, Gruppen, Weiterleitungen und Catch-all;
- mobile Geräte und Outlook-Profile;
- Scanner, Drucker, Website, ERP/Buchhaltung und andere SMTP-Absender;
- Archiv, Aufbewahrung, rechtliche Anforderungen und Backup;
- MFA, SSO, Office-Lizenzen und Teams-Abhängigkeiten;
- gewünschter Support, Datenstandort, SLA und Exit-Möglichkeit.

IMAP überträgt üblicherweise nur E-Mail, nicht zuverlässig Kalender, Kontakte,
Regeln oder Delegationen. Für Microsoft-365-zu-Microsoft-365 bzw. Exchange-Ziele
ist ein dafür vorgesehenes Migrationstool oder ein Partnerverfahren zu wählen.

### 6.2 Inventar und Sicherung

1. Alle mailfähigen Objekte und ihre Verantwortlichen exportieren.
2. Mailboxgrößen, letzte Aktivität und Sonderrechte erfassen.
3. Vollständiges Backup/Export stichprobenartig wiederherstellen.
4. SMTP-Quellen mit SPF-/Logdaten ermitteln; nicht raten.
5. Einen Pilotbenutzer mit repräsentativem Datenbestand bestimmen.

### 6.3 Ziel vorbereiten

1. Zieltenant/-provider und temporäre Zieladressen einrichten.
2. Benutzer, Shared Mailboxes, Aliase und Gruppen vor MX-Wechsel anlegen.
3. MFA, Adminrollen, Aufbewahrung und Spam-/Malware-Schutz konfigurieren.
4. Domainbesitz mit einem zusätzlichen TXT verifizieren, ohne MX zu ändern.
5. DKIM-Schlüssel/Selectoren am Ziel vorbereiten.
6. SPF als genau einen Record planen; alle legitimen Sender einbeziehen.
7. DMARC zunächst mit Reporting (`p=none`) und kontrollierter Reporting-Adresse
   vorbereiten; erst nach Auswertung auf `quarantine`/`reject` verschärfen.

Microsoft weist ausdrücklich darauf hin, Mailboxen vor der MX-Umstellung
anzulegen und SPF durch DKIM und DMARC zu ergänzen:
[Microsoft 365 Domain Setup](https://learn.microsoft.com/en-us/microsoft-365/admin/setup/add-domain?view=o365-worldwide),
[Microsoft SPF/DKIM/DMARC](https://learn.microsoft.com/en-us/defender-office-365/email-authentication-spf-configure).

### 6.4 Pilot und Vorsynchronisierung

- Pilotmailbox initial synchronisieren;
- Ordneranzahl, Nachrichtenzahl, Anhänge und Zeitstempel vergleichen;
- Kalender, Kontakte, Regeln und Delegationen separat verifizieren;
- intern/extern senden und empfangen;
- SPF, DKIM und DMARC in realen Nachrichtenheadern prüfen;
- Outlook, Webmail und mindestens ein Mobilgerät testen.

### 6.5 Mail-Cutover

Mindestens 7 Tage vorher MX-/Autodiscover-TTL senken. Im Wartungsfenster:

1. letzte inkrementelle Synchronisation starten;
2. Zielmailboxen und Aliase final prüfen;
3. MX zum Ziel ändern;
4. SPF atomar auf die gültigen Zielsender aktualisieren;
5. Autodiscover und weitere vom Ziel geforderte Records ändern;
6. DKIM aktivieren und Signatur extern prüfen;
7. DMARC-Reporting aktivieren;
8. extern→intern, intern→extern und intern→intern testen;
9. Kalender, Freigaben, Shared Mailboxes und Geräte testen;
10. Delta-Synchronisation weiterlaufen lassen, bis keine relevanten Daten fehlen.

### 6.6 Nachlauf und Härtung

- alten Maildienst mindestens 30 Tage aktiv und zugänglich halten;
- Zustellfehler, Quarantäne und DMARC-Berichte täglich prüfen;
- alte SMTP-Quellen bereinigen;
- DMARC erst nach belegter Senderabdeckung stufenweise verschärfen;
- optional MTA-STS/TLS-RPT nach stabilem Mailbetrieb planen;
- Altvertrag erst nach Abnahme und verifiziertem Backup kündigen.

### Mail-Rollback

Ein MX-Rollback kann Mail auf zwei Systeme verteilen. Deshalb darf er nicht nur
aus „MX zurücksetzen“ bestehen. Benötigt werden:

- weiterhin aktive Quellmailboxen;
- dokumentierter Delta-Sync in beide relevante Richtungen oder klarer
  Reconciliation-Prozess;
- bekannte DNS-Altwerte;
- Entscheidung, welche Plattform während des Rollbacks führend ist;
- anschließender Abgleich aller während des Fensters eingegangenen Nachrichten.

## 7. Registrar- und Nameservertransfer – zuletzt

### Registrartransfer

1. Zielregistrar auswählen und Konto im Namen des Domaininhabers anlegen.
2. Inhaberdaten einschließlich Telefonnummer verifizieren.
3. AuthInfo beim aktuellen Registrar anfordern.
4. Domain transferieren, zunächst mit unveränderten Nameservern, wenn möglich.
5. Nach erfolgreichem Transfer eine neue AuthInfo setzen.
6. Verlängerung, Rechnungsdaten, MFA und Transfer-/Security-Lock prüfen.

nic.at bestätigt, dass der bisherige Registrar die AuthInfo herausgeben muss
und der neue Registrar den Transfer einleitet:
[nic.at – Provider/Registrar wechseln](https://www.nic.at/de/so-funktioniert-at/faqs/domain-inhaber).

### Nameserverwechsel, falls gewünscht

Nicht gleichzeitig mit dem Registrartransfer durchführen.

1. Komplette Zone beim neuen DNS-Anbieter importieren.
2. Jeden Record inklusive MX/TXT/CNAME/SRV/CAA vergleichen.
3. Zone mit niedrigen TTLs bereitstellen und autoritativ vorab prüfen.
4. DNSSEC nur koordiniert migrieren; falsche DS-Daten können die gesamte Domain
   unerreichbar machen.
5. Nameserver bei Registrar/nic.at ändern.
6. Web und Mail über mehrere Resolver testen.
7. Alten DNS-Dienst mindestens 7 Tage aktiv lassen.
8. DNSSEC nach stabiler Delegation gezielt aktivieren; CAA nach Wahl der
   Zertifizierungsstelle ergänzen.

## 8. Verifikation nach jedem Cutover

### Website

- A/AAAA/CNAME und `www` korrekt;
- gültiges TLS-Zertifikat und automatische Erneuerung;
- HTTP→HTTPS und eine kanonische Hostvariante;
- keine Mixed-Content-, 404- oder Redirect-Schleifen;
- Formulare, Telefon, E-Mail und Karte funktionieren;
- Sitemap, robots, Canonicals und strukturierte Daten korrekt.

### E-Mail

- MX und Autodiscover korrekt;
- exakt ein gültiger SPF-Record;
- DKIM-Signatur auf ausgehenden Nachrichten;
- DMARC-Alignment und Reporting;
- Versand/Empfang mit mindestens Microsoft, Gmail und einem weiteren externen
  Ziel;
- Anhänge, Umlaute, Kalender, Shared Mailboxes und Mobilgeräte;
- keine unbemerkten Weiterleitungen oder alten SMTP-Absender.

### Domain/DNS

- Domaininhaber und Kontaktdaten korrekt;
- Verlängerung und Zahlung gesichert;
- MFA, Recovery und Security-Lock geprüft;
- autoritative Nameserver konsistent;
- DNSSEC/DS konsistent oder bewusst deaktiviert;
- aktueller Zonenexport und Notfalldokument vorhanden.

## 9. Hauptrisiken und Gegenmaßnahmen

| Risiko | Auswirkung | Gegenmaßnahme |
|---|---|---|
| Domain liegt nicht unter Unternehmenskontrolle | Verlust der Domain | Inhaber/Registrar vor Projektstart verifizieren |
| gleichzeitiger Web-, Mail- und Registrarwechsel | schwer lokalisierbarer Totalausfall | getrennte Wartungsfenster und Gates |
| DNS-Zone unvollständig kopiert | Website/Mail/Tools fallen aus | Export plus Record-für-Record-Diff |
| GitHub-Custom-Domain erst nach DNS gesetzt | Domainübernahme oder fehlerhafte Zuordnung | Domain zuerst verifizieren und in Pages eintragen |
| Wildcard-DNS bleibt aktiv | Übernahmerisiko für ungenutzte Subdomains | Wildcard vor Pages-Cutover entfernen |
| MX versehentlich beim Weblaunch geändert | E-Mail-Ausfall | Mailrecords sperren und nach Launch testen |
| hohe TTL 86.400 | langsamer Cutover/Rollback | mindestens eine TTL-Periode vorher auf 300 senken |
| IMAP als Vollmigration missverstanden | Kalender/Kontakte/Rechte fehlen | workload-fähiges Tool und Pilot verwenden |
| SPF/DKIM/DMARC falsch | Spam oder Ablehnung | echte Sender inventarisieren, Header testen, DMARC stufenweise |
| alter Provider zu früh gekündigt | kein Rollback/Datenverlust | 30 Tage Parallelbetrieb und verifiziertes Backup |
| DNSSEC falsch migriert | gesamte Domain nicht auflösbar | DS koordiniert, nicht am selben Tag aktivieren |
| Rechtstexte aus Altseite übernommen | Abmahn-/Compliance-Risiko | reale Datenflüsse und österreichische Pflichtangaben prüfen |
