import store from "app-store-scraper";
import fs from "fs/promises";

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from App Store
 * Combines multiple collections and search results with category filtering
 * @param {number} numApps - Total number of apps to retrieve per category
 * @returns {Promise<Array>} Promise that resolves to an array of filtered app objects
 */
async function getSportsAndFitnessAppsAppStore(numApps = 1000) {
  try {
    let allApps = [];
    const targetCategories = [
      store.category.SPORTS,
      store.category.HEALTH_AND_FITNESS,
    ];

    // Countries to search - major markets for App Store
    const targetCountries = [
      "dz",
      "ao",
      "ai",
      "ar",
      "am",
      "au",
      "at",
      "az",
      "bh",
      "bb",
      "by",
      "be",
      "bz",
      "bm",
      "bo",
      "bw",
      "br",
      "vg",
      "bn",
      "bg",
      "ca",
      "ky",
      "cl",
      "cn",
      "co",
      "cr",
      "hr",
      "cy",
      "cz",
      "dk",
      "dm",
      "ec",
      "eg",
      "sv",
      "ee",
      "fi",
      "fr",
      "de",
      "gb",
      "gh",
      "gr",
      "gd",
      "gt",
      "gy",
      "hn",
      "hk",
      "hu",
      "is",
      "in",
      "id",
      "ie",
      "il",
      "it",
      "jm",
      "jp",
      "jo",
      "ke",
      "kr",
      "kw",
      "lv",
      "lb",
      "lt",
      "lu",
      "mo",
      "mk",
      "mg",
      "my",
      "ml",
      "mt",
      "mu",
      "mx",
      "ms",
      "np",
      "nl",
      "nz",
      "ni",
      "ne",
      "ng",
      "no",
      "om",
      "pk",
      "pa",
      "py",
      "pe",
      "ph",
      "pl",
      "pt",
      "qa",
      "ro",
      "ru",
      "sa",
      "sn",
      "sg",
      "sk",
      "si",
      "za",
      "es",
      "lk",
      "sr",
      "se",
      "ch",
      "tw",
      "tz",
      "th",
      "tn",
      "tr",
      "ug",
      "ua",
      "ae",
      "us",
      "uy",
      "uz",
      "ve",
      "vn",
      "ye",
    ];

    console.log(
      "🍎 Starting comprehensive App Store SPORTS & FITNESS app collection..."
    );
    console.log(
      `🌍 Searching across ${
        targetCountries.length
      } countries: ${targetCountries.join(", ").toUpperCase()}`
    );

    for (const category of targetCategories) {
      const categoryName = Object.keys(store.category).find(
        (key) => store.category[key] === category
      );
      console.log(`\n📱 Processing ${categoryName} category...`);

      // Step 1: Get apps from multiple collections across different countries
      const collections = [
        store.collection.TOP_MAC,
        store.collection.TOP_FREE_MAC,
        store.collection.TOP_GROSSING_MAC,
        store.collection.TOP_PAID_MAC,
        store.collection.NEW_IOS,
        store.collection.NEW_FREE_IOS,
        store.collection.NEW_PAID_IOS,
        store.collection.TOP_FREE_IOS,
        store.collection.TOP_FREE_IPAD,
        store.collection.TOP_GROSSING_IOS,
        store.collection.TOP_GROSSING_IPAD,
        store.collection.TOP_PAID_IOS,
        store.collection.TOP_PAID_IPAD,
      ];

      for (const collection of collections) {
        for (const country of targetCountries) {
          try {
            const collectionName = Object.keys(store.collection).find(
              (key) => store.collection[key] === collection
            );
            console.log(
              `  📋 Fetching from ${collectionName} in ${country.toUpperCase()}...`
            );

            const listApps = await store.list({
              category: category,
              collection: collection,
              num: 200, // Maximum per collection per country
              country: country,
            });

            // Filter apps based on category
            const filteredApps = listApps.filter((app) => {
              // For SPORTS category, accept all apps (already categorized by Apple)
              if (category === store.category.SPORTS) return true;

              // For HEALTH_AND_FITNESS category, apply filtering
              const title = app.title ? app.title.toLowerCase() : "";
              const description = app.description
                ? app.description.toLowerCase()
                : "";
              const developer = app.developer
                ? app.developer.toLowerCase()
                : "";
              const textToCheck =
                `${title} ${description} ${developer}`.toLowerCase();

              // Sports/fitness indicators
              const sportsIndicators = [
                "workout",
                "exercise",
                "fitness",
                "gym",
                "training",
                "muscle",
                "strength",
                "cardio",
                "hiit",
                "crossfit",
                "bodybuilding",
                "powerlifting",
                "athletic",
                "coach",
                "personal trainer",
                "sports",
                "running",
                "cycling",
                "swimming",
                "football",
                "soccer",
                "basketball",
                "tennis",
                "golf",
                "baseball",
                "hockey",
                "volleyball",
                "rugby",
                "cricket",
                "athletics",
                "marathon",
                "triathlon",
                "activity tracker",
                "step counter",
                "fitness tracker",
              ];

              const hasSportsContent = sportsIndicators.some((indicator) =>
                textToCheck.includes(indicator)
              );

              // Exclude purely non-sports apps
              const purelyExcludedKeywords = [
                "period tracker",
                "menstrual",
                "pregnancy",
                "baby",
                "fertility",
                "ovulation",
                "brain training",
                "meditation app",
                "sleep stories",
                "mindfulness",
                "dating",
                "relationship",
                "social network",
                "chat",
                "messaging",
                "blood pressure",
                "diabetes",
                "medication",
                "pill reminder",
                "doctor",
                "hospital",
                "beauty",
                "skincare",
                "hair",
                "makeup",
                "fashion",
                "water reminder",
                "drinking water reminder",
              ];

              const isPurelyExcluded = purelyExcludedKeywords.some((keyword) =>
                textToCheck.includes(keyword)
              );

              // Exclude only if purely excluded AND has no sports content
              if (isPurelyExcluded && !hasSportsContent) return false;

              // Language filtering: prefer English content
              const isLikelyEnglish = (text) => {
                const englishIndicators =
                  /\b(and|the|for|with|app|your|free|best|new|get|play|game|sport|fitness|workout|training|run|bike|swim|coach|team|score|live|watch|track|timer|stats)\b/i;
                const hasExcessiveNonLatinChars =
                  /[^\x00-\x7F].*[^\x00-\x7F].*[^\x00-\x7F]/;
                return (
                  englishIndicators.test(text) &&
                  !hasExcessiveNonLatinChars.test(text)
                );
              };

              const titleAndDescription = `${title} ${description}`.substring(
                0,
                300
              );
              if (!isLikelyEnglish(titleAndDescription)) {
                return false;
              }

              return hasSportsContent;
            });

            let newAppsCount = 0;
            filteredApps.forEach((app) => {
              if (!allApps.find((existingApp) => existingApp.id === app.id)) {
                allApps.push({
                  ...app,
                  sourceMethod: "list",
                  sourceCollection: collectionName,
                  sourceCountry: country,
                  targetCategory: categoryName,
                });
                newAppsCount++;
              }
            });

            console.log(
              `    ✅ Added ${newAppsCount} new apps from ${collectionName} in ${country.toUpperCase()}`
            );

            // Delay to avoid rate limiting
            await new Promise((resolve) => setTimeout(resolve, 1000));
          } catch (error) {
            console.warn(
              `    ⚠️ Failed to fetch from ${collection} in ${country.toUpperCase()}: ${
                error.message
              }`
            );
          }
        }
      }

      // Step 2: Search with category-specific terms
      const searchQueries = {
        [store.category.SPORTS]: [
         // Traditional Sports
          "football",
          "soccer",
          "basketball",
          "baseball",
          "tennis",
          "golf",
          "disc golf",
          "running",
          "cycling",
          "swimming",
          "volleyball",
          "hockey",
          "ice hockey",
          "floorball",
          "padel",
          "rugby",
          "cricket",
          "athletics",
          "track and field",
          "marathon",
          "triathlon",
          "badminton",
          "squash",
          "boxing",
          "martial arts",
          "gymnastics",
          "skiing",
          "snowboarding",
          "surfing",
          "skateboarding",
          "climbing",
          "hiking",
          "fishing",
          "hunting",
          "sailing",
          "rowing",
          "kayaking",
          "table tennis",
          "darts",
          "bowling",
          "archery",
          "motorsports",
          "auto racing",
          "motocross",
          "equestrian",
          "horse racing",
          "kabaddi",
          "sepak takraw",
          "hurling",
          "petanque",
          "water polo",
          "biathlon",
          "synchronized swimming",
          "canoeing",
          "bouldering",
          "futsal",
          "breakdancing",
          "polo",
          "netball",
          "lacrosse",
          "field hockey",
          "handball",
          "ultimate frisbee",
          "figure skating",
          "speed skating",
          "bobsled",
          "luge",
          "skeleton",
          "diving",
          "water skiing",
          "wakeboarding",
          "windsurfing",
          "kitesurfing",
          "shot put",
          "discus",
          "javelin",
          "hammer throw",
          "pole vault",
          "long jump",
          "high jump",
          "racquetball",
          "pickleball",
          "cheerleading",
          "dance sport",
          "roller derby",
          "bmx",
          "weightlifting",
          "powerlifting",
          "crossfit",

          

          // Combat Sports
          "mma",
          "mixed martial arts",
          "judo",
          "karate",
          "taekwondo",
          "kickboxing",
          "sumo",
          "wrestling",
          "kendo",
          "jai alai",
          "kung fu",
          "kung fu combat",
          "capoeira",


          // Sports Services
          "sports news",
          "sports scores",
          "fantasy sports",
          "sports betting",
          "esports",
          "sports coach",
          "sports training",
          "team management",
          "sports analytics",
          "sports statistics",
          "sports live",
          "sports streaming",

          // Equipment & Tracking
          "sports tracker",
          "sports timer",
          "sports stats",
          "referee",
          "scorekeeper",
        ],
        [store.category.HEALTH_AND_FITNESS]: [
          // Workout Types
          "workout",
          "exercise",
          "gym",
          "fitness training",
          "strength training",
          "cardio workout",
          "hiit workout",
          "crossfit",
          "bodybuilding",
          "powerlifting",
          "weightlifting",
          "calisthenics",
          "functional training",
          "circuit training",
          "interval training",
          "tabata",
          "pilates",
          "yoga",
          "barre",
          "zumba",

          // Home & Equipment
          "home workout",
          "home gym",
          "dumbbell workout",
          "barbell workout",
          "kettlebell",
          "resistance band",
          "pull up",
          "push up",
          "abs workout",
          "core workout",
          "leg workout",
          "arm workout",
          "chest workout",
          "back workout",

          // Trainers & Coaching
          "personal trainer",
          "fitness coach",
          "workout coach",
          "exercise coach",
          "training program",
          "workout plan",
          "fitness plan",
          "exercise routine",

          // Tracking & Measurement
          "exercise tracker",
          "workout tracker",
          "fitness tracker",
          "activity tracker",
          "step counter",
          "fitness monitoring",

          // Specialized Fitness
          "muscle building",
          "weight training",
          "athletic training",
          "sports performance",
          "flexibility",
          "mobility",
          "stretching",
        ],
      };

      console.log(
        `  🔍 Searching with ${categoryName} specific terms across multiple countries...`
      );
      const queries = searchQueries[category] || [];

      for (const query of queries) {
        // Search across top countries for each query
        for (const country of targetCountries.slice(0, 8)) {
          // Top 8 countries for search
          try {
            console.log(
              `    Searching: "${query}" in ${country.toUpperCase()}`
            );
            const searchApps = await store.search({
              term: query,
              num: 50, // Maximum results per search
              country: country,
            });

            // Apply sports-focused filtering
            const filteredSearchApps = searchApps.filter((app) => {
              const genre = app.genre ? app.genre.toLowerCase() : "";
              const title = app.title ? app.title.toLowerCase() : "";
              const developer = app.developer
                ? app.developer.toLowerCase()
                : "";
              const description = app.description
                ? app.description.toLowerCase()
                : "";
              const searchQuery = query.toLowerCase();
              const textToCheck =
                `${title} ${description} ${developer}`.toLowerCase();

              // For SPORTS category searches, be more lenient - only exclude obvious non-sports
              if (category === store.category.SPORTS) {
                // Only exclude purely non-sports apps
                const obviouslyNonSports = [
                  "period tracker",
                  "menstrual cycle",
                  "pregnancy tracker",
                  "baby tracker",
                  "fertility tracker",
                  "ovulation tracker",
                  "brain training games",
                  "meditation app",
                  "sleep stories",
                  "mindfulness meditation",
                  "dating app",
                  "relationship advice",
                  "social dating",
                  "chat app",
                  "messaging app",
                  "blood pressure monitor",
                  "diabetes management",
                  "medication reminder",
                  "pill reminder",
                  "doctor appointment",
                  "hospital finder",
                  "beauty tips",
                  "skincare routine",
                  "hair care",
                  "makeup tutorial",
                  "fashion advice",
                  "water reminder app",
                  "drinking water reminder",
                  "hydration reminder",
                ];

                const isObviouslyNonSports = obviouslyNonSports.some(
                  (keyword) => textToCheck.includes(keyword)
                );

                // For SPORTS searches, exclude only obviously non-sports apps
                return !isObviouslyNonSports;
              }

              // For HEALTH_AND_FITNESS category searches, apply full filtering
              // Check if app has sports/fitness content
              const sportsIndicators = [
                "workout",
                "exercise",
                "fitness",
                "gym",
                "training",
                "muscle",
                "strength",
                "cardio",
                "hiit",
                "crossfit",
                "bodybuilding",
                "powerlifting",
                "athletic",
                "coach",
                "personal trainer",
                "sports",
                "running",
                "cycling",
                "swimming",
                "football",
                "soccer",
                "basketball",
                "tennis",
                "golf",
                "baseball",
                "hockey",
                "volleyball",
                "rugby",
                "cricket",
                "athletics",
                "marathon",
                "triathlon",
                "activity tracker",
                "step counter",
                "fitness tracker",
              ];

              const hasSportsContent = sportsIndicators.some((indicator) =>
                textToCheck.includes(indicator)
              );

              // Exclude purely non-sports apps
              const purelyExcludedKeywords = [
                "period tracker",
                "menstrual cycle",
                "pregnancy tracker",
                "baby tracker",
                "fertility tracker",
                "ovulation tracker",
                "brain training games",
                "meditation app",
                "sleep stories",
                "mindfulness meditation",
                "dating app",
                "relationship advice",
                "social dating",
                "chat app",
                "messaging app",
                "blood pressure monitor",
                "diabetes management",
                "medication reminder",
                "pill reminder",
                "doctor appointment",
                "hospital finder",
                "beauty tips",
                "skincare routine",
                "hair care",
                "makeup tutorial",
                "fashion advice",
                "water reminder app",
                "drinking water reminder",
                "hydration reminder",
              ];

              const isPurelyExcluded = purelyExcludedKeywords.some((keyword) =>
                textToCheck.includes(keyword)
              );

              if (isPurelyExcluded && !hasSportsContent) return false;

              // Language filtering
              const isLikelyEnglish = (text) => {
                const englishIndicators =
                  /\b(and|the|for|with|app|your|free|best|new|get|play|game|sport|fitness|workout|training|run|bike|swim|coach|team|score|live|watch|track|timer|stats)\b/i;
                const hasExcessiveNonLatinChars =
                  /[^\x00-\x7F].*[^\x00-\x7F].*[^\x00-\x7F]/;
                return (
                  englishIndicators.test(text) &&
                  !hasExcessiveNonLatinChars.test(text)
                );
              };

              const titleAndDescription = `${title} ${description}`.substring(
                0,
                300
              );
              if (!isLikelyEnglish(titleAndDescription)) {
                return false;
              }

              // Include if it matches sports/athletics criteria
              return (
                // Primary sports genre
                genre.includes("sports") ||
                genre.includes("health") ||
                genre.includes("fitness") ||
                // Has sports/fitness content
                hasSportsContent ||
                // Sports-specific terms in title
                title.includes("football") ||
                title.includes("soccer") ||
                title.includes("basketball") ||
                title.includes("tennis") ||
                title.includes("golf") ||
                title.includes("baseball") ||
                title.includes("hockey") ||
                title.includes("volleyball") ||
                title.includes("rugby") ||
                title.includes("cricket") ||
                title.includes("athletics") ||
                title.includes("marathon") ||
                title.includes("triathlon") ||
                title.includes("cycling") ||
                title.includes("running") ||
                title.includes("swimming") ||
                title.includes("sports") ||
                title.includes("fitness") ||
                title.includes("workout") ||
                title.includes("exercise") ||
                // If search query is sport-specific and appears in title/description
                (searchQuery.match(
                  /football|soccer|basketball|tennis|golf|baseball|hockey|volleyball|rugby|cricket|athletics|marathon|triathlon|cycling|running|swimming|workout|exercise|fitness|gym|training/
                ) &&
                  (title.includes(searchQuery) ||
                    description.includes(searchQuery)))
              );
            });

            let newSearchAppsCount = 0;
            filteredSearchApps.forEach((app) => {
              if (!allApps.find((existingApp) => existingApp.id === app.id)) {
                allApps.push({
                  ...app,
                  sourceMethod: "search",
                  searchQuery: query,
                  sourceCountry: country,
                  targetCategory: categoryName,
                });
                newSearchAppsCount++;
              }
            });

            if (newSearchAppsCount > 0) {
              console.log(
                `      ✅ Added ${newSearchAppsCount} new apps from "${query}" in ${country.toUpperCase()}`
              );
            }

            // Delay to avoid rate limiting
            await new Promise((resolve) => setTimeout(resolve, 800));
          } catch (searchError) {
            console.warn(
              `      ⚠️ Search failed for "${query}" in ${country.toUpperCase()}: ${
                searchError.message
              }`
            );
          }
        }
      }
    }

    console.log(
      `\n🎯 Total unique App Store sports/fitness apps collected: ${allApps.length}`
    );
    return allApps;
  } catch (error) {
    console.error(
      `Error in App Store comprehensive app collection: ${error.message}`
    );
    return [];
  }
}

