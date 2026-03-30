/**
 * Summary module.
 * Computes and logs aggregate statistics for categories, sources, countries, and free/paid split.
 */
export function printCombinedSummary(apps, logToFile) {
  logToFile("\n📊 COMBINED COLLECTION SUMMARY");
  logToFile("=".repeat(50));

  const categoryCount = {};
  const sourceMethodCount = {};
  const countryCount = {};
  const freeVsPaid = { free: 0, paid: 0 };

  apps.forEach((app) => {

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
