# CyberCase Design Language

> **IMPORTANT GOVERNANCE RULE**  
> Any new production UI color, major component visual pattern, or semantic visual treatment must conform to this document. If a new design requirement cannot be expressed using this system, **DESIGN.md must be intentionally updated rather than introducing ad-hoc styling.**

---

## 1. Product Character

CyberCase is a specialized investigative case-analysis workspace.

### The product must feel like:
- An **investigative case file**
- A **legal / analytical dossier**
- A **professional research brief**
- A **modern document workspace**

### The product must NOT feel like:
- An AI SaaS dashboard
- A SOC console or dark-mode security operations center
- A hacker UI with neon glowing text
- A startup gradient interface
- A colorful administrative dashboard
- A generic component-library demo

The **case content** must visually dominate the interface. UI chrome (sidebar, headers, borders, navigation) must remain restrained, quiet, and secondary.

---

## 2. Core Principles

1. **Content-First Document Aesthetic**: Whitespace, crisp typography, and thin horizontal rules structure information. Large decorative card wrappers are avoided.
2. **Restrained Visual Hierarchy**: Information hierarchy is established through typography size, weight, letter spacing, alignment, and dividers — **never** through rainbow color-coding.
3. **60 / 30 / 10 Visual Balance**: The majority of the surface is warm paper, structured with neutral ink and stone, with brand accent and semantic annotations strictly limited to small accents.
4. **Strict Semantic Annotation Rule**: **Semantic colors are annotations, never large surfaces.** They are restricted to tiny dots, thin rules, small tags, and subtle text accents.
5. **Provable Source Traceability**: The ability to trace analytical claims to original case evidence is central to CyberCase, presented through quiet document annotations rather than loud buttons.
6. **Anti-AI-Slop Discipline**: Avoid generic boilerplate copy, unnecessary card-in-card containers, repetitive bilingual labels, and decorative metrics lacking investigative value.

---

## 3. 60 / 30 / 10 Palette

The visual balance of CyberCase is locked to the **60 / 30 / 10** visual distribution principle:

```
┌────────────────────────────────────────────────────────────┐
│ 60% — Paper / Background (#F6F3EA / #FCFAF5)              │
│ Warm, calm, readable document surfaces and application canvas│
├────────────────────────────────────────────────────────────┤
│ 30% — Neutral Structure (#262522 / #68645D / #D5CEC1)      │
│ Primary ink, body typography, navigation, structural lines │
├────────────────────────────────────────────────────────────┤
│ 10% — Brand Accent & Semantic Annotations                  │
│ Oxblood (#9A4438), Evidence (#356C8A), MITRE (#6654A3)     │
└────────────────────────────────────────────────────────────┘
```

- **60% (Warm Paper / Neutral Background)**: Application canvas, sidebar background, reading surfaces, document workspaces. Avoid pure white for normal application canvas; pure white is reserved for true PDF/rendered document sheets.
- **30% (Neutral Structure)**: Typography, navigation items, structural dividers, controls, neutral selected states.
- **10% (Brand Accent & Semantic Annotations)**: Selected navigation indicators, primary calls to action, high-attention findings, and small semantic annotations.

---

## 4. Core Color Tokens

| Token Name | Hex Value | Purpose |
| :--- | :--- | :--- |
| `--paper` | `#F6F3EA` | Primary application canvas, sidebar background, workspace backdrop |
| `--paper-raised` | `#FCFAF5` | Raised document surface, card reading area, input containers |
| `--ink` | `#262522` | Primary headings, titles, high-contrast text, primary action fill |
| `--ink-muted` | `#68645D` | Body text, secondary descriptions, metadata, subtitles |
| `--stone` | `#E4DED2` | Subdued backgrounds, nested surfaces, disabled controls |
| `--border` | `#D5CEC1` | Structural rules, dividers, subtle input borders, card boundaries |
| `--accent` | `#9A4438` | Oxblood primary brand accent, selected nav indicators, high-priority flags |
| `--accent-soft` | `#F2E3DE` | Soft brand highlight background, active navigation tint |

---

## 5. Semantic Annotation Colors

Semantic colors represent epistemic and analytical status. They must remain **tiny annotations** and must **never** become full card backgrounds.

