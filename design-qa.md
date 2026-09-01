# Design QA – project gallery and section separator

## Comparison target

- Source visual truth: `C:/Users/hueberl/AppData/Local/Temp/codex-clipboard-268618b4-418d-4deb-a6c5-65c7b99214b3.png` (1487 × 1058 px).
- Browser-rendered implementation: `.codex-audit/projects-gallery-implementation-v2.png` (1487 × 1058 px, normalized from the section capture).
- Full-view comparison: `.codex-audit/projects-gallery-comparison-v2.png`.
- Mobile evidence: `.codex-audit/projects-gallery-mobile-v1.png` at 390 × 844 CSS px, DPR 1.
- Separator evidence: `.codex-audit/company-contact-separator-v1.png`.
- Desktop capture viewport: 1488 × 1400 CSS px, DPR 1; section crop normalized only to remove the scrollbar gutter and align it with the source dimensions.
- State: project section at `#projekte`; no interaction state active.

The full-view composite keeps the complete heading, all six cards, titles, categories, rules, image crops, and white-space rhythm readable. A separate focused crop was not needed because every fidelity-critical detail remains legible at the comparison scale.

## Findings

- No actionable P0, P1, or P2 differences remain.
- Fonts and typography: existing Inter Tight/Inter typography is preserved. Heading size, compact project titles, muted categories, weights, line heights, and wrapping follow the selected mockup.
- Spacing and layout rhythm: the section uses a 1392 px editorial frame, two-column introduction, single hairline rule, and a three-by-two gallery. The normalized section height is within roughly 2% of the source. Mobile collapses to one column without horizontal overflow.
- Colors and visual tokens: existing white, black, muted gray, and restrained red Hubmann tokens remain unchanged. No new radii, shadows, gradients, or card chrome were introduced.
- Image quality and asset fidelity: six distinct 1280 × 853 WebP assets match the residential, renovation, commercial, hospitality, photovoltaic, and KNX subjects. Total delivered gallery image weight is about 612 KB.
- Copy and content: all six supplied project titles and the selected category labels are present and legible.
- Section transition: a semantic hairline separator now creates a clear break between the company block and the Fachgeschäft/contact area.
- Interaction and accessibility: images retain descriptive alt text and explicit dimensions. Browser console contains no errors or warnings.

## Comparison history

1. Initial implementation: `.codex-audit/projects-gallery-viewport-v1.png`.
   - P2: the section was approximately 118 px taller than the source because the introduction and bottom padding were too generous.
   - Fix: tightened project-only vertical padding, heading size, heading rule spacing, and gallery offset.
2. Final implementation: `.codex-audit/projects-gallery-viewport-v2.png` and `.codex-audit/projects-gallery-comparison-v2.png`.
   - Post-fix section height is 1074.7 CSS px versus a 1058 px source, with matching card proportions and row rhythm.

## Technical verification

- Vitest: 13/13 tests passed.
- Astro production build: 0 errors, 0 warnings, 7 static pages built successfully.
- Desktop and 390 px mobile states rendered in the in-app browser.
- Mobile document width: 375 CSS px with no horizontal overflow; gallery card width: 347 CSS px.
- Browser console: no errors or warnings.

## Follow-up polish

- P3: the generated project photography intentionally differs in exact scene details from the conceptual mockup while preserving its composition and art direction.

final result: passed
