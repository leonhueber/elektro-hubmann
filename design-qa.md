# Design QA – Version G

**Source visual truth**

- `C:/Users/hueberl/.codex/codex-remote-attachments/01a04a96-8142-7883-a181-7e8b120d4281/1090ECC8-E82C-4C9C-9468-9D1B9FE9BACD/1-Foto-1.jpg`
- Source: 1280 × 910 px, desktop planning state.

**Implementation evidence**

- `docs/version-g-qa/01-planning-1440x1024.png`
- `docs/version-g-qa/02-installation-1440x1024.png`
- `docs/version-g-qa/03-energy-1440x1024.png`
- `docs/version-g-qa/04-service-1440x1024.png`
- `docs/version-g-qa/mobile-390x844.png`
- `docs/version-g-qa/tablet-768x1024.png`
- `docs/version-g-qa/tablet-1024x768.png`
- Normalized side-by-side comparison: `docs/version-g-qa/comparison-planning.png`

Viewport comparison used CSS pixels at device scale factor 1. Source and implementation were normalized to two 720 × 512 crops for the side-by-side comparison. Browser-owned inspection controls at the bottom edge are not part of the website.

## Findings

- No actionable P0, P1 or P2 issue remains.
- Typography: Inter Tight and Inter match the reference's reduced grotesk direction; hierarchy, wrapping and optical weights remain legible at all tested widths.
- Spacing and layout: header, left copy, central house and right progress rail reproduce the reference composition. The live variants bar is an intentional preview-only addition.
- Colors: pure white, anthracite and exact logo red `#e30613`; no gradients, large color fields or decorative effects were introduced.
- Image and model quality: the source photorealistic house was intentionally translated into a consistent real-time architectural 3D model so its shell, installation and PV layers can be animated. All four states use the same geometry and camera system.
- Copy: the requested four story chapters and calls to action are present. Unverified project data is clearly marked instead of fabricated.
- Responsive behavior: 1440 × 1024, 1024 × 768, 768 × 1024 and 390 × 844 were checked. The earlier 768 px horizontal overflow was fixed by containing the variants switcher.
- Accessibility: one H1, semantic page landmarks, skip link, focus states, labelled form controls, keyboard-accessible menu, useful alt text and reduced-motion chapters are present.

## Comparison history

1. Initial browser pass: 3D scene stayed blank because the environment preset suspended the scene while loading an external asset. Fix: removed the external environment dependency and retained local lighting. Post-fix evidence showed the house rendering without console errors.
2. First model pass: two roof planes read as floating slabs. Fix: replaced them with one procedural gable volume and aligned PV modules to the actual roof slopes.
3. Installation pass: exterior surfaces hid the interior. Fix: remove front/right shell and roof in the installation state while retaining floors, interior walls, lights, systems and the red route.
4. Tablet pass: seven preview links widened the document at 768 px. Fix: constrain scrolling to the variants navigation. Post-fix document width no longer exceeds the viewport.

## Interaction checks

- Normal page scrolling switches all four states; no wheel interception.
- Main navigation and nested Version-G routes resolve.
- Mobile menu remains a native keyboard-operable disclosure.
- Empty contact form exposes six invalid required controls.
- Completed contact form reports that online sending is unavailable and performs no network submission.
- Browser console: no application errors. Two upstream Three.js deprecation warnings are non-functional library warnings.

## Follow-up polish

- P3: replace design-preview project imagery and metadata once verified reference projects are available.
- P3: legal pages require Austrian legal and DSGVO review before production indexing.

final result: passed