/**
 * Print summary statistics of the collected App Store apps
 * @param {Array} apps - Array of app objects
 */
function printAppStoreSummary(apps) {
  console.log("\n📊 APP STORE COLLECTION SUMMARY");
  console.log("=".repeat(50));

  // Category breakdown
  const categoryCount = {};
  const sourceMethodCount = {};
  const countryCount = {};
  const freeVsPaid = { free: 0, paid: 0 };

  apps.forEach((app) => {
    // Count by target category
    const category = app.targetCategory || app.genre || "Unknown";
    categoryCount[category] = (categoryCount[category] || 0) + 1;

    // Count by source method
    const source = app.sourceMethod || "unknown";
    sourceMethodCount[source] = (sourceMethodCount[source] || 0) + 1;

    // Count by country
    const country = app.sourceCountry || "unknown";
    countryCount[country] = (countryCount[country] || 0) + 1;

    // Count free vs paid
    if (app.free) {
      freeVsPaid.free++;
    } else {
      freeVsPaid.paid++;
    }
  });

  console.log(`Total Apps: ${apps.length}`);

  console.log("\nBy Category:");
  Object.entries(categoryCount).forEach(([cat, count]) => {
    console.log(`  ${cat}: ${count} apps`);
  });

  console.log("\nBy Source Method:");
  Object.entries(sourceMethodCount).forEach(([method, count]) => {
    console.log(`  ${method}: ${count} apps`);
  });

  console.log("\nBy Country (Top 10):");
  const topCountries = Object.entries(countryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 30);
  topCountries.forEach(([country, count]) => {
    console.log(`  ${country.toUpperCase()}: ${count} apps`);
  });

  console.log(`\nFree vs Paid:`);
  console.log(`  Free: ${freeVsPaid.free} apps`);
  console.log(`  Paid: ${freeVsPaid.paid} apps`);

  // Top developers
  const developerCount = {};
  apps.forEach((app) => {
    if (app.developer) {
      developerCount[app.developer] = (developerCount[app.developer] || 0) + 1;
    }
  });

  const topDevelopers = Object.entries(developerCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  console.log("\nTop 10 Developers:");
  topDevelopers.forEach(([dev, count], index) => {
    console.log(`  ${index + 1}. ${dev}: ${count} apps`);
  });
}

/**
 * Export App Store apps data to JSON file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportAppStoreToJSON(
  apps,
  filename = "appstore_sports_fitness_apps.json"
) {
  try {
    const exportData = {
      platform: "Apple App Store",
      exportDate: new Date().toISOString(),
      totalApps: apps.length,
      searchScope: "Global - Multiple Countries",
      countriesSearched: [
        "US",
        "GB",
        "CA",
        "AU",
        "DE",
        "FR",
        "IT",
        "ES",
        "NL",
        "SE",
        "DK",
        "NO",
        "FI",
        "IE",
        "CH",
        "AT",
        "BE",
        "JP",
        "KR",
        "BR",
      ],
      languageFilter: "English preferred",
      apps: apps.map((app) => ({
        title: app.title,
        appId: app.appId,
        id: app.id,
        developer: app.developer,
        category: app.genre || app.targetCategory,
        rating: app.score,
        price: app.price,
        currency: app.currency,
        free: app.free,
        url: app.url,
        description: app.description,
        icon: app.icon,
        released: app.released,
        sourceMethod: app.sourceMethod,
        sourceCollection: app.sourceCollection || null,
        sourceCountry: app.sourceCountry || null,
        searchQuery: app.searchQuery || null,
        targetCategory: app.targetCategory,
      })),
    };

    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    console.log(`\n📁 App Store JSON data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export App Store JSON: ${error.message}`);
  }
}

/**
 * Export App Store apps data to CSV file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportAppStoreToCSV(
  apps,
  filename = "appstore_sports_fitness_apps.csv"
) {
  try {
    const headers = [
      "Title",
      "App ID",
      "ID",
      "Developer",
      "Category",
      "Rating",
      "Price",
      "Currency",
      "Free",
      "URL",
      "Description",
      "Icon",
      "Released",
      "Source Method",
      "Source Collection",
      "Source Country",
      "Search Query",
      "Target Category",
    ];

    const csvRows = [headers.join(",")];

    apps.forEach((app) => {
      const row = [
        `"${(app.title || "").replace(/"/g, '""')}"`,
        `"${app.appId || ""}"`,
        `"${app.id || ""}"`,
        `"${(app.developer || "").replace(/"/g, '""')}"`,
        `"${app.genre || app.targetCategory || ""}"`,
        app.score || "",
        app.price || "",
        app.currency || "",
        app.free ? "TRUE" : "FALSE",
        `"${app.url || ""}"`,
        `"${(app.description || "").replace(/"/g, '""').substring(0, 200)}"`,
        `"${app.icon || ""}"`,
        `"${app.released || ""}"`,
        app.sourceMethod || "",
        app.sourceCollection || "",
        app.sourceCountry || "",
        app.searchQuery || "",
        app.targetCategory || "",
      ];
      csvRows.push(row.join(","));
    });

    await fs.writeFile(filename, csvRows.join("\n"));
    console.log(`📊 App Store CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export App Store CSV: ${error.message}`);
  }
}

// Main execution
async function main() {
  console.log(
    "🚀 Starting comprehensive App Store SPORTS & FITNESS app mapping..."
  );
  console.log(
    "🍎 Target: Apple App Store apps in SPORTS and HEALTH_AND_FITNESS categories"
  );

  const apps = await getSportsAndFitnessAppsAppStore(5000); // Large limit for maximum coverage

  if (apps.length > 0) {
    printAppStoreSummary(apps);

    // Export to both formats
    await exportAppStoreToJSON(
      apps,
      "appstore_sports_fitness_apps_comprehensive.json"
    );
    await exportAppStoreToCSV(
      apps,
      "appstore_sports_fitness_apps_comprehensive.csv"
    );

    console.log(
      "\n✅ Comprehensive App Store sports & fitness app mapping completed!"
    );
    console.log("📄 Files created:");
    console.log(
      "  - appstore_sports_fitness_apps_comprehensive.json (for data analysis)"
    );
    console.log(
      "  - appstore_sports_fitness_apps_comprehensive.csv (for Excel import)"
    );
    console.log(
      `\n🍎 Summary: Collected ${apps.length} sports/fitness apps from Apple App Store`
    );
  } else {
    console.log(
      "❌ No apps were collected. Check your internet connection and try again."
    );
  }
}

main();
