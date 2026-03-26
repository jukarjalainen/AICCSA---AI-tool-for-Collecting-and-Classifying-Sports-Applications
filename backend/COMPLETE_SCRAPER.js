/**
 * Entrypoint orchestrator for the full scraping pipeline.
 * Runs both store scrapers, merges/deduplicates results, exports files, and writes logs.
 */
import fs from "fs/promises";
import { spawn } from "child_process";
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
  exportCombinedToXLSX,
} from "./modules/exporters.js";

function parseBoolean(value, fallback = false) {
  if (value == null) return fallback;
  if (value === "") return true;
  return String(value).toLowerCase() === "true";
}

function normalizeStoreTarget(value) {
  const normalized = String(value || "both").toLowerCase();
  if (normalized === "google" || normalized === "google_play") {
    return "google_play";
  }
  if (normalized === "apple" || normalized === "app_store") {
    return "app_store";
  }
  if (normalized === "both") {
    return "both";
  }
  return "both";
}

function parseCliArgs() {
  const args = process.argv.slice(2);
  const parsed = {};

  for (const arg of args) {
    if (!arg.startsWith("--")) continue;
    const [key, ...rest] = arg.slice(2).split("=");
    parsed[key] = rest.join("=");
  }

  return parsed;
}

async function resolveSearchQueries(keywordsArg, useEssentialQueries) {
  if (useEssentialQueries) {
    return searchQueriesEssential;
  }

  if (!keywordsArg || keywordsArg.trim().length === 0) {
    return [];
  }

  const raw = keywordsArg.trim();

  if (raw.toLowerCase().endsWith(".txt")) {
    try {
      const content = await fs.readFile(raw, "utf-8");
      return content
        .split(/\r?\n/)
        .map((q) => q.trim())
        .filter((q) => q.length > 0);
    } catch {
      // Fall back to comma-separated parsing if file cannot be read.
    }
  }

  return raw
    .split(",")
    .map((q) => q.trim())
    .filter((q) => q.length > 0);
}

function normalizeCountries(countriesArg) {
  if (!countriesArg) {
    return countriesEssential;
  }

  const parsed = countriesArg
    .split(",")
    .map((c) => c.trim().toLowerCase())
    .filter((c) => c.length > 0);

  return parsed.length > 0 ? parsed : countriesEssential;
}

const cliArgs = parseCliArgs();
const targetStore = normalizeStoreTarget(cliArgs.store);
const useEssentialQueries = parseBoolean(
  cliArgs["use-essential-queries"],
  false,
);
const searchTopCollections = parseBoolean(
  cliArgs["search-top-collections"],
  false,
);
const scrapeOnly = parseBoolean(cliArgs["scrape-only"], false);
const selectedCountries = normalizeCountries(cliArgs.countries);
const selectedModel = cliArgs.model || "gpt-5-mini";
const apiKey = cliArgs["api-key"] || "";

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

function runOpenAIBatchClassifier({ inputFile, model, apiKey }) {
  return new Promise((resolve, reject) => {
    const args = [
      "-m",
      "backend.openAIBatchClassifier.src.main",
      `--input-file=${inputFile}`,
      `--model=${model}`,
    ];

    if (apiKey && apiKey.length > 0) {
      args.push(`--api-key=${apiKey}`);
    }

    logToFile("\n🤖 Starting OpenAI batch classification pipeline...");
    const child = spawn("python", args, {
      cwd: process.cwd(),
      env: {
        ...process.env,
        ...(apiKey && apiKey.length > 0 ? { OPENAI_API_KEY: apiKey } : {}),
      },
      stdio: ["ignore", "pipe", "pipe"],
    });

    child.stdout.on("data", (data) => {
      const lines = data.toString().split(/\r?\n/).filter(Boolean);
      for (const line of lines) {
        logToFile(`[openai-batch] ${line}`);
      }
    });

    child.stderr.on("data", (data) => {
      const lines = data.toString().split(/\r?\n/).filter(Boolean);
      for (const line of lines) {
        logToFile(`[openai-batch][stderr] ${line}`);
      }
    });

    child.on("error", (error) => {
      reject(
        new Error(`Failed to start Python batch classifier: ${error.message}`),
      );
    });

    child.on("close", (code) => {
      if (code === 0) {
        logToFile("✅ OpenAI batch classification completed successfully");
        resolve();
        return;
      }
      reject(new Error(`Python batch classifier exited with code ${code}`));
    });
  });
}

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from Apple App Store
 */
