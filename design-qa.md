# Design QA – mobile shop actions

## Comparison target

- Source visual truth: `C:/Users/hueberl/AppData/Local/Temp/codex-clipboard-d450a540-b325-45bb-8277-dfb900aaaa30.png` (790 × 456 px), showing the oversized stacked mobile actions.
- Browser-rendered implementation: `.codex-audit/shop-mobile-actions-final.png` (375 × 812 px), captured from the in-app browser with a requested 390 × 844 CSS viewport, DPR 1.
- Focused implementation crop: `.codex-audit/shop-mobile-actions-focus-final.png` (375 × 216 px).
- Full comparison: `.codex-audit/shop-mobile-actions-source-vs-final.jpg`; the source was proportionally normalized to 375 × 216 px and stacked with the equally sized implementation crop.
- State: Fachgeschäft section at `#fachhandel`; no hover or focus state active.

## Findings

- No actionable P0, P1, or P2 differences remain after the responsive refinement.
- Fonts and typography: the established Inter typography, weights, and labels remain unchanged. Both action labels render at 0.88 rem and remain clearly legible.
- Spacing and layout rhythm: at 390 px the call button and route link now share one compact 48 px row. The button uses content-aware width instead of filling the viewport, and the following opening-hours rule sits closer to the actions.
- Colors and tokens: the existing white background, black call-to-action text, red border, and red route link are preserved.
- Image quality: this region contains no image assets; the logo and surrounding page assets remain unchanged.
- Copy and functionality: “Jetzt anrufen” and “Route planen” are unchanged and retain their existing working links.
- Responsiveness: at 390 px the actions measure 220 px and 103 px with a 22 px gap. At 320 px they wrap into two clean 48 px rows without horizontal overflow.
- Browser console: no errors or warnings.

## Comparison history

1. Source state: the full-width call button and separately stacked route link produced excess width and vertical whitespace on mobile.
2. Final implementation: changed the mobile action group to a wrapping horizontal row, reduced the button height from 52 px to 48 px, switched it to content-aware width, and tightened font size and outer spacing. The normalized comparison confirms the denser layout.

## Technical verification

- Prettier: affected CSS and QA files pass formatting checks.
- Vitest and Astro production build were run after the change.
- In-app browser verification covered 390 × 844 and 320 × 844 responsive viewports.
- No horizontal page overflow was detected at either mobile width.

## Follow-up polish

- No additional polish is required for this scoped change.

final result: passed
