---
name: TasteFinder
colors:
  surface: '#f9f9ff'
  surface-dim: '#d3daef'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3ff'
  surface-container: '#e9edff'
  surface-container-high: '#e1e8fd'
  surface-container-highest: '#dce2f7'
  on-surface: '#141b2b'
  on-surface-variant: '#5b403f'
  inverse-surface: '#293040'
  inverse-on-surface: '#edf0ff'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#7c5800'
  on-secondary: '#ffffff'
  secondary-container: '#feb700'
  on-secondary-container: '#6b4b00'
  tertiary: '#5e39e0'
  on-tertiary: '#ffffff'
  tertiary-container: '#7757fa'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdea8'
  secondary-fixed-dim: '#ffba20'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5e4200'
  tertiary-fixed: '#e6deff'
  tertiary-fixed-dim: '#cabeff'
  on-tertiary-fixed: '#1c0062'
  on-tertiary-fixed-variant: '#4816cb'
  background: '#f9f9ff'
  on-background: '#141b2b'
  surface-variant: '#dce2f7'
typography:
  display-lg:
    fontFamily: DM Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: DM Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: DM Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: DM Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: DM Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: DM Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: DM Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: DM Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: DM Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-max-width: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style
The design system is built to evoke an immediate appetite and a sense of effortless discovery. The brand personality is **Friendly, Confident, and Appetizing**, positioning itself as a premium but accessible culinary authority. 

The visual style is **Corporate Modern with Tactile Warmth**. It avoids the sterility of typical SaaS platforms by using soft shadows, high-quality food photography as a primary UI element, and a warm-neutral base. The aesthetic is "food-forward," meaning the interface recedes to let vibrant dish imagery take center stage, while primary red accents provide a confident energy that drives conversion and action.

## Colors
This design system utilizes a high-energy primary red to signal flavor and urgency, balanced by a sophisticated palette of warm neutrals and functional accents.

- **Primary (#E23744):** A vibrant coral-red used for the most important actions, branding, and status indicators.
- **Secondary / Gold (#FFB800):** Reserved specifically for "Top Ranked" badges, star ratings, and premium curated content.
- **Tertiary / AI Sparkle (#7C5CFF):** A soft, modern violet used as a secondary accent for AI-driven recommendations and intelligent search features.
- **Neutrals:** The background uses an off-white (#F8F9FA) to reduce glare while maintaining a clean look. Text uses a deep charcoal (#111827) for maximum legibility and WCAG AA compliance.
- **Semantic:** Success uses a deep forest green, and warnings use a warm amber to maintain the overall "warm" palette.

## Typography
The system uses **DM Sans** across all levels to maintain a modern, geometric, yet friendly appearance. 

The hierarchy is intentionally "top-heavy" to give restaurant names and dish titles a commanding presence. Large headlines use tighter letter-spacing and bold weights to feel impactful and editorial. Body text is kept at a comfortable 16px minimum to ensure readability on various screens, while labels utilize a slightly heavier weight (Medium 500) to stand out against the soft UI containers.

## Layout & Spacing
This design system employs a **12-column fluid grid** for desktop and a **single-column stack** for mobile. 

A strict 8px spacing scale (8, 16, 24, 32, 40, 48, 64) is used to ensure rhythm across all components. Content should be centered in a container with a maximum width of 1280px to prevent excessive line lengths on ultra-wide monitors. On mobile, margins are reduced to 16px to maximize the "edge-to-edge" impact of food imagery.

## Elevation & Depth
Depth is achieved through **Ambient Shadows** and **Tonal Layering**. 

The base layer is the background (#F8F9FA). Cards and primary containers sit on a "Level 1" elevation, using a white background (#FFFFFF) and a very soft, diffused shadow (0px 4px 20px rgba(0,0,0,0.05)). 

For interactive elements like hover states on restaurant cards, the shadow deepens and the element slightly lifts. Overlays and modals use a "Level 2" elevation with a more pronounced shadow and a 20% backdrop blur (glassmorphism) on the scrim to maintain the warm color bleed from the content beneath.

## Shapes
The shape language is consistently **Rounded**, reflecting the approachable and organic nature of food. 

Standard components (buttons, small inputs) use a 0.5rem (8px) radius. Restaurant and food cards use a more generous **rounded-lg (16px)** radius to create a soft, premium feel. Budget selectors and search bars use a "Pill" shape (full roundedness) to distinguish them as high-interaction, tactile utility elements.

## Components
- **Restaurant Cards:** Feature a 16px corner radius, a subtle 1px border (#E9ECEF), and a bottom-aligned text gradient over the image for high legibility.
- **Primary Buttons:** Solid primary red (#E23744) with white text. 44px minimum height for mobile accessibility.
- **Segmented Controls:** For budget ($ / $$ / $$$), use a pill-shaped container with a light gray background and a white "floating" active state.
- **AI Explanation Block:** A specialized component with a 5% opacity purple background (#7C5CFF), a 4px solid purple left-border accent, and a "Sparkle" icon. 
- **Input Fields:** Soft 1px borders in warm gray. Location inputs must always include a map-pin icon (left-aligned) and a "Current Location" action (right-aligned) in primary red.
- **Skeleton Loaders:** Use a subtle "shimmer" animation with a warm-gray gradient (#E9ECEF to #F8F9FA) to maintain the app's warmth even during loading states.
- **Chips/Filters:** Rounded-pill shapes with a primary red outline when active and a light gray background when inactive.