async function getAppStoreApps() {
  const searchQueries = await resolveSearchQueries(
    cliArgs.keywords || "",
    useEssentialQueries,
  );

  const scraper = new AppStoreScraper({
    countries: selectedCountries,
    searchQueries,
    logToFile,
    includeTopCollections: searchTopCollections,
  });
  return scraper.scrape();
}

/**
 * Get comprehensive list of SPORTS and HEALTH_AND_FITNESS apps from Google Play Store
 */
async function getGooglePlayApps() {
  const searchQueries = await resolveSearchQueries(
    cliArgs.keywords || "",
    useEssentialQueries,
  );

  const scraper = new GooglePlayScraper({
    countries: selectedCountries,
    searchQueries,
    logToFile,
    includeTopCollections: searchTopCollections,
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
  logToFile(`⚙️ Store target: ${targetStore}`);
  logToFile(`⚙️ Countries: ${selectedCountries.join(",")}`);
  logToFile(`⚙️ Use essential queries: ${useEssentialQueries}`);
  logToFile(`⚙️ Search top collections: ${searchTopCollections}`);
  logToFile(`⚙️ Scrape-only mode: ${scrapeOnly}`);
  logToFile(`⚙️ Model: ${selectedModel}`);
  logToFile(`⚙️ API key provided: ${apiKey.length > 0}`);

  try {
    // Scrape both platforms in parallel for better performance
    logToFile("\n📱 Starting parallel scraping of both platforms...");

    let appStoreApps = [];
    let googlePlayApps = [];

    if (targetStore === "both") {
      [appStoreApps, googlePlayApps] = await Promise.all([
        getAppStoreApps(),
        getGooglePlayApps(),
      ]);
    } else if (targetStore === "app_store") {
      appStoreApps = await getAppStoreApps();
    } else if (targetStore === "google_play") {
      googlePlayApps = await getGooglePlayApps();
    }

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
      const outputDir = "backend/output";
      await fs.mkdir(outputDir, { recursive: true });

      // Create timestamped filenames
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const jsonFilename = `${outputDir}/COMPLETE_sports_fitness_apps_${timestamp}.json`;
      const csvFilename = `${outputDir}/COMPLETE_sports_fitness_apps_${timestamp}.csv`;
      const xlsxFilename = `${outputDir}/COMPLETE_sports_fitness_apps_${timestamp}.xlsx`;
      // Apple only
      const appleJsonFilename = `${outputDir}/COMPLETE_appstore_sports_fitness_apps_${timestamp}.json`;
      const appleCsvFilename = `${outputDir}/COMPLETE_appstore_sports_fitness_apps_${timestamp}.csv`;
      // Google Play only
      const playJsonFilename = `${outputDir}/COMPLETE_playstore_sports_fitness_apps_${timestamp}.json`;
      const playCsvFilename = `${outputDir}/COMPLETE_playstore_sports_fitness_apps_${timestamp}.csv`;

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
      if (scrapeOnly) {
        await exportCombinedToXLSX(combinedApps, xlsxFilename, logToFile);
        await fs.copyFile(csvFilename, `${outputDir}/latest_scrape_output.csv`);
        await fs.copyFile(
          xlsxFilename,
          `${outputDir}/latest_scrape_output.xlsx`,
        );
      }

      if (!scrapeOnly) {
        await runOpenAIBatchClassifier({
          inputFile: csvFilename,
          model: selectedModel,
          apiKey,
        });
      } else {
        logToFile(
          "⏭️ Scrape-only mode enabled: skipping OpenAI batch classification.",
        );
      }

      logToFile("\n✅ scraping completed successfully!");
      logToFile("📄 Files created:");
      logToFile(`  - ${jsonFilename} (Combined JSON)`);
      logToFile(`  - ${csvFilename} (Combined CSV)`);
      if (scrapeOnly) {
        logToFile(`  - ${xlsxFilename} (Combined XLSX)`);
      }
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
