import {
  IconArrowRight,
  IconBolt,
  IconBuilding,
  IconCheck,
  IconClipboardCheck,
  IconCrane,
  IconMapPin,
  IconMenu2,
  IconNetwork,
  IconPhoneCall,
  IconShieldCheck,
  IconSolarPanel,
  IconUpload,
  IconUser,
  IconX,
} from '@tabler/icons-react';
import { useEffect, useRef, useState } from 'react';
import { company, processSteps, projects, services } from '../../config/site';

interface Props {
  baseUrl: string;
}

const serviceIcons = [
  IconCrane,
  IconSolarPanel,
  IconBuilding,
  IconNetwork,
  IconClipboardCheck,
];

const panelStates = [
  ['HAUPTVERTEILER', '400 V / 50 Hz', 'Bereit'],
  ['KREIS 07', 'Beleuchtung OG', '16 A'],
  ['FI-SCHUTZ', 'IΔn 30 mA', 'Typ A'],
] as const;

const trustItems = [
  [IconBolt, 'Seit 1972', 'Erfahrung, die verbindet.'],
  [IconMapPin, 'Regional verwurzelt', 'Gitschtal, Hermagor & Weißensee.'],
  [IconUser, 'Persönlich für Sie da', 'Ein Ansprechpartner. Klare Lösungen.'],
] as const;

function normalizeBase(baseUrl: string) {
  return baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
}

