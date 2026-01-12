# IntellyWeave Design System

**Version:** 1.0.1
**Last Updated:** 2025-11-19

---

## Core Principles

1. **Semantic Color Usage** - Always use CSS variables, never hardcoded values
2. **Gray by Default** - Cards use gray (grey-500) unless a specific color is explicitly required
3. **Opacity-Driven Depth** - Use opacity variations for layering and hierarchy
4. **Minimal, Professional** - Subtle effects, low-opacity overlays, clean typography

---

## Color System

### Semantic Colors

Defined in `globals.css` as HSL variables:

```css
--background: 0 0% 9%;        /* Primary dark background */
--background_alt: 0 0% 14%;   /* Card backgrounds */
--foreground: 0 0% 18%;       /* Tertiary surfaces */
--foreground_alt: 0 0% 20%;   /* Borders, dividers, edges */
--primary: 0 0% 95%;          /* Primary text */
--secondary: 0 0% 50%;        /* Secondary text (gray) */
```

### Usage

```tsx
// ✅ Correct
className="bg-background_alt text-primary border-foreground_alt/40"

// ❌ Wrong
className="bg-[#242424] text-white border-white/40"
```

### Opacity Scale

Standard opacity levels for consistency:

- **5-10%** - Subtle gradient backgrounds
- **20-30%** - Badge backgrounds, secondary borders
- **40-60%** - Primary borders, network edges, accent elements
- **60-80%** - Hover states
- **70-90%** - Card overlays, selected states
- **95%** - Tooltips, modals

---

## Typography

### Size Scale

```tsx
text-[10px]  // Badges, metadata
text-[12px]  // Chart labels, small UI
text-[13px]  // Secondary content, descriptions
text-sm      // Primary content (14px)
text-[16px]  // Headings, titles
```

### Line Height

```tsx
leading-tight    // Compact data (1.25)
leading-snug     // Secondary text (1.375)
leading-relaxed  // Primary content (1.625)
```

### Font Weight

```tsx
font-normal      // Body text
font-medium      // Emphasis
font-semibold    // Headings, labels
```

---

## Spacing

### Component Padding

```tsx
p-4       // Standard card padding (16px)
p-2.5     // Nested content (10px)
space-y-3 // Vertical sections (12px)
space-y-2 // Nested items (8px)
gap-2     // Flex/grid gaps (8px)
```

### Indentation

```tsx
pl-3      // Standard indent (12px)
pl-5      // Nested indent (20px)
```

---

## Component Patterns

### Card (Default)

Cards use **gray by default** unless a specific color is explicitly required:

```tsx
<Card className="
  w-full
  border-l-4 border-grey-500/40
  bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent
  hover:border-grey-500/60
  transition-all duration-300 ease-in-out
  backdrop-blur-sm
  shadow-lg
  rounded-xl
">
  <div className="p-5 space-y-3">
    {children}
  </div>
</Card>
```

**Key Features:**
- 4px left border in gray (40% opacity)
- Diagonal gradient (10% → 5% → transparent)
- Hover state increases opacity to 60%
- Light backdrop blur for depth
- Charts use p-5, other cards use p-4

### Nested Card

```tsx
<Card className="bg-background_alt/80 border border-foreground_alt/25 shadow-sm">
  <div className="flex">
    <div className="w-1 bg-grey-500/40 rounded-l-md" />
    <div className="flex-1 p-2.5 space-y-1.5">
      {content}
    </div>
  </div>
</Card>
```

**Key Features:**
- Vertical accent bar (4px wide) in gray
- 80% background opacity for layering
- 25% border opacity for subtle definition

### Badge

```tsx
// Colored (only when explicitly required)
<Badge className="bg-{color}-500/20 text-{color}-300 border-{color}-500/30 text-[10px]">
  {label}
</Badge>

// Neutral metadata (default)
<Badge variant="outline" className="border-foreground_alt/30 text-[10px] text-secondary">
  {count}
</Badge>
```

### Collapsible Section

```tsx
<Collapsible>
  <CollapsibleTrigger className="
    flex items-center gap-2 text-sm text-secondary
    hover:text-primary transition-colors group
  ">
    <ChevronRight className="h-3.5 w-3.5 transition-transform" />
    <span className="group-hover:underline">{title}</span>
  </CollapsibleTrigger>

  <CollapsibleContent className="mt-2 pl-5 border-l-2 border-foreground_alt/30">
    {content}
  </CollapsibleContent>
</Collapsible>
```

---

## Visual Effects

### Transitions

```tsx
transition-all duration-300 ease-in-out  // Comprehensive (borders, shadows)
transition-colors                        // Color changes only
transition-transform                     // Transforms (chevrons, etc.)
```

### Backdrop Blur

```tsx
backdrop-blur-sm  // Cards (4px blur)
backdrop-blur-md  // Modals, overlays (12px blur)
```

### Shadows

```tsx
shadow-sm   // Nested elements
shadow-lg   // Primary cards
shadow-xl   // Floating elements (tooltips)
```

