/**
 * Entrypoint orchestrator for the full scraping pipeline.
 * Runs both store scrapers, merges/deduplicates results, exports files, and writes logs.
 */
import fs from "fs/promises";
import { countriesEssential } from "./lists/countries_essential.js";
import { searchQueriesEssential } from "./lists/searchQueries_essential.js";
import { AppStoreScraper } from "./scrapers/AppStoreScraper.js";
import { GooglePlayScraper } from "./scrapers/GooglePlayScraper.js";
import { combineAndDeduplicateApps } from "./modules/merger.js";
import { printCombinedSummary } from "./modules/summary.js";
import {
  exportPlayStoreToJSON,
  exportPlayStoreToCSV,
  exportCombinedToJSON,
  exportCombinedToCSV,
} from "./modules/exporters.js";

// Test configuration - minimal setup for quick testing
const searchQueries = searchQueriesEssential;
const countries = countriesEssential;

// Create a logging utility that writes to both console and file
let logStream = "";
const logFileName = `scraper_log_${new Date()
  .toISOString()
  .replace(/[:.]/g, "-")}.txt`;

function logToFile(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}`;
  console.log(message); // Still show in console
  logStream += logMessage + "\n";
}

async function saveLogFile() {
  try {
    await fs.writeFile(logFileName, logStream);
    console.log(`\n📝 Console log saved to: ${logFileName}`);
  } catch (error) {
    console.error(`Failed to save log file: ${error.message}`);
  }
}

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from Apple App Store
 */
async function getAppStoreApps() {
  const scraper = new AppStoreScraper({
    countries,
    searchQueries,
    logToFile,
  });
  return scraper.scrape();
}

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from Google Play Store
 */
async function getGooglePlayApps() {
  const scraper = new GooglePlayScraper({
    countries,
    searchQueries,
    logToFile,
  });
  return scraper.scrape();
}

/**
 * Main execution function
 */
async function main() {
  const startTime = Date.now();
  const startTimeFormatted = new Date().toISOString();

  logToFile("🚀 Starting scraper for Apple App Store & Google Play Store...");
  logToFile(`⏰ Started at: ${startTimeFormatted}`);

  try {
    // Scrape both platforms in parallel for better performance
    logToFile("\n📱 Starting parallel scraping of both platforms...");

    const [appStoreApps, googlePlayApps] = await Promise.all([
      getAppStoreApps(),
      getGooglePlayApps(),
    ]);

    if (appStoreApps.length === 0 && googlePlayApps.length === 0) {
      logToFile(
        "❌ No apps were collected from either platform. Check your internet connection and try again.",
      );
      await saveLogFile();
      return;
    }

    // Combine and deduplicate
    const combinedApps = combineAndDeduplicateApps(
      appStoreApps,
      googlePlayApps,
      logToFile,
    );

    if (combinedApps.length > 0) {
      printCombinedSummary(combinedApps, logToFile);

      // Create timestamped filenames
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const jsonFilename = `COMPLETE_sports_fitness_apps_${timestamp}.json`;
      const csvFilename = `COMPLETE_sports_fitness_apps_${timestamp}.csv`;
      // Apple only
      const appleJsonFilename = `COMPLETE_appstore_sports_fitness_apps_${timestamp}.json`;
      const appleCsvFilename = `COMPLETE_appstore_sports_fitness_apps_${timestamp}.csv`;
      // Google Play only
      const playJsonFilename = `COMPLETE_playstore_sports_fitness_apps_${timestamp}.json`;
      const playCsvFilename = `COMPLETE_playstore_sports_fitness_apps_${timestamp}.csv`;

      // Export Apple App Store results
      if (appStoreApps.length > 0) {
        await exportCombinedToJSON(appStoreApps, appleJsonFilename, logToFile);
        await exportCombinedToCSV(appStoreApps, appleCsvFilename, logToFile);
        logToFile(`  - ${appleJsonFilename} (Apple App Store JSON)`);
        logToFile(`  - ${appleCsvFilename} (Apple App Store CSV)`);
      }
      // Export Google Play Store results (all fields)
      if (googlePlayApps.length > 0) {
        await exportPlayStoreToJSON(
          googlePlayApps,
          playJsonFilename,
          logToFile,
        );
        await exportPlayStoreToCSV(googlePlayApps, playCsvFilename, logToFile);
        logToFile(`  - ${playJsonFilename} (Google Play Store JSON)`);
        logToFile(`  - ${playCsvFilename} (Google Play Store CSV)`);
      }

      // Export combined files
      await exportCombinedToJSON(combinedApps, jsonFilename, logToFile);
      await exportCombinedToCSV(combinedApps, csvFilename, logToFile);

      logToFile("\n✅ scraping completed successfully!");
      logToFile("📄 Files created:");
      logToFile(`  - ${jsonFilename} (Combined JSON)`);
      logToFile(`  - ${csvFilename} (Combined CSV)`);
      logToFile(
        `\n🎯 Summary: Collected ${combinedApps.length} unique sports & fitness apps from both platforms`,
      );

      // Calculate and display actual time taken
      const endTime = Date.now();
      const endTimeFormatted = new Date().toISOString();
      const actualDurationMs = endTime - startTime;
      const actualDurationSeconds = Math.round(actualDurationMs / 1000);
      const actualDurationMinutes = Math.floor(actualDurationSeconds / 60);
      const actualDurationHours = Math.floor(actualDurationMinutes / 60);
      const remainingMinutes = actualDurationMinutes % 60;
      const remainingSeconds = actualDurationSeconds % 60;

      logToFile(`\n⏱️  ACTUAL TIME TAKEN:`);
      logToFile(`   🏁 Finished at: ${endTimeFormatted}`);
      logToFile(
        `   ⌛ Total duration: ${actualDurationHours}h ${remainingMinutes}m ${remainingSeconds}s`,
      );
      logToFile(`   📊 Performance: ${actualDurationMs}ms total`);

      // Save the log file
      await saveLogFile();
    }
  } catch (error) {
    logToFile(`❌ Fatal error in main execution: ${error.message}`);
    await saveLogFile();
  }
}

// Execute the main function
main().catch((error) => {
  console.error("Unhandled error:", error);
});
