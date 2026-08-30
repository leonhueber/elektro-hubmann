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
  cta?: string;
  href?: string;
  hint: string;
  callouts?: string[];
};

const FRAME_COUNT = 120;
const PRIORITY_FRAMES = [0, 19, 27, 36, 49, 52, 67, 74, 82, 91, 104, 119];

const chapters: StoryChapter[] = [
  {
    id: 'planning',
    number: '01',
    label: 'Planung',
    title: 'Ein Haus beginnt mit einem guten Plan.',
    description:
      'Wir planen die komplette Elektrotechnik für Neubau, Sanierung und Gewerbe.',
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
    cta: 'Projekt anfragen →',
    href: '#projektanfrage',
    hint: 'Das fertige Haus',
  },
];

const clamp = (value: number) => Math.min(1, Math.max(0, value));

export function getStoryState(progress: number): HouseStoryState {
  if (progress < 0.22) return 'planning';
  if (progress < 0.56) return 'installation';
  if (progress < 0.82) return 'energy';
  return 'service';
}

export function getFrameIndex(progress: number) {
  const value = clamp(progress);
  const segments = [
    { start: 0, end: 0.1, from: 0, to: 19 },
    { start: 0.1, end: 0.5, from: 19, to: 49 },
    { start: 0.5, end: 0.58, from: 49, to: 67 },
    { start: 0.58, end: 0.82, from: 67, to: 91 },
    { start: 0.82, end: 1, from: 91, to: FRAME_COUNT - 1 },
  ];
  const segment = segments.find(({ end }) => value <= end) ?? segments.at(-1)!;
  const localProgress = clamp(
    (value - segment.start) / (segment.end - segment.start),
  );
  return Math.round(segment.from + (segment.to - segment.from) * localProgress);
}

export function getMobileFrameIndex(progress: number) {
  const frame = getFrameIndex(progress);
  if (frame === FRAME_COUNT - 1) return frame;
  return Math.min(FRAME_COUNT - 2, Math.round(frame / 2) * 2);
}

function stateIndex(state: HouseStoryState) {
  return chapters.findIndex((chapter) => chapter.id === state);
}

