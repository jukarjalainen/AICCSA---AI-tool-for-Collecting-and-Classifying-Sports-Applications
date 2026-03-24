import gplay from "google-play-scraper";

/**
 * Create a list of apps from a given category using multiple collections
 * @param {string} category - The category to search for apps
 * @param {number} numApps - Total number of apps to retrieve
 * @returns {Promise<Array>} Promise that resolves to an array of app objects
 */
async function listAppsByCategory(category = "GAME", numApps = 10) {
  try {
    let allApps = [];
    const maxPerRequest = 200; // Maximum apps per request
    const collections = [
      gplay.collection.GROSSING,
      gplay.collection.TOP_FREE,
      gplay.collection.TOP_PAID,
    ];

    // If requesting more than 200, use multiple collections
    if (numApps > maxPerRequest) {
      const appsPerCollection = Math.ceil(numApps / collections.length);

      for (const collection of collections) {
        if (allApps.length >= numApps) break;

        try {
          console.log(`Fetching from collection: ${collection}...`);
          const apps = await gplay.list({
            category:
              gplay.category[category.toUpperCase()] || gplay.category.GAME,
            collection: collection,
            num: Math.min(appsPerCollection, maxPerRequest),
            country: "us",
          });

          // Add apps that aren't already in our list (avoid duplicates)
          apps.forEach((app) => {
            if (
              !allApps.find((existingApp) => existingApp.appId === app.appId)
            ) {
              allApps.push(app);
            }
          });

          console.log(
            `Found ${apps.length} apps from ${collection}, total unique: ${allApps.length}`
          );
        } catch (collectionError) {
          console.warn(
            `Failed to fetch from collection ${collection}: ${collectionError.message}`
          );
        }
      }
    } else {
      // Single request for smaller numbers
      allApps = await gplay.list({
        category: gplay.category[category.toUpperCase()] || gplay.category.GAME,
        collection: gplay.collection.GROSSING,
        num: Math.min(numApps, maxPerRequest),
        country: "us",
      });
    }

    // Return only the requested number of apps
    return allApps.slice(0, numApps);
  } catch (error) {
    console.error(`Error fetching apps: ${error.message}`);
    return [];
  }
}

/**
 * Print the list of apps in a formatted way
 * @param {Array} apps - Array of app objects
 */
function printApps(apps) {
  if (!apps || apps.length === 0) {
    console.log("No apps found.");
    return;
  }

  console.log(`\nFound ${apps.length} apps:`);
  console.log("=".repeat(80));

  apps.forEach((app, index) => {
    console.log(`\n${index + 1}. ${app.title}`);
    console.log(`   📱 Package: ${app.appId}`);
    console.log(`   👩‍💻 Developer: ${app.developer}`);
    console.log(`   ⭐ Rating: ${app.score || "N/A"}`);
    console.log(`   📥 Installs: ${app.installs || "N/A"}`);
    console.log(`   💰 Free: ${app.free ? "Yes" : "No"}`);
    console.log("-".repeat(80));
  });
}

// Example usage
async function main() {
  console.log("🏆 Scraping SPORTS apps using multiple collections...");

  const sportsApps = await listAppsByCategory("SPORTS", 800);
  console.log(`\n✅ Successfully retrieved ${sportsApps.length} unique apps`);

  // Print first 10 for display
  console.log("\n📱 First 10 apps:");
  printApps(sportsApps.slice(0, 10));

  if (sportsApps.length > 10) {
    console.log(`\n... and ${sportsApps.length - 10} more apps available`);
  }
}

main();
