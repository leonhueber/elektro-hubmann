import type { CSSProperties } from 'react';
import { useEffect, useRef, useState } from 'react';
import {
  VERSION_G_STORY_CHAPTERS,
  versionGStoryAssetUrl,
  type VersionGStoryState,
} from '../../../config/version-g-story-assets';

export type HouseStoryState = VersionGStoryState;

type SceneMotion = {
  opacity: number;
  x: number;
  y: number;
  scale: number;
};

export type SceneMotionProfile = 'standard' | 'compact';

const chapters = VERSION_G_STORY_CHAPTERS;
const desktopScrollDistancePerChapter = 55;
const mobileScrollDistancePerChapter = 36;
const sceneMotionProfiles = {
  standard: {
    fadeDistance: 0.18,
    xTravel: 1.8,
    inactiveX: 32,
    yTravel: 0.7,
    inactiveY: 1.6,
    scaleTravel: 0.012,
    inactiveScale: 0.12,
  },
  compact: {
    fadeDistance: 0.12,
    xTravel: 0.65,
    inactiveX: 8,
    yTravel: 0.25,
    inactiveY: 0.5,
    scaleTravel: 0.004,
    inactiveScale: 0.035,
  },
} as const;

const clamp = (value: number) => Math.min(1, Math.max(0, value));
const smoothstep = (value: number) => {
  const safeValue = clamp(value);
  return safeValue * safeValue * (3 - 2 * safeValue);
};

export function getStoryState(progress: number): HouseStoryState {
  const value = clamp(progress);
  const index = Math.min(
    chapters.length - 1,
    Math.floor(value * chapters.length),
  );
  return chapters[index]!.id;
}

export function getChapterScrollProgress(chapterIndex: number) {
  const safeIndex = Math.min(chapters.length - 1, Math.max(0, chapterIndex));
  return (safeIndex + 0.5) / chapters.length;
}