| Semantic Purpose | Hex Value | Permitted Uses | Prohibited Uses |
| :--- | :--- | :--- | :--- |
| **Case Evidence** | `#356C8A` | Source links (`Source ↗`), evidence markers, popover left rule | Blue container cards, blue hero banners |
| **MITRE Context** | `#6654A3` | MITRE technique ID tag (`T1546.011`), external reference note | Full-page purple tint, large purple alert boxes |
| **Unresolved / Gaps** | `#A66A20` | Question indicator (`?`), unconfirmed point note | Yellow/amber warning banners, full yellow cards |
| **Established Fact** | `#4F725B` | Checkmark indicator (`✓`), verified fact note | Green dashboard widgets, green container cards |
| **Critical / High Attention** | `#9A4438` | High priority label, destructive actions | Red error alerts covering entire sections |

---

## 6. Color Usage Rules

1. **No arbitrary colors**: All colors must originate from the tokens in Sections 4 & 5.
2. **No gradients**: Gradient backgrounds, borders, or text fills are strictly prohibited.
3. **No neon colors**: Saturated high-luminance colors are never allowed.
4. **No cyber-blue dashboard aesthetic**: CyberCase is a dossier, not a SOC monitor.
5. **No large semantic surfaces**: Semantic colors are annotations only (dots, rules, labels).
6. **No full-section tinting**: Do not tint an entire section just because it represents an analytical state.
7. **No pure black**: Use `#262522` for high-contrast ink instead of `#000000`.
8. **Avoid pure white**: Use `#F6F3EA` and `#FCFAF5` for workspace surfaces; pure `#FFFFFF` is only permitted inside the PDF preview iframe.
9. **Accent communicates meaning**: Colors must serve an analytical purpose, not visual decoration.
10. **Color is not the sole indicator**: Every color indicator must be accompanied by explicit text or typography weight for accessibility.
11. **Restrain MITRE violet**: Violet must occupy less than 5% of any given viewport.
12. **Restrain amber & green**: Gaps and facts are styled as prose with small glyphs, not colored alert boxes.

---

## 7. Typography

### Font Family & Scale
- **Primary Font**: `Manrope`, system sans-serif fallback.
- **Monospace Font**: System monospace (`ui-monospace`, `monospace`) for technique IDs (`T1190`), ordinals (`01 / OVERVIEW`), and timestamps.

### Hierarchy Guidelines
- **Page Title**: `text-xl font-bold tracking-tight text-ink sm:text-2xl`
- **Section Heading**: `text-base font-bold tracking-tight text-ink sm:text-lg`
- **Eyebrow / Category**: `font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase`
- **Body Prose**: `text-xs leading-relaxed text-ink sm:text-[13px]`
- **Secondary Text / Notes**: `text-xs text-ink-muted leading-relaxed`
- **Metadata / Timestamps**: `text-[11px] text-ink-muted`

### Thai Typography & Localization
- Ensure comfortable Thai line height (`leading-relaxed` or `leading-normal`). Avoid tight vertical line spacing.
- **Single UI Language**: Do not mechanically duplicate every interface label in both Thai and English (e.g., avoid `WHY IT IS RELEVANT · เหตุผลที่เกี่ยวข้อง`). Use one primary interface language according to the current case locale.
- **Technical Terms**: Standard cybersecurity terminology remains English (`MITRE ATT&CK`, `Application Shimming`, `Remote System Discovery`, `PowerShell`).

---

## 8. Spacing and Density

- **Section Separation**: `space-y-6` to `space-y-8` between major thematic case sections.
- **Within Sections**: Compact vertical rhythm (`space-y-2` or `divide-y divide-line/60`) for rapid scanning.
- **Padding**: Modest padding (`p-4` to `p-6`). Avoid large empty container interiors (`p-12+` on normal content).
- **Prose Reading Width**: Constrain text containers to `max-w-3xl` or `max-w-4xl` for optimal document readability.

---

## 9. Borders, Radius, and Shadows

- **Dividers over Containers**: Prefer thin horizontal rules (`border-b border-line` or `divide-y divide-line/60`) over boxing everything in cards.
- **Border Color**: Subtle `#D5CEC1` (`border-line`). Avoid heavy high-contrast borders.
- **Radius**: Modest corner radius (`rounded-lg` / `8px` or `rounded-md` / `6px`).
- **No Pill Containers**: Never use `rounded-full` for content cards, inputs, or major buttons. Pills are reserved solely for compact single-word status tags.
- **No Nested Cards**: Do not place bordered cards inside other bordered cards.
- **Shadows**: Restrained and subtle (`shadow-xs` or `shadow-[0_1px_2px_rgba(39,39,39,0.03)]`). Floating popovers use `shadow-xl shadow-black/10`.

