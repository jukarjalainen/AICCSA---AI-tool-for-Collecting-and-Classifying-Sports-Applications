import store from "app-store-scraper";
import fs from "fs/promises";
import { countries } from "../countries.js";

/**
 * Käy läpi SPORTS kategoriaa kaikista maista ja kaikista kokoelmista.
 * Hakee myös appeja search metodilla käyttäen hakusanoja
 */

// Create a logging utility that writes to both console and file
let logStream = "";
const logFileName = `appstore_scraper_log_${new Date()
  .toISOString()
  .replace(/[:.]/g, "-")}.txt`;

function logToFile(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}`;
  console.log(message); // Still show in console
  logStream += logMessage + "\n";
}

async function saveLogFile() {
  try {
    await fs.writeFile(logFileName, logStream);
    console.log(`\n📝 Console log saved to: ${logFileName}`);
  } catch (error) {
    console.error(`Failed to save log file: ${error.message}`);
  }
}

/**
 * Get comprehensive list of SPORTS apps from App Store
 * Combines multiple collections and search results - no filtering needed since SPORTS category is pre-filtered by Apple
 * @param {number} numApps - Total number of apps to retrieve per category
 * @returns {Promise<Array>} Promise that resolves to an array of app objects
 */
async function getSportsAndFitnessAppsAppStore(numApps = 1000) {
  try {
    let allApps = [];
    const targetCategories = [
      store.category.SPORTS,
      store.category.HEALTH_AND_FITNESS,
    ];

    // Countries to search - all available App Store markets
    const targetCountries = countries;

    logToFile(
      "🍎 Starting comprehensive App Store SPORTS & HEALTH_AND_FITNESS app collection..."
    );
    logToFile(
      `🌍 Searching across ${
        targetCountries.length
      } countries: ${targetCountries.join(", ").toUpperCase()}`
    );

    // Calculate time estimation
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

    const searchQueries = [
      // Traditional Sports
      "football",
      "soccer",
      "futbol",
      "american football",
      "flag football",
      "australian football",
      "gaelic football",
      "gridiron",
      "basketball",
      "3x3 basketball",
      "streetball",
      "baseball",
      "softball",
      "fastpitch",
      "tennis",
      "padel",
      "beach tennis",
      "paddle tennis",
      "golf",
      "disc golf",
      "mini golf",
      "putting",
      "golf swing",
      "running",
      "trail running",
      "jogging",
      "sprint",
      "ultra running",
      "cycling",
      "mountain biking",
      "road cycling",
      "gravel cycling",
      "cyclocross",
      "velodrome",
      "track cycling",
      "bmx",
      "scooter",
      "swimming",
      "open water swimming",
      "pool swimming",
      "swim workout",
      "volleyball",
      "beach volleyball",
      "indoor volleyball",
      "net sport",
      "hockey",
      "ice hockey",
      "field hockey",
      "street hockey",
      "ball hockey",
      "floorball",
      "rugby",
      "sevens rugby",
      "cricket",
      "test cricket",
      "T20",
      "ODI",
      "cricket live",
      "athletics",
      "track and field",
      "marathon",
      "triathlon",
      "ironman",
      "duathlon",
      "aquathlon",
      "badminton",
      "squash",
      "racquetball",
      "boxing",
      "muay thai",
      "savate",
      "martial arts",
      "kung fu",
      "capoeira",
      "wushu",
      "gymnastics",
      "trampoline",
      "skiing",
      "cross-country skiing",
      "snowboarding",
      "surfing",
      "bodyboarding",
      "wake surfing",
      "windsurfing",
      "kitesurfing",
      "skateboarding",
      "longboarding",
      "skateboard tricks",
      "climbing",
      "bouldering",
      "top rope",
      "lead climbing",
      "mountaineering",
      "hiking",
      "backpacking",
      "trekking",
      "fishing",
      "fly fishing",
      "ice fishing",
      "bass fishing",
      "hunting",
      "deer hunting",
      "duck hunting",
      "sailing",
      "rowing",
      "kayaking",
      "canoeing",
      "table tennis",
      "darts",
      "bowling",
      "ten-pin bowling",
      "nine-pin",
      "bowls",
      "archery",
      "kyudo",
      "motorsports",
      "auto racing",
      "motocross",
      "F1",
      "equestrian",
      "horse racing",
      "dressage",
      "show jumping",
      "eventing",
      "rodeo",
      "bandy",
      "shinty",
      "curling",
      "sledge hockey",
      "goalball",
      "bocce",
      "croquet",
      "petanque",
      "fencing",
      "sport shooting",
      "biathlon",
      "modern pentathlon",
      "decathlon",
      "water polo",
      "synchronized swimming",
      "diving",
      "water skiing",
      "wakeboarding",
      "ultimate frisbee",
      "futsal",
      "netball",
      "lacrosse",
      "handball",
      "figure skating",
      "speed skating",
      "bobsled",
      "luge",
      "skeleton",
      "parkour",
      "breakdancing",
      "cheerleading",
      "dance sport",
      "roller derby",
      "kabaddi",
      "sepak takraw",
      "hurling",
      "kho kho",
      "gilli danda",
      "footvolley",
      "jai alai",
      "bullfighting",
      "arnis",
      "sipa",
      "pesäpallo",
      "salibandy",

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
      "sambo",
      "krav maga",
      "bjj",
      "brazilian jiu-jitsu",

      // Sports Services & Management
      "sports news",
      "sports scores",
      "sports highlights",
      "sports live",
      "sports streaming",
      "manager",
      "fantasy sports",
      "sports betting",
      "sports odds",
      "sports coach",
      "sports training",
      "sports technique",
      "sports drills",
      "team management",
      "team roster",
      "match scheduler",
      "sports league",
      "sports tournament",
      "tournament manager",
      "league manager",
      "sports registration",
      "sports club",
      "sports academy",
      "fixtures",
      "sports tryouts",
      "sports recruiting",
      "sports analytics",
      "sports statistics",
      "sports metrics",
      "sports AI",
      "sports physio",
      "sports rehab",
      "sports injury",
      "sports medicine",
      "sports nutrition",
      "sports diet",
      "sports psychology",
      "sports tickets",
      "sports events",
      "sports events near me",
      "sports video analysis",
      "sports replay",
      "sports VR",
      "sports AR",
      "scoreboard",
      "stadium",
      "arena",
      "live match",
      "live sports",
      "race timing",
      "official results",

      // Equipment & Tracking
      "sports tracker",
      "sports GPS",
      "sports wearable",
      "sports watch",
      "sports timer",
      "sports sensor",
      "sports tech",
      "sports performance",
      "referee",
      "scorekeeper",
      "sports whistle",

      // Youth & Specialized
      "youth sports",
      "sports for kids",
      "sports camps",
      "paralympic sports",
      "adaptive sports",
      "veteran sports",

      // eSports & Virtual
      "esports",
      "esports team",
      "esports tournament",
      "esports news",
      "esports scores",
      "esports betting",
      "esports stream",

      // Health & Fitness - Workout Types
      "workout",
      "exercise",
      "gym",
      "fitness training",
      "strength training",
      "cardio workout",
      "hiit workout",
      "bodybuilding",
      "weightlifting",
      "functional training",
      "circuit training",
      "interval training",
      "tabata",
      "pilates",
      "yoga",
      "barre",
      "zumba",
      "bodyweight workout",
      "plyometrics",
      "functional fitness",
      "endurance training",
      "sports conditioning",

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
      "gps running",
      "vo2 max",
      "pace tracker",
      "distance tracker",

      // Specialized Fitness
      "muscle building",
      "fat loss",
      "athletic training",
      "flexibility",
      "mobility",
      "stretching",
      "rehabilitation",
      "physical therapy",
      "injury prevention",
      "foam rolling",
      "myofascial release",
      "sports massage",
      "post workout recovery",
      "active recovery",

      // Group Fitness
      "group fitness",
      "fitness class",
      "workout class",
      "boot camp",
      "spin class",
      "cycling class",
      "aerobics",
      "dance fitness",
      "les mills",
      "trx",
      "booty workout",
      "kickboxing workout",
      "martial arts fitness",

      // Motivational & Gamified
      "challenge tracker",
      "fitness challenge",
      "30 day workout",
      "step challenge",
      "leaderboard fitness",
    ];

    const totalCollectionCalls =
      targetCountries.length * targetCategories.length * collections.length; // countries × categories × collections
    const totalSearchCalls = targetCountries.length * searchQueries.length; // countries × search terms (shared across categories)
    const totalAPICalls = totalCollectionCalls + totalSearchCalls;
    const estimatedTimeSeconds = totalAPICalls * 3; // approximate 3 seconds per call
    const estimatedTimeMinutes = Math.round(estimatedTimeSeconds / 60);
    const estimatedTimeHours = Math.floor(estimatedTimeMinutes / 60);

    logToFile(`\n⏱️  TIME ESTIMATION:`);
    logToFile(
      `   📋 Collection calls: ${totalCollectionCalls} (${targetCountries.length} countries × ${targetCategories.length} categories × ${collections.length} collections)`
    );
    logToFile(
      `   🔍 Search calls: ${totalSearchCalls} (${targetCountries.length} countries × ${searchQueries.length} search terms)`
    );
    logToFile(`   🎯 Total API calls: ${totalAPICalls}`);
    logToFile(
      `   ⌛ Estimated time: ~ ${estimatedTimeHours} hours ${estimatedTimeMinutes} minutes (${estimatedTimeSeconds} seconds)`
    );
    logToFile(`   🚀 Starting collection process...\n`);

    // Process each country completely before moving to the next
    for (const country of targetCountries) {
      logToFile(`\n🌍 Processing country: ${country.toUpperCase()}`);

      for (const category of targetCategories) {
        const categoryName = Object.keys(store.category).find(
          (key) => store.category[key] === category
        );
        logToFile(
          `\n📱 Processing ${categoryName} category in ${country.toUpperCase()}...`
        );

        // Step 1: Get apps from multiple collections for this country
        for (const collection of collections) {
          try {
            const collectionName = Object.keys(store.collection).find(
              (key) => store.collection[key] === collection
            );
            logToFile(
              `  📋 Fetching from ${collectionName} in ${country.toUpperCase()}...`
            );

            const listApps = await store.list({
              category: category,
              collection: collection,
              num: 200, // Maximum per collection per country
              country: country,
            });

            // For SPORTS and HEALTH_AND_FITNESS categories, accept all apps (already categorized by Apple)
            const filteredApps = listApps;

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

            logToFile(
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

      // Step 2: Search with comprehensive terms for this country (applies to both SPORTS and HEALTH_AND_FITNESS)
      logToFile(
        `  🔍 Searching with comprehensive sports & fitness terms in ${country.toUpperCase()}...`
      );

      // Use the same search queries for both categories since we filter results afterward
      const searchQueries = [
        //Traditional Sports
        "football",
        "soccer",
        "futbol",
        "american football",
        "flag football",
        "australian football",
        "gaelic football",
        "basketball",
        "3x3 basketball",
        "streetball",
        "baseball",
        "softball",
        "fastpitch",
        "tennis",
        "padel",
        "beach tennis",
        "paddle tennis",
        "golf",
        "disc golf",
        "mini golf",
        "putting",
        "golf swing",
        "running",
        "trail running",
        "jogging",
        "sprint",
        "ultra running",
        "cycling",
        "mountain biking",
        "road cycling",
        "gravel cycling",
        "cyclocross",
        "swimming",
        "open water swimming",
        "pool swimming",
        "swim workout",
        "volleyball",
        "beach volleyball",
        "indoor volleyball",
        "hockey",
        "ice hockey",
        "field hockey",
        "street hockey",
        "ball hockey",
        "floorball",
        "rugby",
        "sevens rugby",
        "cricket",
        "test cricket",
        "T20",
        "ODI",
        "cricket live",
        "athletics",
        "track and field",
        "marathon",
        "triathlon",
        "ironman",
        "duathlon",
        "aquathlon",
        "badminton",
        "squash",
        "racquetball",
        "boxing",
        "muay thai",
        "savate",
        "martial arts",
        "kung fu",
        "capoeira",
        "wushu",
        "gymnastics",
        "trampoline",
        "skiing",
        "cross-country skiing",
        "snowboarding",
        "surfing",
        "bodyboarding",
        "wake surfing",
        "windsurfing",
        "kitesurfing",
        "skateboarding",
        "longboarding",
        "skateboard tricks",
        "climbing",
        "bouldering",
        "top rope",
        "lead climbing",
        "mountaineering",
        "hiking",
        "backpacking",
        "trekking",
        "fishing",
        "fly fishing",
        "ice fishing",
        "bass fishing",
        "hunting",
        "deer hunting",
        "duck hunting",
        "sailing",
        "rowing",
        "kayaking",
        "canoeing",
        "table tennis",
        "darts",
        "bowling",
        "ten-pin bowling",
        "nine-pin",
        "bowls",
        "archery",
        "kyudo",
        "motorsports",
        "auto racing",
        "motocross",
        "F1",
        "equestrian",
        "horse racing",
        "dressage",
        "show jumping",
        "eventing",
        "rodeo",

        // New Sports Additions
        "curling",
        "sledge hockey",
        "goalball",
        "bocce",
        "croquet",
        "petanque",
        "fencing",
        "sport shooting",
        "biathlon",
        "modern pentathlon",
        "decathlon",
        "water polo",
        "synchronized swimming",
        "diving",
        "water skiing",
        "wakeboarding",
        "ultimate frisbee",
        "futsal",
        "netball",
        "lacrosse",
        "handball",
        "figure skating",
        "speed skating",
        "bobsled",
        "luge",
        "skeleton",
        "powerlifting",
        "bodybuilding",
        "crossfit",
        "calisthenics",
        "parkour",
        "breakdancing",
        "cheerleading",
        "dance sport",
        "roller derby",
        "kabaddi",
        "sepak takraw",
        "hurling",
        "kho kho",
        "gilli danda",
        "footvolley",
        "jai alai",
        "bullfighting",
        "arnis",
        "sipa",

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
        "sambo",
        "krav maga",
        "bjj",
        "brazilian jiu-jitsu",

        // Sports Services & Management
        "sports news",
        "sports scores",
        "sports highlights",
        "sports live",
        "sports streaming",
        "fantasy sports",
        "sports betting",
        "sports odds",
        "sports coach",
        "sports training",
        "sports technique",
        "sports drills",
        "team management",
        "sports league",
        "sports tournament",
        "sports registration",
        "sports club",
        "sports academy",
        "sports tryouts",
        "sports recruiting",
        "sports analytics",
        "sports statistics",
        "sports metrics",
        "sports AI",
        "sports physio",
        "sports rehab",
        "sports injury",
        "sports medicine",
        "sports nutrition",
        "sports diet",
        "sports psychology",
        "sports tickets",
        "sports events",
        "sports events near me",
        "sports video analysis",
        "sports replay",
        "sports VR",
        "sports AR",

        // Equipment & Tracking
        "sports tracker",
        "sports GPS",
        "sports wearable",
        "sports watch",
        "sports timer",
        "sports sensor",
        "sports tech",
        "sports performance",
        "referee",
        "scorekeeper",
        "sports whistle",

        // Youth & Specialized
        "youth sports",
        "sports for kids",
        "sports camps",
        "paralympic sports",
        "adaptive sports",
        "veteran sports",

        // eSports & Virtual
        "esports",
        "esports team",
        "esports tournament",
        "esports news",
        "esports scores",
        "esports betting",
        "esports stream",

        // Health & Fitness - Workout Types
        "workout",
        "exercise",
        "gym",
        "fitness training",
        "strength training",
        "cardio workout",
        "hiit workout",
        "bodybuilding",
        "weightlifting",
        "functional training",
        "circuit training",
        "interval training",
        "tabata",
        "pilates",
        "yoga",
        "barre",
        "zumba",
        "bodyweight workout",
        "plyometrics",
        "functional fitness",
        "endurance training",
        "sports conditioning",

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
        "gps running",
        "vo2 max",
        "pace tracker",
        "distance tracker",

        // Specialized Fitness
        "muscle building",
        "fat loss",
        "athletic training",
        "flexibility",
        "mobility",
        "stretching",
        "rehabilitation",
        "physical therapy",
        "injury prevention",
        "foam rolling",
        "myofascial release",
        "sports massage",
        "post workout recovery",
        "active recovery",

        // Group Fitness
        "group fitness",
        "fitness class",
        "workout class",
        "boot camp",
        "spin class",
        "cycling class",
        "aerobics",
        "dance fitness",
        "les mills",
        "trx",
        "booty workout",
        "kickboxing workout",
        "martial arts fitness",

        // Motivational & Gamified
        "challenge tracker",
        "fitness challenge",
        "30 day workout",
        "step challenge",
        "leaderboard fitness",
      ];

      for (const query of searchQueries) {
        try {
          logToFile(`    Searching: "${query}" in ${country.toUpperCase()}`);
          const searchApps = await store.search({
            term: query,
            num: 500, // Maximum results per search
            country: country,
          });

          // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps
          const filteredSearchApps = searchApps.filter((app) => {
            // Check if app's genre/category matches SPORTS or HEALTH_AND_FITNESS
            const appGenre = app.genre || app.primaryGenre || "";
            const appGenreId = app.genreIds || [];

            // Check both genre name and ID
            // Apple's SPORTS category ID is typically 6004
            // Apple's HEALTH_AND_FITNESS category ID is typically 6013
            const isSportsGenre =
              appGenre.toLowerCase().includes("sports") ||
              appGenre.toLowerCase().includes("sport");
            const isHealthFitnessGenre =
              appGenre.toLowerCase().includes("health") ||
              appGenre.toLowerCase().includes("fitness") ||
              appGenre.toLowerCase().includes("medical");
            const isSportsId =
              appGenreId.includes(6004) || appGenreId.includes("6004");
            const isHealthFitnessId =
              appGenreId.includes(6013) || appGenreId.includes("6013");

            return (
              isSportsGenre ||
              isHealthFitnessGenre ||
              isSportsId ||
              isHealthFitnessId
            );
          });

          const filteredOutCount =
            searchApps.length - filteredSearchApps.length;
          if (filteredOutCount > 0) {
            logToFile(
              `      🔍 Filtered out ${filteredOutCount} non-sports/fitness apps from search results`
            );
          }

          let newSearchAppsCount = 0;
          filteredSearchApps.forEach((app) => {
            if (!allApps.find((existingApp) => existingApp.id === app.id)) {
              allApps.push({
                ...app,
                sourceMethod: "search",
                searchQuery: query,
                sourceCountry: country,
                targetCategory: "SPORTS_AND_FITNESS", // Generic label for search results
                actualGenre: app.genre || app.primaryGenre, // Track actual category
              });
              newSearchAppsCount++;
            }
          });

          if (newSearchAppsCount > 0) {
            logToFile(
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

    logToFile(
      `\n🎯 Total unique App Store sports & fitness apps collected: ${allApps.length}`
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
  logToFile("\n📊 APP STORE COLLECTION SUMMARY");
  logToFile("=".repeat(50));

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

  logToFile(`Total Apps: ${apps.length}`);

  logToFile("\nBy Category:");
  Object.entries(categoryCount).forEach(([cat, count]) => {
    logToFile(`  ${cat}: ${count} apps`);
  });

  logToFile("\nBy Source Method:");
  Object.entries(sourceMethodCount).forEach(([method, count]) => {
    logToFile(`  ${method}: ${count} apps`);
  });

  logToFile("\nBy Country (Top 10):");
  const topCountries = Object.entries(countryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 30);
  topCountries.forEach(([country, count]) => {
    logToFile(`  ${country.toUpperCase()}: ${count} apps`);
  });

  logToFile(`\nFree vs Paid:`);
  logToFile(`  Free: ${freeVsPaid.free} apps`);
  logToFile(`  Paid: ${freeVsPaid.paid} apps`);

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

  logToFile("\nTop 10 Developers:");
  topDevelopers.forEach(([dev, count], index) => {
    logToFile(`  ${index + 1}. ${dev}: ${count} apps`);
  });
}

/**
 * Export App Store apps data to JSON file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportAppStoreToJSON(
  apps,
  filename = `appstore_sports_fitness_apps_${new Date()
    .toISOString()
    .replace(/[:.]/g, "-")}.json`
) {
  try {
    const exportData = {
      platform: "Apple App Store",
      exportDate: new Date().toISOString(),
      totalApps: apps.length,
      searchScope: "Global - Multiple Countries",
      categoriesSearched: ["SPORTS", "HEALTH_AND_FITNESS"],
      countriesSearched: ["au", "ca", "gb", "nz", "us"],
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
    logToFile(`\n📁 App Store JSON data exported to ${filename}`);
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
  filename = `appstore_sports_fitness_apps_${new Date()
    .toISOString()
    .replace(/[:.]/g, "-")}.csv`
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
    logToFile(`📊 App Store CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export App Store CSV: ${error.message}`);
  }
}

// Main execution
async function main() {
  const startTime = Date.now();
  const startTimeFormatted = new Date().toISOString();

  logToFile(
    "🚀 Starting comprehensive App Store SPORTS & HEALTH_AND_FITNESS app mapping..."
  );
  logToFile(
    "🍎 Target: Apple App Store apps in SPORTS and HEALTH_AND_FITNESS categories"
  );
  logToFile(`⏰ Started at: ${startTimeFormatted}`);

  const apps = await getSportsAndFitnessAppsAppStore(50000); // Large limit for maximum coverage

  if (apps.length > 0) {
    printAppStoreSummary(apps);

    // Create timestamped filenames to ensure both files have the same timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const jsonFilename = `appstore_sports_fitness_apps_comprehensive_${timestamp}.json`;
    const csvFilename = `appstore_sports_fitness_apps_comprehensive_${timestamp}.csv`;

    // Export to both formats
    await exportAppStoreToJSON(apps, jsonFilename);
    await exportAppStoreToCSV(apps, csvFilename);

    logToFile(
      "\n✅ Comprehensive App Store sports & fitness app mapping completed!"
    );
    logToFile("📄 Files created:");
    logToFile(`  - ${jsonFilename} (for data analysis)`);
    logToFile(`  - ${csvFilename} (for Excel import)`);
    logToFile(
      `\n🍎 Summary: Collected ${apps.length} sports & fitness apps from Apple App Store`
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

    logToFile(`\n⏱️  ACTUAL TIME TAKEN:`);
    logToFile(`   🏁 Finished at: ${endTimeFormatted}`);
    logToFile(
      `   ⌛ Total duration: ${actualDurationHours}h ${remainingMinutes}m ${remainingSeconds}s (${actualDurationSeconds} seconds)`
    );
    logToFile(`   📊 Performance: ${actualDurationMs}ms total`);

    // Save the log file
    await saveLogFile();
  } else {
    logToFile(
      "❌ No apps were collected. Check your internet connection and try again."
    );
    // Save the log file even if no apps were collected
    await saveLogFile();
  }
}

main();