export function getSceneMotion(
  progress: number,
  sceneIndex: number,
  profile: SceneMotionProfile = 'standard',
): SceneMotion {
  const motionProfile = sceneMotionProfiles[profile];
  const value = clamp(progress);
  const start = sceneIndex / chapters.length;
  const end = (sceneIndex + 1) / chapters.length;
  const fadeDistance = motionProfile.fadeDistance / chapters.length;
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
  const signedDistance = Math.max(
    -1,
    Math.min(1, (value - center) * chapters.length * 1.25),
  );
  const inactiveOffset = (1 - opacity) * (value < center ? 1 : -1);

  return {
    opacity,
    x:
      signedDistance * -motionProfile.xTravel +
      inactiveOffset * motionProfile.inactiveX,
    y:
      Math.abs(signedDistance) * motionProfile.yTravel +
      (1 - opacity) * motionProfile.inactiveY,
    scale:
      1 +
      Math.abs(signedDistance) * motionProfile.scaleTravel -
      (1 - opacity) * motionProfile.inactiveScale,
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
  compactMotion,
}: {
  chapter: (typeof chapters)[number];
  index: number;
  activeIndex: number;
  baseUrl: string;
  compactMotion: boolean;
}) {
  const active = index === activeIndex;
  const offset = (index < activeIndex ? -1 : 1) * (compactMotion ? 22 : 56);
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
  const [compactMotion, setCompactMotion] = useState(false);
  const activeIndexRef = useRef(0);

  const scrollToChapter = (chapterIndex: number) => {
    const root = wrapper.current;
    if (!root) return;

    const headerHeight =
      document.querySelector<HTMLElement>('.g-header-shell')?.offsetHeight ?? 0;
    const rootTop = window.scrollY + root.getBoundingClientRect().top;
    const storyStart = rootTop - headerHeight;
    const storyEnd = rootTop + root.offsetHeight - window.innerHeight;
    const storyDistance = Math.max(0, storyEnd - storyStart);
    const targetProgress = getChapterScrollProgress(chapterIndex);

    window.scrollTo({
      top: storyStart + storyDistance * targetProgress,
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        ? 'auto'
        : 'smooth',
    });
  };

  useEffect(() => {
    const root = wrapper.current;
    if (!root) return;

    const compactMotionQuery = window.matchMedia('(max-width: 860px)');
    let useCompactMotion = compactMotionQuery.matches;
    setCompactMotion(useCompactMotion);

    let disposed = false;
    let trigger: { kill: () => void; progress: number } | undefined;

    const updateVisuals = (progress: number) => {
      const nextProgress = clamp(progress);
      root.style.setProperty('--g-story-progress', `${nextProgress * 100}%`);

      imageLayers.current.forEach((layer, index) => {
        if (!layer) return;
        const motion = getSceneMotion(
          nextProgress,
          index,
          useCompactMotion ? 'compact' : 'standard',
        );
        const visible = motion.opacity > 0.001;
        layer.style.opacity = `${motion.opacity}`;
        layer.style.visibility = visible ? 'visible' : 'hidden';
        layer.style.willChange = visible ? 'transform, opacity' : 'auto';
        layer.style.transform = `translate3d(${motion.x}vw, ${motion.y}vh, 0) scale(${motion.scale})`;
      });

      const nextIndex = stateIndex(getStoryState(nextProgress));
      if (nextIndex !== activeIndexRef.current) {
        activeIndexRef.current = nextIndex;
        setActiveIndex(nextIndex);
      }
    };

    const handleMotionProfileChange = (event: MediaQueryListEvent) => {
      useCompactMotion = event.matches;
      setCompactMotion(event.matches);
      updateVisuals(trigger?.progress ?? 0);
    };
    compactMotionQuery.addEventListener('change', handleMotionProfileChange);

    const setupScroll = async () => {
      const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
        import('gsap'),
        import('gsap/ScrollTrigger'),
      ]);
      if (disposed) return;
      gsap.registerPlugin(ScrollTrigger);
      trigger = ScrollTrigger.create({
        trigger: root,
        start: () => {
          const headerHeight =
            document.querySelector<HTMLElement>('.g-header-shell')
              ?.offsetHeight ?? 0;
          return `top ${headerHeight}px`;
        },
        end: 'bottom bottom',
        scrub: useCompactMotion ? 0.06 : 0.12,
        invalidateOnRefresh: true,
        onUpdate: ({ progress }) => updateVisuals(progress),
      });
      updateVisuals(trigger.progress);
    };

    void setupScroll();

    return () => {
      disposed = true;
      compactMotionQuery.removeEventListener(
        'change',
        handleMotionProfileChange,
      );
      trigger?.kill();
    };
  }, []);

  return (
    <section
      ref={wrapper}
      className="g-story"
      aria-label="Leistungen von der Planung bis zu integrierten Energiesystemen"
      data-state={chapters[activeIndex]?.id}
      style={
        {
          '--g-story-progress': '0%',
          '--g-story-chapter-count': chapters.length,
          '--g-story-height': `${100 + chapters.length * desktopScrollDistancePerChapter}svh`,
          '--g-story-height-mobile': `${100 + chapters.length * mobileScrollDistancePerChapter}svh`,
        } as CSSProperties
      }
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
                visibility: index === 0 ? 'visible' : 'hidden',
                willChange: index === 0 ? 'transform, opacity' : 'auto',
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
              compactMotion={compactMotion}
            />
          ))}
        </div>
        <div
          className="g-progress"
          role="group"
          aria-label="Fortschritt der Leistungs-Story"
        >
          <strong>
            <span>{chapters[activeIndex]?.number}</span> /{' '}
            {String(chapters.length).padStart(2, '0')}
          </strong>
          <ol aria-label="Leistungsabschnitt wählen">
            {chapters.map((chapter, index) => (
              <li
                className={index === activeIndex ? 'is-active' : ''}
                key={chapter.id}
              >
                <button
                  type="button"
                  aria-label={`${chapter.number} ${chapter.label} anzeigen`}
                  aria-current={index === activeIndex ? 'step' : undefined}
                  onClick={() => scrollToChapter(index)}
                >
                  <span>{chapter.label}</span>
                </button>
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
