/**
 * Summary module.
 * Computes and logs aggregate statistics for platform coverage, categories, sources, countries, and free/paid split.
 */
export function printCombinedSummary(apps, logToFile) {
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
    `  📊 Cross-platform coverage: ${crossPlatformPercentage}% of apps`,
  );

  logToFile("\nCross-Platform Detection Methods:");
  logToFile(`  🆔 Matched by AppId: ${crossPlatformMethods.appId} apps`);
  logToFile(`  📝 Matched by Title: ${crossPlatformMethods.title} apps`);
  logToFile(
    `  🎯 Total detected: ${
      crossPlatformMethods.appId + crossPlatformMethods.title
    } apps`,
  );

  logToFile("\nBy Category:");
  Object.entries(categoryCount).forEach(([cat, count]) => {
    logToFile(`  ${cat}: ${count} apps`);
  });

  logToFile("\nBy Source Method:");
  Object.entries(sourceMethodCount).forEach(([method, count]) => {
    logToFile(`  ${method}: ${count} apps`);
  });

  logToFile("\nBy Country:");
  const topCountries = Object.entries(countryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 30);
  topCountries.forEach(([country, count]) => {
    logToFile(`  ${country.toUpperCase()}: ${count} apps`);
  });

  logToFile(`\nFree vs Paid:`);
  logToFile(`  Free: ${freeVsPaid.free} apps`);
  logToFile(`  Paid: ${freeVsPaid.paid} apps`);
}