export default function VariantFExperience({ baseUrl }: Props) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [formSent, setFormSent] = useState(false);
  const normalizedBase = normalizeBase(baseUrl);
  const asset = (path: string) => `${normalizedBase}${path.replace(/^\//, '')}`;

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const reduceMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches;
    if (!reduceMotion) root.classList.add('is-motion-ready');
    const reveals = Array.from(
      root.querySelectorAll<HTMLElement>('[data-reveal]'),
    );
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -12% 0px', threshold: 0.12 },
    );

    reveals.forEach((element) => observer.observe(element));

    let frame = 0;
    const update = () => {
      frame = 0;
      const scrollMax = document.documentElement.scrollHeight - innerHeight;
      const pageProgress = scrollMax > 0 ? scrollY / scrollMax : 0;
      root.style.setProperty('--page-progress', String(pageProgress));

      if (!reduceMotion) {
        const hero = root.querySelector<HTMLElement>('.f-hero');
        const stage = root.querySelector<HTMLElement>('.f-projects-stage');

        if (hero) {
          const rect = hero.getBoundingClientRect();
          const travel = Math.max(hero.offsetHeight - innerHeight, 1);
          const progress = Math.min(Math.max(-rect.top / travel, 0), 1);
          root.style.setProperty('--hero-progress', String(progress));
          root.dataset.panel = String(Math.min(2, Math.floor(progress * 3)));
        }

        if (stage) {
          const rect = stage.getBoundingClientRect();
          const travel = Math.max(stage.offsetHeight - innerHeight, 1);
          const progress = Math.min(Math.max(-rect.top / travel, 0), 1);
          root.style.setProperty('--project-progress', String(progress));
        }
      }
    };

    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };

    update();
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll, { passive: true });

    return () => {
      root.classList.remove('is-motion-ready');
      observer.disconnect();
      removeEventListener('scroll', onScroll);
      removeEventListener('resize', onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="f-site" ref={rootRef}>
      <div className="f-page-progress" aria-hidden="true">
        <span />
      </div>

      <main id="hauptinhalt">
        <section className="f-hero" aria-labelledby="f-hero-title">
          <div className="f-hero__scene">
            <img
              className="f-hero__image"
              src={asset('/images/version-f/live-circuit-hero.png')}
              alt="Elektrotechniker bei der Arbeit an einem großen Hauptverteiler"
              width="1536"
              height="1024"
              fetchPriority="high"
            />
            <div className="f-hero__shade" aria-hidden="true" />

            <header className="f-header">
              <a
                className="f-brand"
                href="#hauptinhalt"
                aria-label="Elektro Hubmann Startseite"
              >
                <img
                  src={asset('/logo-elektrotechnik-hubmann-dark.png')}
                  width="287"
                  height="78"
                  alt="Elektrotechnik Hubmann"
                />
              </a>
              <nav className="f-nav" aria-label="Hauptnavigation">
                <a href="#leistungen">Leistungen</a>
                <a href="#projekte">Projekte</a>
                <a href="#unternehmen">Unternehmen</a>
                <a href="#kontakt">Kontakt</a>
              </nav>
              <a className="f-button f-button--compact" href="#projektanfrage">
                Projekt anfragen
                <IconArrowRight size={19} stroke={1.7} aria-hidden="true" />
              </a>
              <button
                className="f-menu-button"
                type="button"
                aria-expanded={menuOpen}
                aria-controls="f-mobile-menu"
                aria-label={menuOpen ? 'Menü schließen' : 'Menü öffnen'}
                onClick={() => setMenuOpen((open) => !open)}
              >
                {menuOpen ? (
                  <IconX size={24} aria-hidden="true" />
                ) : (
                  <IconMenu2 size={24} aria-hidden="true" />
                )}
              </button>
              <nav
                id="f-mobile-menu"
                className={`f-mobile-menu${menuOpen ? ' is-open' : ''}`}
                aria-label="Mobile Hauptnavigation"
              >
                <a href="#leistungen" onClick={closeMenu}>
                  Leistungen
                </a>
                <a href="#projekte" onClick={closeMenu}>
                  Projekte
                </a>
                <a href="#unternehmen" onClick={closeMenu}>
                  Unternehmen
                </a>
                <a href="#kontakt" onClick={closeMenu}>
                  Kontakt
                </a>
                <a href="#projektanfrage" onClick={closeMenu}>
                  Projekt anfragen
                </a>
              </nav>
            </header>

            <a className="f-emergency" href={company.emergencyHref}>
              <span>Störungsdienst</span>
              <strong>{company.emergency}</strong>
              <IconArrowRight size={18} stroke={1.7} aria-hidden="true" />
            </a>

            <div className="f-hero__copy">
              <span className="f-kicker">Seit 1972 · Strom mit Substanz</span>
              <h1 id="f-hero-title">
                Strom,
                <br />
                der
                <br />
                verbindet.
              </h1>
              <p>
                Elektroinstallationen für Neubau, Sanierung und Gewerbe –
                geplant und umgesetzt in Gitschtal, Hermagor und am Weißensee.
              </p>
              <div className="f-hero__actions">
                <a className="f-button" href="#projektanfrage">
                  Projekt anfragen
                  <IconArrowRight size={22} stroke={1.7} aria-hidden="true" />
                </a>
                <a className="f-text-link" href="#projekte">
                  Projekte entdecken
                  <IconArrowRight size={20} stroke={1.7} aria-hidden="true" />
                </a>
              </div>
            </div>

            <div className="f-conductor" aria-hidden="true">
              <span className="f-conductor__line" />
              <span className="f-conductor__pulse" />
            </div>

            <aside
              className="f-panel-data"
              aria-label="Technische Projektinformationen"
            >
              {panelStates.map(([title, line, value], index) => (
                <div
                  className="f-panel-data__item"
                  key={title}
                  data-panel-index={index}
                >
                  <span>{title}</span>
                  <strong>{line}</strong>
                  <small>{value}</small>
                </div>
              ))}
            </aside>

            <div
              className="f-hero__trust"
              aria-label="Erfahrung und Arbeitsweise"
            >
              {trustItems.map(([Icon, title, description]) => (
                <div key={title}>
                  <Icon size={27} stroke={1.35} aria-hidden="true" />
                  <span>
                    <strong>{title}</strong>
                    <small>{description}</small>
                  </span>
                </div>
              ))}
            </div>

            <a className="f-scroll-cue" href="#leistungen">
              <span>Scrollen, um den Stromkreis zu starten</span>
              <IconArrowRight size={17} stroke={1.5} aria-hidden="true" />
            </a>
          </div>
        </section>

        <section className="f-services" id="leistungen">
          <div className="f-section-head" data-reveal>
            <div>
              <span className="f-kicker f-kicker--dark">
                Das System Hubmann
              </span>
              <h2>
                Ein Stromkreis.
                <br />
                Fünf Kompetenzen.
              </h2>
            </div>
            <p>
              Von der ersten Leitung bis zur geprüften Übergabe greifen Planung,
              Ausführung und Service präzise ineinander.
            </p>
          </div>

          <div className="f-service-grid">
            {services.map((service, index) => {
              const Icon = serviceIcons[index] ?? IconShieldCheck;
              return (
                <article
                  className="f-service-card"
                  key={service.title}
                  data-reveal
                  style={
                    { '--delay': `${index * 70}ms` } as React.CSSProperties
                  }
                >
                  <div className="f-service-card__port" aria-hidden="true">
                    <span />
                  </div>
                  <div className="f-service-card__top">
                    <Icon size={38} stroke={1.25} aria-hidden="true" />
                    <span>{String(index + 1).padStart(2, '0')}</span>
                  </div>
                  <h3>{service.shortTitle}</h3>
                  <p>{service.description}</p>
                  <div className="f-service-card__image">
                    <img
                      src={asset(service.image)}
                      alt={service.imageAlt}
                      width={service.imageWidth}
                      height={service.imageHeight}
                      loading="lazy"
                    />
                  </div>
                  <a
                    href="#projektanfrage"
                    aria-label={`${service.title} anfragen`}
                  >
                    Leistung anfragen
                    <IconArrowRight size={18} stroke={1.6} aria-hidden="true" />
                  </a>
                </article>
              );
            })}
          </div>
        </section>

        <section className="f-projects-stage" id="projekte">
          <div className="f-projects-sticky">
            <div className="f-projects-head">
              <span className="f-kicker">Referenzprojekte</span>
              <h2>
                Gebaut.
                <br />
                Geprüft.
                <br />
                Verbunden.
              </h2>
              <p>Wischen oder scrollen Sie durch ausgewählte Projekttypen.</p>
            </div>
            <div className="f-project-track">
              {projects.slice(0, 5).map((project, index) => (
                <article className="f-project-card" key={project.type}>
                  <div className="f-project-card__image">
                    <img
                      src={asset(project.image)}
                      alt={project.alt}
                      width={project.width}
                      height={project.height}
                      loading="lazy"
                    />
                    <span>0{index + 1}</span>
                  </div>
                  <div className="f-project-card__body">
                    <small>Referenz · Region Hermagor</small>
                    <h3>{project.type}</h3>
                    <p>Planung · Installation · Prüfung · Übergabe</p>
                  </div>
                </article>
              ))}
            </div>
            <div className="f-project-meter" aria-hidden="true">
              <span />
            </div>
          </div>
        </section>

        <section className="f-process" id="ablauf">
          <div className="f-process__intro" data-reveal>
            <span className="f-kicker">Vom Erstkontakt bis zur Übergabe</span>
            <h2>Ein klarer Weg durch jedes Projekt.</h2>
            <p>
              Gute Elektrotechnik beginnt nicht mit dem ersten Kabel, sondern
              mit Zuhören, Verstehen und einer sauberen Planung.
            </p>
          </div>
          <ol className="f-process__steps">
            {processSteps.map(([number, title, description], index) => (
              <li
                key={number}
                data-reveal
                style={{ '--delay': `${index * 80}ms` } as React.CSSProperties}
              >
                <span className="f-process__number">{number}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{description}</p>
                </div>
                <IconCheck size={22} stroke={1.5} aria-hidden="true" />
              </li>
            ))}
          </ol>
        </section>

        <section className="f-company" id="unternehmen">
          <div className="f-company__image" data-reveal>
            <img
              src={asset('/images/version-e/baustellen-hero.webp')}
              alt="Elektrotechniker von Elektro Hubmann auf einer Baustelle"
              width="1586"
              height="992"
              loading="lazy"
            />
            <span>
              <strong>50+</strong> Jahre Erfahrung
            </span>
          </div>
          <div className="f-company__copy" data-reveal>
            <span className="f-kicker f-kicker--dark">
              Familienbetrieb seit 1972
            </span>
            <h2>Nähe ist unser stärkstes Netzwerk.</h2>
            <p>
              Elektro Hubmann begleitet Bauherren und Betriebe mit kurzen Wegen,
              direkter Abstimmung und persönlicher Verantwortung – von der
              ersten Idee bis zur fertigen Anlage.
            </p>
            <a className="f-text-link f-text-link--dark" href="#projektanfrage">
              Unternehmen kennenlernen
              <IconArrowRight size={20} stroke={1.7} aria-hidden="true" />
            </a>
          </div>
        </section>

        <section className="f-inquiry" id="projektanfrage">
          <div className="f-inquiry__intro" data-reveal>
            <span className="f-kicker">Projektanfrage</span>
            <h2>Bringen wir Ihr Projekt unter Strom.</h2>
            <p>
              Erzählen Sie uns kurz, was Sie vorhaben. Wir melden uns persönlich
              und klären die nächsten Schritte.
            </p>
            <a href={company.emergencyHref} className="f-call-card">
              <IconPhoneCall size={26} stroke={1.4} aria-hidden="true" />
              <span>Störungsdienst</span>
              <strong>{company.emergency}</strong>
            </a>
          </div>

          <form
            className="f-form"
            onSubmit={(event) => {
              event.preventDefault();
              setFormSent(true);
            }}
            data-reveal
          >
            {formSent ? (
              <div className="f-form__success" role="status" tabIndex={-1}>
                <IconCheck size={42} stroke={1.4} aria-hidden="true" />
                <h3>Anfrage ist vorbereitet.</h3>
                <p>
                  In dieser Designvorschau wird noch nichts versendet. Der
                  sichere Formularversand wird im finalen Design angebunden.
                </p>
                <button type="button" onClick={() => setFormSent(false)}>
                  Angaben ändern
                </button>
              </div>
            ) : (
              <>
                <div className="f-form__grid">
                  <label>
                    <span>Name *</span>
                    <input name="name" autoComplete="name" required />
                  </label>
                  <label>
                    <span>Telefon *</span>
                    <input
                      name="phone"
                      type="tel"
                      autoComplete="tel"
                      required
                    />
                  </label>
                  <label>
                    <span>E-Mail *</span>
                    <input
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                    />
                  </label>
                  <label>
                    <span>Baustellenort</span>
                    <input name="location" autoComplete="address-level2" />
                  </label>
                  <label>
                    <span>Projektart</span>
                    <select name="type" defaultValue="">
                      <option value="" disabled>
                        Bitte auswählen
                      </option>
                      <option>Neubau</option>
                      <option>Sanierung</option>
                      <option>Gewerbe</option>
                      <option>Photovoltaik</option>
                      <option>Service</option>
                    </select>
                  </label>
                  <label>
                    <span>Gewünschter Zeitraum</span>
                    <input name="timeframe" placeholder="z. B. Herbst 2026" />
                  </label>
                  <label className="f-form__wide">
                    <span>Projektbeschreibung *</span>
                    <textarea name="message" rows={5} required />
                  </label>
                  <label className="f-upload f-form__wide">
                    <IconUpload size={23} stroke={1.4} aria-hidden="true" />
                    <span>
                      Pläne oder Fotos hinzufügen{' '}
                      <small>optional · PDF, JPG, PNG</small>
                    </span>
                    <input type="file" accept=".pdf,.jpg,.jpeg,.png" multiple />
                  </label>
                </div>
                <label className="f-privacy">
                  <input type="checkbox" required />
                  <span>
                    Ich stimme der Verarbeitung meiner Angaben zur Bearbeitung
                    der Anfrage zu.
                  </span>
                </label>
                <button className="f-button" type="submit">
                  Anfrage vorbereiten
                  <IconArrowRight size={21} stroke={1.7} aria-hidden="true" />
                </button>
              </>
            )}
          </form>
        </section>
      </main>

      <footer className="f-footer" id="kontakt">
        <a className="f-footer__brand" href="#hauptinhalt">
          <img
            src={asset('/logo-elektrotechnik-hubmann-dark.png')}
            width="287"
            height="78"
            alt="Elektrotechnik Hubmann"
          />
        </a>
        <div>
          <span>Kontakt</span>
          <a href={company.phoneHref}>{company.phone}</a>
          <a href={company.emailHref}>{company.email}</a>
          <a href={company.emergencyHref}>Störung: {company.emergency}</a>
        </div>
        <div id="fachhandel">
          <span>Fachgeschäft</span>
          <p>{company.address}</p>
          <p>{company.shopHours}</p>
        </div>
        <div>
          <span>Rechtliches</span>
          <a href="#kontakt">Impressum</a>
          <a href="#kontakt">Datenschutz</a>
        </div>
        <small>
          Designvorschau – Inhalte, Referenzen und Formularversand werden vor
          dem Launch finalisiert.
        </small>
      </footer>
    </div>
  );
}
