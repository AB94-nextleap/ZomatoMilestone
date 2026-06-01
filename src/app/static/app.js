const { useState, useEffect } = React;

const IMAGE_POOL = [
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAdnLGOmAKkQO0Z3ksDBdSv9d-RIRbvjQBxz0Hdhr9laa5VT0TxPxyneciPPyVjY-r1IjoX9gvS6JGIaVjgduf_smu4YJmdppi6xYNWD5I9SxGwTJcaGoxDJ9BSiLlAgIEGJRYiazcrwOP_EYrUExPb5EkENtjQJrCUT7VoQZe5759oApdZ07rGOaJUUlaG7Mjpcj47fCoyoK297iloJ5FyxwViFencs2oL87qUOVOH1V9RW4bp2Fg-ddnvJaVJPE5OAFT-A4mw95Y",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuDD9l3h0bd3VpPxmmYqu5kfn3j2S8OOSaA2YmrxrEfMrt1aedLkQBW6RjyfeWbbT0E91b6ijNqykN2vxvtr0QRnwsi6_S0OWL6Py4IdeeC2d_ylro06kZiVNKKlwZfEVxJe4WwJKzfqYWIYZ01zWE_Kgemcb5C_WV1lNuvKOigSmcfD7s1kC6dv8wJrjpbgnne0swhTgErB0doZtqyCpmkXwmcwqIyyHwWSHQo0Gp9MlExnzGlAublZ_c1eq0-xJKvfC5fCRaSzmMM",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuDds-4mcD9VPP-AGEbTXF7kq0Nx56TwFjWkkyTTh4fQdXVt-LcGmVlt5SniPodyD4urV-36IjLoARIGJqEG4J_Te5yZO5PpHnuCsQguY37xhkrSUtdcnO5lyZ91aEvOTFM6NBMnyV61rTEkujUtniAfjKHnl6hErNAmnG5K1wx0GMg2rm_Fbzn3Ygg1gM-Jpw18YuiKCYfYpMKZydfq1GOPXCq2Ypu0ewHDZsb8O5cWEvWbcZpITs6A2nXQQJYlImVfCqo_mUv-XLc",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuCywDz1zauo6lpCicVQ8pXUKjpQYu2Nb7bIAvsH54CFM0Py3k50mcbxhlSsr4oXysMYd1JqFaJbSGMPIVk-dtdD9ylihrYq96rpkX518R4FGvlxlIQfvNXg-i2gksWodNRZDZCLEELNUGmPT5NOMVy6KubiOv6svgIsa7WvQwaF6yKtz1pIU4If1JZ0gxNrQFhQrRK48uhHS9XwyS5aDMsOfiumXBbwA1HXDCrtkjJoBOpsrp7HkoWmjO1sepclWhooGt_Aq0Hx7-Y",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAl9M0LTe_vbhpHgo4UYTwIQDW28UIEUR0PLNbXEC0iIoUUxSlPer--lRB3AtskDzd7bzPpP0fkYy7fONCNkkakl66JKBroLmLKpql7IdoLm3hq0qBT0K0hZqqMfHf2okXOpJoKNtLkrvdr3Zk9oS9ek8n7uR0_uek1vcGy1vLMaTs_x6-RCH2BgJXsUaJ7ooYH-eXIm1JPybMMvBjR1Z9T2RXynGm8MOfb46zLJN-_HFF6VNtxK_5KR6UrsFEI2HslI2TvbDJUXhw",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBI3hJ6JcR0jCg61ZITkqBhCB3jdxzHerQkPJTIuC1Oz9eMKNRMKBgevYIwcHOKws2BHwtdAFsEebekgR5r7Is_TG39Tz82k0ak3Qm5vXSLDfAoWwQfgK0R9eh1u8ZOVbHyKlz6dcOLC26kQtoS-wT7JL2pSsv6d0wtI9uJIHrmqxPrkGMrzCeeSGZJeb0usE-McDvUK3dWK1N8gsHvQYgrKeYQFSudjjbnBzAROzDS5LsmgZ-UENY8gbk2O7ArF2iBWJ7Kq-FtJw0"
];

function getRestaurantImage(id) {
  if (!id) return IMAGE_POOL[0];
  let sum = 0;
  for (let i = 0; i < id.length; i++) {
    sum += id.charCodeAt(i);
  }
  return IMAGE_POOL[sum % IMAGE_POOL.length];
}

