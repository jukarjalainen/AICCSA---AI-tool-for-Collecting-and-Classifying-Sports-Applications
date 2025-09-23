import fs from "fs/promises";
import path from "path";

/**
 * Combine Google Play Store and Apple App Store sports/fitness apps data
 * Removes duplications based on appId and creates unified JSON and CSV files
 */
async function combineAppStoreData() {
  try {
    console.log(
      "🔄 Starting to combine Google Play Store and Apple App Store data..."
    );

    // File paths
    const googlePlayFile = path.join(
      process.cwd(),
      "google-play-scraper",
      "global_sports_fitness_apps_comprehensive.json"
    );
    const appleStoreFile = path.join(
      process.cwd(),
      "app-store-scraper",
      "appstore_sports_fitness_apps_comprehensive.json"
    );

    console.log("📂 Reading Google Play Store data...");
    let googlePlayData;
    try {
      const googlePlayContent = await fs.readFile(googlePlayFile, "utf8");
      googlePlayData = JSON.parse(googlePlayContent);
      console.log(
        `✅ Loaded ${googlePlayData.apps?.length || 0} Google Play Store apps`
      );
    } catch (error) {
      console.error(
        `❌ Failed to read Google Play Store file: ${error.message}`
      );
      return;
    }

    console.log("📂 Reading Apple App Store data...");
    let appleStoreData;
    try {
      const appleStoreContent = await fs.readFile(appleStoreFile, "utf8");
      appleStoreData = JSON.parse(appleStoreContent);
      console.log(
        `✅ Loaded ${appleStoreData.apps?.length || 0} Apple App Store apps`
      );
    } catch (error) {
      console.error(`❌ Failed to read Apple App Store file: ${error.message}`);
      return;
    }

    console.log("🔍 Combining and deduplicating apps...");

    // Combine all apps
    const allApps = [];
    const seenAppIds = new Set();
    const duplicateStats = {
      googlePlayTotal: googlePlayData.apps?.length || 0,
      appleStoreTotal: appleStoreData.apps?.length || 0,
      googlePlayAdded: 0,
      appleStoreAdded: 0,
      duplicatesSkipped: 0,
    };

    // Add Google Play Store apps first
    if (googlePlayData.apps) {
      googlePlayData.apps.forEach((app) => {
        const appId = app.appId || app.id;
        if (appId && !seenAppIds.has(appId)) {
          allApps.push({
            ...app,
            platform: "Google Play Store",
            originalPlatform: "google-play",
          });
          seenAppIds.add(appId);
          duplicateStats.googlePlayAdded++;
        } else if (appId) {
          duplicateStats.duplicatesSkipped++;
        }
      });
    }

    // Add Apple App Store apps, checking for duplicates
    if (appleStoreData.apps) {
      appleStoreData.apps.forEach((app) => {
        const appId = app.appId || app.id;
        if (appId && !seenAppIds.has(appId)) {
          allApps.push({
            ...app,
            platform: "Apple App Store",
            originalPlatform: "app-store",
          });
          seenAppIds.add(appId);
          duplicateStats.appleStoreAdded++;
        } else if (appId) {
          duplicateStats.duplicatesSkipped++;
          console.log(
            `🔄 Skipped duplicate: ${app.title || "Unknown"} (ID: ${appId})`
          );
        }
      });
    }

    // Print deduplication statistics
    console.log("\n📊 DEDUPLICATION STATISTICS");
    console.log("=".repeat(40));
    console.log(
      `Google Play Store apps loaded: ${duplicateStats.googlePlayTotal}`
    );
    console.log(
      `Apple App Store apps loaded: ${duplicateStats.appleStoreTotal}`
    );
    console.log(
      `Total apps loaded: ${
        duplicateStats.googlePlayTotal + duplicateStats.appleStoreTotal
      }`
    );
    console.log(
      `Google Play Store apps added: ${duplicateStats.googlePlayAdded}`
    );
    console.log(
      `Apple App Store apps added: ${duplicateStats.appleStoreAdded}`
    );
    console.log(`Duplicates skipped: ${duplicateStats.duplicatesSkipped}`);
    console.log(`Final unique apps: ${allApps.length}`);

    // Create combined metadata
    const combinedData = {
      platform: "Combined - Google Play Store & Apple App Store",
      exportDate: new Date().toISOString(),
      totalApps: allApps.length,
      googlePlayApps: duplicateStats.googlePlayAdded,
      appleStoreApps: duplicateStats.appleStoreAdded,
      duplicatesRemoved: duplicateStats.duplicatesSkipped,
      searchScope: "Global - Multiple Countries",
      languageFilter: "English preferred",
      deduplicationMethod: "Based on appId field",
      sourceFiles: [
        "global_sports_fitness_apps_comprehensive.json",
        "appstore_sports_fitness_apps_comprehensive.json",
      ],
      apps: allApps.map((app) => ({
        title: app.title,
        appId: app.appId || app.id,
        id: app.id,
        developer: app.developer,
        category: app.genre || app.targetCategory || app.category,
        rating: app.score || app.rating,
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
        platform: app.platform,
        originalPlatform: app.originalPlatform,
      })),
    };

    // Export to JSON
    await exportCombinedToJSON(
      combinedData,
      "combined_sports_fitness_apps_comprehensive.json"
    );

    // Export to CSV
    await exportCombinedToCSV(
      combinedData.apps,
      "combined_sports_fitness_apps_comprehensive.csv"
    );

    // Print summary statistics
    printCombinedSummary(combinedData.apps);

    console.log(
      "\n✅ Successfully combined Google Play Store and Apple App Store data!"
    );
    console.log("📄 Files created:");
    console.log(
      "  - combined_sports_fitness_apps_comprehensive.json (for data analysis)"
    );
    console.log(
      "  - combined_sports_fitness_apps_comprehensive.csv (for Excel import)"
    );
    console.log(
      `\n📱 Summary: Combined ${allApps.length} unique sports/fitness apps from both platforms`
    );
  } catch (error) {
    console.error(`❌ Error combining app store data: ${error.message}`);
  }
}

