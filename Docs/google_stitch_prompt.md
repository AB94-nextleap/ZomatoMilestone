# Google Stitch Prompt: Premium Zomato AI Advisor Frontend

This document provides a highly detailed, professional prompt that you can copy and paste directly into **Google Stitch** (or other AI web-design/code generators) to create a premium, state-of-the-art interface.

It has been custom-tailored to reference the exact structural layout in [`context.md`](../context.md) and [`architecture.md`](../architecture.md), ensuring that the generated styling will align perfectly with your code. Crucially, it highlights the exact element IDs and classes required by your existing [`app.js`](../src/app/static/app.js) so that the interactive functionality does not break when the design is updated.

***

## Google Stitch Copy-Paste Prompt

```text
Act as a world-class senior frontend developer and UI/UX designer. I need you to generate a premium, state-of-the-art frontend UI design (HTML structure and custom CSS) for an application named "Zomato AI Restaurant Advisor". 

The application is an AI-powered, data-grounded restaurant recommendation system. It filters real Zomato dataset records deterministically and uses a Large Language Model (LLM) to rank the options and provide detailed, personalized "AI Explanations" for each recommendation.

### 1. High-Level UI Layout
Implement a modern split-panel layout:
- Left-Hand Panel (Sidebar): A sticky, scrolling sidebar hosting the search preferences form.
- Right-Hand Panel (Main Content): A dynamic viewport that transitions between different screen states (welcome, loading, results, empty state, and error state).
- The interface must be fully responsive, collapsing the sidebar into a collapsible/sliding panel or top bar on mobile screens (< 900px).

### 2. Design System & Aesthetics (WOW Factor)
- Theme: A curated, high-end Dark Mode. Use deep, premium dark hues (e.g., pitch-black backgrounds, charcoal cards, dark red undertones) rather than generic dark gray.
- Accent Color: A warm, vibrant food-inspired rose-red gradient (like Zomato's branding, e.g., HSL 353°, 100%, 62%) for buttons, highlights, active states, and focus states.
- Typography: Use Google Fonts. Import 'Outfit' (sans-serif) for clean, geometric UI controls, counts, and headers, and a serif font like 'Playfair Display' for editorial accents, quotes, and the AI explanation block text.
- UI Style: Modern Glassmorphism. Apply semi-transparent card panels with subtle backdrop-blur (e.g., backdrop-filter: blur(12px)), very thin borders (rgba white at 5-8% opacity), and soft, glowing drop shadows.
- Micro-interactions: Include smooth transitions on form elements, interactive hover effects (cards lift up slightly, borders glow with red accents on focus/hover), and subtle pulse animations for emojis/icons.

### 3. Page Views & Dynamic States (To Style)
- Welcome View: A welcoming onboarding card with an illustrated or animated element, guiding the user to input their preferences in the sidebar.
- Loading View: A modern shimmering skeleton screen representing both the AI summary container and a list of recommendation cards. Use a subtle linear-gradient shimmer keyframe animation.
- Results View:
  - AI Summary Banner: A prominent conversational bubble or alert box with a robot/AI icon, styling the AI-generated paragraph in a friendly, distinct manner.
  - Recommendations Cards (List): A stack of premium cards. Each card must represent a single restaurant.
- Empty State: A clean, centered illustration card showing no matching results, with a blue-hued visual box detailing troubleshooting/modification tips.
- Error State: A crimson-tinted card displaying system errors with clear advice.

### 4. Technical Constraints: IDs & Classes (CRITICAL)
Your generated HTML/CSS must preserve the following DOM structures and element IDs/classes so my existing Javascript file (app.js) can connect seamlessly:

1. Sidebar Form Controls:
   - Form ID: #preferences-form
   - Location Dropdown: #location-select
   - Budget Dropdown: #budget-select
   - Cuisine Dropdown: #cuisine-select
   - Minimum Rating Range Slider: #rating-slider (with inline label span ID #rating-val for the slider value)
   - Additional Preferences Textarea: #additional-input
   - Recommendation Count Dropdown: #top-k-select
   - Submit Button: #submit-btn

2. Dynamic Panels (Main Content):
   - Welcome Container: #welcome-view
   - Loading Container: #loading-view
   - Results Container: #results-view
   - AI Summary Container: #summary-container (with text element ID #summary-text)
   - Dynamic List Container: #recommendations-list
   - Empty State Container: #empty-view (with modifications list ID #suggestions-list)
   - Error Container: #error-view (with ID #error-title, ID #error-message, and ID #error-suggestions-list)

3. Dynamically Injected Restaurant Card Elements (Your CSS must style this exact structure):
   - Card container: .restaurant-card
   - Header row: .card-header
     - Left header (title/location): .header-left, with .restaurant-name and .restaurant-location
     - Right header (rank/rating): .header-right, with .rank-badge and .rating-badge
   - Cuisine tags wrapper: .cuisines-list (each child tag is .cuisine-tag)
   - Metadata row: .card-meta-row
     - Wallet/Cost display: .cost-display
     - Highlights wrapper: .highlights-container (each child badge is .highlight-pill)
   - AI Explanation block: .explanation-block (with title .explanation-title and text .explanation-text)

Ensure all layouts are built with semantic HTML5 elements (aside, main, header, section) and modern CSS (flexbox, grid, custom properties). Provide only pure HTML and clean Vanilla CSS (no Tailwind unless requested, using standard stylesheet linking).
```

***

## How to use this prompt in Google Stitch:

1. Open **Google Stitch** in your browser.
2. Select **Create New App** or **Edit Existing Component**.
3. Paste the copy-paste prompt block above into the text input area.
4. When Stitch generates the output, review it to ensure that the layout matches your expectations.
5. Replace your current `index.html` and `style.css` in the project's static folder with the generated code. Because the prompt forces Stitch to use your exact IDs and class names, your backend connections and dynamic rendering in `app.js` will continue to work immediately without changes.