---

## 10. Buttons and Actions

### 1. Primary Action
- **Style**: Solid charcoal fill (`bg-primary` / `#262522`), light text (`text-ivory` / `#FCFAF5`), `rounded-lg`, `h-9` or `px-4 py-2`, `text-xs font-bold`.
- **Usage**: Main destructive or decisive actions (`Analyze Case`, `New Case`, `Generate Report`).

### 2. Secondary Action
- **Style**: Transparent or neutral surface (`bg-surface`), thin border (`border border-line`), charcoal text (`text-ink`), `hover:border-ink hover:bg-surface-hover`.
- **Usage**: Supplemental navigation or options (`Download PDF`, `View Report`, `Ask about this case`).

### 3. Tertiary / Text Action
- **Style**: Borderless or quiet text link (`text-ink-secondary hover:text-ink hover:underline`), optional small arrow (`↗` or `→`).
- **Usage**: Inline evidence inspection (`Source — Initial case description ↗`), expandable drawers (`คำอธิบายทางเทคนิค ▾`).

---

## 11. Navigation

- **Sidebar Background**: `#F6F3EA` (`bg-sidebar`).
- **Sidebar Dividers**: `#D5CEC1` (`border-line`).
- **Navigation Tabs**:
  - Inactive: `text-ink-secondary hover:bg-surface/70 hover:text-ink`
  - Active: Neutral raised surface (`bg-surface border-line text-ink font-bold`) with subtle left indicator or oxblood accent (`#9A4438`).
- **New Case Action**: Compact dark charcoal action (`bg-primary text-ivory rounded-lg h-9`), no isolated square container around the plus icon.
- **Consistency**: Do not give each navigation tab an arbitrary distinctive color.

---

## 12. Cards and Containers (Card Policy)

CyberCase does **NOT** treat cards as the default UI wrapper.

### Permitted Uses of Containers:
- Truly discrete bounded objects (e.g. initial intake composer, raw evidence items in Case Materials).
- Floating anchored inspection popovers.

### Prohibited Uses of Containers:
- Wrapping individual MITRE techniques in giant bordered cards.
- Wrapping individual timeline steps in separate cards.
- Wrapping individual facts or gaps in separate cards.
- **Section Card → Content Card → Status Card nesting**.

---

## 13. Badges and Status (Badge / Pill Policy)

- Badges must be **rare** and used only when status genuinely carries investigative weight:
  - `Provisional` (Report status)
  - `Candidate only` (External analytical mapping)
  - `High Priority` (Critical investigation gap)
- **Do not use pills for**:
  - Section headers
  - Technique counts with no decision value (e.g., remove `"8 techniques referenced"`)
  - Redundant taxonomy labels
  - Surrounding normal metadata

---

## 14. Source / Provenance Interaction

Source provenance connects analytical claims directly to raw user-submitted evidence.

- **Source Reference**: Styled as a quiet inline annotation:  
  `Source — Initial case description ↗`  
  Uses evidence color `#356C8A` for text or quiet neutral styling with a subtle evidence indicator.
- **Anchored Popover**:
  - Surface: Raised document surface (`#FCFAF5`), thin border (`#D5CEC1`).
  - Left Accent Rule: Thin `#356C8A` evidence border (`border-l-[3px] border-l-[#356C8A]`).
  - Typography: Primary ink (`#262522`), metadata in `#68645D`.
  - Elevation: Floating with restrained shadow (`shadow-xl shadow-black/10`).

---

## 15. Workspace-Specific Guidance

### Overview (`/overview`)
- Clean document brief layout organized into 6 clear sections.
- Flattened prose and timeline; MITRE associations presented as quiet analytical annotations.
- Facts and gaps indicated with quiet glyphs (`✓`, `?`), not saturated green/yellow blocks.

### Case Materials (`/materials`)
- Document-oriented presentation of user-authored evidence (initial narrative, clarifications, add-info).
- Thin evidence marker (`#356C8A`) on headers; avoids blue card collections.

