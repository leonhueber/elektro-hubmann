import type { CSSProperties } from 'react';
import { useEffect, useRef, useState } from 'react';
import { VERSION_G_STORY_CHAPTERS as chapters } from '../../../config/version-g-story-assets';
import annotations from '../../../config/house-v3-annotations.json';
import {
  FrameQueue,
  annotationsVisible,
  chapterAt,
  chapterProgress,
  frameAt,
  frameUrl,
  houseManifest,
  posterUrl,
  progressAtFrame,
  type HouseProfile,
} from '../../../lib/house-v3';

export default function HouseStory({ baseUrl }: { baseUrl: string }) {
  const root = useRef<HTMLElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const jump = useRef<(index: number) => void>(() => {});
  const [activeIndex, setActiveIndex] = useState(0);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const wrapper = root.current;
    const surface = canvas.current;
    const context = surface?.getContext('2d', { alpha: false });
    if (!wrapper || !surface || !context) {
      if (wrapper) wrapper.dataset.fallback = 'true';
      return;
    }
    const media = window.matchMedia('(max-width: 860px)');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const short = window.matchMedia('(max-height: 580px)');
    let profile: HouseProfile = media.matches ? 'mobile' : 'desktop';
    let queue: FrameQueue<ImageBitmap> | undefined;
    let disposed = false;
    let raf = 0;
    let target = 0;
    let currentChapter = 0;
    let fallbackGeneration = 0;
    let lastFallbackFrame = -1;
    let trigger:
      | { kill(): void; progress: number; start: number; end: number }
      | undefined;
    const fallbackController = new AbortController();
    const display = (image: ImageBitmap, progress: number) => {
      surface.width = image.width;
      surface.height = image.height;
      context.fillStyle = '#fff';
      context.fillRect(0, 0, surface.width, surface.height);
      context.drawImage(image, 0, 0);
      wrapper.dataset.frame = String(frameAt(progress, profile));
      wrapper.style.setProperty('--g-story-progress', `${progress * 100}%`);
      wrapper.style.setProperty(
        '--g-annotation-opacity',
        annotationsVisible(progress) ? '1' : '0',
      );
      const nextChapter = chapterAt(progress);
      if (nextChapter !== currentChapter) {
        currentChapter = nextChapter;
        setActiveIndex(nextChapter);
      }
      setReady(true);
    };
    const loadImage = async (url: string, signal: AbortSignal) => {
      const response = await fetch(url, { signal });
      if (!response.ok)
        throw new Error(`House asset unavailable: ${response.status}`);
      return createImageBitmap(await response.blob());
    };
    const fail = () => {
      wrapper.dataset.fallback = 'true';
      queue?.dispose();
      trigger?.kill();
      setReady(false);
    };
    const fallback = async (frame: number) => {
      if (frame === lastFallbackFrame) return;
      lastFallbackFrame = frame;
      const generation = ++fallbackGeneration;
      const index = chapterAt(progressAtFrame(frame));
      try {
        const image = await loadImage(
          posterUrl(baseUrl, profile, index),
          fallbackController.signal,
        );
        if (
          !disposed &&
          generation === fallbackGeneration &&
          frame === frameAt(target, profile)
        ) {
          display(image, chapterProgress(index));
        }
        image.close();
      } catch {
        if (!disposed && generation === fallbackGeneration) fail();
      }
    };
    const resetQueue = () => {
      queue?.dispose();
      fallbackGeneration++;
      lastFallbackFrame = -1;
      const outputProfile = profile;
      queue = new FrameQueue<ImageBitmap>(
        (frame, signal) =>
          loadImage(frameUrl(baseUrl, outputProfile, frame), signal),
        (image, frame) => {
          fallbackGeneration++;
          display(image, progressAtFrame(frame));
        },
        (frame) => {
          void fallback(frame);
        },
        {
          // Keep the larger desktop renders near the previous decoded-memory budget.
          capacity: profile === 'mobile' ? 14 : 12,
          concurrency: 3,
          step: houseManifest.profiles[profile].step,
          count: houseManifest.frameCount,
        },
      );
    };
    const update = (progress: number) => {
      target = progress;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() =>
        queue?.request(frameAt(target, profile)),
      );
    };
    const onProfile = () => {
      profile = media.matches ? 'mobile' : 'desktop';
      if (!reduced.matches && !short.matches) {
        resetQueue();
        update(target);
      }
    };
    const onMotion = () => {
      if (reduced.matches || short.matches) {
        queue?.dispose();
        queue = undefined;
      } else if (!trigger) {
        void setup();
      } else {
        resetQueue();
        update(trigger?.progress ?? 0);
      }
    };
    const setup = async () => {
      try {
        if (reduced.matches || short.matches) {
          wrapper.dataset.enabled = 'true';
          return;
        }
        const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
          import('gsap'),
          import('gsap/ScrollTrigger'),
        ]);
        if (disposed || wrapper.dataset.fallback === 'true') return;
        gsap.registerPlugin(ScrollTrigger);
        wrapper.dataset.enabled = 'true';
        if (!reduced.matches && !short.matches) resetQueue();
        trigger = ScrollTrigger.create({
          trigger: wrapper,
          start: () =>
            `top ${document.querySelector('.g-header-shell')?.getBoundingClientRect().height ?? 0}px`,
          end: 'bottom bottom',
          invalidateOnRefresh: true,
          onUpdate: ({ progress }) => update(progress),
          onRefresh: ({ progress }) => update(progress),
        });
        jump.current = (index) => {
          if (!trigger) return;
          window.scrollTo({
            top:
              trigger.start +
              (trigger.end - trigger.start) * chapterProgress(index),
            behavior: reduced.matches ? 'auto' : 'smooth',
          });
        };
        update(trigger.progress);
      } catch {
        if (!disposed) fail();
      }
    };
    media.addEventListener('change', onProfile);
    reduced.addEventListener('change', onMotion);
    short.addEventListener('change', onMotion);
    void setup();
    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      fallbackController.abort();
      queue?.dispose();
      trigger?.kill();
      media.removeEventListener('change', onProfile);
      reduced.removeEventListener('change', onMotion);
      short.removeEventListener('change', onMotion);
    };
  }, [baseUrl]);
  return (
    <section
      ref={root}
      className="g-story g-house-v3"
      data-model="r3"
      aria-label="Elektrotechnik im Haus entdecken"
      data-state={chapters[activeIndex]!.id}
      style={
        {
          '--g-story-height': '900svh',
          '--g-story-height-mobile': '750svh',
          '--g-story-chapter-count': chapters.length,
        } as CSSProperties
      }
    >
      <div className="g-story-stage">
        <div className="g-story-visual" aria-hidden="true">
          <picture className={`g-house-poster ${ready ? 'is-hidden' : ''}`}>
            <source
              media="(max-width: 860px)"
              srcSet={posterUrl(baseUrl, 'mobile', 0)}
            />
            <img
              src={posterUrl(baseUrl, 'desktop', 0)}
              width={houseManifest.profiles.desktop.width}
              height={houseManifest.profiles.desktop.height}
              alt=""
              fetchPriority="high"
            />
          </picture>
          <canvas
            ref={canvas}
            className={`g-house-canvas ${ready ? 'is-ready' : ''}`}
            width={houseManifest.profiles.desktop.width}
            height={houseManifest.profiles.desktop.height}
          />
          {(['desktop', 'mobile'] as const).map((profile) => {
            const config = houseManifest.profiles[profile];
            const annotationScale =
              config.width / (profile === 'mobile' ? 640 : 960);
            const labels = annotations[profile][chapters[activeIndex]!.id];
            return (
              <svg
                key={profile}
                className={`g-house-annotations g-house-annotations--${profile}`}
                viewBox={`0 0 ${config.width} ${config.height}`}
                aria-hidden="true"
              >
                {(profile === 'mobile' ? labels.slice(0, 1) : labels).map(
                  (projected) => {
                    const label = {
                      ...projected,
                      x: projected.x / annotationScale,
                      y: projected.y / annotationScale,
                      labelX: projected.labelX / annotationScale,
                      labelY: projected.labelY / annotationScale,
                    };
                    const width =
                      label.text.length * (profile === 'mobile' ? 14 : 11) + 28;
                    return (
                      <g
                        key={label.text}
                        transform={`scale(${annotationScale})`}
                      >
                        <line
                          x1={label.x}
                          y1={label.y}
                          x2={label.labelX}
                          y2={label.labelY}
                        />
                        <circle cx={label.x} cy={label.y} r="4" />
                        <rect
                          x={label.labelX - width / 2}
                          y={label.labelY - 18}
                          width={width}
                          height="36"
                          rx="3"
                        />
                        <text
                          x={label.labelX}
                          y={label.labelY}
                          dy=".35em"
                          textAnchor="middle"
                        >
                          {label.text}
                        </text>
                      </g>
                    );
                  },
                )}
              </svg>
            );
          })}
        </div>
        <div className="g-story-copy-stack">
          {chapters.map((chapter, index) => (
            <article
              key={chapter.id}
              className={`g-story-copy ${index === activeIndex ? 'is-active' : ''}`}
              aria-hidden={index !== activeIndex}
            >
              <p className="g-eyebrow">
                <strong>{chapter.number}</strong> · {chapter.label}
              </p>
              <h2>
                {chapter.title.map((line) => (
                  <span className="g-story-title-line" key={line}>
                    {line}
                  </span>
                ))}
              </h2>
              <p className="g-story-description">{chapter.description}</p>
              <ul
                className="g-house-components"
                aria-label="Komponenten im Modell"
              >
                {chapter.components.map((component) => (
                  <li key={component}>{component}</li>
                ))}
              </ul>
              <a
                className="g-outline-button"
                href={`${baseUrl}${chapter.href}`}
                tabIndex={index === activeIndex ? undefined : -1}
              >
                <span>{chapter.cta}</span>
                <span aria-hidden="true">→</span>
              </a>
              <span className="g-scroll-hint">
                {chapter.hint}
                <i aria-hidden="true">↓</i>
              </span>
            </article>
          ))}
        </div>
        <nav className="g-progress" aria-label="Leistungsabschnitt wählen">
          <strong>
            <span>{chapters[activeIndex]!.number}</span> / 06
          </strong>
          <ol>
            {chapters.map((chapter, index) => (
              <li
                className={index === activeIndex ? 'is-active' : ''}
                key={chapter.id}
              >
                <button
                  type="button"
                  aria-label={`${chapter.number} ${chapter.label} anzeigen`}
                  aria-current={index === activeIndex ? 'step' : undefined}
                  onClick={() => jump.current(index)}
                >
                  <span>{chapter.label}</span>
                </button>
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
