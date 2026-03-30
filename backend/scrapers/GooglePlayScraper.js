/**
 * Google Play scraper class.
 * Collects sports and health/fitness apps from top lists and search terms per country.
 */
import gplay from "google-play-scraper";

export class GooglePlayScraper {
  constructor({ countries, searchQueries, logToFile, includeTopCollections }) {
    this.countries = countries;
    this.searchQueries = searchQueries;
    this.logToFile = logToFile;
    this.includeTopCollections = includeTopCollections;
  }

  async scrape() {
    try {
      let allApps = [];
      const targetCategories = ["SPORTS", "HEALTH_AND_FITNESS"];
      const allowedCategoryIds = new Set(targetCategories);
      const targetCountries = this.countries;
      const { logToFile } = this;

      const normalizeCategoryId = (value) => {
        if (!value) {
          return "";
        }

        const raw = String(value).trim().toUpperCase();
        const collapsed = raw.replace(/&/g, "AND").replace(/\s+/g, "_");

        if (
          collapsed === "HEALTH_AND_FITNESS" ||
          collapsed === "HEALTH_FITNESS" ||
          collapsed === "HEALTHANDFITNESS"
        ) {
          return "HEALTH_AND_FITNESS";
        }

        if (collapsed === "SPORTS" || collapsed === "SPORT") {
          return "SPORTS";
        }

        return collapsed;
      };

      const getCategoryIds = (app) => {
        const ids = new Set();

        const directGenreIds = [
          app?.genreId,
          app?.genreID,
          app?.genre,
          app?.appCategory,
        ]
          .filter(Boolean)
          .map((v) => normalizeCategoryId(v));
        directGenreIds.forEach((id) => ids.add(id));

        if (Array.isArray(app?.categories)) {
          app.categories.forEach((cat) => {
            const candidate =
              typeof cat === "string"
                ? cat
                : cat?.id || cat?.genreId || cat?.genreID || cat?.name;
            if (candidate) {
              ids.add(normalizeCategoryId(candidate));
            }
          });
        }

        return [...ids];
      };

      const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

      const hasUsableGenre = (app) => getCategoryIds(app).length > 0;

      const isLikelyGameApp = (app) => {
        const text =
          `${app?.title || ""} ${app?.summary || ""} ${app?.description || ""}`.toLowerCase();
        const hints = [
          " game",
          "clash",
          "battle",
          "simulator",
          "arcade",
          "puzzle",
          "idle",
          "rpg",
          "shooter",
        ];
        return hints.some((hint) => text.includes(hint));
      };

      const fetchFullDetailForApp = async (appId, country) => {
        const argVariants = [
          { appId, country, lang: "en" },
          { appId, country },
          { appId },
        ];

        for (const args of argVariants) {
          for (let attempt = 1; attempt <= 2; attempt++) {
            try {
              const fullApp = await gplay.app(args);
              if (fullApp && hasUsableGenre(fullApp)) {
                return fullApp;
              }
            } catch {
              // Try next attempt/variant.
            }
            await sleep(100);
          }
        }

        return null;
      };

      const enrichAppsWithFullDetails = async (apps, country) => {
        const enriched = [];
        const batchSize = 8;

        for (let i = 0; i < apps.length; i += batchSize) {
          const chunk = apps.slice(i, i + batchSize);
          const results = await Promise.all(
            chunk.map(async (app) => {
              if (!app?.appId) {
                return null;
              }

              if (hasUsableGenre(app)) {
                return app;
              }

              const detailed = await fetchFullDetailForApp(app.appId, country);
              if (!detailed) {
                logToFile(
                  `      ⚠️ PLAY STORE Detail fetch failed for ${app.appId}: unable to obtain full detail with genre`,
                );
                return {
                  ...app,
                  _detailFetchFailed: true,
                };
              }
              return detailed;
            }),
          );

          results.forEach((item) => {
            if (item) {
              enriched.push(item);
            }
          });

          await sleep(150);
        }

        return enriched;
      };

      const isAllowedNonGameCategory = (app) => {
        const categoryIds = getCategoryIds(app);
        const hasGameCategory = categoryIds.some((id) =>
          id.startsWith("GAME_"),
        );
        const hasAllowedCategory = categoryIds.some((id) =>
          allowedCategoryIds.has(id),
        );
        return {
          isAllowed: hasAllowedCategory && !hasGameCategory,
          categoryIds,
          hasGameCategory,
        };
      };

      logToFile("🤖 Starting Google Play Store collection...");

      const collections = [
        gplay.collection.GROSSING,
        gplay.collection.TOP_FREE,
        gplay.collection.TOP_PAID,
      ];
      const totalCollectionCalls = this.includeTopCollections
        ? targetCountries.length * targetCategories.length * collections.length
        : 0;
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

          if (!this.includeTopCollections) {
            continue;
          }

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

              const filteredListApps = listApps.filter((app) => {
                const { isAllowed, categoryIds } =
                  isAllowedNonGameCategory(app);
                if (!isAllowed) {
                  logToFile(
                    `    🚫 PLAY STORE Filtered out from ${collection}: "${app.title}" (Categories: ${categoryIds.join("|") || "UNKNOWN"})`,
                  );
                }
                return isAllowed;
              });

              let newAppsCount = 0;
              filteredListApps.forEach((app) => {
                const categoryIds = getCategoryIds(app);
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
                    actualGenre:
                      categoryIds[0] || app.genreId || app.genreID || "",
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
            let baseSearchApps = [];

            try {
              const searchAppsRaw = await gplay.search({
                term: query,
                num: 250, // max is 250
                country: country,
                fullDetail: true,
              });
              baseSearchApps = Array.isArray(searchAppsRaw)
                ? searchAppsRaw
                : [];
            } catch (searchFullDetailError) {
              logToFile(
                `      ⚠️ PLAY STORE fullDetail search failed for "${query}" in ${country.toUpperCase()}: ${searchFullDetailError.message}`,
              );
              logToFile(
                "      🔁 PLAY STORE Falling back to summary search before per-app full detail enrichment...",
              );

              const summaryResults = await gplay.search({
                term: query,
                num: 250,
                country: country,
                fullDetail: false,
              });
              baseSearchApps = Array.isArray(summaryResults)
                ? summaryResults
                : [];
            }

            const searchApps = await enrichAppsWithFullDetails(
              baseSearchApps,
              country,
            );

            // Log total results found
            logToFile(
              `      📊 PLAY STORE Found ${baseSearchApps.length} raw results for "${query}"`,
            );
            logToFile(
              `      🧩 PLAY STORE Enriched ${searchApps.length} results with full detail`,
            );

            // Log genre distribution for debugging
            const genreCount = {};
            searchApps.forEach((app) => {
              const genre = app.genreId || app.genre || "UNKNOWN";
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

            // Filter search results to only include SPORTS or HEALTH_AND_FITNESS category apps.
            // At this point, apps should have full detail (genre/category metadata).
            const filteredSearchApps = searchApps.filter((app) => {
              const { isAllowed, categoryIds, hasGameCategory } =
                isAllowedNonGameCategory(app);
              const allowFallbackUnknown =
                !isAllowed &&
                !hasGameCategory &&
                categoryIds.length === 0 &&
                app?._detailFetchFailed &&
                !isLikelyGameApp(app);
              const shouldKeep = isAllowed || allowFallbackUnknown;

              // Log filtered apps for debugging
              if (!shouldKeep) {
                logToFile(
                  `      🚫 PLAY STORE Filtered out (wrong genre): "${app.title}" (Categories: ${categoryIds.join("|") || "UNKNOWN"})`,
                );
              } else {
                const reason = isAllowed
                  ? "category"
                  : "fallback-after-detail-fail";
                logToFile(
                  `      ✅ PLAY STORE Keeping (${reason}): "${app.title}" (Categories: ${categoryIds.join("|") || "UNKNOWN"})`,
                );
              }

              return shouldKeep;
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
              const categoryIds = getCategoryIds(app);
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
                  actualGenre:
                    categoryIds[0] ||
                    app.genreId ||
                    app.genreID ||
                    app.genre ||
                    "",
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
