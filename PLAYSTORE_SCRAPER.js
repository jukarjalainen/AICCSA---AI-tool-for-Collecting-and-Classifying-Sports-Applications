import gplay from "google-play-scraper";
import fs from "fs/promises";
import { searchQueriesEssential, TESTSearchQueries } from "./searchQueries_essential.js";
import { countriesEssential, TESTcountries } from "./countries_essential.js";
import { release } from "os";

/**
 * Scrapes the Google Play Store for app data based on search queries and countries.
 */

// Create a logging utility that writes to both console and file
let logStream = "";
let logFileName = null;
function logToFile(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}`;
  console.log(message); // Still show in console
  logStream += logMessage + "\n";
}
async function saveLogFile() {
  if (!logFileName) {
    logFileName = `playstore_scraper_log_${new Date()
      .toISOString()
      .replace(/[:.]/g, "-")}.txt`;
  }
  try {
    await fs.writeFile(logFileName, logStream);
    console.log(`\n📝 Console log saved to: ${logFileName}`);
  } catch (error) {
    console.error(`Failed to save log file: ${error.message}`);
  }
}

async function getGooglePlayApps() {
  try {
    let allApps = [];
    const targetCategories = ["SPORTS", "HEALTH_AND_FITNESS"];
    const targetCountries = TESTcountries;

    logToFile("🤖 Starting Google Play Store collection...");

    const collections = [
      gplay.collection.TOP_FREE,
      gplay.collection.TOP_PAID,
      gplay.collection.GROSSING,
    ];
    const totalCollectionCalls =
      targetCountries.length * targetCategories.length * collections.length;
    const totalSearchCalls = targetCountries.length * TESTSearchQueries.length;
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
              num: 250,
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
            await new Promise((resolve) => setTimeout(resolve, 800));
          } catch (error) {
            logToFile(
              `    ⚠️ Failed to fetch from ${collection}: ${error.message}`
            );
          }
        }
      }

      // Step 2: Search with comprehensive terms for this country
      logToFile(
        `  🔍 Searching with ${
          TESTSearchQueries.length
        } comprehensive terms in ${country.toUpperCase()}...`
      );

      for (const query of TESTSearchQueries) {
        try {
          logToFile(
            `PLAYSTORE    Searching: "${query}" in ${country.toUpperCase()}`
          );
          const searchApps = await gplay.search({
            term: query,
            num: 250,
            country: country,
            fullDetail: true, // Need full details for information
          });

          // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps
          const filteredSearchApps = searchApps.filter((app) => {
            const appGenre = app.genreId || "";

            // Only include apps that are explicitly in Sports or Health & Fitness categories
            const isSportsGenre =
              appGenre === "SPORTS" ||
              appGenre === "Sports" ||
              appGenre === "sports";

            const isHealthFitnessGenre =
              appGenre === "HEALTH_AND_FITNESS" ||
              appGenre === "health_and_fitness";

            return isSportsGenre || isHealthFitnessGenre;
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
                actualGenre: app.genreId,
              });
              newSearchAppsCount++;
            }
          });

          if (newSearchAppsCount > 0) {
            logToFile(
              `      ✅ Added ${newSearchAppsCount} new apps from "${query}" in ${country.toUpperCase()}`
            );
          }

          await new Promise((resolve) => setTimeout(resolve, 100));
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
 * Export apps data to JSON file with global metadata
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportToJSONGlobal(
  apps,
  filename = "playstore_sports_fitness_apps.json"
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
        developerID: app.developerID,
        category: app.genre,
        rating: app.score,
        scoreText: app.scoreText,
        release: app.released || null,
        installs: app.installs,
        ratings: app.ratings,
        reviews: app.reviews,
        priceText: app.priceText,
        free: app.free,
        price: app.price,
        url: app.url,
        summary: app.summary,
        sourceMethod: app.sourceMethod,
        sourceCollection: app.sourceCollection || null,
        sourceCountry: app.sourceCountry || null,
        searchQuery: app.searchQuery || null,
        targetCategory: app.targetCategory,
        categories: app.categories || null,
        contentRating: app.contentRating || null
      })),
    };

    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    console.log(`\n📁 Play store JSON data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export global JSON: ${error.message}`);
  }
}

/**
 * Export apps data to CSV file
 */
async function exportToCSV(
  apps,
  filename
) {
  try {
    const headers = [
      "Title",
      "App ID",
      "Developer",
      "Developer ID",
      "Category",
      "Rating",
      "Score Text",
      "Release Date",
      "Ratings",
      "Reviews",
      "Installs",
      "Price Text",
      "Free",
      "URL",
      "Summary",
      "Source Method",
      "Source Collection",
      "Source Country",
      "Search Query",
      "Target Category",
      "Categories",
      "Content Rating"
    ];
    const csvRows = [headers.join(",")];
    apps.forEach((app) => {
      const row = [
        `"${(app.title || "").replace(/"/g, '""')}"`,
        `"${app.appId || ""}"`,
        `"${(app.developer || "").replace(/"/g, '""')}"`,
        `"${app.developerID || ""}"`,
        `"${app.genreID || ""}"`,
        app.score || "",
        `"${app.scoreText || ""}"`,
        app.released || "",
        app.ratings || "",
        app.reviews || "",
        app.installs || "",
        `"${app.priceText || ""}"`,
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
    console.log(`📊 Play store CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export global CSV: ${error.message}`);
  }
}

