import type { CSSProperties } from 'react';
import { useEffect, useRef, useState } from 'react';

export type HouseStoryState =
  'planning' | 'installation' | 'energy' | 'service';

type StoryChapter = {
  id: HouseStoryState;
  number: string;
  label: string;
  title: string;
  description: string;
  image: string;
  cta?: string;
  href?: string;
  hint: string;
  callouts?: string[];
};

const chapters: StoryChapter[] = [
  {
    id: 'planning',
    number: '01',
    label: 'Planung',
    title: 'Ein Haus beginnt mit einem guten Plan.',
    description:
      'Wir planen die komplette Elektrotechnik für Neubau, Sanierung und Gewerbe.',
    image: 'house-planning-v2.jpg',
    cta: 'Projekt besprechen →',
    href: '#projektanfrage',
    hint: 'Scrollen, um das Haus zu öffnen',
  },
  {
    id: 'installation',
    number: '02',
    label: 'Installation',
    title: 'Im Inneren greift alles ineinander.',
    description:
      'Elektroinstallation, Beleuchtung, Netzwerk und Gebäudetechnik – sauber geplant und umgesetzt.',
    image: 'house-installation-v2.jpg',
    hint: 'Weiter zum Dach',
    callouts: [
      'Elektroinstallation',
      'Beleuchtung & KNX',
      'Netzwerk & Sicherheit',
    ],
  },
  {
    id: 'energy',
    number: '03',
    label: 'Energie',
    title: 'Auf dem Dach wird das Haus zum Energieerzeuger.',
    description:
      'Photovoltaik, Speicher und elektrische Einbindung – als durchdachtes Gesamtsystem.',
    image: 'house-energy-v2.jpg',
    cta: 'Photovoltaik anfragen →',
    href: '#projektanfrage',
    hint: 'Weiter zur Prüfung & Übergabe',
    callouts: ['Photovoltaik', 'Speicher & Einspeisung'],
  },
  {
    id: 'service',
    number: '04',
    label: 'Service',
    title: 'Geprüft. Dokumentiert. Übergeben.',
    description:
      'Wir begleiten das Projekt von der ersten Planung bis zur fachgerechten Übergabe und stehen auch danach für Service und Überprüfungen zur Verfügung.',
    image: 'house-service-v2.jpg',
    cta: 'Projekt anfragen →',
    href: '#projektanfrage',
    hint: 'Das fertige Haus',
  },
];

const clamp = (value: number) => Math.min(1, Math.max(0, value));
const range = (value: number, start: number, end: number) =>
  clamp((value - start) / (end - start));
const ease = (value: number) =>
  value < 0.5 ? 4 * value * value * value : 1 - Math.pow(-2 * value + 2, 3) / 2;

export function getStoryState(progress: number): HouseStoryState {
  if (progress < 0.24) return 'planning';
  if (progress < 0.51) return 'installation';
  if (progress < 0.78) return 'energy';
  return 'service';
}

export function getLayerMotion(index: number, progress: number) {
  if (index === 0) {
    const leave = ease(range(progress, 0.16, 0.3));
    return {
      opacity: 1 - leave,
      x: 30 * leave,
      y: -2 * leave,
      scale: 1 - 0.06 * leave,
    };
  }
  if (index === 1) {
    const enter = ease(range(progress, 0.13, 0.3));
    const leave = ease(range(progress, 0.45, 0.6));
    return {
      opacity: Math.min(enter, 1 - leave),
      x: -24 * (1 - enter) - 22 * leave,
      y: 3 * (1 - enter) + 2 * leave,
      scale: 0.94 + 0.06 * enter + 0.025 * leave,
    };
  }
  if (index === 2) {
    const enter = ease(range(progress, 0.43, 0.62));
    const leave = ease(range(progress, 0.72, 0.87));
    return {
      opacity: Math.min(enter, 1 - leave),
      x: 26 * (1 - enter) - 10 * leave,
      y: 8 * (1 - enter) - 5 * enter - 2 * leave,
      scale: 0.9 + 0.16 * enter - 0.1 * leave,
    };
  }
  const enter = ease(range(progress, 0.74, 0.92));
  return {
    opacity: enter,
    x: 22 * (1 - enter),
    y: 3 * (1 - enter),
    scale: 0.93 + 0.07 * enter,
  };
}

