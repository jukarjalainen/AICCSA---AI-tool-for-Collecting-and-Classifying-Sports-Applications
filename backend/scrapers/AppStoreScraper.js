/**
 * Apple App Store scraper class.
 * Collects sports and health/fitness apps from top collections and search terms per country.
 */
import store from "app-store-scraper";

export class AppStoreScraper {
  constructor({ countries, searchQueries, logToFile, includeTopCollections }) {
    this.countries = countries;
    this.searchQueries = searchQueries;
    this.logToFile = logToFile;
    this.includeTopCollections = includeTopCollections;
  }

  async scrape() {
    try {
      let allApps = [];
      const targetCategories = [
        store.category.SPORTS,
        store.category.HEALTH_AND_FITNESS,
      ];
      const targetCountries = this.countries;
      const { logToFile } = this;

      logToFile("🍎 Starting Apple App Store collection...");

      // Calculate time estimation
      const collections = [
        store.collection.TOP_FREE_IOS,
        store.collection.TOP_PAID_IOS,
        store.collection.TOP_GROSSING_IOS,
        store.collection.TOP_FREE_IPAD,
        store.collection.TOP_PAID_IPAD,
        store.collection.TOP_GROSSING_IPAD,
      ];

      const totalCollectionCalls = this.includeTopCollections
        ? targetCountries.length * targetCategories.length * collections.length
        : 0;
      const totalSearchCalls =
        targetCountries.length * this.searchQueries.length;
      const totalAPICalls = totalCollectionCalls + totalSearchCalls;

      logToFile(`   📋 APP STORE Collection calls: ${totalCollectionCalls}`);
      logToFile(`   🔍 APP STORE Search calls: ${totalSearchCalls}`);
      logToFile(`   🎯 APP STORE Total API calls: ${totalAPICalls}`);

      // Process each country
      for (const country of targetCountries) {
        logToFile(`\n🌍 Processing APP STORE in: ${country.toUpperCase()}`);

        for (const category of targetCategories) {
          const categoryName = Object.keys(store.category).find(
            (key) => store.category[key] === category,
          );
          logToFile(`\n📱 APP STORE Processing ${categoryName} category...`);

          if (!this.includeTopCollections) {
            continue;
          }

          // Step 1: Get apps from collections
          for (const collection of collections) {
            try {
              const collectionName = Object.keys(store.collection).find(
                (key) => store.collection[key] === collection,
              );
              logToFile(`  📋 APP STORE Fetching from ${collectionName}...`);

              const listApps = await store.list({
                category: category,
                collection: collection,
                num: 200, // max 200
                country: country,
                fullDetail: true,
              });

              let newAppsCount = 0;
              listApps.forEach((app) => {
                if (
                  !allApps.find(
                    (existingApp) => existingApp.appId === app.appId,
                  )
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
                `    ✅ APP STORE Added ${newAppsCount} new apps from ${collectionName}`,
              );
              await new Promise((resolve) => setTimeout(resolve, 500));
            } catch (error) {
              logToFile(
                `    ⚠️ APP STORE Failed to fetch from ${collection}: ${error.message}`,
              );
            }
          }
        }

        // Step 2: Search with queries for this country
        logToFile(
          `  🔍 APP STORE Searching with ${
            this.searchQueries.length
          } terms in ${country.toUpperCase()}...`,
        );

        for (const query of this.searchQueries) {
          try {
            logToFile(
              ` APP STORE Searching: "${query}" in ${country.toUpperCase()}`,
            );
            const searchApps = await store.search({
              term: query,
              num: 200,
              country: country,
              fullDetail: true,
            });

            // Log total results found
            logToFile(
              `      📊 APP STORE Found ${searchApps.length} total results for "${query}"`,
            );

            // Log genre distribution for debugging
            const genreCount = {};
            searchApps.forEach((app) => {
              const genre = app.primaryGenre;
              genreCount[genre] = (genreCount[genre] || 0) + 1;
            });
            logToFile(
              `      🏷️  APP STORE Genres found: ${JSON.stringify(genreCount)}`,
            );

            // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps
            const filteredSearchApps = searchApps.filter((app) => {
              const appGenreID = app.primaryGenreID || "";
              const appPrimaryGenre = app.primaryGenre || "";

              // Only include apps that are explicitly in Sports or Health & Fitness categories
              const isSportsGenre =
                appGenreID === 6004 ||
                appGenreID === "SPORTS" ||
                appPrimaryGenre === "Sports";
              const isHealthFitnessGenre =
                appGenreID === 6013 ||
                appGenreID === "HEALTH_AND_FITNESS" ||
                appPrimaryGenre === "Health & Fitness";

              const isValidCategory = isSportsGenre || isHealthFitnessGenre;

              // Log filtered apps for debugging
              if (!isValidCategory) {
                logToFile(
                  `      🚫 APP STORE Filtered out: "${app.title}" (Genre: ${
                    app.primaryGenre
                  }, IDs: ${JSON.stringify(appGenreID)})`,
                );
              } else {
                logToFile(
                  `      ✅ APP STORE Keeping: "${app.title}" (Genre: ${app.primaryGenre})`,
                );
              }

              return isValidCategory;
            });

            const filteredOutCount =
              searchApps.length - filteredSearchApps.length;
            if (filteredOutCount > 0) {
              logToFile(
                `      🔍 APP STORE Filtered out ${filteredOutCount} non-sports/fitness apps`,
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
                `      ✅ APP STORE Added ${newSearchAppsCount} new apps from "${query}" in ${country.toUpperCase()}`,
              );
            }

            await new Promise((resolve) => setTimeout(resolve, 500));
          } catch (searchError) {
            logToFile(
              `      ⚠️ APP STORE Search failed for "${query}" in ${country.toUpperCase()}: ${
                searchError.message
              }`,
            );
          }
        }

        logToFile(
          `🏁 APP STORE Completed ${country.toUpperCase()}: Total apps collected so far: ${
            allApps.length
          }`,
        );
      }

      logToFile(
        `\n🎯 Apple App Store collection completed: ${allApps.length} apps`,
      );
      return allApps;
    } catch (error) {
      this.logToFile(`Error in Apple App Store collection: ${error.message}`);
      return [];
    }
  }
}
