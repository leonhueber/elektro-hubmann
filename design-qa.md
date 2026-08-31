# Design QA – image-based Version G story

## Visual truth

- `C:/Users/hueberl/AppData/Local/Temp/codex-clipboard-fc040fd0-d062-4ff7-afa1-9958ed4f1fa0.png` – planning
- `C:/Users/hueberl/AppData/Local/Temp/codex-clipboard-6b33bccc-2d70-4be6-882f-9d0537336cfe.png` – installation
- `C:/Users/hueberl/AppData/Local/Temp/codex-clipboard-30019ed9-674d-4e60-82a3-6fa4417e9bb5.png` – photovoltaic
- `C:/Users/hueberl/AppData/Local/Temp/codex-clipboard-4c5cad6b-110d-4250-95ba-48343ec0462a.png` – service

All four references are 1448 × 1086 px. They define one desktop scroll story with four states. The implementation was captured at a CSS viewport of 1448 × 1086 px and DPR 1. The browser content screenshots are 1433 × 1075 px because the visible browser content excludes its chrome and scrollbar; paired comparisons normalize both sides to the 1448 × 1086 reference size.

## Implementation evidence

- Planning: `.codex-audit/image-story/qa3-1448-planning.png`
- Installation: `.codex-audit/image-story/qa2-1448-installation.png`
- Photovoltaic: `.codex-audit/image-story/qa2-1448-photovoltaic.png`
- Service: `.codex-audit/image-story/qa2-1448-service.png`
- Full paired comparisons: `.codex-audit/image-story/compare3-planning.jpg`, `.codex-audit/image-story/compare2-installation.jpg`, `.codex-audit/image-story/compare2-photovoltaic.jpg`, `.codex-audit/image-story/compare2-service.jpg`

Focused comparison captures were not necessary: the native-resolution full-state composites make the header, typography, CTA proportions, product edges, progress rail, and background transitions legible.

## Iteration log

1. Replaced the Blender/canvas sequence and grey render surfaces with four purpose-made, unbranded image assets on a seamless white background.
2. First pass findings: P2 – visual objects were too small; title wraps and CTA proportions diverged; the wallbox source exposed a rectangular background boundary.
3. Corrected object scale, explicit title line breaks, CTA sizing and spacing; regenerated the wallbox image with a pure white edge-to-edge surface.
4. Second pass finding: P2 – the planning house sat too close to the progress rail.
5. Reduced planning scale from 1.18 to 1.12 and shifted it left. The third planning capture verifies clear separation and alignment.

## Final surface review

- Typography: Inter Tight and Inter, with deliberate desktop line breaks matching the references.
- Layout: left editorial column, large central object stage, right progress rail; mobile switches to four complete vertical chapters.
- Color: white, black/anthracite, and restrained Hubmann red only.
- Imagery: high-resolution WebP assets, no embedded Hubmann or manufacturer branding, no captions, watermarks, or visible image bounds.
- Motion: normal page scrolling with GSAP-controlled opacity, scale, and lateral transitions; no wheel interception.
- Accessibility: semantic headings, descriptive alt text, inactive story links removed from tab order, `aria-current` on the active step, and complete static content for reduced motion and widths up to 860 px.
- Responsive checks: 1440 × 1024, 1024 × 768, 768 × 1024, and 390 × 844; no horizontal overflow found.
- Interaction check: navigation, CTAs, mobile disclosure menu, and chapter links inspected. Browser console had no errors or warnings.

## Intentional differences

- The live site retains the official two-line company logo and the required information bar instead of copying the mockup header verbatim.
- Product visuals intentionally omit the mockups' fictional Hubmann/product branding.
- Fine blueprint annotations are simplified so they remain decorative and do not introduce unreadable generated text.

## Technical checks

- Astro check: 0 errors, 0 warnings, 0 hints.
- ESLint: passed.
- Vitest: 15/15 tests passed.
- Production build: 20 static pages built successfully.

final result: passed
