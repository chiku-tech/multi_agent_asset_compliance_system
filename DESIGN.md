---
name: Enterprise Dark
colors:
  surface: '#10131b'
  surface-dim: '#10131b'
  surface-bright: '#363942'
  surface-container-lowest: '#0b0e16'
  surface-container-low: '#181c23'
  surface-container: '#1c2027'
  surface-container-high: '#272a32'
  surface-container-highest: '#31353d'
  on-surface: '#e0e2ed'
  on-surface-variant: '#c1c6d7'
  inverse-surface: '#e0e2ed'
  inverse-on-surface: '#2d3039'
  outline: '#8b90a0'
  outline-variant: '#414754'
  surface-tint: '#adc7ff'
  primary: '#adc7ff'
  on-primary: '#002e68'
  primary-container: '#4a8eff'
  on-primary-container: '#00285b'
  inverse-primary: '#005bc0'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb695'
  on-tertiary: '#571e00'
  tertiary-container: '#ef6719'
  on-tertiary-container: '#4c1a00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc7ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7c2e00'
  background: '#10131b'
  on-background: '#e0e2ed'
  surface-variant: '#31353d'
  slate-900: '#0F172A'
  slate-800: '#1E293B'
  slate-700: '#334155'
  cobalt-primary: '#2563EB'
  emerald-success: '#10B981'
  amber-warning: '#F59E0B'
  rose-error: '#F43F5E'
  charcoal-bg: '#0B0E14'
typography:
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-page: 32px
  sidebar-width: 260px
  max-content-width: 1440px
---

## Brand & Style

The design system is engineered for **Asset Compliance AI**, a high-stakes enterprise environment where precision, data density, and systemic trust are paramount. The brand personality is authoritative and technical, functioning as a "digital auditor" that remains calm under the pressure of complex multi-agent workflows.

The visual style is a **Corporate Modern** approach with a heavy emphasis on **Tonal Minimalism**. It utilizes a deep, dark aesthetic to reduce eye strain during prolonged technical reviews, while using high-saturation chromatic accents to signal status and action.

**Key Emotional Responses:**
- **Reliability:** Through structured grids and consistent alignment.
- **Intelligence:** Through real-time streaming feedback and transparent RAG citations.
- **Urgency:** Through high-contrast status indicators (Rose/Amber) against the dark void.
- **Clarity:** Through functional typography and prioritized data hierarchy.

The UI should feel like a high-end terminal or command center—efficient, professional, and devoid of unnecessary decoration.

## Colors

The palette is anchored in a **Deep Slate and Charcoal** spectrum to create a sophisticated dark mode that prioritizes content legibility and reduces visual noise.

- **Primary (Cobalt):** Used for primary actions, active states, and focus indicators. It provides a "crisp" functional point of interest.
- **Success (Emerald):** Reserved strictly for positive audit outcomes and completed agent nodes.
- **Warning (Amber):** Used for system alerts, non-fatal agent errors, and cautionary compliance findings.
- **Error (Rose):** High-visibility red for critical failures, compliance breaches, and destructive actions (e.g., GDPR erasure).
- **Neutrals:** Use the `slate` range for surfaces. Backgrounds should use `charcoal-bg` (#0B0E14), while cards and modals use `slate-900` (#0F172A) to create subtle depth.

## Typography

The typography system balances modern accessibility with technical utility.

1.  **Headlines (Hanken Grotesk):** Provides a sharp, contemporary professional feel for page titles and section headers.
2.  **Body (Inter):** The workhorse for all data, forms, and descriptions. Chosen for its neutral character and excellent readability in dark modes.
3.  **Technical Data (JetBrains Mono):** Used for "Agent Progress" logs, streaming consoles, RAG citations, and any raw data outputs. This distinguishes human-centric content from machine-generated logs.

**Hierarchy Rules:**
- Use `label-caps` for table headers and small metadata tags.
- Use `code-sm` for all streaming console text to maintain a "terminal" aesthetic.

## Layout & Spacing

The layout uses a **Fixed Grid** approach for the main content area to ensure data tables and citation panels remain readable on ultra-wide monitors, while the sidebar remains a fixed anchor.

- **Grid Model:** 12-column grid for desktop with 24px gutters.
- **Sidebar:** A persistent left-hand navigation at 260px.
- **RAG Citation Panels:** Should slide in from the right or occupy a dedicated 4-column span on the right of the chat interface.
- **Streaming Consoles:** Should have a fixed height (e.g., 300px) with internal scrolling to prevent page jumping during long audit runs.

**Adaptations:**
- **Tablet:** Collapse sidebar into a hamburger menu; reduce page margins to 24px.
- **Mobile:** Single column layout; font sizes for headlines scale down using the `-mobile` tokens.

## Elevation & Depth

This design system avoids heavy shadows in favor of **Tonal Layers** and **Low-Contrast Outlines**. Depth is communicated through lightness shifts in the slate palette.

- **Level 0 (Background):** `charcoal-bg` (#0B0E14).
- **Level 1 (Cards/Sidebar):** `slate-900` (#0F172A) with a 1px border of `slate-800`.
- **Level 2 (Modals/Popovers):** `slate-800` (#1E293B) with a subtle ambient shadow (Black, 25% opacity, 12px blur).
- **Streaming Console:** Inset appearance using a slightly darker background than its container and a 1px `slate-700` border to create a "well" effect.

## Shapes

The shape language is **Soft (0.25rem)**. This keeps the UI looking precise and "engineered" rather than "friendly" or "bubbly."

- **Buttons & Inputs:** 4px (0.25rem) corner radius.
- **Cards & Citation Panels:** 8px (0.5rem) corner radius for larger containers.
- **Status Pills:** Fully rounded (pill-shaped) to distinguish them from functional buttons.

## Components

### Buttons & Inputs
- **Primary Action:** `cobalt-primary` background, white text, no border.
- **Ghost/Secondary:** Transparent background, `slate-700` border, `slate-200` text.
- **Inputs:** `slate-900` background, `slate-700` border. On focus, border changes to `cobalt-primary` with a subtle outer glow.

### Agent Progress Indicators
- **Step Component:** A vertical or horizontal sequence of nodes.
- **In-Progress:** Pulse animation on the current node using `cobalt-primary`.
- **Completed:** Solid `emerald-success` with a checkmark icon.
- **Error:** Solid `rose-error` with an "X" icon.

### Streaming Consoles
- Use a monospaced font (`code-sm`).
- Background: Black (#000000).
- Text: `slate-300` for standard logs, `emerald-success` for "Node Complete" events.

### RAG Citation Panels
- Stylized as a "Source Card."
- Header: Document name with a small icon.
- Body: Excerpt text in `body-sm`.
- Footer: Relevance score and "View Document" link in `cobalt-primary`.

### Status Badges
- **Audit Verdict:** Large banner at the top of results. "COMPLIANT" uses `emerald-success` (10% opacity) with `emerald-success` text/border. "NON-COMPLIANT" uses `rose-error` equivalents.