function stateIndex(state: HouseStoryState) {
  return chapters.findIndex((chapter) => chapter.id === state);
}

function ChapterContent({
  chapter,
  index,
  activeIndex,
}: {
  chapter: StoryChapter;
  index: number;
  activeIndex: number;
}) {
  const active = index === activeIndex;
  const offset = index < activeIndex ? -56 : 56;
  return (
    <article
      className={`g-story-copy ${active ? 'is-active' : ''}`}
      aria-hidden={!active}
      style={{
        opacity: active ? 1 : 0,
        transform: `translate3d(${active ? 0 : offset}px, 0, 0)`,
      }}
    >
      <p className="g-eyebrow">
        <strong>{chapter.number}</strong> · {chapter.label}
      </p>
      <h2 id={`g-title-${chapter.id}`}>{chapter.title}</h2>
      <p className="g-story-description">{chapter.description}</p>
      {chapter.callouts && (
        <ul className="g-callouts">
          {chapter.callouts.map((callout) => (
            <li key={callout}>{callout}</li>
          ))}
        </ul>
      )}
      {chapter.cta && chapter.href && (
        <a className="g-outline-button" href={chapter.href}>
          {chapter.cta}
        </a>
      )}
      <span className="g-scroll-hint">
        {chapter.hint}
        <i aria-hidden="true">↓</i>
      </span>
    </article>
  );
}

export default function HouseStory({ baseUrl }: { baseUrl: string }) {
  const wrapper = useRef<HTMLElement>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      if (!wrapper.current) return;
      const rect = wrapper.current.getBoundingClientRect();
      const scrollable = wrapper.current.offsetHeight - window.innerHeight;
      setProgress(clamp(-rect.top / Math.max(scrollable, 1)));
    };
    const onScroll = () => {
      if (!frame) frame = window.requestAnimationFrame(update);
    };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);

  const activeIndex = stateIndex(getStoryState(progress));
  const progressStyle = {
    '--g-story-progress': `${progress * 100}%`,
  } as CSSProperties;

  return (
    <section
      ref={wrapper}
      className="g-story"
      aria-label="Leistungen von der Planung bis zur Übergabe"
      style={progressStyle}
    >
      <div className="g-story-stage">
        <div className="g-story-visual" aria-hidden="true">
          {chapters.map((chapter, index) => {
            const motion = getLayerMotion(index, progress);
            return (
              <figure
                className={`g-house-layer g-house-layer--${chapter.id}`}
                key={chapter.id}
                style={{
                  opacity: motion.opacity,
                  transform: `translate3d(${motion.x}vw, ${motion.y}vh, 0) scale(${motion.scale})`,
                }}
              >
                <img
                  src={`${baseUrl}images/version-g/${chapter.image}`}
                  width="1536"
                  height="1024"
                  alt=""
                  loading={index === 0 ? 'eager' : 'lazy'}
                  fetchPriority={index === 0 ? 'high' : 'auto'}
                  decoding="async"
                />
              </figure>
            );
          })}
        </div>
        <div className="g-story-copy-stack" aria-live="polite">
          {chapters.map((chapter, index) => (
            <ChapterContent
              key={chapter.id}
              chapter={chapter}
              index={index}
              activeIndex={activeIndex}
            />
          ))}
        </div>
        <nav className="g-progress" aria-label="Fortschritt der Haus-Story">
          <strong>
            <span>{chapters[activeIndex]?.number}</span> / 04
          </strong>
          <ol>
            {chapters.map((chapter, index) => (
              <li
                className={index === activeIndex ? 'is-active' : ''}
                key={chapter.id}
              >
                <span>{chapter.label}</span>
              </li>
            ))}
          </ol>
        </nav>
        <div className="g-story-meter" aria-hidden="true">
          <i />
        </div>
      </div>
    </section>
  );
}