function frameUrl(baseUrl: string, index: number) {
  return `${baseUrl}images/version-g/sequence/house-${String(index + 1).padStart(4, '0')}.jpg`;
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
  const canvas = useRef<HTMLCanvasElement>(null);
  const frames = useRef<Array<HTMLImageElement | undefined>>([]);
  const requestedFrames = useRef(new Set<number>());
  const targetFrame = useRef(0);
  const [activeIndex, setActiveIndex] = useState(0);
  const activeIndexRef = useRef(0);

  useEffect(() => {
    const root = wrapper.current;
    const surface = canvas.current;
    if (!root || !surface) return;

    let disposed = false;
    let resizeFrame = 0;
    let trigger: { kill: () => void } | undefined;
    const mobileSequence = window.matchMedia('(max-width: 620px)').matches;
    const context = surface.getContext('2d', { alpha: false });
    if (!context) return;

    const nearestLoadedFrame = (wanted: number) => {
      if (frames.current[wanted]?.naturalWidth) return frames.current[wanted];
      for (let offset = 1; offset < FRAME_COUNT; offset += 1) {
        const before = frames.current[wanted - offset];
        const after = frames.current[wanted + offset];
        if (before?.naturalWidth) return before;
        if (after?.naturalWidth) return after;
      }
      return undefined;
    };

    const draw = () => {
      const image = nearestLoadedFrame(targetFrame.current);
      if (!image || !surface.width || !surface.height) return;
      const imageRatio = image.naturalWidth / image.naturalHeight;
      const canvasRatio = surface.width / surface.height;
      const width =
        imageRatio > canvasRatio ? surface.width : surface.height * imageRatio;
      const height =
        imageRatio > canvasRatio ? surface.width / imageRatio : surface.height;
      context.fillStyle = '#fff';
      context.fillRect(0, 0, surface.width, surface.height);
      context.drawImage(
        image,
        (surface.width - width) / 2,
        (surface.height - height) / 2,
        width,
        height,
      );
    };

    const resize = () => {
      resizeFrame = 0;
      const bounds = surface.getBoundingClientRect();
      const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      surface.width = Math.max(1, Math.round(bounds.width * pixelRatio));
      surface.height = Math.max(1, Math.round(bounds.height * pixelRatio));
      draw();
    };

    const loadFrame = (index: number) => {
      const safeIndex = Math.min(FRAME_COUNT - 1, Math.max(0, index));
      if (requestedFrames.current.has(safeIndex)) return Promise.resolve();
      requestedFrames.current.add(safeIndex);
      return new Promise<void>((resolve) => {
        const image = new Image();
        image.decoding = 'async';
        image.src = frameUrl(baseUrl, safeIndex);
        frames.current[safeIndex] = image;
        image.onload = () => {
          if (
            !disposed &&
            (safeIndex === 0 || safeIndex === targetFrame.current)
          )
            draw();
          resolve();
        };
        image.onerror = () => resolve();
      });
    };

    const preload = async () => {
      await loadFrame(0);
      await Promise.all(PRIORITY_FRAMES.map((index) => loadFrame(index)));
      const step = mobileSequence ? 2 : 1;
      const remaining = Array.from(
        { length: Math.ceil(FRAME_COUNT / step) },
        (_, index) => Math.min(FRAME_COUNT - 1, index * step),
      ).filter((index) => !requestedFrames.current.has(index));
      for (let start = 0; start < remaining.length && !disposed; start += 12) {
        await Promise.all(
          remaining.slice(start, start + 12).map((index) => loadFrame(index)),
        );
      }
    };

    const setupScroll = async () => {
      const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
        import('gsap'),
        import('gsap/ScrollTrigger'),
      ]);
      if (disposed) return;
      gsap.registerPlugin(ScrollTrigger);
      trigger = ScrollTrigger.create({
        trigger: root,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.18,
        invalidateOnRefresh: true,
        onUpdate: ({ progress }) => {
          const nextProgress = clamp(progress);
          targetFrame.current = mobileSequence
            ? getMobileFrameIndex(nextProgress)
            : getFrameIndex(nextProgress);
          for (const offset of [-4, -2, 0, 2, 4]) {
            void loadFrame(targetFrame.current + offset);
          }
          root.style.setProperty(
            '--g-story-progress',
            `${nextProgress * 100}%`,
          );
          root.style.setProperty(
            '--g-canvas-scale',
            `${1.015 + Math.sin(nextProgress * Math.PI) * 0.035}`,
          );
          root.style.setProperty(
            '--g-canvas-y',
            `${Math.sin(nextProgress * Math.PI * 2) * -6}px`,
          );
          draw();
          const nextIndex = stateIndex(getStoryState(nextProgress));
          if (nextIndex !== activeIndexRef.current) {
            activeIndexRef.current = nextIndex;
            setActiveIndex(nextIndex);
          }
        },
      });
    };

    void preload();
    void setupScroll();
    resize();
    const onResize = () => {
      if (!resizeFrame) resizeFrame = window.requestAnimationFrame(resize);
    };
    window.addEventListener('resize', onResize, { passive: true });

    return () => {
      disposed = true;
      trigger?.kill();
      window.removeEventListener('resize', onResize);
      if (resizeFrame) window.cancelAnimationFrame(resizeFrame);
      frames.current = [];
      requestedFrames.current.clear();
    };
  }, [baseUrl]);

  return (
    <section
      ref={wrapper}
      className="g-story"
      aria-label="Leistungen von der Planung bis zur Übergabe"
      data-state={chapters[activeIndex]?.id}
      style={{ '--g-story-progress': '0%' } as CSSProperties}
    >
      <div className="g-story-stage">
        <div className="g-story-visual" aria-hidden="true">
          <canvas ref={canvas} className="g-house-canvas" />
          <div className="g-visual-callouts g-visual-callouts--installation">
            <span>Verteiler &amp; Prüfung</span>
            <span>KNX &amp; Beleuchtung</span>
            <span>Netzwerk &amp; Sicherheit</span>
          </div>
          <div className="g-visual-callouts g-visual-callouts--energy">
            <span>PV-Module</span>
            <span>Speicher &amp; Einspeisung</span>
          </div>
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
        <div
          className="g-progress"
          role="group"
          aria-label="Fortschritt der Haus-Story"
        >
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
        </div>
        <div className="g-story-meter" aria-hidden="true">
          <i />
        </div>
      </div>
    </section>
  );
}
