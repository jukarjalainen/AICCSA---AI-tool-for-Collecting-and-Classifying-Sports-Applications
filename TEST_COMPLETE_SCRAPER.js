// Play Store-specific JSON export with all available fields
async function exportPlayStoreToJSON(apps, filename) {
  try {
    const exportData = {
      exportInfo: {
        platform: "Google Play Store",
        exportDate: new Date().toISOString(),
        totalApps: apps.length,
      },
      apps: apps.map((app) => ({
        title: app.title,
        description: app.description,
        descriptionHTML: app.descriptionHTML,
        summary: app.summary,
        installs: app.installs,
        minInstalls: app.minInstalls,
        maxInstalls: app.maxInstalls,
        score: app.score,
        scoreText: app.scoreText,
        ratings: app.ratings,
        reviews: app.reviews,
        histogram: app.histogram,
        price: app.price,
        free: app.free,
        currency: app.currency,
        priceText: app.priceText,
        offersIAP: app.offersIAP,
        IAPRange: app.IAPRange,
        androidVersion: app.androidVersion,
        androidVersionText: app.androidVersionText,
        androidMaxVersion: app.androidMaxVersion,
        developer: app.developer,
        developerId: app.developerId,
        developerEmail: app.developerEmail,
        developerWebsite: app.developerWebsite,
        developerAddress: app.developerAddress,
        developerLegalName: app.developerLegalName,
        developerLegalEmail: app.developerLegalEmail,
        developerLegalAddress: app.developerLegalAddress,
        developerLegalPhoneNumber: app.developerLegalPhoneNumber,
        privacyPolicy: app.privacyPolicy,
        developerInternalID: app.developerInternalID,
        genre: app.genre,
        genreId: app.genreId,
        categories: app.categories,
        icon: app.icon,
        headerImage: app.headerImage,
        screenshots: app.screenshots,
        video: app.video,
        videoImage: app.videoImage,
        previewVideo: app.previewVideo,
        contentRating: app.contentRating,
        contentRatingDescription: app.contentRatingDescription,
        adSupported: app.adSupported,
        released: app.released,
        updated: app.updated,
        version: app.version,
        recentChanges: app.recentChanges,
        comments: app.comments,
        preregister: app.preregister,
        earlyAccessEnabled: app.earlyAccessEnabled,
        isAvailableInPlayPass: app.isAvailableInPlayPass,
        editorsChoice: app.editorsChoice,
        features: app.features,
        appId: app.appId,
        url: app.url,
        // Existing cross-platform and source fields
        platform: app.platform,
        platforms: app.platforms || [app.platform],
        availableOnBothPlatforms: app.availableOnBothPlatforms || false,
        crossPlatformMethod: app.crossPlatformMethod || null,
        crossPlatformAppIds: app.crossPlatformAppIds || null,
        sourceMethod: app.sourceMethod,
        sourceCollection: app.sourceCollection || null,
        sourceCountry: app.sourceCountry || null,
        searchQuery: app.searchQuery || null,
        subCategory: app.subCategory || app.searchQuery || null,
        targetCategory: app.targetCategory,
      })),
    };
    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    logToFile(`\n📁 Play Store JSON data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export Play Store JSON: ${error.message}`);
  }
}

