import gplay from "google-play-scraper";

/**
 * Combine list and search results for maximum app coverage
 * @param {string} category - The category to search for apps
 * @param {number} numApps - Total number of apps to retrieve
 * @returns {Promise<Array>} Promise that resolves to an array of app objects
 */
async function getAppsByListAndSearch(category = "GAME", numApps = 10) {
  try {
    let allApps = [];

    // Step 1: Get apps from the list API
    console.log("📋 Fetching from list API...");
    try {
      const listApps = await gplay.list({
        category: gplay.category[category.toUpperCase()] || gplay.category.GAME,
        collection: gplay.collection.GROSSING,
        num: Math.min(200, numApps),
        country: "us",
      });
      allApps = [...listApps];
      console.log(`✅ Got ${listApps.length} apps from list API`);
    } catch (listError) {
      console.warn(`⚠️ List API failed: ${listError.message}`);
    }

    // Step 2: If we need more apps, use search API with category-specific terms
    if (numApps > allApps.length) {
      console.log("🔍 Fetching additional apps from search API...");

      const categoryQueries = {
        SPORTS: [
          "sports",
          "fitness",
          "workout",
          "exercise",
          "training",
          "health",
          "gym",
        ],
        HEALTH_AND_FITNESS: [
          "health",
          "fitness",
          "wellness",
          "exercise",
          "workout",
          "training",
          "gym",
        ],
      };

      const queries = categoryQueries[category.toUpperCase()] || [
        category.toLowerCase(),
      ];

      for (const query of queries) {
        if (allApps.length >= numApps) break;

        try {
          console.log(`   Searching for: "${query}"`);
          const searchApps = await gplay.search({
            term: query,
            num: 50,
            country: "us",
          });

          // Add unique apps only
          let newAppsCount = 0;
          searchApps.forEach((app) => {
            if (
              !allApps.find((existingApp) => existingApp.appId === app.appId)
            ) {
              allApps.push(app);
              newAppsCount++;
            }
          });

          console.log(
            `   ✅ Added ${newAppsCount} new unique apps from "${query}"`
          );

          // Small delay to avoid rate limiting
          await new Promise((resolve) => setTimeout(resolve, 500));
        } catch (searchError) {
          console.warn(
            `   ⚠️ Search failed for query "${query}": ${searchError.message}`
          );
        }
      }
    }

    console.log(`\n🎯 Total unique apps collected: ${allApps.length}`);
    return allApps.slice(0, numApps);
  } catch (error) {
    console.error(`Error fetching apps: ${error.message}`);
    return [];
  }
}

/**
 * Print the list of apps in a formatted way
 * @param {Array} apps - Array of app objects
 * @param {number} limit - Maximum number of apps to display (default: 10)
 */
function printApps(apps, limit = 10) {
  if (!apps || apps.length === 0) {
    console.log("No apps found.");
    return;
  }

  const appsToShow = apps.slice(0, limit);
  console.log(
    `\nDisplaying ${appsToShow.length} apps (out of ${apps.length} total):`
  );
  console.log("=".repeat(80));

  appsToShow.forEach((app, index) => {
    console.log(`\n${index + 1}. ${app.title}`);
    console.log(`   📱 Package: ${app.appId}`);
    console.log(`   👩‍💻 Developer: ${app.developer}`);
    console.log(`   ⭐ Rating: ${app.score || "N/A"}`);
    console.log(`   📥 Installs: ${app.installs || "N/A"}`);
    console.log(`   💰 Free: ${app.free ? "Yes" : "No"}`);
    console.log("-".repeat(80));
  });

  if (apps.length > limit) {
    console.log(`\n... and ${apps.length - limit} more apps available`);
  }
}

/**
 * Export apps data to JSON file
 * @param {Array} apps - Array of app objects
 * @param {string} filename - Output filename
 */
async function exportToJSON(apps, filename = "apps_data.json") {
  try {
    const fs = await import("fs/promises");
    await fs.writeFile(filename, JSON.stringify(apps, null, 2));
    console.log(`📁 Data exported to ${filename}`);
  } catch (error) {
    console.error(`Failed to export data: ${error.message}`);
  }
}

// Example usage
async function main() {
  console.log(
    "🔄 Scraping SPORTS apps using combined list + search approach..."
  );

  const sportsApps = await getAppsByListAndSearch("SPORTS", 1000);
  console.log(`\n✅ Successfully retrieved ${sportsApps.length} unique apps`);

  // Print sample of results
  printApps(sportsApps, 15);

  // Export to JSON file
  await exportToJSON(sportsApps, "sports_apps_data.json");
}

main();
