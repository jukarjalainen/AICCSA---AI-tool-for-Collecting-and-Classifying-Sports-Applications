/**
 * Merger module.
 * Combines Apple and Google datasets, detects cross-platform duplicates, and normalizes platform fields.
 */
export function combineAndDeduplicateApps(
  appStoreApps,
  googlePlayApps,
  logToFile,
) {
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
        `   🔄 Cross-platform app found (appId): "${existingApp.title}" (${existingApp.appId})`,
      );
    } else {
      // Check for title similarity (exact match for now, could be enhanced with fuzzy matching)
      existingApp = allApps.find(
        (app) =>
          app.title &&
          playApp.title &&
          app.title.trim().toLowerCase() === playApp.title.trim().toLowerCase(),
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
          `   🔄 Cross-platform app found (title): "${existingApp.title}"`,
        );
        logToFile(
          `     📱 Apple: ${existingApp.appId} | 🤖 Google: ${playApp.appId}`,
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
    }`,
  );
  logToFile(`   ➕ New apps added from Google Play: ${newAppsAdded}`);
  logToFile(`   🎯 Total unique apps: ${allApps.length}`);

  return allApps;
}
