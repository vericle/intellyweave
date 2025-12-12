export type NodeColorStyle = {
  border: string;
  background: string;
  highlight: { border: string; background: string };
  hover: { border: string; background: string };
};

/**
 * Get computed CSS variable value from document root
 */
const getCSSVar = (varName: string): string => {
  if (typeof window === 'undefined') return '0 0% 50%'; // SSR fallback
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
};

/**
 * Entity color mapping using Tailwind chart colors
 * Maps to CSS variables defined in globals.css
 * Colors are computed at runtime to resolve CSS variables
 */
export const baseEntityColorStyles: Record<string, NodeColorStyle> = {
  // Person entity types - chart-1 (orange-ish: 12 76% 61%)
  Person: {
    border: `hsl(${getCSSVar('--chart-1')})`,
    background: `hsl(${getCSSVar('--chart-1')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-1')})`, background: `hsl(${getCSSVar('--chart-1')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-1')})`, background: `hsl(${getCSSVar('--chart-1')} / 0.85)` },
  },
  PersonOfInterest: {
    border: `hsl(${getCSSVar('--chart-1')})`,
    background: `hsl(${getCSSVar('--chart-1')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-1')})`, background: `hsl(${getCSSVar('--chart-1')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-1')})`, background: `hsl(${getCSSVar('--chart-1')} / 0.85)` },
  },
  person: {
    border: `hsl(${getCSSVar('--chart-1')})`,
    background: `hsl(${getCSSVar('--chart-1')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-1')})`, background: `hsl(${getCSSVar('--chart-1')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-1')})`, background: `hsl(${getCSSVar('--chart-1')} / 0.85)` },
  },
  
  // Organization entity types - chart-2 (teal: 173 58% 39%)
  Organization: {
    border: `hsl(${getCSSVar('--chart-2')})`,
    background: `hsl(${getCSSVar('--chart-2')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-2')})`, background: `hsl(${getCSSVar('--chart-2')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-2')})`, background: `hsl(${getCSSVar('--chart-2')} / 0.85)` },
  },
  organization: {
    border: `hsl(${getCSSVar('--chart-2')})`,
    background: `hsl(${getCSSVar('--chart-2')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-2')})`, background: `hsl(${getCSSVar('--chart-2')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-2')})`, background: `hsl(${getCSSVar('--chart-2')} / 0.85)` },
  },
  
  // Location entity types - chart-3 (darker teal: 197 37% 24%)  
  Location: {
    border: `hsl(197 58% 50%)`, // Brightened for visibility
    background: `hsl(197 58% 50% / 0.8)`,
    highlight: { border: `hsl(197 58% 60%)`, background: `hsl(197 58% 60% / 0.9)` },
    hover: { border: `hsl(197 58% 60%)`, background: `hsl(197 58% 60% / 0.9)` },
  },
  location: {
    border: `hsl(197 58% 50%)`, // Brightened for visibility
    background: `hsl(197 58% 50% / 0.8)`,
    highlight: { border: `hsl(197 58% 60%)`, background: `hsl(197 58% 60% / 0.9)` },
    hover: { border: `hsl(197 58% 60%)`, background: `hsl(197 58% 60% / 0.9)` },
  },
  
  // Event entity types - chart-4 (yellow: 43 74% 66%)
  Event: {
    border: `hsl(${getCSSVar('--chart-4')})`,
    background: `hsl(${getCSSVar('--chart-4')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-4')})`, background: `hsl(${getCSSVar('--chart-4')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-4')})`, background: `hsl(${getCSSVar('--chart-4')} / 0.85)` },
  },
  event: {
    border: `hsl(${getCSSVar('--chart-4')})`,
    background: `hsl(${getCSSVar('--chart-4')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-4')})`, background: `hsl(${getCSSVar('--chart-4')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-4')})`, background: `hsl(${getCSSVar('--chart-4')} / 0.85)` },
  },
  
  // Law entity types - chart-5 (orange: 27 87% 67%)
  Law: {
    border: `hsl(${getCSSVar('--chart-5')})`,
    background: `hsl(${getCSSVar('--chart-5')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-5')})`, background: `hsl(${getCSSVar('--chart-5')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-5')})`, background: `hsl(${getCSSVar('--chart-5')} / 0.85)` },
  },
  law: {
    border: `hsl(${getCSSVar('--chart-5')})`,
    background: `hsl(${getCSSVar('--chart-5')} / 0.7)`,
    highlight: { border: `hsl(${getCSSVar('--chart-5')})`, background: `hsl(${getCSSVar('--chart-5')} / 0.85)` },
    hover: { border: `hsl(${getCSSVar('--chart-5')})`, background: `hsl(${getCSSVar('--chart-5')} / 0.85)` },
  },
  
  // Default for unknown types
  default: {
    border: `hsl(${getCSSVar('--secondary')})`,
    background: `hsl(${getCSSVar('--secondary')} / 0.5)`,
    highlight: { border: `hsl(${getCSSVar('--primary')})`, background: `hsl(${getCSSVar('--primary')} / 0.6)` },
    hover: { border: `hsl(${getCSSVar('--primary')})`, background: `hsl(${getCSSVar('--primary')} / 0.6)` },
  },
};

export function stringToHslColor(str: string, saturation = 50, lightness = 70): string {
  let hash = 0;
  for (let i = 0; i < str.length; i += 1) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

/**
 * Get chart color by index for bar charts and other visualizations
 * Uses the same Tailwind chart colors as network nodes
 */
export const getChartColorByIndex = (index: number): string => {
  const chartIndex = ((index % 5) + 1) as 1 | 2 | 3 | 4 | 5;
  const cssVar = `--chart-${chartIndex}`;
  
  if (typeof window === 'undefined') {
    // SSR fallback - return default colors
    const fallbackColors = ['12 76% 61%', '173 58% 39%', '197 37% 24%', '43 74% 66%', '27 87% 67%'];
    return `hsl(${fallbackColors[index % 5]})`;
  }
  
  const hslValue = getComputedStyle(document.documentElement).getPropertyValue(cssVar).trim();
  return `hsl(${hslValue})`;
};

export const getNodeColor = (type?: string, label?: string): NodeColorStyle => {
  if (type && baseEntityColorStyles[type]) {
    return baseEntityColorStyles[type];
  }

  const identifier = type && !baseEntityColorStyles[type] ? type : label || type || "default";
  const hueColor = stringToHslColor(identifier);

  return {
    border: hueColor,
    background: hueColor,
    highlight: { border: hueColor, background: hueColor },
    hover: { border: hueColor, background: hueColor },
  };
};