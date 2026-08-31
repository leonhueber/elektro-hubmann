import type { CSSProperties } from 'react';
import { useEffect, useRef, useState } from 'react';
import {
  VERSION_G_STORY_ASSETS,
  versionGStoryAssetUrl,
  type VersionGStoryAsset,
  type VersionGStoryState,
} from '../../../config/version-g-story-assets';

export type HouseStoryState = VersionGStoryState;

type StoryChapter = {
  id: HouseStoryState;
  number: string;
  label: string;
  title: string[];
  description: string;
  cta: string;
  href: string;
  hint: string;
  asset: VersionGStoryAsset;
};

type SceneMotion = {
  opacity: number;
  x: number;
  y: number;
  scale: number;
};

const chapters: StoryChapter[] = [
  {
    id: 'planning',
    number: '01',
    label: 'Planung',
    title: ['Ein gutes Haus', 'beginnt mit', 'einem klaren Plan.'],
    description:
      'Wir planen Elektrotechnik für Neubau, Sanierung und Gewerbe – durchdacht, präzise und zukunftssicher.',
    cta: 'Projekt besprechen',
    href: 'kontakt/#projektanfrage',
    hint: 'Scrollen, um die Planung weiterzuführen',
    asset: VERSION_G_STORY_ASSETS.planning,
  },
  {
    id: 'installation',
    number: '02',
    label: 'Installation',
    title: ['Saubere Installation.', 'Präzise umgesetzt.'],
    description:
      'Von Elektroinstallationen über Netzwerktechnik bis zu Beleuchtung setzen wir Technik sauber, sicher und zuverlässig um.',
    cta: 'Leistungen ansehen',
    href: 'leistungen/elektroinstallation-sanierung/',
    hint: 'Weiter zur Photovoltaik',
    asset: VERSION_G_STORY_ASSETS.installation,
  },
  {
    id: 'photovoltaic',
    number: '03',
    label: 'Photovoltaik',
    title: ['Energie smart', 'nutzen.', 'Zukunft sicher', 'denken.'],
    description:
      'Mit Photovoltaik, Speicher und intelligenten Lösungen schaffen wir nachhaltige Energiekonzepte.',
    cta: 'Energie entdecken',
    href: 'leistungen/photovoltaik-energie/',
    hint: 'Weiter zu Service und Wartung',
    asset: VERSION_G_STORY_ASSETS.photovoltaic,
  },
  {
    id: 'service',
    number: '04',
    label: 'Service',
    title: ['Auch nach dem', 'Projekt verlässlich', 'an Ihrer Seite.'],
    description:
      'Kundendienst, Wartung und Erweiterungen begleiten Ihre Anlage langfristig und unkompliziert.',
    cta: 'Service anfragen',
    href: 'kontakt/#projektanfrage',
    hint: 'Weiter zu unseren Referenzprojekten',
    asset: VERSION_G_STORY_ASSETS.service,
  },
];

const clamp = (value: number) => Math.min(1, Math.max(0, value));
const smoothstep = (value: number) => {
  const safeValue = clamp(value);
  return safeValue * safeValue * (3 - 2 * safeValue);
};

export function getStoryState(progress: number): HouseStoryState {
  const value = clamp(progress);
  if (value < 0.25) return 'planning';
  if (value < 0.5) return 'installation';
  if (value < 0.75) return 'photovoltaic';
  return 'service';
}

export function getSceneMotion(
  progress: number,
  sceneIndex: number,
): SceneMotion {
  const value = clamp(progress);
  const start = sceneIndex / chapters.length;
  const end = (sceneIndex + 1) / chapters.length;
  const fadeDistance = 0.045;
  let opacity = 1;

  if (sceneIndex > 0 && value < start + fadeDistance) {
    opacity = smoothstep((value - (start - fadeDistance)) / (fadeDistance * 2));
  }
  if (sceneIndex < chapters.length - 1 && value > end - fadeDistance) {
    opacity = Math.min(
      opacity,
      1 - smoothstep((value - (end - fadeDistance)) / (fadeDistance * 2)),
    );
  }
  if (value < start - fadeDistance || value > end + fadeDistance) {
    opacity = 0;
  }

  const center = (start + end) / 2;
  const signedDistance = Math.max(-1, Math.min(1, (value - center) * 5));
  const inactiveOffset = (1 - opacity) * (value < center ? 1 : -1);

  return {
    opacity,
    x: signedDistance * -1.8 + inactiveOffset * 32,
    y: Math.abs(signedDistance) * 0.7 + (1 - opacity) * 1.6,
    scale: 1 + Math.abs(signedDistance) * 0.012 - (1 - opacity) * 0.12,
  };
}

