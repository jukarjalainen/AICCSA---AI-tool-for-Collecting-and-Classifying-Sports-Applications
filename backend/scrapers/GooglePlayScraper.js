import gplay from "google-play-scraper";

export class GooglePlayScraper {
  constructor({ countries, searchQueries, logToFile }) {
    this.countries = countries;
    this.searchQueries = searchQueries;
    this.logToFile = logToFile;
  }

  async scrape() {
    try {
      let allApps = [];
      const targetCategories = ["SPORTS", "HEALTH_AND_FITNESS"];
      const targetCountries = this.countries;
      const { logToFile } = this;

      logToFile("🤖 Starting Google Play Store collection...");

      const collections = [
        gplay.collection.GROSSING,
        gplay.collection.TOP_FREE,
        gplay.collection.TOP_PAID,
      ];
      const totalCollectionCalls =
        targetCountries.length * targetCategories.length * collections.length;
      const totalSearchCalls =
        targetCountries.length * this.searchQueries.length;
      const totalAPICalls = totalCollectionCalls + totalSearchCalls;

      logToFile(`   📋 PLAY STORE Collection calls: ${totalCollectionCalls}`);
      logToFile(`   🔍 PLAY STORE Search calls: ${totalSearchCalls}`);
      logToFile(
        `   🎯 PLAY STORE Total Google Play API calls: ${totalAPICalls}`,
      );

      // Process each country
      for (const country of targetCountries) {
        logToFile(
          `\n🌍 Processing Google Play Store in: ${country.toUpperCase()}`,
        );

        for (const category of targetCategories) {
          logToFile(`\n📱 PLAY STORE Processing ${category} category...`);

          // Step 1: Get apps from collections
          for (const collection of collections) {
            try {
              logToFile(`  📋 PLAY STORE Fetching from ${collection}...`);

              const listApps = await gplay.list({
                category: category,
                collection: collection,
                num: 500,
                country: country,
                fullDetail: true, // Need full details for genre information
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
                    platform: "Google Play Store",
                    sourceMethod: "list",
                    sourceCollection: collection,
                    sourceCountry: country,
                    targetCategory: category,
                    actualGenre: app.genreID,
                  });
                  newAppsCount++;
                }
              });

              logToFile(
                `    ✅ PLAY STORE Added ${newAppsCount} new apps from ${collection}`,
              );
              await new Promise((resolve) => setTimeout(resolve, 500));
            } catch (error) {
              logToFile(
                `    ⚠️ PLAY STORE Failed to fetch from ${collection}: ${error.message}`,
              );
            }
          }
        }

        // Step 2: Search with search queries for this country
        logToFile(
          `  🔍 PLAY STORE Searching with ${
            this.searchQueries.length
          } search terms in ${country.toUpperCase()}...`,
        );

        for (const query of this.searchQueries) {
          try {
            logToFile(
              `PLAYSTORE    Searching: "${query}" in ${country.toUpperCase()}`,
            );
            const searchApps = await gplay.search({
              term: query,
              num: 250, // max is 250
              country: country,
              fullDetail: true, // Need full details for genre information
            });

            // Log total results found
            logToFile(
              `      📊 PLAY STORE Found ${searchApps.length} total results for "${query}"`,
            );

            // Log genre distribution for debugging
            const genreCount = {};
            searchApps.forEach((app) => {
              const genre = app.genreID;
              genreCount[genre] = (genreCount[genre] || 0) + 1;
            });
            logToFile(`      🏷️  Genres found: ${JSON.stringify(genreCount)}`);

            // Debug: log a few sample apps with all their properties
            if (searchApps.length > 0) {
              const sampleApp = searchApps[0];
              logToFile(
                `      🔍 PLAY STORE Sample app properties: ${JSON.stringify(
                  {
                    title: sampleApp.title,
                    genre: sampleApp.genre,
                    genreId: sampleApp.genreId,
                    categories: sampleApp.categories,
                  },
                  null,
                  2,
                )}`,
              );
            }

            // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps
            const filteredSearchApps = searchApps.filter((app) => {
              const appGenreID = app.genreId;
              const appGenre = app.genre;

              // Only include apps that are explicitly in Sports or Health & Fitness categories
              const isSportsGenre =
                appGenreID === "SPORTS" || appGenre === "Sports";

              const isHealthFitnessGenre =
                appGenreID === "HEALTH_AND_FITNESS" ||
                appGenre === "Health & Fitness";

              const isValidCategory = isSportsGenre || isHealthFitnessGenre;

              // Log filtered apps for debugging
              if (!isValidCategory) {
                logToFile(
                  `      🚫 PLAY STORE Filtered out (wrong genre): "${app.title}" (Genre: ${appGenre})`,
                );
              } else {
                logToFile(
                  `      ✅ PLAY STORE Keeping: "${app.title}" (Genre: ${appGenre})`,
                );
              }

              return isValidCategory;
            });

            const filteredOutCount =
              searchApps.length - filteredSearchApps.length;
            if (filteredOutCount > 0) {
              logToFile(
                `      🔍 PLAY STORE Filtered out ${filteredOutCount} non-sports/fitness apps`,
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
                  actualGenre: app.genreID,
                });
                newSearchAppsCount++;
              }
            });

            if (newSearchAppsCount > 0) {
              logToFile(
                `      ✅ PLAY STORE Added ${newSearchAppsCount} new apps from "${query}" in ${country.toUpperCase()}`,
              );
            }

            await new Promise((resolve) => setTimeout(resolve, 500));
          } catch (searchError) {
            logToFile(
              `      ⚠️ PLAY STORE Search failed for "${query}" in ${country.toUpperCase()}: ${
                searchError.message
              }`,
            );
          }
        }

        logToFile(
          `🏁 PLAY STORE Completed ${country.toUpperCase()}: Total apps collected so far: ${
            allApps.length
          }`,
        );
      }

      logToFile(`\n🎯 PLAY STORE collection completed: ${allApps.length} apps`);
      return allApps;
    } catch (error) {
      this.logToFile(` PLAY STORE Error in collection: ${error.message}`);
      return [];
    }
  }
}