### Technical Context (`/technical-context`)
- Flattened reference notes separated by thin horizontal rules (`divide-y divide-line/60`).
- Technique headings with small `#6654A3` ID tag; concise plain-language summary in main reading flow.
- Full MITRE definition tucked inside collapsible `คำอธิบายทางเทคนิค ▾`.
- Quiet 2-line external reference notice under header; no purple alert banner.

### Chat (`/chat`)
- Conversation integrated seamlessly into the case workspace.
- Avoids loud blue-user / gray-assistant bubbles; user messages distinguished through clean structure and evidence attribution.

### Report (`/report`)
- Workspace shell remains warm neutral (`#F6F3EA`).
- Embedded PDF viewer is the primary hero element, surrounded by quiet charcoal/neutral toolbar controls.

### New Case Intake (`/intake`)
- Focused case intake workspace. Large document-like narrative textarea (`#FCFAF5` on `#F6F3EA`).
- Primary action: Charcoal `#262522` button. No glowing inputs, neon borders, or hero gradients.

---

## 16. PDF / Print Guidance

PDF reports must look like formal investigative documents:
- **Paper**: White (`#FFFFFF`) or soft document white (`#FCFAF5`).
- **Headings**: `#262522` bold serif/sans-serif.
- **Body**: `#262522` or `#353330` with comfortable line height.
- **Rules & Borders**: `#D5CEC1`.
- **Accent**: `#9A4438` used sparingly for section bars or high-priority markers.
- **Restraint**: Saturated semantic colors (violet, blue, amber) are omitted or reduced to tiny grayscale/muted accents in formal PDF output.

---

## 17. Copy and Localization

- **Tone**: Objective, precise, non-promotional, non-theatrical.
- **Concrete Language**: State concrete case facts rather than generic AI boilerplate (e.g. `"The case states that Application Shimming was used to persist on startup"` instead of `"This technique is used as an analytical framework..."`).
- **Single Locale**: Keep interface labels in one language per case/locale; do not duplicate Thai and English on every header.

---

## 18. Accessibility

- **Contrast Ratios**: All text must exceed WCAG 2.1 AA contrast requirements against its background (`#262522` on `#F6F3EA` achieves 11.5:1; `#68645D` achieves 5.1:1).
- **Non-Color Indicators**: Every analytical state must include explicit text labels or glyphs alongside color accents.
- **Focus States**: High-visibility focus ring (`outline-2 outline-offset-2 outline-ink`) for keyboard navigation.
- **Motion Safety**: Respect `prefers-reduced-motion` across all transitions and animations.

---

## 19. Anti-AI-Slop Rules

1. **Do not put every concept in a card.**
2. **Do not use a different color for every semantic category.**
3. **Do not use gradients under any circumstance.**
4. **Do not add decorative metric pills without decision value.**
5. **Do not repeat English + Thai labels mechanically.**
6. **Do not create oversized trust-boundary banners.**
7. **Do not use generic filler copy.**
8. **Do not use decorative icons merely because a section exists.**
9. **Do not wrap plain prose in bordered boxes unnecessarily.**
10. **Do not create dashboard metrics when document-style information is more useful.**
11. **Do not let metadata become visually louder than case content.**
12. **Do not make MITRE visually more important than the incident.**
13. **Do not use rounded containers as the primary visual hierarchy.**
14. **Do not introduce a new color without updating DESIGN.md first.**

---

## 20. Do / Don't Examples

| Area | ❌ Don't (AI SaaS Slop) | ✅ Do (CyberCase Dossier) |
| :--- | :--- | :--- |
| **Technique Reference** | Giant purple card with badges, confidence scores, and raw MITRE dumps | Clean heading (`T1546.011`), concise explanation, quiet source link, thin divider |
| **Trust Notice** | Huge purple alert banner with exclamation icons | Quiet 2-line muted note under page header |
| **Unresolved Issues** | Bright yellow dashboard cards with warning icons | Clean prose paragraph with small `?` indicator and concrete rationale |
| **Established Facts** | Green checkmark cards with glowing borders | Clean prose with small `✓` glyph and inline source reference |
| **Source Provenance** | Bright blue pills with loud hover shadows | Quiet inline text `Source — Initial case description ↗` opening anchored popover |
| **Sidebar Action** | Outlined pill button with oversized icons | Compact solid charcoal button (`#262522`) with clean icon-label alignment |
| **Case Navigation** | Multi-colored rainbow navigation tabs | Neutral stone active tab with subtle oxblood (`#9A4438`) indicator |