/**
 * Print summary statistics of the collected apps
 */
function printSummary(apps) {
  console.log("\n📊 PLAY STORE SCRAPER SUMMARY");
  console.log("=".repeat(50));
  const platformCount = {};
  const categoryCount = {};
  const countryCount = {};
  let freeCount = 0;
  let paidCount = 0;
  apps.forEach((app) => {
    // Platform
    const platform = app.platform || "Unknown";
    platformCount[platform] = (platformCount[platform] || 0) + 1;
    // Category
    const category = app.targetCategory || app.genre || "Unknown";
    categoryCount[category] = (categoryCount[category] || 0) + 1;
    // Country
    const country = app.sourceCountry || "unknown";
    countryCount[country] = (countryCount[country] || 0) + 1;
    // Free/Paid
    if (app.free) freeCount++;
    else paidCount++;
  });
  console.log(`Total Apps: ${apps.length}`);
  console.log("\nPlatform Distribution:");
  Object.entries(platformCount).forEach(([platform, count]) => {
    console.log(`  ${platform}: ${count} apps`);
  });
  console.log("\nBy Category:");
  Object.entries(categoryCount).forEach(([cat, count]) => {
    console.log(`  ${cat}: ${count} apps`);
  });
  console.log("\nBy Country (Top 10):");
  const topCountries = Object.entries(countryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);
  topCountries.forEach(([country, count]) => {
    console.log(`  ${country.toUpperCase()}: ${count} apps`);
  });
  console.log(`\nFree: ${freeCount} apps`);
  console.log(`Paid: ${paidCount} apps`);
}

// Main execution function
async function exportToCSVGlobal(apps, filename = "playstore_sports_fitness_apps.csv") {
  try {
    const headers = [
      "Title",
      "App ID",
      "Developer",
      "Developer ID",
      "Category",
      "Rating",
      "Score Text",
      "Installs",
      "Price Text",
      "Free",
      "URL",
      "Summary",
      "Source Method",
      "Source Collection",
      "Source Country",
      "Search Query",
      "Target Category",
    ];
    const csvRows = [];
    csvRows.push(headers.join(","));
    for (const app of apps) {
      const row = [
        (app.title || "").replace(/"/g, '""'),
        app.appId || "",
        (app.developer || "").replace(/"/g, '""'),
        app.developerID || "",
        app.genre || app.category || "",
        app.score || "",
        app.scoreText || "",
        app.installs || "",
        app.priceText || "",
        app.free ? "TRUE" : "FALSE",
        app.url || "",
        (app.summary || "").replace(/"/g, '""').substring(0, 200),
        app.sourceMethod || "",
        app.sourceCollection || "",
        app.sourceCountry || "",
        app.searchQuery || "",
        app.targetCategory || "",
      ].map(field => `"${field}"`).join(",");
      csvRows.push(row);
    }
    await fs.writeFile(filename, csvRows.join("\n"));
    console.log(`📊 Play store CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export global CSV: ${error.message}`);
  }
}
// ...existing code...
