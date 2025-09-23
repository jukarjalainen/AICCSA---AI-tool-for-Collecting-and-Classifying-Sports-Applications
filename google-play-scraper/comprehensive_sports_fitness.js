import gplay from "google-play-scraper";
import fs from "fs/promises";

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps
 * Combines multiple collections and search results with category filtering
 * @param {number} numApps - Total number of apps to retrieve per category
 * @returns {Promise<Array>} Promise that resolves to an array of filtered app objects
 */
async function getSportsAndFitnessApps(numApps = 1000) {
  try {
    let allApps = [];
    const targetCategories = ["SPORTS", "HEALTH_AND_FITNESS"];

    // Countries to search - includes US, major EU countries, and English-speaking countries
    const targetCountries = [
      "us", // United States
      "gb", // United Kingdom
      "ca", // Canada
      "au", // Australia
      "de", // Germany
      "fr", // France
      "it", // Italy
      "es", // Spain
      "nl", // Netherlands
      "se", // Sweden
      "dk", // Denmark
      "no", // Norway
      "fi", // Finland
      "ie", // Ireland
      "ch", // Switzerland
      "at", // Austria
      "be", // Belgium
    ];

    console.log("🏃‍♂️ Starting comprehensive SPORTS & FITNESS app collection...");
    console.log(
      `🌍 Searching across ${
        targetCountries.length
      } countries: ${targetCountries.join(", ").toUpperCase()}`
    );

    for (const category of targetCategories) {
      console.log(`\n📱 Processing ${category} category...`);

      // Step 1: Get apps from multiple collections across different countries
      const collections = [
        gplay.collection.GROSSING,
        gplay.collection.TOP_FREE,
        gplay.collection.TOP_PAID,
      ];

      for (const collection of collections) {
        for (const country of targetCountries) {
          try {
            console.log(
              `  📋 Fetching from ${collection} in ${country.toUpperCase()}...`
            );
            const listApps = await gplay.list({
              category: gplay.category[category],
              collection: collection,
              num: 200, // Reduced per country to avoid overwhelming results
              country: country,
            });

            // Filter out non-sports apps even from SPORTS and HEALTH_AND_FITNESS categories
            const filteredApps = listApps.filter((app) => {
              const title = app.title ? app.title.toLowerCase() : "";
              const summary = app.summary ? app.summary.toLowerCase() : "";
              const developer = app.developer
                ? app.developer.toLowerCase()
                : "";
              const textToCheck =
                `${title} ${summary} ${developer}`.toLowerCase();

              // First check if app has sports/fitness indicators
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
              ];

              const hasSportsContent = sportsIndicators.some((indicator) =>
                textToCheck.includes(indicator)
              );

              // Only exclude apps that are PURELY focused on excluded topics AND have no sports content
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

              // Exclude only if it's purely about excluded topics AND has no sports content
              if (isPurelyExcluded && !hasSportsContent) return false;

              // Language filtering: prefer English content (basic check)
              const isLikelyEnglish = (text) => {
                // Basic heuristic: check for common English words and absence of non-Latin scripts
                const englishIndicators =
                  /\b(and|the|for|with|app|your|free|best|new|get|play|game|sport|fitness|workout|training)\b/i;
                const hasNonLatinChars = /[^\x00-\x7F]/;
                return (
                  englishIndicators.test(text) && !hasNonLatinChars.test(text)
                );
              };

              const titleAndSummary = `${title} ${summary}`.substring(0, 200);
              if (!isLikelyEnglish(titleAndSummary)) {
                return false; // Skip non-English apps
              }

              // For SPORTS category, be more lenient - include most apps
              if (category === "SPORTS") return true;

              // For HEALTH_AND_FITNESS, include if it has any sports/fitness content
              if (category === "HEALTH_AND_FITNESS") {
                return hasSportsContent;
              }

              return true;
            });

            let newAppsCount = 0;
            filteredApps.forEach((app) => {
              if (
                !allApps.find((existingApp) => existingApp.appId === app.appId)
              ) {
                allApps.push({
                  ...app,
                  sourceMethod: "list",
                  sourceCollection: collection,
                  targetCategory: category,
                });
                newAppsCount++;
              }
            });

            console.log(
              `    ✅ Added ${newAppsCount} new apps from ${collection} in ${country.toUpperCase()}`
            );

            // Delay to avoid rate limiting
            await new Promise((resolve) => setTimeout(resolve, 1200));
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
        SPORTS: [
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
          "sports news",
          "sports scores",
          "fantasy sports",
          "sports betting",
          "badminton",
          "squash",
          "boxing",
          "martial arts",
          "wrestling",
          "gymnastics",
          "skiing",
          "snowboarding",
          "surfing",
          "skateboarding",
          "climbing",
          "hiking",
          "fishing",
          "hunting",
          "esports",
          "sports coach",
          "sports training",
          "team management",
        ],
        HEALTH_AND_FITNESS: [
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
          "personal trainer",
          "home workout",
          "exercise tracker",
          "fitness coach",
          "muscle building",
          "athletic training",
          "sports performance",
        ],
      };

      console.log(
        `  🔍 Searching with ${category} specific terms across multiple countries...`
      );
      const queries = searchQueries[category];

      for (const query of queries) {
        // Remove app limit check for maximum coverage
        // if (allApps.length >= numApps * targetCategories.length) break;

        // Search across multiple countries for each query
        for (const country of targetCountries.slice(0, 5)) {
          // Use top 5 countries for search to avoid too many requests
          try {
            console.log(
              `    Searching: "${query}" in ${country.toUpperCase()}`
            );
            const searchApps = await gplay.search({
              term: query,
              num: 30, // Reduced per country since we're searching multiple countries
              country: country,
            });

            // Sports-focused filtering to exclude general health/diet/lifestyle apps
            const filteredSearchApps = searchApps.filter((app) => {
              const genre = app.genre ? app.genre.toLowerCase() : "";
              const title = app.title ? app.title.toLowerCase() : "";
              const developer = app.developer
                ? app.developer.toLowerCase()
                : "";
              const summary = app.summary ? app.summary.toLowerCase() : "";
              const searchQuery = query.toLowerCase();
              const textToCheck =
                `${title} ${summary} ${developer}`.toLowerCase();

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

              // Exclude apps that are PURELY about these topics AND have no sports content
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

              // Exclude only if it's purely about excluded topics AND has no sports content
              if (isPurelyExcluded && !hasSportsContent) return false;

              // Language filtering: prefer English content
              const isLikelyEnglish = (text) => {
                const englishIndicators =
                  /\b(and|the|for|with|app|your|free|best|new|get|play|game|sport|fitness|workout|training)\b/i;
                const hasNonLatinChars = /[^\x00-\x7F]/;
                return (
                  englishIndicators.test(text) && !hasNonLatinChars.test(text)
                );
              };

              const titleAndSummary = `${title} ${summary}`.substring(0, 200);
              if (!isLikelyEnglish(titleAndSummary)) {
                return false; // Skip non-English apps
              }

              // Include if it matches sports/athletics criteria OR if search query is sport-specific
              return (
                // Primary sports genre
                genre.includes("sports") ||
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
                title.includes("paddle") ||
                title.includes("padel") ||
                title.includes("badminton") ||
                title.includes("squash") ||
                title.includes("boxing") ||
                title.includes("martial") ||
                title.includes("karate") ||
                title.includes("judo") ||
                title.includes("wrestling") ||
                title.includes("mma") ||
                // Sports-related services
                title.includes("sports") ||
                title.includes("fantasy sports") ||
                title.includes("sports news") ||
                title.includes("sports score") ||
                title.includes("team") ||
                title.includes("league") ||
                title.includes("tournament") ||
                // If search query is sport-specific and appears in title/summary
                (searchQuery.match(
                  /football|soccer|basketball|tennis|golf|baseball|hockey|volleyball|rugby|cricket|athletics|marathon|triathlon|cycling|running|swimming|workout|exercise|fitness|gym|training/
                ) &&
                  (title.includes(searchQuery) ||
                    summary.includes(searchQuery)))
              );
            });

            let newSearchAppsCount = 0;
            filteredSearchApps.forEach((app) => {
              if (
                !allApps.find((existingApp) => existingApp.appId === app.appId)
              ) {
                allApps.push({
                  ...app,
                  sourceMethod: "search",
                  searchQuery: query,
                  targetCategory: category,
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
            await new Promise((resolve) => setTimeout(resolve, 1000));
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
      `\n🎯 Total unique sports/fitness apps collected: ${allApps.length}`
    );
    return allApps;
  } catch (error) {
    console.error(`Error in comprehensive app collection: ${error.message}`);
    return [];
  }
}

/**
 * Print summary statistics of the collected apps
 * @param {Array} apps - Array of app objects
 */
function printSummary(apps) {
  console.log("\n📊 COLLECTION SUMMARY");
  console.log("=".repeat(50));

  // Category breakdown
  const categoryCount = {};
  const sourceMethodCount = {};
  const freeVsPaid = { free: 0, paid: 0 };

  apps.forEach((app) => {
    // Count by target category
    const category = app.targetCategory || app.genre || "Unknown";
    categoryCount[category] = (categoryCount[category] || 0) + 1;

    // Count by source method
    const source = app.sourceMethod || "unknown";
    sourceMethodCount[source] = (sourceMethodCount[source] || 0) + 1;

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
 * Export apps data to JSON file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportToJSON(apps, filename = "sports_fitness_apps.json") {
  try {
    const exportData = {
      exportDate: new Date().toISOString(),
      totalApps: apps.length,
      apps: apps.map((app) => ({
        title: app.title,
        appId: app.appId,
        developer: app.developer,
        category: app.genre || app.targetCategory,
        rating: app.score,
        installs: app.installs,
        free: app.free,
        url: app.url,
        summary: app.summary,
        sourceMethod: app.sourceMethod,
        sourceCollection: app.sourceCollection || null,
        searchQuery: app.searchQuery || null,
        targetCategory: app.targetCategory,
      })),
    };

    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    console.log(`\n📁 JSON data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export JSON: ${error.message}`);
  }
}

/**
 * Export apps data to CSV file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportToCSV(apps, filename = "sports_fitness_apps.csv") {
  try {
    const headers = [
      "Title",
      "App ID",
      "Developer",
      "Category",
      "Rating",
      "Installs",
      "Free",
      "URL",
      "Summary",
      "Source Method",
      "Source Collection",
      "Search Query",
      "Target Category",
    ];

    const csvRows = [headers.join(",")];

    apps.forEach((app) => {
      const row = [
        `"${(app.title || "").replace(/"/g, '""')}"`,
        `"${app.appId || ""}"`,
        `"${(app.developer || "").replace(/"/g, '""')}"`,
        `"${app.genre || app.targetCategory || ""}"`,
        app.score || "",
        `"${app.installs || ""}"`,
        app.free ? "TRUE" : "FALSE",
        `"${app.url || ""}"`,
        `"${(app.summary || "").replace(/"/g, '""').substring(0, 200)}"`,
        app.sourceMethod || "",
        app.sourceCollection || "",
        app.searchQuery || "",
        app.targetCategory || "",
      ];
      csvRows.push(row.join(","));
    });

    await fs.writeFile(filename, csvRows.join("\n"));
    console.log(`📊 CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export CSV: ${error.message}`);
  }
}

// Main execution
async function main() {
  console.log("🚀 Starting comprehensive SPORTS & FITNESS app mapping...");
  console.log(
    "Target: Google Play Store apps in SPORTS and HEALTH_AND_FITNESS categories"
  );

  const apps = await getSportsAndFitnessApps(10000); // Massive limit for maximum coverage

  if (apps.length > 0) {
    printSummary(apps);

    // Export to both formats
    await exportToJSON(apps, "sports_fitness_apps_comprehensive.json");
    await exportToCSV(apps, "sports_fitness_apps_comprehensive.csv");

    console.log("\n✅ Comprehensive sports & fitness app mapping completed!");
    console.log("📄 Files created:");
    console.log(
      "  - sports_fitness_apps_comprehensive.json (for data analysis)"
    );
    console.log("  - sports_fitness_apps_comprehensive.csv (for Excel import)");
  } else {
    console.log(
      "❌ No apps were collected. Check your internet connection and try again."
    );
  }
}

main();
