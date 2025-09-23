import gplay from "google-play-scraper";
import fs from "fs/promises";

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from multiple countries
 * Combines multiple collections and search results
 * @param {number} numApps - Total number of apps to retrieve per category
 * @returns {Promise<Array>} Promise that resolves to an array of filtered app objects
 */
async function getSportsAndFitnessAppsGlobal(numApps = 1000) {
  try {
    let allApps = [];
    const targetCategories = ["SPORTS", "HEALTH_AND_FITNESS"];

    // Countries to search - expanded for maximum global coverage
    const targetCountries = [
      // English-speaking countries (primary)
      "us",
      "gb",
      "ca",
      "au",
      "nz",
      "ie",
      "za",

      // Major EU countries
      "de",
      "fr",
      "it",
      "es",
      "nl",
      "se",
      "dk",
      "no",
      "fi",
      "ch",
      "at",
      "be",
      "pt",
      "pl",

      // Additional European countries
      "cz",
      "sk",
      "hu",
      "gr",
      "ro",
      "bg",
      "hr",
      "si",
      "ee",
      "lv",
      "lt",
      "lu",
      "mt",
      "cy",

      // Major global markets
      "br",
      "mx",
      "ar",
      "cl",
      "co",
      "pe", // Latin America
      "jp",
      "kr",
      "sg",
      "my",
      "th",
      "ph",
      "vn",
      "id", // Asia Pacific
      "in",
      "pk",
      "bd",
      "lk", // South Asia
      "eg",
      "ma",
      "ng",
      "ke",
      "za", // Africa & Middle East
      "tr",
      "il",
      "ae",
      "sa", // Middle East
      "ru",
      "ua",
      "by",
      "kz", // Eastern Europe/CIS
    ];

    console.log(
      "🏃‍♂️ Starting GLOBAL comprehensive SPORTS & FITNESS app collection..."
    );
    console.log(
      `🌍 Searching across ${
        targetCountries.length
      } countries: ${targetCountries.join(", ").toUpperCase()}`
    );

    // Calculate time estimation
    const collections = [
      gplay.collection.GROSSING,
      gplay.collection.TOP_FREE,
      gplay.collection.TOP_PAID,
    ];

    // Calculate search queries for both categories
    const sportsQueries = [
        "football", "soccer", "futbol", "american football", "flag football", "australian football", "gaelic football",
  "basketball", "3x3 basketball", "streetball", 
  "baseball", "softball", "fastpitch",
  "tennis", "padel", "beach tennis", "paddle tennis",
  "golf", "disc golf", "mini golf", "putting", "golf swing",
  "running", "trail running", "jogging", "sprint", "ultra running",
  "cycling", "mountain biking", "road cycling", "gravel cycling", "cyclocross",
  "swimming", "open water swimming", "pool swimming", "swim workout",
  "volleyball", "beach volleyball", "indoor volleyball",
  "hockey", "ice hockey", "field hockey", "street hockey", "ball hockey", "floorball",
  "rugby", "sevens rugby",
  "cricket", "test cricket", "T20", "ODI", "cricket live",
  "athletics", "track and field", "marathon", "triathlon", "ironman", "duathlon", "aquathlon",
  "badminton", "squash", "racquetball", 
  "boxing", "muay thai", "savate",
  "martial arts", "kung fu", "capoeira", "wushu",
  "gymnastics", "trampoline",
  "skiing", "cross-country skiing", "snowboarding", 
  "surfing", "bodyboarding", "wake surfing", "windsurfing", "kitesurfing",
  "skateboarding", "longboarding", "skateboard tricks",
  "climbing", "bouldering", "top rope", "lead climbing", "mountaineering",
  "hiking", "backpacking", "trekking",
  "fishing", "fly fishing", "ice fishing", "bass fishing",
  "hunting", "deer hunting", "duck hunting",
  "sailing", "rowing", "kayaking", "canoeing",
  "table tennis", "darts", "bowling", "ten-pin bowling", "nine-pin", "bowls",
  "archery", "kyudo",
  "motorsports", "auto racing", "motocross", "F1",
  "equestrian", "horse racing", "dressage", "show jumping", "eventing", "rodeo",
  
  // New Sports Additions
  "curling", "sledge hockey", "goalball", "bocce", "croquet", "petanque",
  "fencing", "sport shooting", "biathlon", "modern pentathlon", "decathlon",
  "water polo", "synchronized swimming", "diving", "water skiing", "wakeboarding",
  "ultimate frisbee", "futsal", "netball", "lacrosse", "handball",
  "figure skating", "speed skating", "bobsled", "luge", "skeleton",
  "powerlifting", "bodybuilding", "crossfit", "calisthenics", "parkour",
  "breakdancing", "cheerleading", "dance sport", "roller derby", 
  "kabaddi", "sepak takraw", "hurling", "kho kho", "gilli danda",
  "footvolley", "jai alai", "bullfighting", "arnis", "sipa",
  
  // Combat Sports
  "mma", "mixed martial arts", "judo", "karate", "taekwondo", "kickboxing", 
  "sumo", "wrestling", "kendo", "sambo", "krav maga", "bjj", "brazilian jiu-jitsu",
  
  // Sports Services & Management
  "sports news", "sports scores", "sports highlights", "sports live", "sports streaming",
  "fantasy sports", "sports betting", "sports odds", 
  "sports coach", "sports training", "sports technique", "sports drills",
  "team management", "sports league", "sports tournament", "sports registration",
  "sports club", "sports academy", "sports tryouts", "sports recruiting",
  "sports analytics", "sports statistics", "sports metrics", "sports AI",
  "sports physio", "sports rehab", "sports injury", "sports medicine",
  "sports nutrition", "sports diet", "sports psychology",
  "sports tickets", "sports events", "sports events near me",
 "sports video analysis", "sports replay", "sports VR", "sports AR",
  
  // Equipment & Tracking
  "sports tracker", "sports GPS", "sports wearable", "sports watch",
  "sports timer", "sports sensor", "sports tech", "sports performance",
  "referee", "scorekeeper", "sports whistle",
  
  // Youth & Specialized
  "youth sports", "sports for kids", "sports camps",
  "paralympic sports", "adaptive sports", "veteran sports",
  
  // eSports & Virtual
  "esports", "esports team", "esports tournament", 
  "esports news", "esports scores", "esports betting", "esports stream"
    ];

    const fitnessQueries = [
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
      "personal trainer",
      "fitness coach",
      "workout coach",
      "exercise coach",
      "training program",
      "workout plan",
      "fitness plan",
      "exercise routine",
      "exercise tracker",
      "workout tracker",
      "fitness tracker",
      "activity tracker",
      "step counter",
      "calorie tracker",
      "heart rate",
      "fitness monitoring",
      "muscle building",
      "fat loss",
      "weight training",
      "athletic training",
      "sports performance",
      "flexibility",
      "mobility",
      "stretching",
      "rehabilitation",
      "physical therapy",
      "injury prevention",
      "group fitness",
      "fitness class",
      "workout class",
      "boot camp",
      "spin class",
      "cycling class",
      "aerobics",
      "dance fitness",
    ];

    const totalCollectionCalls =
      targetCategories.length * collections.length * targetCountries.length; // categories × collections × countries
    const totalSearchCalls =
      (sportsQueries.length + fitnessQueries.length) * targetCountries.length; 
    const totalAPICalls = totalCollectionCalls + totalSearchCalls;
    const estimatedTimeSeconds = totalAPICalls * 0.8; // 0.8 seconds per call (faster than App Store)
    const estimatedTimeMinutes = Math.round(estimatedTimeSeconds / 60);
    const estimatedTimeHours = Math.floor(estimatedTimeMinutes / 60);
    const remainingMinutes = estimatedTimeMinutes % 60;

    console.log(`\n⏱️  TIME ESTIMATION:`);
    console.log(
      `   📋 Collection calls: ${totalCollectionCalls} (${targetCategories.length} categories × ${collections.length} collections × ${targetCountries.length} countries)`
    );
    console.log(
      `   🔍 Search calls: ${totalSearchCalls} (${
        sportsQueries.length + fitnessQueries.length
      } search terms × ${targetCountries.length} countries)`
    );
    console.log(`   🎯 Total API calls: ${totalAPICalls}`);
    console.log(
      `   ⌛ Estimated time: ~ ${estimatedTimeHours}h ${remainingMinutes}m (${estimatedTimeSeconds} seconds)`
    );
    console.log(`   🚀 Starting collection process...\n`);

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
              num: 250, // Maximum apps per collection per country
              country: country,
            });

            // No filtering - accept all apps from the categories
            const filteredApps = listApps;

            let newAppsCount = 0;
            filteredApps.forEach((app) => {
              if (
                !allApps.find((existingApp) => existingApp.appId === app.appId)
              ) {
                allApps.push({
                  ...app,
                  sourceMethod: "list",
                  sourceCollection: collection,
                  sourceCountry: country,
                  targetCategory: category,
                });
                newAppsCount++;
              }
            });

            console.log(
              `    ✅ Added ${newAppsCount} new apps from ${collection} in ${country.toUpperCase()}`
            );

            // Delay to avoid rate limiting (reduced for faster execution)
            await new Promise((resolve) => setTimeout(resolve, 800));
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
          "sailing",
          "rowing",

          // Regional & European Sports
          "handball",
          "waterpolo",
          "table tennis",
          "ping pong",
          "darts",
          "snooker",
          "pool",
          "billiards",
          "archery",
          "fencing",
          "judo",
          "karate",
          "taekwondo",
          "kickboxing",
          "mma",
          "mixed martial arts",
          "crossfit",
          "powerlifting",
          "weightlifting",
          "bodybuilding",
          "calisthenics",
          "parkour",
          "skateboard",

          // Winter Sports
          "alpine skiing",
          "cross country skiing",
          "biathlon",
          "bobsled",
          "luge",
          "figure skating",
          "speed skating",
          "curling",
          "snowboard",

          // Water Sports
          "diving",
          "synchronized swimming",
          "water skiing",
          "wakeboarding",
          "kitesurfing",
          "windsurfing",
          "paddleboarding",
          "sup",
          "kayaking",
          "canoeing",

          // Motor Sports
          "formula 1",
          "f1",
          "motorsport",
          "racing",
          "nascar",
          "rally",
          "motocross",
          "motorcycle",
          "karting",

          // Olympics & Multi-sport
          "olympics",
          "paralympics",
          "decathlon",
          "heptathlon",
          "pentathlon",

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

          // Equipment & Gear
          "sports equipment",
          "sports gear",
          "athletic gear",
          "sports shop",

          // Fitness crossover
          "athletic training",
          "sports performance",
          "sports science",
          "sports medicine",
        ],
        HEALTH_AND_FITNESS: [
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
          "calorie tracker",
          "heart rate",
          "fitness monitoring",

          // Specialized Fitness
          "muscle building",
          "fat loss",
          "weight training",
          "athletic training",
          "sports performance",
          "flexibility",
          "mobility",
          "stretching",
          "rehabilitation",
          "physical therapy",
          "injury prevention",

          // Group Fitness
          "group fitness",
          "fitness class",
          "workout class",
          "boot camp",
          "spin class",
          "cycling class",
          "aerobics",
          "dance fitness",
        ],
      };

      console.log(
        `  🔍 Searching with ${category} specific terms across multiple countries...`
      );
      const queries = searchQueries[category];

      for (const query of queries) {
        // Remove the app limit check for maximum coverage
        // if (allApps.length >= numApps * targetCategories.length) break;

        // Search across ALL countries for each query (maximum coverage)
        for (const country of targetCountries) {
          // Use ALL countries for maximum coverage
          try {
            console.log(
              `    Searching: "${query}" in ${country.toUpperCase()}`
            );
            const searchApps = await gplay.search({
              term: query,
              num: 50, // Maximum results per search
              country: country,
            });

            // No filtering - accept all search results
            const filteredSearchApps = searchApps;

            let newSearchAppsCount = 0;
            filteredSearchApps.forEach((app) => {
              if (
                !allApps.find((existingApp) => existingApp.appId === app.appId)
              ) {
                allApps.push({
                  ...app,
                  sourceMethod: "search",
                  searchQuery: query,
                  sourceCountry: country,
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

            // Delay to avoid rate limiting (reduced for faster execution)
            await new Promise((resolve) => setTimeout(resolve, 600));
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
      `\n🎯 Total unique sports/fitness apps collected globally: ${allApps.length}`
    );
    return allApps;
  } catch (error) {
    console.error(
      `Error in global comprehensive app collection: ${error.message}`
    );
    return [];
  }
}

/**
 * Print summary statistics of the collected apps including country breakdown
 * @param {Array} apps - Array of app objects
 */
function printGlobalSummary(apps) {
  console.log("\n📊 GLOBAL COLLECTION SUMMARY");
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
    .slice(0, 10);
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
 * Export apps data to JSON file with global metadata
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportToJSONGlobal(
  apps,
  filename = "global_sports_fitness_apps.json"
) {
  try {
    const exportData = {
      exportDate: new Date().toISOString(),
      totalApps: apps.length,
      searchScope: "Global - Maximum Coverage",
      languageFilter: "English preferred",
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
        sourceCountry: app.sourceCountry || null,
        searchQuery: app.searchQuery || null,
        targetCategory: app.targetCategory,
      })),
    };

    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    console.log(`\n📁 Global JSON data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export global JSON: ${error.message}`);
  }
}

/**
 * Export apps data to CSV file with country information
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportToCSVGlobal(
  apps,
  filename = "global_sports_fitness_apps.csv"
) {
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
      "Source Country",
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
        app.sourceCountry || "",
        app.searchQuery || "",
        app.targetCategory || "",
      ];
      csvRows.push(row.join(","));
    });

    await fs.writeFile(filename, csvRows.join("\n"));
    console.log(`📊 Global CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export global CSV: ${error.message}`);
  }
}

// Main execution
async function main() {
  const startTime = Date.now();
  const startTimeFormatted = new Date().toISOString();

  console.log(
    "🚀 Starting GLOBAL comprehensive SPORTS & FITNESS app mapping..."
  );
  console.log("🌍 Target: Google Play Store apps from multiple countries");
  console.log("📱 Categories: SPORTS and HEALTH_AND_FITNESS");
  console.log(`⏰ Started at: ${startTimeFormatted}`);

  const apps = await getSportsAndFitnessAppsGlobal(100000); // Massive limit for maximum coverage

  if (apps.length > 0) {
    printGlobalSummary(apps);

    // Export to both formats with global prefix
    await exportToJSONGlobal(
      apps,
      "global_sports_fitness_apps_comprehensive.json"
    );
    await exportToCSVGlobal(
      apps,
      "global_sports_fitness_apps_comprehensive.csv"
    );

    console.log(
      "\n✅ Global comprehensive sports & fitness app mapping completed!"
    );
    console.log("📄 Files created:");
    console.log(
      "  - global_sports_fitness_apps_comprehensive.json (for data analysis)"
    );
    console.log(
      "  - global_sports_fitness_apps_comprehensive.csv (for Excel import)"
    );
    console.log(
      `\n🌍 Summary: Collected ${apps.length} sports/fitness apps from multiple countries`
    );

    // Calculate and display actual time taken
    const endTime = Date.now();
    const endTimeFormatted = new Date().toISOString();
    const actualDurationMs = endTime - startTime;
    const actualDurationSeconds = Math.round(actualDurationMs / 1000);
    const actualDurationMinutes = Math.floor(actualDurationSeconds / 60);
    const actualDurationHours = Math.floor(actualDurationMinutes / 60);
    const remainingMinutes = actualDurationMinutes % 60;
    const remainingSeconds = actualDurationSeconds % 60;

    console.log(`\n⏱️  ACTUAL TIME TAKEN:`);
    console.log(`   🏁 Finished at: ${endTimeFormatted}`);
    console.log(
      `   ⌛ Total duration: ${actualDurationHours}h ${remainingMinutes}m ${remainingSeconds}s (${actualDurationSeconds} seconds)`
    );
    console.log(`   📊 Performance: ${actualDurationMs}ms total`);
  } else {
    console.log(
      "❌ No apps were collected. Check your internet connection and try again."
    );
  }
}

main();