---

## Borders

### Widths & Positions

```tsx
border           // 1px standard
border-l-4       // 4px left accent (role indicator)
border-l-2       // 2px left (collapsible content)
```

### Opacity Patterns

```tsx
border-foreground_alt/20        // Minimal separation
border-foreground_alt/30        // Standard borders
border-{color}-500/40           // Primary role borders
hover:border-{color}-500/60     // Hover states
```

### Radius

```tsx
rounded       // 4px - small elements
rounded-md    // 6px - badges, pills
rounded-lg    // 8px - cards
rounded-xl    // 12px - large containers
```

---

## Charts & Data Visualization

### Chart Container (Default Gray)

```tsx
<div className="
  w-full border-l-4 border-grey-500/40
  bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent
  backdrop-blur-sm shadow-lg
  hover:border-grey-500/60 transition-all duration-300
  rounded-xl
">
  <div className="p-5 space-y-3">
    {/* Chart content */}
  </div>
</div>
```

### Chart Elements

```tsx
// Grid
<CartesianGrid stroke="hsl(var(--foreground_alt) / 0.2)" />

// Axes
tick={{ fill: "hsl(var(--secondary))", fontSize: 12 }}
axisLine={{ stroke: "hsl(var(--foreground_alt))" }}

// Tooltip
<div className="bg-background/95 border border-foreground_alt/40 rounded-lg px-3 py-2 shadow-xl">
  <p className="text-[13px] text-primary font-medium">{label}</p>
  <p className="text-[12px]" style={{ color: seriesColor }}>{value}</p>
</div>
```

### Network Chart Edges

Network edges use `foreground_alt` with varying opacity for visibility:

```tsx
// Edge configuration
edges: {
  width: 1.5 + strength * 3,  // 1.5-4.5px based on strength
  color: {
    color: `hsl(var(--foreground_alt) / ${0.4 + strength * 0.2})`,      // Base: 40-60%
    hover: `hsl(var(--foreground_alt) / ${0.65 + strength * 0.15})`,    // Hover: 65-80%
    highlight: `hsl(var(--foreground_alt) / ${0.75 + strength * 0.15})` // Select: 75-90%
  },
  shadow: false
}
```

**Key Points:**
- Edges are dark gray (not bright accent colors)
- Width: 1.5-4.5px based on relationship strength
- Opacity increases on hover/select for visibility
- No shadows on edges for cleaner appearance

---

## Common Anti-Patterns

### ❌ Don't Use Hardcoded Colors

```tsx
// Wrong
bg-[#0B0E11] text-white border-white/20 rgba(255,255,255,0.6)

// Correct
bg-background_alt text-primary border-foreground_alt/20 hsl(var(--secondary))
```

### ❌ Don't Use Colors Without Explicit Need

```tsx
// Wrong (using blue when gray is sufficient)
<Card className="border-l-4 border-blue-500/40 bg-gradient-to-br from-blue-500/10...">

// Correct (default gray)
<Card className="border-l-4 border-grey-500/40 bg-gradient-to-br from-grey-500/10...">
```

### ❌ Don't Skip Gradient Pattern

```tsx
// Wrong (flat card)
<Card className="bg-background_alt border border-foreground_alt/20">

// Correct (gradient)
<Card className="
  border-l-4 border-grey-500/40
  bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent
">
```

### ❌ Don't Mix Opacity Patterns

```tsx
// Wrong (inconsistent opacities)
border-grey-500/15 bg-grey-500/35

// Correct (standard scale)
border-grey-500/40 bg-grey-500/10
```

---

## Accessibility

- **Contrast:** Primary text (95% lightness) provides strong contrast on dark backgrounds
- **Focus States:** All interactive elements have clear hover/focus indicators
- **Semantic HTML:** Use proper heading hierarchy and landmark elements
- **Motion:** All animations respect `prefers-reduced-motion`

---

## Quick Reference

```tsx
// Standard card pattern (gray by default)
"w-full border-l-4 border-grey-500/40 bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent"
"hover:border-grey-500/60 transition-all duration-300 backdrop-blur-sm shadow-lg rounded-xl"

// Typography hierarchy
"text-[16px] font-semibold text-primary"        // Title
"text-[13px] text-secondary leading-relaxed"    // Description
"text-[10px] text-secondary"                    // Metadata

// Common spacing
"p-5 space-y-3"              // Chart card content
"p-4 space-y-3"              // Standard card content
"flex items-center gap-2"    // Inline elements
"mt-2 pl-5 border-l-2"       // Nested indentation
```

---

## File References

- **Colors & Variables:** `frontend/app/globals.css`
- **Tailwind Config:** `frontend/tailwind.config.ts`
- **Component Examples:**
  - `frontend/app/components/chat/displays/Intelligence/IntelligenceAgentMessage.tsx`
  - `frontend/app/components/chat/displays/ChartTable/BarDisplay.tsx`