import gplay from "google-play-scraper";

/**
 * Create a list of apps from a given category with multiple collections
 * @param {string} category - The category to search for apps
 * @param {number} numApps - Total number of apps to retrieve
 * @returns {Promise<Array>} Promise that resolves to an array of app objects
 */
async function listAppsByCategory(category = "GAME", numApps = 10) {
  try {
    let allApps = [];
    const maxPerRequest = 200; // Maximum apps per request
    const collections = [
      gplay.collection.TOP_GROSSING,
      gplay.collection.TOP_FREE,
      gplay.collection.TOP_PAID,
      gplay.collection.NEW_FREE,
      gplay.collection.NEW_PAID,
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
        collection: gplay.collection.TOP_GROSSING,
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

/**
 * Alternative method: Combine list and search results for more apps
 * @param {string} category - The category to search for apps
 * @param {number} numApps - Total number of apps to retrieve
 * @returns {Promise<Array>} Promise that resolves to an array of app objects
 */
async function getMoreAppsByCategory(category = "GAME", numApps = 10) {
  try {
    let allApps = [];

    // First, get apps from the list API
    console.log("Fetching from list API...");
    const listApps = await gplay.list({
      category: gplay.category[category.toUpperCase()] || gplay.category.GAME,
      collection: gplay.collection.TOP_GROSSING,
      num: 200,
      country: "us",
    });
    allApps = [...listApps];

    // If we need more apps, use search API with category-specific terms
    if (numApps > 200) {
      console.log("Fetching additional apps from search API...");
      const categoryQueries = {
        GAME: ["game", "games", "gaming", "arcade", "puzzle"],
        BUSINESS: ["business", "productivity", "office", "work"],
        EDUCATION: ["education", "learning", "study", "school"],
        SOCIAL: ["social", "chat", "messaging", "friends"],
        SPORTS: ["sports", "fitness", "workout", "exercise"],
        ENTERTAINMENT: ["entertainment", "video", "movie", "tv"],
      };

      const queries = categoryQueries[category.toUpperCase()] || [
        category.toLowerCase(),
      ];

      for (const query of queries) {
        if (allApps.length >= numApps) break;

        try {
          const searchApps = await gplay.search({
            term: query,
            num: 50,
            country: "us",
          });

          // Add unique apps
          searchApps.forEach((app) => {
            if (
              !allApps.find((existingApp) => existingApp.appId === app.appId)
            ) {
              allApps.push(app);
            }
          });
        } catch (searchError) {
          console.warn(
            `Search failed for query "${query}": ${searchError.message}`
          );
        }
      }
    }

    return allApps.slice(0, numApps);
  } catch (error) {
    console.error(`Error fetching apps: ${error.message}`);
    return [];
  }
}

// Example usage
async function main() {
  console.log("🏆 Scraping SPORTS apps...");

  // Try the enhanced method for more apps
  const sportsApps = await getMoreAppsByCategory("SPORTS", 500);
  console.log(`Successfully retrieved ${sportsApps.length} apps`);

  // Print first 10 for display
  printApps(sportsApps.slice(0, 10));

  console.log(`\n... and ${sportsApps.length - 10} more apps`);
}

main();