function App() {
  // Navigation State
  const [activeTab, setActiveTab] = useState("discover"); // discover | saved | ai_plan
  const [view, setView] = useState("home"); // home | loading | results | empty | error

  // Preference Form States
  const [location, setLocation] = useState("Indiranagar");
  const [budget, setBudget] = useState("medium"); // low | medium | high
  const [cuisine, setCuisine] = useState("Italian");
  const [minRating, setMinRating] = useState("4.0+"); // 3.5+ | 4.0+ | 4.5+ | Any
  const [additionalPreferences, setAdditionalPreferences] = useState("family-friendly, quick service");
  const [topK, setTopK] = useState(5);

  // Dynamic Metadata States (dropdown values loaded from API)
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);

  // Results State
  const [results, setResults] = useState(null);
  const [loadingStep, setLoadingStep] = useState(1); // 1, 2, or 3
  const [errorMessage, setErrorMessage] = useState("");
  const [errorTitle, setErrorTitle] = useState("");
  const [suggestions, setSuggestions] = useState([]);

  // Bookmarks State
  const [savedRestaurants, setSavedRestaurants] = useState([]);
  const [savedDetails, setSavedDetails] = useState({});

  // Fetch locations and cuisines metadata on mount
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [locRes, cuisRes] = await Promise.all([
          fetch("/api/v1/metadata/locations"),
          fetch("/api/v1/metadata/cuisines")
        ]);
        if (locRes.ok && cuisRes.ok) {
          const locs = await locRes.json();
          const cuiss = await cuisRes.json();
          setLocations(locs);
          setCuisines(cuiss);
          
          if (locs.length > 0 && !locs.includes(location)) {
            setLocation(locs[0]);
          }
          if (cuiss.length > 0 && !cuiss.includes(cuisine)) {
            setCuisine(cuiss[0]);
          }
        } else {
          throw new Error("Metadata request returned non-OK status");
        }
      } catch (err) {
        console.warn("Failed to load backend metadata, using local fallbacks:", err);
        // Fallbacks if server is in raw/empty state
        setLocations(["Indiranagar", "Koramangala", "HSR Layout", "BTM Layout", "Jayanagar", "Whitefield", "Bellandur"]);
        setCuisines(["Italian", "Indian", "Chinese", "Mexican", "Japanese", "Continental", "North Indian", "South Indian", "Desserts"]);
      }
    };
    
    // Load Bookmarks from localStorage
    const saved = localStorage.getItem("savedRestaurants");
    if (saved) {
      setSavedRestaurants(JSON.parse(saved));
    }
    const cachedDetails = localStorage.getItem("savedDetailsCache");
    if (cachedDetails) {
      setSavedDetails(JSON.parse(cachedDetails));
    }

    fetchMetadata();
  }, []);

  const handleToggleBookmark = (restaurant) => {
    let newSaved;
    let newDetails = { ...savedDetails };
    if (savedRestaurants.includes(restaurant.id)) {
      newSaved = savedRestaurants.filter(id => id !== restaurant.id);
    } else {
      newSaved = [...savedRestaurants, restaurant.id];
      newDetails[restaurant.id] = restaurant;
    }
    setSavedRestaurants(newSaved);
    setSavedDetails(newDetails);
    localStorage.setItem("savedRestaurants", JSON.stringify(newSaved));
    localStorage.setItem("savedDetailsCache", JSON.stringify(newDetails));
  };

  const handleGetRecommendations = async (e) => {
    if (e) e.preventDefault();
    setView("loading");
    setLoadingStep(1);

    // Simulated progress transitions
    const t1 = setTimeout(() => setLoadingStep(2), 1200);
    const t2 = setTimeout(() => setLoadingStep(3), 2800);

    try {
      // Parse numeric rating threshold
      let ratingVal = null;
      if (minRating === "3.5+") ratingVal = 3.5;
      else if (minRating === "4.0+") ratingVal = 4.0;
      else if (minRating === "4.5+") ratingVal = 4.5;

      // Parse additional preferences
      const cleanAdd = additionalPreferences.trim();
      const addList = cleanAdd
        ? cleanAdd.split(",").map(p => p.trim()).filter(Boolean)
        : [];

      const payload = {
        location: location,
        budget: budget,
        cuisine: cuisine || null,
        min_rating: ratingVal,
        additional_preferences: addList,
        top_k: parseInt(topK, 10)
      };

      const response = await fetch("/api/v1/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw {
          title: data.error_code || "API Failure",
          message: data.message || `API request failed with status ${response.status}`,
          suggestions: data.suggestions || ["Adjust your filters and try again."]
        };
      }

      // Handle Empty Results (grounded filtering matches 0)
      if (!data.recommendations || data.recommendations.length === 0) {
        setSuggestions(data.suggestions || [
          "Choose a wider search area or neighborhood.",
          "Clear the cuisine filter to search for all types of food.",
          "Decrease the minimum rating threshold.",
          "Relax or remove additional preference tags."
        ]);
        setView("empty");
      } else {
        setResults(data);
        
        // Cache details of newly received restaurants
        const newDetails = { ...savedDetails };
        data.recommendations.forEach(rec => {
          newDetails[rec.restaurant.id] = rec.restaurant;
        });
        setSavedDetails(newDetails);
        localStorage.setItem("savedDetailsCache", JSON.stringify(newDetails));

        setView("results");
        setActiveTab("ai_plan");
      }
    } catch (err) {
      console.error(err);
      setErrorTitle(err.title || "Network Error");
      setErrorMessage(err.message || "Failed to establish a connection to the TasteFinder recommendation server.");
      setSuggestions(err.suggestions || [
        "Confirm that the backend uvicorn service is active.",
        "Check that the Zomato Hugging Face dataset has been loaded: run 'python scripts/ingest.py'.",
        "Inspect the server terminal for backend traceback errors."
      ]);
      setView("error");
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
    }
  };

  const handleResetFilters = () => {
    setLocation(locations[0] || "Indiranagar");
    setBudget("medium");
    setCuisine(cuisines[0] || "Italian");
    setMinRating("4.0+");
    setAdditionalPreferences("");
    setTopK(5);
    setView("home");
    setActiveTab("discover");
  };

  // Navigations Actions
  const handleNavClick = (tab) => {
    setActiveTab(tab);
    if (tab === "discover") {
      // Keep last view state of Discover (home, results, empty, etc.)
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navigation Bar (Desktop Only) */}
      <header className="hidden md:flex fixed top-0 left-0 w-full z-50 flex-col items-center px-margin-desktop py-base bg-surface shadow-sm border-b border-surface-variant">
        <div className="w-full max-w-container-max-width flex justify-between items-center h-16">
          <div className="flex items-center" onClick={() => handleNavClick("discover")} style={{ cursor: 'pointer' }}>
            <span className="text-headline-md font-headline-md font-bold text-primary tracking-tight">TasteFinder</span>
            <span className="text-[12px] bg-tertiary/10 text-tertiary px-2 py-0.5 rounded-full font-bold ml-2">AI</span>
          </div>
          
          <nav className="flex gap-8">
            <button 
              onClick={() => handleNavClick("discover")} 
              className={`flex items-center gap-1.5 font-label-md text-label-md transition-all pb-1 ${
                activeTab === "discover" ? "text-primary border-b-2 border-primary font-semibold" : "text-on-surface-variant hover:text-primary"
              }`}
            >
              <span className="material-symbols-outlined text-[20px]">explore</span>
              Discover
            </button>
            <button 
              onClick={() => handleNavClick("saved")} 
              className={`flex items-center gap-1.5 font-label-md text-label-md transition-all pb-1 ${
                activeTab === "saved" ? "text-primary border-b-2 border-primary font-semibold" : "text-on-surface-variant hover:text-primary"
              }`}
            >
              <span className={`material-symbols-outlined text-[20px] ${activeTab === "saved" ? "filled" : ""}`}>bookmark</span>
              Saved ({savedRestaurants.length})
            </button>
            <button 
              onClick={() => {
                if (results) {
                  handleNavClick("ai_plan");
                  setView("results");
                } else {
                  alert("Please generate recommendations on the Discover tab first!");
                }
              }} 
              className={`flex items-center gap-1.5 font-label-md text-label-md transition-all pb-1 ${
                activeTab === "ai_plan" ? "text-primary border-b-2 border-primary font-semibold" : "text-on-surface-variant hover:text-primary"
              } ${!results ? "opacity-40 cursor-not-allowed" : ""}`}
            >
              <span className={`material-symbols-outlined text-[20px] ${activeTab === "ai_plan" ? "filled" : ""}`}>auto_awesome</span>
              AI Plan
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <button className="text-on-surface-variant hover:text-primary p-2 rounded-full hover:bg-surface-variant">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="text-on-surface-variant hover:text-primary p-2 rounded-full hover:bg-surface-variant">
              <span className="material-symbols-outlined">person</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Canvas View */}
      <main className="flex-grow w-full max-w-container-max-width mx-auto px-margin-mobile md:px-margin-desktop pt-6 md:pt-32 pb-32">
        {activeTab === "discover" && (
          <div className="animate-fade-in">
            {/* Page Title Header (Desktop) */}
            <header className="mb-8 hidden md:block">
              <h2 className="font-headline-sm text-headline-sm text-on-surface mb-1">Find Your Next Great Meal</h2>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Personalized picks from real Zomato data — filtered by you, ranked by AI.
              </p>
            </header>

            {/* Mobile Header */}
            <header className="mb-6 text-center md:hidden block">
              <h1 className="font-headline-lg font-bold text-primary tracking-tight mb-1">TasteFinder</h1>
              <p className="font-body-md text-body-md text-on-surface-variant">AI-curated food recommendations</p>
            </header>

            {view === "home" && (
              <>
                {/* Search Form Card */}
                <section className="bg-surface-container-lowest shadow-sm rounded-2xl border border-surface-variant/40 p-6 md:p-8 mb-8">
                  <form onSubmit={handleGetRecommendations} className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
                    {/* Location Field */}
                    <div className="flex flex-col gap-2">
                      <label className="font-label-md text-label-md text-on-surface font-semibold">Location Area</label>
                      <div className="relative flex items-center">
                        <span className="material-symbols-outlined absolute left-3 text-on-surface-variant pointer-events-none">location_on</span>
                        <select 
                          value={location}
                          onChange={(e) => setLocation(e.target.value)}
                          className="w-full appearance-none bg-background border border-outline-variant/60 rounded-xl pl-10 pr-10 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                        >
                          {locations.map((loc) => (
                            <option key={loc} value={loc}>{loc}</option>
                          ))}
                        </select>
                        <span className="material-symbols-outlined absolute right-3 text-on-surface-variant pointer-events-none">expand_more</span>
                      </div>
                    </div>

                    {/* Budget Field (Segmented Controls) */}
                    <div className="flex flex-col gap-2">
                      <label className="font-label-md text-label-md text-on-surface font-semibold">Budget Band</label>
                      <div className="flex bg-surface-container rounded-full p-1 h-[50px] border border-outline-variant/40">
                        <button 
                          type="button"
                          onClick={() => setBudget("low")}
                          className={`flex-1 flex items-center justify-center rounded-full font-label-md text-label-md transition-all ${
                            budget === "low" ? "bg-surface-container-lowest shadow-sm text-primary font-bold" : "text-on-surface-variant hover:text-on-surface"
                          }`}
                        >
                          $ (Low)
                        </button>
                        <button 
                          type="button"
                          onClick={() => setBudget("medium")}
                          className={`flex-1 flex items-center justify-center rounded-full font-label-md text-label-md transition-all ${
                            budget === "medium" ? "bg-surface-container-lowest shadow-sm text-primary font-bold" : "text-on-surface-variant hover:text-on-surface"
                          }`}
                        >
                          $$ (Mid)
                        </button>
                        <button 
                          type="button"
                          onClick={() => setBudget("high")}
                          className={`flex-1 flex items-center justify-center rounded-full font-label-md text-label-md transition-all ${
                            budget === "high" ? "bg-surface-container-lowest shadow-sm text-primary font-bold" : "text-on-surface-variant hover:text-on-surface"
                          }`}
                        >
                          $$$ (High)
                        </button>
                      </div>
                    </div>

                    {/* Cuisine Field */}
                    <div className="flex flex-col gap-2">
                      <label className="font-label-md text-label-md text-on-surface font-semibold">Cuisine Type</label>
                      <div className="relative flex items-center">
                        <span className="material-symbols-outlined absolute left-3 text-on-surface-variant pointer-events-none">restaurant</span>
                        <select 
                          value={cuisine}
                          onChange={(e) => setCuisine(e.target.value)}
                          className="w-full appearance-none bg-background border border-outline-variant/60 rounded-xl pl-10 pr-10 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                        >
                          {cuisines.map((c) => (
                            <option key={c} value={c}>{c}</option>
                          ))}
                        </select>
                        <span className="material-symbols-outlined absolute right-3 text-on-surface-variant pointer-events-none">expand_more</span>
                      </div>
                    </div>

                    {/* Min Rating Field (Chips Selectors) */}
                    <div className="flex flex-col gap-2">
                      <label className="font-label-md text-label-md text-on-surface font-semibold">Minimum Rating</label>
                      <div className="flex gap-2 overflow-x-auto no-scrollbar py-1">
                        {["3.5+", "4.0+", "4.5+", "Any"].map((r) => (
                          <button
                            key={r}
                            type="button"
                            onClick={() => setMinRating(r)}
                            className={`flex-shrink-0 px-4 py-2 rounded-full font-label-md text-label-md transition-all border flex items-center gap-1 ${
                              minRating === r
                                ? "border-2 border-primary bg-primary-fixed/20 text-primary font-bold shadow-sm"
                                : "border-outline-variant/60 bg-background text-on-surface-variant hover:bg-surface-container-low"
                            }`}
                          >
                            {r}
                            {r !== "Any" && <span className={`material-symbols-outlined text-[14px] ${minRating === r ? "filled text-primary" : "text-on-surface-variant"}`}>star</span>}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Additional Preferences (Vibe & Extras) */}
                    <div className="flex flex-col gap-2 md:col-span-2">
                      <label className="font-label-md text-label-md text-on-surface flex items-center gap-2 font-semibold">
                        Vibe &amp; Extra Preferences
                        <span className="material-symbols-outlined text-[16px] text-tertiary font-bold">auto_awesome</span>
                      </label>
                      <input 
                        type="text"
                        value={additionalPreferences}
                        onChange={(e) => setAdditionalPreferences(e.target.value)}
                        placeholder="e.g. outdoor seating, romantic, pet friendly, live music"
                        className="w-full bg-background border border-outline-variant/60 rounded-xl px-4 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-tertiary focus:ring-1 focus:ring-tertiary transition-all"
                      />
                      <p className="font-label-sm text-label-sm text-on-surface-variant ml-1">AI search will filter and rank using these contextual clues.</p>
                    </div>

                    {/* Recommendations Count */}
                    <div className="flex flex-col gap-2">
                      <label className="font-label-md text-label-md text-on-surface font-semibold">Number of Results</label>
                      <div className="relative flex items-center">
                        <span className="material-symbols-outlined absolute left-3 text-on-surface-variant pointer-events-none">list_alt</span>
                        <select 
                          value={topK}
                          onChange={(e) => setTopK(parseInt(e.target.value, 10))}
                          className="w-full appearance-none bg-background border border-outline-variant/60 rounded-xl pl-10 pr-10 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                        >
                          <option value={3}>Top 3 spots</option>
                          <option value={5}>Top 5 spots</option>
                          <option value={10}>Top 10 spots</option>
                        </select>
                        <span className="material-symbols-outlined absolute right-3 text-on-surface-variant pointer-events-none">expand_more</span>
                      </div>
                    </div>
                  </form>
                </section>

                {/* Submit button */}
                <div className="flex justify-center mb-12">
                  <button 
                    onClick={handleGetRecommendations}
                    className="w-full md:w-auto md:min-w-[300px] flex items-center justify-center gap-2 bg-primary hover:bg-surface-tint text-on-primary font-headline-sm text-headline-sm py-4 px-8 rounded-2xl shadow-lg transition-all active:scale-[0.98]"
                  >
                    <span className="material-symbols-outlined icon-fill">search</span>
                    Get AI Recommendations
                  </button>
                </div>

                {/* Empty State Onboarding Graphic */}
                <div className="flex flex-col items-center justify-center text-center opacity-85 mt-4">
                  <div className="w-full max-w-[400px] aspect-video rounded-3xl overflow-hidden mb-6 shadow-sm border border-surface-variant/40 bg-surface-container relative">
                    <img 
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuBAZk-PYQo5yaupYI7MFTrVVjBd3tSK6WY4A2y9aHZ8-jJreebgGZp77vaJ3HvkXX_ovXNXzAR2bWEIhR3J84oolPtzvJXPaj8uinxlYeZzwaHnwz7Y-u63a1uORq7rLYWJfIFUN-psgEYDyBlhbiMPOsUweuef4LKh3FmeXEzDCbf6FKjA_C2tKJ7ZKkzkcfXgoCgS6fgRBCjo35AT1HAzCqw4WGt1HDkKxRK5682MaZCBkUsZv-HgmLMm4gcd_N8zjlSpsxGqdSo" 
                      className="w-full h-full object-cover mix-blend-multiply opacity-90"
                      alt="Food photography Plated Italian Pasta"
                    />
                  </div>
                  <p className="font-body-lg text-body-md md:text-body-lg text-on-surface-variant max-w-sm">
                    Select your dining criteria above and our AI will build your perfect meal itinerary.
                  </p>
                </div>
              </>
            )}

            {/* Loading Modal Overlay */}
            {view === "loading" && (
              <div className="fixed inset-0 z-50 bg-surface/65 backdrop-blur-md flex items-center justify-center px-margin-mobile">
                <div className="bg-surface-container-lowest rounded-2xl shadow-xl border border-surface-variant p-8 flex flex-col items-center max-w-md w-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-tertiary-container via-primary to-secondary-container"></div>
                  
                  <div className="loader-ring mt-4 mb-6">
                    <div></div><div></div><div></div><div></div>
                  </div>
                  
                  <h2 className="font-headline-md text-headline-md text-on-surface text-center mb-8 font-bold">TasteFinder is curating your matches...</h2>
                  
                  <div className="w-full flex flex-col gap-5">
                    {/* Step 1: Filter */}
                    <div className={`flex items-center gap-4 transition-opacity duration-300 ${loadingStep >= 2 ? "opacity-75" : "opacity-100"}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        loadingStep >= 2 ? "bg-surface-container text-primary" : "bg-primary text-on-primary animate-pulse"
                      }`}>
                        {loadingStep >= 2 ? (
                          <span className="material-symbols-outlined filled text-[20px]">check_circle</span>
                        ) : (
                          <span className="material-symbols-outlined text-[20px]">filter_alt</span>
                        )}
                      </div>
                      <span className={`font-label-md text-label-md ${loadingStep === 1 ? "text-on-surface font-semibold" : "text-on-surface-variant"}`}>
                        Filtering Zomato database records
                      </span>
                    </div>

                    {/* Step 2: Ask AI */}
                    <div className={`flex items-center gap-4 transition-all duration-300 ${
                      loadingStep === 2 ? "bg-tertiary-container/5 p-2 -mx-2 rounded-lg border-l-4 border-tertiary" : "opacity-40"
                    }`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        loadingStep === 2 ? "bg-tertiary text-on-tertiary shadow-sm animate-pulse" : (loadingStep > 2 ? "bg-surface-container text-primary" : "border-2 border-outline-variant")
                      }`}>
                        {loadingStep > 2 ? (
                          <span className="material-symbols-outlined filled text-[20px]">check_circle</span>
                        ) : (
                          <span className="material-symbols-outlined text-[20px] font-bold">auto_awesome</span>
                        )}
                      </div>
                      <span className={`font-label-md text-label-md ${loadingStep === 2 ? "text-on-surface font-semibold" : "text-on-surface-variant"}`}>
                        Querying Groq LLM ranking engine
                      </span>
                    </div>

                    {/* Step 3: Parse and Ground */}
                    <div className={`flex items-center gap-4 transition-all duration-300 ${
                      loadingStep === 3 ? "bg-primary-container/5 p-2 -mx-2 rounded-lg border-l-4 border-primary" : "opacity-40"
                    }`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        loadingStep === 3 ? "bg-primary text-on-primary animate-pulse" : "border-2 border-outline-variant"
                      }`}>
                        <span className="material-symbols-outlined text-[20px]">list_alt</span>
                      </div>
                      <span className={`font-label-md text-label-md ${loadingStep === 3 ? "text-on-surface font-semibold" : "text-on-surface-variant"}`}>
                        Grounding recommendation details
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Empty State View */}
            {view === "empty" && (
              <div className="flex flex-col items-center justify-center min-h-[500px] text-center">
                <div className="bg-surface-container rounded-full p-8 mb-6 shadow-sm border border-surface-variant/40">
                  <span className="material-symbols-outlined text-outline" style={{ fontSize: "64px" }}>search_off</span>
                </div>
                <h2 className="font-headline-lg text-headline-lg text-on-surface mb-3 font-bold">No Restaurant Matches</h2>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto mb-8">
                  We couldn't find any restaurants in <b>{location}</b> matching all your filters. Try widening your filters.
                </p>
                <div className="bg-surface-container-low rounded-2xl border border-surface-variant/40 p-6 text-left max-w-md mb-8">
                  <h3 className="font-label-md text-label-md text-on-surface font-bold mb-3 flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[18px]">lightbulb</span>
                    Try these modifications:
                  </h3>
                  <ul className="space-y-2 text-on-surface-variant">
                    {suggestions.map((sug, idx) => (
                      <li key={idx} className="flex gap-2 items-start text-sm">
                        <span className="text-primary font-bold">•</span>
                        <span>{sug}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <button 
                  onClick={handleResetFilters}
                  className="bg-primary text-on-primary font-label-md text-label-md px-8 py-3 rounded-full hover:bg-surface-tint active:scale-95 transition-all shadow-md flex items-center gap-2"
                >
                  <span className="material-symbols-outlined">tune</span>
                  Adjust Filters
                </button>
              </div>
            )}

            {/* Error View */}
            {view === "error" && (
              <div className="flex flex-col items-center justify-center min-h-[500px] text-center">
                <div className="bg-error/10 text-error rounded-full p-8 mb-6 shadow-sm border border-error/20">
                  <span className="material-symbols-outlined" style={{ fontSize: "64px" }}>error</span>
                </div>
                <h2 className="font-headline-lg text-headline-lg text-error mb-3 font-bold">{errorTitle}</h2>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto mb-8">
                  {errorMessage}
                </p>
                <div className="bg-surface-container-low rounded-2xl border border-surface-variant/40 p-6 text-left max-w-md mb-8">
                  <h3 className="font-label-md text-label-md text-on-surface font-bold mb-3 flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[18px]">build</span>
                    Troubleshooting Steps:
                  </h3>
                  <ul className="space-y-2 text-on-surface-variant">
                    {suggestions.map((sug, idx) => (
                      <li key={idx} className="flex gap-2 items-start text-sm">
                        <span className="text-primary font-bold">-</span>
                        <span>{sug}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <button 
                  onClick={handleResetFilters}
                  className="bg-primary text-on-primary font-label-md text-label-md px-8 py-3 rounded-full hover:bg-surface-tint active:scale-95 transition-all shadow-md"
                >
                  Return to Home
                </button>
              </div>
            )}
          </div>
        )}

        {/* AI Results View (activeTab === "ai_plan" or results view) */}
        {activeTab === "ai_plan" && results && (
          <div className="animate-fade-in">
            {/* AI Summary Banner */}
            <section className="bg-surface-container-lowest rounded-xl p-gutter ambient-shadow-sm border border-surface-variant mb-gutter relative overflow-hidden flex flex-col md:flex-row md:items-center gap-gutter">
              <div className="absolute -right-10 -top-10 text-primary-fixed-dim opacity-10 pointer-events-none">
                <span className="material-symbols-outlined" style={{ fontSize: "160px" }}>auto_awesome</span>
              </div>
              <div className="flex-shrink-0 bg-primary-container text-on-primary-container w-12 h-12 rounded-full flex items-center justify-center z-10 shadow-md">
                <span className="material-symbols-outlined filled">auto_awesome</span>
              </div>
              <div className="z-10 flex-1">
                <h1 class="font-headline-sm text-headline-sm text-on-surface mb-2 font-bold">AI Curated Meal Recommendations</h1>
                <p className="font-body-md text-body-md text-on-surface-variant italic">
                  "{results.summary || `${results.recommendations.length} excellent spots found.`}"
                </p>
              </div>
              <div className="z-10 flex gap-2 flex-wrap md:flex-col md:items-end md:justify-center">
                <span className="inline-flex items-center gap-1 bg-surface-container-high text-on-surface px-3 py-1.5 rounded-full font-label-sm text-label-sm font-semibold">
                  <span className="material-symbols-outlined" style={{ fontSize: "14px" }}>location_on</span> {results.query?.location || location}
                </span>
                <span className="inline-flex items-center gap-1 bg-surface-container-high text-on-surface px-3 py-1.5 rounded-full font-label-sm text-label-sm font-semibold">
                  <span className="material-symbols-outlined" style={{ fontSize: "14px" }}>payments</span> {results.query?.budget ? results.query.budget.toUpperCase() : budget.toUpperCase()} Budget
                </span>
              </div>
            </section>

            {/* Back to Filters CTA */}
            <div className="mb-6 flex justify-between items-center">
              <button 
                onClick={() => handleNavClick("discover")}
                className="flex items-center gap-1 text-primary hover:text-surface-tint font-bold text-sm"
              >
                <span className="material-symbols-outlined text-[18px]">arrow_back</span>
                Change filters
              </button>
              <span className="text-on-surface-variant text-sm font-medium">{results.recommendations.length} Results loaded</span>
            </div>

            {/* Recommendations List */}
            <div className="flex flex-col gap-gutter mb-gutter">
              {results.recommendations.map((rec) => {
                const rest = rec.restaurant;
                const isSaved = savedRestaurants.includes(rest.id);
                return (
                  <article key={rest.id} className="bg-surface-container-lowest rounded-xl ambient-shadow-sm border border-surface-variant overflow-hidden flex flex-col md:flex-row transition-all duration-300 hover:ambient-shadow-md hover:-translate-y-1">
                    {/* Image Cover */}
                    <div className="relative w-full md:w-[320px] h-48 md:h-auto flex-shrink-0 bg-surface-variant overflow-hidden">
                      <img 
                        src={getRestaurantImage(rest.id)} 
                        alt={rest.name}
                        className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
                      />
                      
                      {/* Rank tag */}
                      <div className="absolute top-4 left-4 bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full font-label-md text-label-md shadow-md flex items-center gap-1 font-bold">
                        <span className="material-symbols-outlined filled text-[16px]">workspace_premium</span>
                        #{rec.rank} Match
                      </div>

                      {/* Bookmark Save toggle */}
                      <button 
                        onClick={() => handleToggleBookmark(rest)}
                        className={`absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center transition-colors shadow-sm ${
                          isSaved ? "bg-primary text-on-primary" : "bg-surface/80 backdrop-blur-md text-on-surface hover:text-primary hover:bg-surface"
                        }`}
                      >
                        <span className={`material-symbols-outlined ${isSaved ? "filled" : ""}`}>bookmark</span>
                      </button>
                    </div>

                    {/* Restaurant Info */}
                    <div className="p-gutter flex flex-col flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h2 className="font-headline-md text-headline-md text-on-surface font-bold">{rest.name}</h2>
                          <p className="font-body-md text-body-md text-on-surface-variant flex items-center gap-1 mt-1">
                            <span className="material-symbols-outlined text-[16px]">location_on</span>
                            {rest.location}
                          </p>
                        </div>
                        <div className="bg-surface-container px-2.5 py-1 rounded font-label-md text-label-md text-on-surface flex items-center gap-1 border border-outline-variant/30">
                          <span className="material-symbols-outlined text-secondary-fixed-dim filled" style={{ fontSize: "16px" }}>star</span>
                          {parseFloat(rest.rating).toFixed(1)}
                        </div>
                      </div>

                      {/* Cuisines and Metadata list */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        <span className="text-on-surface-variant font-label-sm text-label-sm border border-surface-variant px-2.5 py-1 rounded-full bg-background/50 font-medium">
                          ₹{parseInt(rest.estimated_cost_for_two || 0, 10).toLocaleString()} for two
                        </span>
                        {rest.cuisines.map((c) => (
                          <span key={c} className="text-on-surface-variant font-label-sm text-label-sm border border-surface-variant px-2.5 py-1 rounded-full bg-background/50 font-medium">
                            {c}
                          </span>
                        ))}
                      </div>

                      {/* AI Pick Explanation section */}
                      <div className="mt-auto pt-4 border-t border-surface-variant">
                        <div className="ai-explanation-bg ai-explanation-border p-3 rounded-r-lg flex gap-3 items-start">
                          <span className="material-symbols-outlined text-tertiary mt-0.5 filled" style={{ fontSize: "20px" }}>auto_awesome</span>
                          <div>
                            <span className="font-label-sm text-label-sm text-tertiary uppercase tracking-wider block mb-1 font-bold">Why we picked this</span>
                            <p className="font-body-md text-body-md text-on-surface italic">
                              "{rec.explanation}"
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>

            {/* Collapsible search metadata */}
            <details className="group bg-surface-container-lowest rounded-xl ambient-shadow-sm border border-surface-variant overflow-hidden mb-gutter">
              <summary className="flex justify-between items-center cursor-pointer p-4 font-label-md text-label-md text-on-surface hover:bg-surface-container-low transition-colors list-none">
                <div className="flex items-center gap-2 font-semibold">
                  <span className="material-symbols-outlined text-on-surface-variant" style={{ fontSize: "20px" }}>manage_search</span>
                  Search details
                </div>
                <span className="material-symbols-outlined transform transition-transform group-open:rotate-180 text-on-surface-variant">expand_more</span>
              </summary>
              <div className="p-4 pt-0 border-t border-surface-variant mt-2 bg-surface-container-lowest text-on-surface-variant font-body-md text-body-md">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <span className="block font-label-sm text-label-sm text-on-surface uppercase mb-1 font-bold">Parameters Applied</span>
                    <ul className="list-disc list-inside space-y-1 ml-1 text-sm">
                      <li>Location Area: {results.query?.location || location}</li>
                      <li>Budget: {results.query?.budget ? results.query.budget.toUpperCase() : budget.toUpperCase()}</li>
                      {results.query?.cuisine && <li>Cuisine: {results.query.cuisine}</li>}
                      {results.query?.min_rating && <li>Rating Threshold: {results.query.min_rating}+</li>}
                      {results.query?.additional_preferences?.length > 0 && (
                        <li>Modifiers: {results.query.additional_preferences.join(", ")}</li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <span className="block font-label-sm text-label-sm text-on-surface uppercase mb-1 font-bold">Confidence & Data</span>
                    <p className="text-sm">
                      Processed {results.meta?.candidates_considered || 0} candidates from Zomato dataset.
                      Filter criteria: {results.meta?.filters_applied?.join(", ") || "default"}.
                    </p>
                  </div>
                </div>
              </div>
            </details>
          </div>
        )}

        {/* Saved Restaurants Tab View (activeTab === "saved") */}
        {activeTab === "saved" && (
          <div className="animate-fade-in">
            <header className="mb-8">
              <h2 className="font-headline-sm text-headline-sm text-on-surface mb-1 font-bold">Saved Restaurants</h2>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Your bookmarked dining spots saved locally in this browser.
              </p>
            </header>

            {savedRestaurants.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[350px] text-center">
                <div className="bg-surface-container rounded-full p-8 mb-6 shadow-sm border border-surface-variant/40">
                  <span className="material-symbols-outlined text-outline" style={{ fontSize: "64px" }}>bookmark_border</span>
                </div>
                <h3 className="font-headline-sm text-headline-sm text-on-surface mb-2 font-bold">No Saved Restaurants</h3>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-sm mx-auto mb-6">
                  Save restaurants from your AI recommendations list to access them instantly here.
                </p>
                <button 
                  onClick={() => handleNavClick("discover")}
                  className="bg-primary text-on-primary font-label-md text-label-md px-8 py-3 rounded-full hover:bg-surface-tint transition-all shadow-md"
                >
                  Browse Restaurants
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-gutter">
                {savedRestaurants.map((id) => {
                  const rest = savedDetails[id];
                  if (!rest) return null;
                  return (
                    <article key={rest.id} className="bg-surface-container-lowest rounded-xl ambient-shadow-sm border border-surface-variant overflow-hidden flex flex-col md:flex-row transition-all duration-300 hover:ambient-shadow-md hover:-translate-y-1">
                      {/* Image cover */}
                      <div className="relative w-full md:w-[320px] h-48 md:h-auto flex-shrink-0 bg-surface-variant overflow-hidden">
                        <img 
                          src={getRestaurantImage(rest.id)} 
                          alt={rest.name}
                          className="w-full h-full object-cover"
                        />
                        <button 
                          onClick={() => handleToggleBookmark(rest)}
                          className="absolute top-4 right-4 w-10 h-10 bg-primary text-on-primary rounded-full flex items-center justify-center shadow-sm"
                        >
                          <span className="material-symbols-outlined filled">bookmark</span>
                        </button>
                      </div>

                      {/* Content */}
                      <div className="p-gutter flex flex-col flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h2 className="font-headline-md text-headline-md text-on-surface font-bold">{rest.name}</h2>
                            <p className="font-body-md text-body-md text-on-surface-variant flex items-center gap-1 mt-1">
                              <span className="material-symbols-outlined text-[16px]">location_on</span>
                              {rest.location}
                            </p>
                          </div>
                          <div className="bg-surface-container px-2.5 py-1 rounded font-label-md text-label-md text-on-surface flex items-center gap-1 border border-outline-variant/30">
                            <span className="material-symbols-outlined text-secondary-fixed-dim filled" style={{ fontSize: "16px" }}>star</span>
                            {parseFloat(rest.rating).toFixed(1)}
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-2">
                          <span className="text-on-surface-variant font-label-sm text-label-sm border border-surface-variant px-2.5 py-1 rounded-full bg-background/50 font-medium">
                            ₹{parseInt(rest.estimated_cost_for_two || 0, 10).toLocaleString()} for two
                          </span>
                          {rest.cuisines?.map((c) => (
                            <span key={c} className="text-on-surface-variant font-label-sm text-label-sm border border-surface-variant px-2.5 py-1 rounded-full bg-background/50 font-medium">
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Bottom Navigation Bar (Mobile Only) */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 pb-safe bg-surface border-t border-surface-variant shadow-[0_-4px_20px_rgba(0,0,0,0.05)] rounded-t-xl">
        <button 
          onClick={() => handleNavClick("discover")}
          className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all w-16 ${
            activeTab === "discover" ? "bg-primary-container text-on-primary-container font-semibold" : "text-on-surface-variant"
          }`}
        >
          <span className="material-symbols-outlined text-[24px]">explore</span>
          <span className="font-label-sm text-label-sm mt-0.5">Discover</span>
        </button>
        <button 
          onClick={() => handleNavClick("saved")}
          className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all w-16 ${
            activeTab === "saved" ? "bg-primary-container text-on-primary-container font-semibold" : "text-on-surface-variant"
          }`}
        >
          <span className={`material-symbols-outlined text-[24px] ${activeTab === "saved" ? "filled" : ""}`}>bookmark</span>
          <span className="font-label-sm text-label-sm mt-0.5 font-bold">Saved</span>
        </button>
        <button 
          onClick={() => {
            if (results) {
              handleNavClick("ai_plan");
              setView("results");
            } else {
              alert("Please generate recommendations on the Discover tab first!");
            }
          }}
          className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all w-16 ${
            activeTab === "ai_plan" ? "bg-primary-container text-on-primary-container font-semibold" : "text-on-surface-variant"
          } ${!results ? "opacity-35 cursor-not-allowed" : ""}`}
        >
          <span className={`material-symbols-outlined text-[24px] ${activeTab === "ai_plan" ? "filled" : ""}`}>auto_awesome</span>
          <span className="font-label-sm text-label-sm mt-0.5">AI Plan</span>
        </button>
      </nav>
    </div>
  );
}

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);
root.render(<App />);