// Play Store-specific CSV export with all available fields
async function exportPlayStoreToCSV(apps, filename) {
  try {
    const headers = [
      "title",
      "description",
      "descriptionHTML",
      "summary",
      "installs",
      "minInstalls",
      "maxInstalls",
      "score",
      "scoreText",
      "ratings",
      "reviews",
      "histogram_1",
      "histogram_2",
      "histogram_3",
      "histogram_4",
      "histogram_5",
      "price",
      "free",
      "currency",
      "priceText",
      "offersIAP",
      "IAPRange",
      "androidVersion",
      "androidVersionText",
      "androidMaxVersion",
      "developer",
      "developerId",
      "developerEmail",
      "developerWebsite",
      "developerAddress",
      "developerLegalName",
      "developerLegalEmail",
      "developerLegalAddress",
      "developerLegalPhoneNumber",
      "privacyPolicy",
      "developerInternalID",
      "genre",
      "genreId",
      "categories",
      "icon",
      "headerImage",
      "screenshots",
      "video",
      "videoImage",
      "previewVideo",
      "contentRating",
      "contentRatingDescription",
      "adSupported",
      "released",
      "updated",
      "version",
      "recentChanges",
      "comments",
      "preregister",
      "earlyAccessEnabled",
      "isAvailableInPlayPass",
      "editorsChoice",
      "features",
      "appId",
      "url",
      // Existing cross-platform and source fields
      "platform",
      "platforms",
      "availableOnBothPlatforms",
      "crossPlatformMethod",
      "crossPlatformAppIds",
      "sourceMethod",
      "sourceCollection",
      "sourceCountry",
      "searchQuery",
      "subCategory",
      "targetCategory",
    ];
    const csvRows = [headers.join(",")];
    apps.forEach((app) => {
      const row = [
        (app.title || "").replace(/"/g, '""'),
        (app.description || "").replace(/"/g, '""').substring(0, 200),
        (app.descriptionHTML || "").replace(/"/g, '""'),
        (app.summary || "").replace(/"/g, '""'),
        app.installs || "",
        app.minInstalls || "",
        app.maxInstalls || "",
        app.score || "",
        app.scoreText || "",
        app.ratings || "",
        app.reviews || "",
        app.histogram && app.histogram["1"] !== undefined
          ? app.histogram["1"]
          : "",
        app.histogram && app.histogram["2"] !== undefined
          ? app.histogram["2"]
          : "",
        app.histogram && app.histogram["3"] !== undefined
          ? app.histogram["3"]
          : "",
        app.histogram && app.histogram["4"] !== undefined
          ? app.histogram["4"]
          : "",
        app.histogram && app.histogram["5"] !== undefined
          ? app.histogram["5"]
          : "",
        app.price || "",
        app.free ? "TRUE" : "FALSE",
        app.currency || "",
        app.priceText || "",
        app.offersIAP ? "TRUE" : "FALSE",
        app.IAPRange || "",
        app.androidVersion || "",
        app.androidVersionText || "",
        app.androidMaxVersion || "",
        (app.developer || "").replace(/"/g, '""'),
        app.developerId || "",
        app.developerEmail || "",
        app.developerWebsite || "",
        app.developerAddress || "",
        app.developerLegalName || "",
        app.developerLegalEmail || "",
        app.developerLegalAddress || "",
        app.developerLegalPhoneNumber || "",
        app.privacyPolicy || "",
        app.developerInternalID || "",
        app.genre || "",
        app.genreId || "",
        Array.isArray(app.categories)
          ? app.categories.map((c) => `${c.name}:${c.id}`).join("; ")
          : app.categories || "",
        app.icon || "",
        app.headerImage || "",
        Array.isArray(app.screenshots)
          ? app.screenshots.join("; ")
          : app.screenshots || "",
        app.video || "",
        app.videoImage || "",
        app.previewVideo || "",
        app.contentRating || "",
        app.contentRatingDescription || "",
        app.adSupported ? "TRUE" : "FALSE",
        app.released || "",
        app.updated || "",
        app.version || "",
        app.recentChanges || "",
        Array.isArray(app.comments)
          ? app.comments.join("; ")
          : app.comments || "",
        app.preregister ? "TRUE" : "FALSE",
        app.earlyAccessEnabled ? "TRUE" : "FALSE",
        app.isAvailableInPlayPass ? "TRUE" : "FALSE",
        app.editorsChoice ? "TRUE" : "FALSE",
        Array.isArray(app.features)
          ? app.features.map((f) => `${f.title}:${f.description}`).join("; ")
          : app.features || "",
        app.appId || "",
        app.url || "",
        // Existing cross-platform and source fields
        app.platform || "",
        Array.isArray(app.platforms)
          ? app.platforms.join("; ")
          : app.platforms || "",
        app.availableOnBothPlatforms ? "TRUE" : "FALSE",
        app.crossPlatformMethod || "",
        Array.isArray(app.crossPlatformAppIds)
          ? app.crossPlatformAppIds.join("; ")
          : app.crossPlatformAppIds || "",
        app.sourceMethod || "",
        app.sourceCollection || "",
        app.sourceCountry || "",
        app.searchQuery || "",
        app.subCategory || app.searchQuery || "",
        app.targetCategory || "",
      ]
        .map((field) => `"${field}"`)
        .join(",");
      csvRows.push(row);
    });
    await fs.writeFile(filename, csvRows.join("\n"));
    logToFile(`📊 Play Store CSV data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export Play Store CSV: ${error.message}`);
  }
}
import store from "app-store-scraper";
import gplay from "google-play-scraper";
import fs from "fs/promises";
import { TESTcountries } from "./countries_essential.js";
import { TESTSearchQueries } from "./searchQueries_essential.js";

// Test configuration - minimal setup for quick testing
const testSearchQueries = TESTSearchQueries;
const testCountries = ["us"]; // Just US for testing

/**
 * TEST VERSION - Complete scraper that combines Apple App Store and Google Play Store
 * Uses minimal configuration for quick testing:
 * - 1 country (US)
 * - 5 search queries
 * - Reduced API limits
 * Expected runtime: 5-10 minutes
 */

// Create a logging utility that writes to both console and file
let logStream = "";
const logFileName = `test_scraper_log_${new Date()
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
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from Apple App Store
 */
async function getAppStoreApps() {
  try {
    let allApps = [];
    const targetCategories = [
      store.category.SPORTS,
      store.category.HEALTH_AND_FITNESS,
    ];
    const targetCountries = TESTcountries;

    logToFile("🍎 Starting Apple App Store collection (TEST MODE)...");

    // Calculate time estimation
    const collections = [
      store.collection.TOP_FREE_IOS,
      store.collection.TOP_GROSSING_IOS,
    ]; // Reduced to just 2 collections for testing

    const totalCollectionCalls =
      targetCountries.length * targetCategories.length * collections.length;
    const totalSearchCalls = targetCountries.length * testSearchQueries.length;
    const totalAPICalls = totalCollectionCalls + totalSearchCalls;

    logToFile(`   📋 Collection calls: ${totalCollectionCalls}`);
    logToFile(`   🔍 Search calls: ${totalSearchCalls}`);
    logToFile(`   🎯 Total Apple API calls: ${totalAPICalls}`);

    // Process each country
    for (const country of targetCountries) {
      logToFile(`\n🌍 Processing Apple App Store in: ${country.toUpperCase()}`);

      for (const category of targetCategories) {
        const categoryName = Object.keys(store.category).find(
          (key) => store.category[key] === category
        );
        logToFile(`\n📱 Processing ${categoryName} category...`);

        // Step 1: Get apps from collections
        for (const collection of collections) {
          try {
            const collectionName = Object.keys(store.collection).find(
              (key) => store.collection[key] === collection
            );
            logToFile(`  📋 Fetching from ${collectionName}...`);

            const listApps = await store.list({
              category: category,
              collection: collection,
              num: 50, // Reduced for testing
              country: country,
              fullDetail: true,
            });

            let newAppsCount = 0;
            listApps.forEach((app) => {
              if (
                !allApps.find((existingApp) => existingApp.appId === app.appId)
              ) {
                allApps.push({
                  ...app,
                  platform: "Apple App Store",
                  sourceMethod: "list",
                  sourceCollection: collectionName,
                  sourceCountry: country,
                  targetCategory: categoryName,
                  actualGenre: app.primaryGenre,
                });
                newAppsCount++;
              }
            });

            logToFile(
              `    ✅ Added ${newAppsCount} new apps from ${collectionName}`
            );
            await new Promise((resolve) => setTimeout(resolve, 500)); // Reduced from 1000ms
          } catch (error) {
            logToFile(
              `    ⚠️ Failed to fetch from ${collection}: ${error.message}`
            );
          }
        }
      }

      // Step 2: Search with test queries for this country
      logToFile(
        `  🔍 Searching with ${
          testSearchQueries.length
        } test terms in ${country.toUpperCase()}...`
      );

      for (const query of testSearchQueries) {
        try {
          logToFile(
            ` APPSTORE   Searching: "${query}" in ${country.toUpperCase()}`
          );
          const searchApps = await store.search({
            term: query,
            num: 50, // Reduced for testing
            country: country,
            fullDetail: true,
          });

          // Log total results found
          logToFile(
            `      📊 Found ${searchApps.length} total results for "${query}"`
          );

          // Log genre distribution for debugging
          const genreCount = {};
          searchApps.forEach((app) => {
            const genre = app.genre || app.primaryGenre || "Unknown";
            genreCount[genre] = (genreCount[genre] || 0) + 1;
          });
          logToFile(`      🏷️  Genres found: ${JSON.stringify(genreCount)}`);

          // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps
          const filteredSearchApps = searchApps.filter((app) => {
            const appGenreID = app.primaryGenreID || "";

            // Only include apps that are explicitly in Sports or Health & Fitness categories
            const isSportsGenre =
              appGenreID === 6004 || appGenreID === "SPORTS";
            const isHealthFitnessGenre =
              appGenreID === 6013 || appGenreID === "HEALTH_AND_FITNESS";

            const isValidCategory = isSportsGenre || isHealthFitnessGenre;

            // Log filtered apps for debugging
            if (!isValidCategory) {
              logToFile(
                `      🚫 Filtered out: "${app.title}" (Genre: ${
                  app.primaryGenre
                }, IDs: ${JSON.stringify(appGenreID)})`
              );
            }

            return isValidCategory;
          });

          const filteredOutCount =
            searchApps.length - filteredSearchApps.length;
          if (filteredOutCount > 0) {
            logToFile(
              `      🔍 Filtered out ${filteredOutCount} non-sports/fitness apps`
            );
          }

          let newSearchAppsCount = 0;
          filteredSearchApps.forEach((app) => {
            if (
              !allApps.find((existingApp) => existingApp.appId === app.appId)
            ) {
              allApps.push({
                ...app,
                platform: "Apple App Store",
                sourceMethod: "search",
                searchQuery: query,
                sourceCountry: country,
                targetCategory: "sports & fitness apps",
                actualGenre: app.primaryGenre,
              });
              newSearchAppsCount++;
            }
          });

          if (newSearchAppsCount > 0) {
            logToFile(
              `      ✅ Added ${newSearchAppsCount} new apps from "${query}" in ${country.toUpperCase()}`
            );
          }

          await new Promise((resolve) => setTimeout(resolve, 200)); // Faster for testing
        } catch (searchError) {
          logToFile(
            `      ⚠️ Search failed for "${query}" in ${country.toUpperCase()}: ${
              searchError.message
            }`
          );
        }
      }

      logToFile(
        `🏁 Completed ${country.toUpperCase()}: Total apps collected so far: ${
          allApps.length
        }`
      );
    }

    logToFile(
      `\n🎯 Apple App Store collection completed: ${allApps.length} apps`
    );
    return allApps;
  } catch (error) {
    logToFile(`Error in Apple App Store collection: ${error.message}`);
    return [];
  }
}

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from Google Play Store
 */
async function getGooglePlayApps() {
  try {
    let allApps = [];
    const targetCategories = ["SPORTS", "HEALTH_AND_FITNESS"];
    const targetCountries = testCountries;

    logToFile("🤖 Starting Google Play Store collection (TEST MODE)...");

    const collections = [gplay.collection.TOP_FREE, gplay.collection.GROSSING]; // Reduced to just 2 collections for testing
    const totalCollectionCalls =
      targetCountries.length * targetCategories.length * collections.length;
    const totalSearchCalls = targetCountries.length * testSearchQueries.length;
    const totalAPICalls = totalCollectionCalls + totalSearchCalls;

    logToFile(`   📋 Collection calls: ${totalCollectionCalls}`);
    logToFile(`   🔍 Search calls: ${totalSearchCalls}`);
    logToFile(`   🎯 Total Google Play API calls: ${totalAPICalls}`);

    // Process each country
    for (const country of targetCountries) {
      logToFile(
        `\n🌍 Processing Google Play Store in: ${country.toUpperCase()}`
      );

      for (const category of targetCategories) {
        logToFile(`\n📱 Processing ${category} category...`);

        // Step 1: Get apps from collections
        for (const collection of collections) {
          try {
            logToFile(`  📋 Fetching from ${collection}...`);

            const listApps = await gplay.list({
              category: category,
              collection: collection,
              num: 50, // Reduced for testing
              country: country,
              fullDetail: true, // Need full details for genre information
            });

            let newAppsCount = 0;
            listApps.forEach((app) => {
              if (
                !allApps.find((existingApp) => existingApp.appId === app.appId)
              ) {
                allApps.push({
                  ...app,
                  platform: "Google Play Store",
                  sourceMethod: "list",
                  sourceCollection: collection,
                  sourceCountry: country,
                  targetCategory: category,
                  actualGenre: app.genre || app.genreId || app.category,
                });
                newAppsCount++;
              }
            });

            logToFile(
              `    ✅ Added ${newAppsCount} new apps from ${collection}`
            );
            await new Promise((resolve) => setTimeout(resolve, 500)); // Reduced from 1000ms
          } catch (error) {
            logToFile(
              `    ⚠️ Failed to fetch from ${collection}: ${error.message}`
            );
          }
        }
      }

      // Step 2: Search with test queries for this country
      logToFile(
        `  🔍 Searching with ${
          testSearchQueries.length
        } test terms in ${country.toUpperCase()}...`
      );

      for (const query of testSearchQueries) {
        try {
          logToFile(
            `PLAYSTORE    Searching: "${query}" in ${country.toUpperCase()}`
          );
          const searchApps = await gplay.search({
            term: query,
            num: 50, // Reduced for testing
            country: country,
            fullDetail: true, // Need full details for genre information
          });

          // Log total results found
          logToFile(
            `      📊 Found ${searchApps.length} total results for "${query}"`
          );

          // Log genre distribution for debugging
          const genreCount = {};
          searchApps.forEach((app) => {
            const genre = app.genre || app.genreId || app.category || "Unknown";
            genreCount[genre] = (genreCount[genre] || 0) + 1;
          });
          logToFile(`      🏷️  Genres found: ${JSON.stringify(genreCount)}`);

          // Debug: log a few sample apps with all their properties
          if (searchApps.length > 0) {
            const sampleApp = searchApps[0];
            logToFile(
              `      🔍 Sample app properties: ${JSON.stringify(
                {
                  title: sampleApp.title,
                  genre: sampleApp.genre,
                  genreId: sampleApp.genreId,
                  category: sampleApp.category,
                  categories: sampleApp.categories,
                },
                null,
                2
              )}`
            );
          }

          // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps
          const filteredSearchApps = searchApps.filter((app) => {
            const appGenre = app.genre || app.genreId || app.category || "";
            const appFamilyGenre = app.familyGenre || "";

            // Only include apps that are explicitly in Sports or Health & Fitness categories
            const isSportsGenre =
              appGenre === "SPORTS" ||
              appGenre === "Sports" ||
              appGenre === "sports" ||
              appFamilyGenre === "SPORTS" ||
              appFamilyGenre === "Sports";

            const isHealthFitnessGenre =
              appGenre === "HEALTH_AND_FITNESS" ||
              appGenre === "Health & Fitness" ||
              appGenre === "Health and Fitness" ||
              appGenre === "Medical" ||
              appGenre === "health_and_fitness" ||
              appFamilyGenre === "HEALTH_AND_FITNESS" ||
              appFamilyGenre === "Health & Fitness";

            const isValidCategory = isSportsGenre || isHealthFitnessGenre;

            // Log filtered apps for debugging
            if (!isValidCategory) {
              logToFile(
                `      🚫 Filtered out: "${app.title}" (Genre: ${appGenre}, FamilyGenre: ${appFamilyGenre})`
              );
            } else {
              logToFile(
                `      ✅ Keeping: "${app.title}" (Genre: ${appGenre}, FamilyGenre: ${appFamilyGenre})`
              );
            }

            return isValidCategory;
          });

          const filteredOutCount =
            searchApps.length - filteredSearchApps.length;
          if (filteredOutCount > 0) {
            logToFile(
              `      🔍 Filtered out ${filteredOutCount} non-sports/fitness apps`
            );
          }

          let newSearchAppsCount = 0;
          filteredSearchApps.forEach((app) => {
            if (
              !allApps.find((existingApp) => existingApp.appId === app.appId)
            ) {
              allApps.push({
                ...app,
                platform: "Google Play Store",
                sourceMethod: "search",
                searchQuery: query,
                sourceCountry: country,
                targetCategory: "SPORTS_AND_HEALTH_AND_FITNESS",
                actualGenre: app.genre || app.genreId || app.category,
              });
              newSearchAppsCount++;
            }
          });

          if (newSearchAppsCount > 0) {
            logToFile(
              `      ✅ Added ${newSearchAppsCount} new apps from "${query}" in ${country.toUpperCase()}`
            );
          }

          await new Promise((resolve) => setTimeout(resolve, 300)); // Faster for testing
        } catch (searchError) {
          logToFile(
            `      ⚠️ Search failed for "${query}" in ${country.toUpperCase()}: ${
              searchError.message
            }`
          );
        }
      }

      logToFile(
        `🏁 Completed ${country.toUpperCase()}: Total apps collected so far: ${
          allApps.length
        }`
      );
    }

    logToFile(
      `\n🎯 Google Play Store collection completed: ${allApps.length} apps`
    );
    return allApps;
  } catch (error) {
    logToFile(`Error in Google Play Store collection: ${error.message}`);
    return [];
  }
}

/**
 * Combine and deduplicate apps from both platforms with improved cross-platform tracking
 * Uses both appId matching and title similarity for better cross-platform detection
 */
function combineAndDeduplicateApps(appStoreApps, googlePlayApps) {
  logToFile("\n🔄 Combining and deduplicating apps from both platforms...");

  const allApps = [...appStoreApps];
  let duplicatesFoundByAppId = 0;
  let duplicatesFoundByTitle = 0;
  let newAppsAdded = 0;

  // Add Google Play apps, checking for duplicates by appId first, then by title
  googlePlayApps.forEach((playApp) => {
    // First, check for exact appId match
    let existingApp = allApps.find((app) => app.appId === playApp.appId);

    if (existingApp) {
      duplicatesFoundByAppId++;
      // If duplicate found by appId, merge platform information
      if (!existingApp.platforms) {
        existingApp.platforms = [existingApp.platform];
      }
      if (!existingApp.platforms.includes(playApp.platform)) {
        existingApp.platforms.push(playApp.platform);
      }
      existingApp.availableOnBothPlatforms = true;
      existingApp.platform = "Both Platforms";
      existingApp.crossPlatformMethod = "appId";

      logToFile(
        `   🔄 Cross-platform app found (appId): "${existingApp.title}" (${existingApp.appId})`
      );
    } else {
      // Check for title similarity (exact match for now, could be enhanced with fuzzy matching)
      existingApp = allApps.find(
        (app) =>
          app.title &&
          playApp.title &&
          app.title.trim().toLowerCase() === playApp.title.trim().toLowerCase()
      );

      if (existingApp) {
        duplicatesFoundByTitle++;
        // If duplicate found by title, merge platform information
        if (!existingApp.platforms) {
          existingApp.platforms = [existingApp.platform];
        }
        if (!existingApp.platforms.includes(playApp.platform)) {
          existingApp.platforms.push(playApp.platform);
        }
        existingApp.availableOnBothPlatforms = true;
        existingApp.platform = "Both Platforms";
        existingApp.crossPlatformMethod = "title";

        // Store both appIds for reference
        if (!existingApp.crossPlatformAppIds) {
          existingApp.crossPlatformAppIds = [existingApp.appId];
        }
        existingApp.crossPlatformAppIds.push(playApp.appId);

        logToFile(
          `   🔄 Cross-platform app found (title): "${existingApp.title}"`
        );
        logToFile(
          `     📱 Apple: ${existingApp.appId} | 🤖 Google: ${playApp.appId}`
        );
      } else {
        // New app from Google Play
        playApp.platforms = [playApp.platform];
        playApp.availableOnBothPlatforms = false;
        allApps.push(playApp);
        newAppsAdded++;
      }
    }
  });

  // Ensure all Apple-only apps have proper platform information
  allApps.forEach((app) => {
    if (app.platform === "Apple App Store" && !app.platforms) {
      app.platforms = [app.platform];
      app.availableOnBothPlatforms = false;
    }
  });

  logToFile(`   📊 Enhanced deduplication summary:`);
  logToFile(`   📱 Apple App Store apps: ${appStoreApps.length}`);
  logToFile(`   🤖 Google Play Store apps: ${googlePlayApps.length}`);
  logToFile(`   🔄 Cross-platform matches by appId: ${duplicatesFoundByAppId}`);
  logToFile(`   🔄 Cross-platform matches by title: ${duplicatesFoundByTitle}`);
  logToFile(
    `   🔄 Total cross-platform apps: ${
      duplicatesFoundByAppId + duplicatesFoundByTitle
    }`
  );
  logToFile(`   ➕ New apps added from Google Play: ${newAppsAdded}`);
  logToFile(`   🎯 Total unique apps: ${allApps.length}`);

  return allApps;
}

/**
 * Print summary statistics of the collected apps
 */
function printCombinedSummary(apps) {
  logToFile("\n📊 COMBINED COLLECTION SUMMARY");
  logToFile("=".repeat(50));

  // Platform breakdown with detailed cross-platform analysis
  const platformCount = {};
  const categoryCount = {};
  const sourceMethodCount = {};
  const countryCount = {};
  const freeVsPaid = { free: 0, paid: 0 };
  const crossPlatformMethods = { appId: 0, title: 0 };
  let crossPlatformApps = 0;
  let appleOnlyApps = 0;
  let googleOnlyApps = 0;

  apps.forEach((app) => {
    // Count by platform (now shows "Both Platforms" for cross-platform apps)
    const platform = app.platform || "Unknown";
    platformCount[platform] = (platformCount[platform] || 0) + 1;

    // Count cross-platform apps and platform-specific apps
    if (app.availableOnBothPlatforms) {
      crossPlatformApps++;
      // Count by detection method
      if (app.crossPlatformMethod === "appId") {
        crossPlatformMethods.appId++;
      } else if (app.crossPlatformMethod === "title") {
        crossPlatformMethods.title++;
      }
    } else if (app.platform === "Apple App Store") {
      appleOnlyApps++;
    } else if (app.platform === "Google Play Store") {
      googleOnlyApps++;
    }

    // Count by category
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

  logToFile("\nPlatform Distribution:");
  Object.entries(platformCount).forEach(([platform, count]) => {
    logToFile(`  ${platform}: ${count} apps`);
  });

  logToFile("\nDetailed Platform Analysis:");
  logToFile(`  📱 Apple App Store only: ${appleOnlyApps} apps`);
  logToFile(`  🤖 Google Play Store only: ${googleOnlyApps} apps`);
  logToFile(`  🔄 Available on both platforms: ${crossPlatformApps} apps`);

  // Calculate cross-platform percentage
  const crossPlatformPercentage = (
    (crossPlatformApps / apps.length) *
    100
  ).toFixed(1);
  logToFile(
    `  📊 Cross-platform coverage: ${crossPlatformPercentage}% of apps`
  );

  logToFile("\nCross-Platform Detection Methods:");
  logToFile(`  🆔 Matched by AppId: ${crossPlatformMethods.appId} apps`);
  logToFile(`  📝 Matched by Title: ${crossPlatformMethods.title} apps`);
  logToFile(
    `  🎯 Total detected: ${
      crossPlatformMethods.appId + crossPlatformMethods.title
    } apps`
  );

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
    .slice(0, 10);
  topCountries.forEach(([country, count]) => {
    logToFile(`  ${country.toUpperCase()}: ${count} apps`);
  });

  logToFile(`\nFree vs Paid:`);
  logToFile(`  Free: ${freeVsPaid.free} apps`);
  logToFile(`  Paid: ${freeVsPaid.paid} apps`);
}

/**
 * Export combined apps data to JSON file
 */
async function exportCombinedToJSON(apps, filename) {
  try {
    // Superset schema: all App Store and Play Store fields
    const exportData = {
      exportInfo: {
        platforms: ["Apple App Store", "Google Play Store"],
        exportDate: new Date().toISOString(),
        totalApps: apps.length,
        searchScope: "Global - Multiple Countries and Platforms",
        categoriesSearched: ["SPORTS", "HEALTH_AND_FITNESS"],
        deduplicationMethod: "appId and title matching across platforms",
      },
      apps: apps.map((app) => ({
        // App Store fields
        id: app.id || "",
        appId: app.appId || "",
        title: app.title || "",
        url: app.url || "",
        description: app.description || "",
        icon: app.icon || "",
        genres: app.genres || "",
        genreIds: app.genreIds || "",
        primaryGenre: app.primaryGenre || "",
        primaryGenreId: app.primaryGenreId || "",
        contentRating: app.contentRating || "",
        languages: app.languages || "",
        size: app.size || "",
        requiredOsVersion: app.requiredOsVersion || "",
        released: app.released || "",
        updated: app.updated || "",
        releaseNotes: app.releaseNotes || "",
        version: app.version || "",
        price: app.price || "",
        currency: app.currency || "",
        free: app.free != null ? app.free : "",
        developerId: app.developerId || "",
        developer: app.developer || "",
        developerUrl: app.developerUrl || "",
        developerWebsite: app.developerWebsite || "",
        score: app.score || "",
        reviews: app.reviews || "",
        currentVersionScore: app.currentVersionScore || "",
        currentVersionReviews: app.currentVersionReviews || "",
        screenshots: app.screenshots || "",
        ipadScreenshots: app.ipadScreenshots || "",
        appletvScreenshots: app.appletvScreenshots || "",
        supportedDevices: app.supportedDevices || "",
        // Play Store fields
        descriptionHTML: app.descriptionHTML || "",
        summary: app.summary || "",
        installs: app.installs || "",
        minInstalls: app.minInstalls || "",
        maxInstalls: app.maxInstalls || "",
        ratings: app.ratings || "",
        histogram: app.histogram || "",
        priceText: app.priceText || "",
        offersIAP: app.offersIAP != null ? app.offersIAP : "",
        IAPRange: app.IAPRange || "",
        androidVersion: app.androidVersion || "",
        androidVersionText: app.androidVersionText || "",
        androidMaxVersion: app.androidMaxVersion || "",
        developerEmail: app.developerEmail || "",
        developerAddress: app.developerAddress || "",
        developerLegalName: app.developerLegalName || "",
        developerLegalEmail: app.developerLegalEmail || "",
        developerLegalAddress: app.developerLegalAddress || "",
        developerLegalPhoneNumber: app.developerLegalPhoneNumber || "",
        privacyPolicy: app.privacyPolicy || "",
        developerInternalID: app.developerInternalID || "",
        genre: app.genre || "",
        genreId: app.genreId || "",
        categories: app.categories || "",
        headerImage: app.headerImage || "",
        video: app.video || "",
        videoImage: app.videoImage || "",
        previewVideo: app.previewVideo || "",
        contentRatingDescription: app.contentRatingDescription || "",
        adSupported: app.adSupported != null ? app.adSupported : "",
        recentChanges: app.recentChanges || "",
        comments: app.comments || "",
        preregister: app.preregister != null ? app.preregister : "",
        earlyAccessEnabled: app.earlyAccessEnabled != null ? app.earlyAccessEnabled : "",
        isAvailableInPlayPass: app.isAvailableInPlayPass != null ? app.isAvailableInPlayPass : "",
        editorsChoice: app.editorsChoice != null ? app.editorsChoice : "",
        features: app.features || "",
        // Existing cross-platform and source fields
        platform: app.platform || "",
        platforms: app.platforms || [app.platform],
        availableOnBothPlatforms: app.availableOnBothPlatforms || false,
        crossPlatformMethod: app.crossPlatformMethod || null,
        crossPlatformAppIds: app.crossPlatformAppIds || null,
        sourceMethod: app.sourceMethod || "",
        sourceCollection: app.sourceCollection || "",
        sourceCountry: app.sourceCountry || "",
        searchQuery: app.searchQuery || "",
        subCategory: app.subCategory || app.searchQuery || "",
        targetCategory: app.targetCategory || "",
      })),
    };
    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    logToFile(`\n📁 Combined JSON data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export combined JSON: ${error.message}`);
  }
}

/**
 * Export combined apps data to CSV file
 */
async function exportCombinedToCSV(apps, filename) {
  try {
    // Superset schema: all App Store and Play Store fields
    const headers = [
      // App Store fields
      "id","appId","title","url","description","icon","genres","genreIds","primaryGenre","primaryGenreId","contentRating","languages","size","requiredOsVersion","released","updated","releaseNotes","version","price","currency","free","developerId","developer","developerUrl","developerWebsite","score","reviews","currentVersionScore","currentVersionReviews","screenshots","ipadScreenshots","appletvScreenshots","supportedDevices",
      // Play Store fields
      "descriptionHTML","summary","installs","minInstalls","maxInstalls","ratings","histogram_1","histogram_2","histogram_3","histogram_4","histogram_5","priceText","offersIAP","IAPRange","androidVersion","androidVersionText","androidMaxVersion","developerEmail","developerAddress","developerLegalName","developerLegalEmail","developerLegalAddress","developerLegalPhoneNumber","privacyPolicy","developerInternalID","genre","genreId","categories","headerImage","video","videoImage","previewVideo","contentRatingDescription","adSupported","recentChanges","comments","preregister","earlyAccessEnabled","isAvailableInPlayPass","editorsChoice","features",
      // Existing cross-platform and source fields
      "platform","platforms","availableOnBothPlatforms","crossPlatformMethod","crossPlatformAppIds","sourceMethod","sourceCollection","sourceCountry","searchQuery","subCategory","targetCategory"
    ];
    const csvRows = [headers.join(",")];
    apps.forEach((app) => {
      const row = [
        // App Store fields
        app.id || "",
        app.appId || "",
        (app.title || "").replace(/"/g, '""'),
        app.url || "",
        (app.description || "").replace(/"/g, '""').substring(0, 200),
        app.icon || "",
        Array.isArray(app.genres) ? app.genres.join("; ") : (app.genres || ""),
        Array.isArray(app.genreIds) ? app.genreIds.join("; ") : (app.genreIds || ""),
        app.primaryGenre || "",
        app.primaryGenreId || "",
        app.contentRating || "",
        Array.isArray(app.languages) ? app.languages.join("; ") : (app.languages || ""),
        app.size || "",
        app.requiredOsVersion || "",
        app.released || "",
        app.updated || "",
        app.releaseNotes || "",
        app.version || "",
        app.price || "",
        app.currency || "",
        app.free ? "TRUE" : "FALSE",
        app.developerId || "",
        (app.developer || "").replace(/"/g, '""'),
        app.developerUrl || "",
        app.developerWebsite || "",
        app.score || "",
        app.reviews || "",
        app.currentVersionScore || "",
        app.currentVersionReviews || "",
        Array.isArray(app.screenshots) ? app.screenshots.join("; ") : (app.screenshots || ""),
        Array.isArray(app.ipadScreenshots) ? app.ipadScreenshots.join("; ") : (app.ipadScreenshots || ""),
        Array.isArray(app.appletvScreenshots) ? app.appletvScreenshots.join("; ") : (app.appletvScreenshots || ""),
        Array.isArray(app.supportedDevices) ? app.supportedDevices.join("; ") : (app.supportedDevices || ""),
        // Play Store fields
        (app.descriptionHTML || "").replace(/"/g, '""'),
        (app.summary || "").replace(/"/g, '""'),
        app.installs || "",
        app.minInstalls || "",
        app.maxInstalls || "",
        app.ratings || "",
        app.histogram && app.histogram["1"] !== undefined ? app.histogram["1"] : "",
        app.histogram && app.histogram["2"] !== undefined ? app.histogram["2"] : "",
        app.histogram && app.histogram["3"] !== undefined ? app.histogram["3"] : "",
        app.histogram && app.histogram["4"] !== undefined ? app.histogram["4"] : "",
        app.histogram && app.histogram["5"] !== undefined ? app.histogram["5"] : "",
        app.priceText || "",
        app.offersIAP ? "TRUE" : "FALSE",
        app.IAPRange || "",
        app.androidVersion || "",
        app.androidVersionText || "",
        app.androidMaxVersion || "",
        app.developerEmail || "",
        app.developerAddress || "",
        app.developerLegalName || "",
        app.developerLegalEmail || "",
        app.developerLegalAddress || "",
        app.developerLegalPhoneNumber || "",
        app.privacyPolicy || "",
        app.developerInternalID || "",
        app.genre || "",
        app.genreId || "",
        Array.isArray(app.categories) ? app.categories.map(c => `${c.name}:${c.id}`).join("; ") : (app.categories || ""),
        app.headerImage || "",
        app.video || "",
        app.videoImage || "",
        app.previewVideo || "",
        app.contentRatingDescription || "",
        app.adSupported ? "TRUE" : "FALSE",
        app.recentChanges || "",
        Array.isArray(app.comments) ? app.comments.join("; ") : (app.comments || ""),
        app.preregister ? "TRUE" : "FALSE",
        app.earlyAccessEnabled ? "TRUE" : "FALSE",
        app.isAvailableInPlayPass ? "TRUE" : "FALSE",
        app.editorsChoice ? "TRUE" : "FALSE",
        Array.isArray(app.features) ? app.features.map(f => `${f.title}:${f.description}`).join("; ") : (app.features || ""),
        // Existing cross-platform and source fields
        app.platform || "",
        Array.isArray(app.platforms) ? app.platforms.join("; ") : (app.platforms || ""),
        app.availableOnBothPlatforms ? "TRUE" : "FALSE",
        app.crossPlatformMethod || "",
        Array.isArray(app.crossPlatformAppIds) ? app.crossPlatformAppIds.join("; ") : (app.crossPlatformAppIds || ""),
        app.sourceMethod || "",
        app.sourceCollection || "",
        app.sourceCountry || "",
        app.searchQuery || "",
        app.subCategory || app.searchQuery || "",
        app.targetCategory || "",
      ].map(field => `"${field}"`).join(",");
      csvRows.push(row);
    });

    await fs.writeFile(filename, csvRows.join("\n"));
    logToFile(`📊 Enhanced CSV data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export combined CSV: ${error.message}`);
  }
}

/**
 * Main execution function
 */
async function main() {
  const startTime = Date.now();
  const startTimeFormatted = new Date().toISOString();

  logToFile(
    "🚀 Starting TEST scraper for Apple App Store & Google Play Store..."
  );
  logToFile("🎯 TEST MODE: 1 country (US), 5 search terms, reduced limits");
  logToFile(`⏰ Started at: ${startTimeFormatted}`);

  try {
    // Scrape both platforms in parallel for better performance
    logToFile("\n📱 Starting parallel scraping of both platforms...");

    const [appStoreApps, googlePlayApps] = await Promise.all([
      getAppStoreApps(),
      getGooglePlayApps(),
    ]);

    if (appStoreApps.length === 0 && googlePlayApps.length === 0) {
      logToFile(
        "❌ No apps were collected from either platform. Check your internet connection and try again."
      );
      await saveLogFile();
      return;
    }

    // Combine and deduplicate
    const combinedApps = combineAndDeduplicateApps(
      appStoreApps,
      googlePlayApps
    );

    if (combinedApps.length > 0) {
      printCombinedSummary(combinedApps);

      // Create timestamped filenames
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const jsonFilename = `test_sports_fitness_apps_${timestamp}.json`;
      const csvFilename = `test_sports_fitness_apps_${timestamp}.csv`;
      // Apple only
      const appleJsonFilename = `test_appstore_sports_fitness_apps_${timestamp}.json`;
      const appleCsvFilename = `test_appstore_sports_fitness_apps_${timestamp}.csv`;
      // Google Play only
      const playJsonFilename = `test_playstore_sports_fitness_apps_${timestamp}.json`;
      const playCsvFilename = `test_playstore_sports_fitness_apps_${timestamp}.csv`;

      // Export Apple App Store results
      if (appStoreApps.length > 0) {
        await exportCombinedToJSON(appStoreApps, appleJsonFilename);
        await exportCombinedToCSV(appStoreApps, appleCsvFilename);
        logToFile(`  - ${appleJsonFilename} (Apple App Store JSON)`);
        logToFile(`  - ${appleCsvFilename} (Apple App Store CSV)`);
      }
      // Export Google Play Store results (all fields)
      if (googlePlayApps.length > 0) {
        await exportPlayStoreToJSON(googlePlayApps, playJsonFilename);
        await exportPlayStoreToCSV(googlePlayApps, playCsvFilename);
        logToFile(`  - ${playJsonFilename} (Google Play Store JSON)`);
        logToFile(`  - ${playCsvFilename} (Google Play Store CSV)`);
      }

      // Export combined files
      await exportCombinedToJSON(combinedApps, jsonFilename);
      await exportCombinedToCSV(combinedApps, csvFilename);

      logToFile("\n✅ TEST scraping completed successfully!");
      logToFile("📄 Files created:");
      logToFile(`  - ${jsonFilename} (Combined JSON)`);
      logToFile(`  - ${csvFilename} (Combined CSV)`);
      logToFile(
        `\n🎯 TEST Summary: Collected ${combinedApps.length} unique sports & fitness apps from both platforms`
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
        `   ⌛ Total duration: ${actualDurationHours}h ${remainingMinutes}m ${remainingSeconds}s`
      );
      logToFile(`   📊 Performance: ${actualDurationMs}ms total`);

      // Save the log file
      await saveLogFile();
    }
  } catch (error) {
    logToFile(`❌ Fatal error in main execution: ${error.message}`);
    await saveLogFile();
  }
}

// Execute the main function
main().catch((error) => {
  console.error("Unhandled error:", error);
});