function stateIndex(state: HouseStoryState) {
  return chapters.findIndex((chapter) => chapter.id === state);
}

function ChapterContent({
  chapter,
  index,
  activeIndex,
  baseUrl,
}: {
  chapter: StoryChapter;
  index: number;
  activeIndex: number;
  baseUrl: string;
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
      <h2 id={`g-title-${chapter.id}`}>
        {chapter.title.map((line) => (
          <span className="g-story-title-line" key={line}>
            {line}
          </span>
        ))}
      </h2>
      <p className="g-story-description">{chapter.description}</p>
      <a
        className="g-outline-button"
        href={`${baseUrl}${chapter.href}`}
        tabIndex={active ? undefined : -1}
      >
        <span>{chapter.cta}</span>
        <span aria-hidden="true">→</span>
      </a>
      <span className="g-scroll-hint">
        {chapter.hint}
        <i aria-hidden="true">↓</i>
      </span>
    </article>
  );
}

export default function HouseStory({ baseUrl }: { baseUrl: string }) {
  const wrapper = useRef<HTMLElement>(null);
  const imageLayers = useRef<Array<HTMLElement | null>>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const activeIndexRef = useRef(0);

  useEffect(() => {
    const root = wrapper.current;
    if (!root) return;

    let disposed = false;
    let trigger: { kill: () => void; progress: number } | undefined;

    const updateVisuals = (progress: number) => {
      const nextProgress = clamp(progress);
      root.style.setProperty('--g-story-progress', `${nextProgress * 100}%`);

      imageLayers.current.forEach((layer, index) => {
        if (!layer) return;
        const motion = getSceneMotion(nextProgress, index);
        layer.style.opacity = `${motion.opacity}`;
        layer.style.transform = `translate3d(${motion.x}vw, ${motion.y}vh, 0) scale(${motion.scale})`;
      });

      const nextIndex = stateIndex(getStoryState(nextProgress));
      if (nextIndex !== activeIndexRef.current) {
        activeIndexRef.current = nextIndex;
        setActiveIndex(nextIndex);
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
        scrub: 0.2,
        invalidateOnRefresh: true,
        onUpdate: ({ progress }) => updateVisuals(progress),
      });
      updateVisuals(trigger.progress);
    };

    void setupScroll();

    return () => {
      disposed = true;
      trigger?.kill();
    };
  }, []);

  return (
    <section
      ref={wrapper}
      className="g-story"
      aria-label="Leistungen von der Planung bis zum Service"
      data-state={chapters[activeIndex]?.id}
      style={{ '--g-story-progress': '0%' } as CSSProperties}
    >
      <div className="g-story-stage">
        <div className="g-story-visual" aria-hidden="true">
          {chapters.map((chapter, index) => (
            <figure
              className={`g-story-image g-story-image--${chapter.id}`}
              key={chapter.id}
              ref={(layer) => {
                imageLayers.current[index] = layer;
              }}
              style={{
                opacity: index === 0 ? 1 : 0,
                transform: `translate3d(${index === 0 ? 0 : 10}vw, 0, 0) scale(${index === 0 ? 1 : 0.945})`,
              }}
            >
              <img
                src={versionGStoryAssetUrl(baseUrl, chapter.asset)}
                alt=""
                width={chapter.asset.width}
                height={chapter.asset.height}
                loading="eager"
                fetchPriority={index === 0 ? 'high' : 'auto'}
                decoding="async"
              />
            </figure>
          ))}
        </div>
        <div className="g-story-copy-stack">
          {chapters.map((chapter, index) => (
            <ChapterContent
              key={chapter.id}
              chapter={chapter}
              index={index}
              activeIndex={activeIndex}
              baseUrl={baseUrl}
            />
          ))}
        </div>
        <div
          className="g-progress"
          role="group"
          aria-label="Fortschritt der Leistungs-Story"
        >
          <strong>
            <span>{chapters[activeIndex]?.number}</span> / 04
          </strong>
          <ol>
            {chapters.map((chapter, index) => (
              <li
                className={index === activeIndex ? 'is-active' : ''}
                aria-current={index === activeIndex ? 'step' : undefined}
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