/**
 * Export combined apps data to JSON file
 * @param {Object} combinedData - Combined data object with metadata and apps
 * @param {string} filename - Output filename
 */
async function exportCombinedToJSON(
  combinedData,
  filename = "combined_sports_fitness_apps.json"
) {
  try {
    await fs.writeFile(filename, JSON.stringify(combinedData, null, 2));
    console.log(`\n📁 Combined JSON data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export combined JSON: ${error.message}`);
  }
}

/**
 * Export combined apps data to CSV file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportCombinedToCSV(
  apps,
  filename = "combined_sports_fitness_apps.csv"
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
      "Platform",
      "Original Platform",
    ];

    const csvRows = [headers.join(",")];

    apps.forEach((app) => {
      const row = [
        `"${(app.title || "").replace(/"/g, '""')}"`,
        `"${app.appId || ""}"`,
        `"${app.id || ""}"`,
        `"${(app.developer || "").replace(/"/g, '""')}"`,
        `"${app.category || ""}"`,
        app.rating || "",
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
        app.platform || "",
        app.originalPlatform || "",
      ];
      csvRows.push(row.join(","));
    });

    await fs.writeFile(filename, csvRows.join("\n"));
    console.log(`📊 Combined CSV data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export combined CSV: ${error.message}`);
  }
}

/**
 * Print summary statistics of the combined apps
 * @param {Array} apps - Array of app objects
 */
function printCombinedSummary(apps) {
  console.log("\n📊 COMBINED COLLECTION SUMMARY");
  console.log("=".repeat(50));

  // Platform breakdown
  const platformCount = {};
  const categoryCount = {};
  const sourceMethodCount = {};
  const countryCount = {};
  const freeVsPaid = { free: 0, paid: 0 };

  apps.forEach((app) => {
    // Count by platform
    const platform = app.platform || "Unknown";
    platformCount[platform] = (platformCount[platform] || 0) + 1;

    // Count by category
    const category = app.category || app.targetCategory || "Unknown";
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

  console.log("\nBy Platform:");
  Object.entries(platformCount).forEach(([platform, count]) => {
    console.log(`  ${platform}: ${count} apps`);
  });

  console.log("\nBy Category (Top 10):");
  const topCategories = Object.entries(categoryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);
  topCategories.forEach(([cat, count]) => {
    console.log(`  ${cat}: ${count} apps`);
  });

  console.log("\nBy Source Method:");
  Object.entries(sourceMethodCount).forEach(([method, count]) => {
    console.log(`  ${method}: ${count} apps`);
  });

  console.log("\nBy Country (Top 15):");
  const topCountries = Object.entries(countryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 15);
  topCountries.forEach(([country, count]) => {
    console.log(`  ${country.toUpperCase()}: ${count} apps`);
  });

  console.log(`\nFree vs Paid:`);
  console.log(`  Free: ${freeVsPaid.free} apps`);
  console.log(`  Paid: ${freeVsPaid.paid} apps`);

  // Top developers across both platforms
  const developerCount = {};
  apps.forEach((app) => {
    if (app.developer) {
      developerCount[app.developer] = (developerCount[app.developer] || 0) + 1;
    }
  });

  const topDevelopers = Object.entries(developerCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  console.log("\nTop 10 Developers (Both Platforms):");
  topDevelopers.forEach(([dev, count], index) => {
    console.log(`  ${index + 1}. ${dev}: ${count} apps`);
  });

  // Cross-platform developers
  const crossPlatformDevelopers = {};
  apps.forEach((app) => {
    if (app.developer) {
      if (!crossPlatformDevelopers[app.developer]) {
        crossPlatformDevelopers[app.developer] = new Set();
      }
      crossPlatformDevelopers[app.developer].add(app.platform);
    }
  });

  const multiPlatformDevelopers = Object.entries(crossPlatformDevelopers)
    .filter(([, platforms]) => platforms.size > 1)
    .map(([dev, platforms]) => ({
      dev,
      platforms: Array.from(platforms),
      count: developerCount[dev],
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  if (multiPlatformDevelopers.length > 0) {
    console.log("\nTop Cross-Platform Developers:");
    multiPlatformDevelopers.forEach(({ dev, platforms, count }, index) => {
      console.log(
        `  ${index + 1}. ${dev}: ${count} apps (${platforms.join(", ")})`
      );
    });
  }
}

// Main execution
async function main() {
  console.log("🚀 Starting comprehensive app store data combination...");
  console.log(
    "🔄 Combining Google Play Store and Apple App Store sports/fitness apps"
  );
  console.log("📱 Deduplication method: Based on appId field");

  await combineAppStoreData();
}

main();
