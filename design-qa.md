# Design QA – Version G Animated House Story

**Source visual truth**

- `C:/Users/hueberl/.codex/codex-remote-attachments/01a04a96-8142-7883-a181-7e8b120d4281/1090ECC8-E82C-4C9C-9468-9D1B9FE9BACD/1-Foto-1.jpg`
- Source: 1280 × 910 px, desktop planning state.

**Implementation evidence**

- `docs/version-g-qa/animation-planning-v2-1440x1024.png`
- `docs/version-g-qa/animation-transition-mid-v2-1440x1024.png`
- `docs/version-g-qa/animation-installation-v2-1440x1024.png`
- `docs/version-g-qa/animation-energy-v2-1440x1024.png`
- `docs/version-g-qa/animation-service-v2-1440x1024.png`
- `docs/version-g-qa/animation-mobile-start-v2-390x844.png`
- `docs/version-g-qa/animation-mobile-planning-v2-390x844.png`
- Normalized side-by-side comparison: `docs/version-g-qa/comparison-animation-planning-v2.png`

The implementation was captured at 1440 × 1024 and 390 × 844 CSS pixels at device scale factor 1. The 1280 × 910 source was proportionally fitted into a 1440 × 1024 white frame for the side-by-side comparison. The persistent design-version switcher is an intentional preview-only element and not part of the selected source design.

## Findings

- No actionable P0, P1 or P2 issue remains.
- Typography: Inter Tight and Inter retain the reference's reduced grotesk direction. Headings, body copy and progress labels remain legible at desktop and mobile widths.
- Spacing and layout: header, left copy, architectural house and right progress rail reproduce the source composition. Mobile reorganizes the same story into a vertically balanced sticky stage without horizontal overflow.
- Colors: pure white, anthracite and Hubmann red `#e30613`; no gradients, neon effects, colored surfaces or unnecessary shadows were introduced.
- Image quality: the previous primitive real-time model was replaced with four photorealistic architectural render layers. Planning, cutaway installation, PV/energy and completed service states share the same house identity, perspective, framing and studio background.
- Motion: normal scroll drives continuous opacity, horizontal translation, vertical translation and scale. The exterior exits right while the installation cutaway enters from the left; the energy state enters from the right and moves upward toward the roof; the completed house returns from the right. The page does not intercept the wheel or use scroll-jacking.
- Copy: the four requested story chapters, callouts and calls to action are present. Project facts that are not yet verified remain explicitly marked rather than fabricated.
- Responsiveness: the animated story is active at desktop, tablet and 390 px mobile widths. No document overflow was measured at 1440 or 390 px.
- Accessibility: one H1, semantic landmarks, skip link, focus states, keyboard-operable navigation and a static four-chapter fallback for `prefers-reduced-motion` are present. Decorative animated layers are hidden from assistive technology; the equivalent text remains live in the story.

## Comparison history

1. Previous implementation: the main visual was a visibly primitive Three.js house and widths up to 860 px received only static chapters. User feedback correctly classified this as a P1 mismatch with the requested animated story.
2. Asset correction: replaced the primitive model and its low-quality snapshots with four consistent photorealistic architectural renderings derived from the selected visual reference.
3. Motion correction: replaced four discrete state switches with a continuous scroll-progress animation and counter-directional side transitions. Mid-transition browser evidence shows both house layers moving in opposite directions.
4. Mobile correction: removed the viewport-width static fallback. The same sticky animated story now runs on mobile; only the explicit reduced-motion preference selects the static chapters.
5. Performance correction: converted final assets to quality-90 JPEGs of 160–190 KB each and removed unused Three.js packages. Animation uses only transform and opacity.

## Interaction checks

- All four story states reached by normal page scrolling.
- Mid-transition transforms and opacity values change continuously with scroll position.
- Sticky header and story stage remain stable throughout the sequence.
- Desktop and mobile progress indicators update with the active state.
- Main navigation, version navigation and CTAs remain operable.
- Browser console: no warnings or errors.
- Production build, Astro check, ESLint and nine Vitest assertions pass.

## Follow-up polish

- P3: replace preview project imagery and metadata once verified reference projects are available.
- P3: legal pages require Austrian legal and DSGVO review before production indexing.

final result: passed
