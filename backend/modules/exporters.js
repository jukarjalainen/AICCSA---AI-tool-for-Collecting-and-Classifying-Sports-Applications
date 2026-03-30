/**
 * Exporters module.
 * Writes platform-specific and combined scraping results to JSON and CSV formats.
 */
import fs from "fs/promises";
import XLSX from "xlsx";

const OUTPUT_COLUMNS = [
  "appleId",
  "appId",
  "title",
  "url",
  "platform",
  "sourceCountry",
  "sourceMethod",
  "searchQuery",
  "targetCategory",
  "genre",
  "genreId",
  "primaryGenre",
  "primaryGenreId",
  "developer",
  "developerId",
  "installs",
  "minInstalls",
  "maxInstalls",
  "score",
  "scoreText",
  "ratings",
  "reviews",
  "price",
  "currency",
  "priceText",
  "free",
  "offersIAP",
  "IAPRange",
  "androidVersion",
  "androidMaxVersion",
  "contentRating",
  "released",
  "updated",
  "is_relevant",
  "purpose",
  "stakeholder",
  "sport_type",
];

const XLSX_SCHEMA_COLUMNS = [
  "appleId",
  "App_ID",
  "App_Name",
  "url",
  "Is_relevant",
  "Purpose",
  "Stakeholder",
  "Sport_Type",
  "searchQuery",
  "Platform",
  "score",
  "reviews",
  "genreIds_appStore",
  "primaryGenre_appStore",
  "primaryGenreId",
  "genre_playStore",
  "genreId_playStore",
  "contentRating",
  "released",
  "updated",
  "price",
  "currency",
  "free",
  "ratings",
  "developer",
  "developerId",
  "sourceMethod",
  "sourceCollection",
  "targetCategory",
  "sourceCountry",
];

function buildOutputRow(app) {
  const resolvedId = app.id || app.appId || "";
  return {
    appleId: app.id || "",
    appId: app.appId || resolvedId,
    title: app.title || "",
    url: app.url || "",
    platform: app.platform || "",
    sourceCountry: app.sourceCountry || "",
    sourceMethod: app.sourceMethod || "",
    searchQuery: app.searchQuery || "",
    targetCategory: app.targetCategory || "",
    genre: app.genre || "",
    genreId: app.genreId || "",
    primaryGenre: app.primaryGenre || "",
    primaryGenreId: app.primaryGenreId || "",
    developer: app.developer || "",
    developerId: app.developerId || "",
    installs: app.installs || "",
    minInstalls: app.minInstalls || "",
    maxInstalls: app.maxInstalls || "",
    score: app.score || "",
    scoreText: app.scoreText || "",
    ratings: app.ratings || "",
    reviews: app.reviews || "",
    price: app.price || "",
    currency: app.currency || "",
    priceText: app.priceText || "",
    free: app.free ? "TRUE" : "FALSE",
    offersIAP: app.offersIAP ? "TRUE" : "FALSE",
    IAPRange: app.IAPRange || "",
    androidVersion: app.androidVersion || "",
    androidMaxVersion: app.androidMaxVersion || "",
    contentRating: app.contentRating || "",
    released: app.released || "",
    updated: app.updated || "",

    // Filled during OpenAIBatchClassifier phase
    is_relevant: app.is_relevant ?? "",
    purpose: app.purpose ?? "",
    stakeholder: app.stakeholder ?? "",
    sport_type: app.sport_type ?? "",
  };
}

function buildSchemaXlsxRow(app) {
  const platform = app.platform || "";

  return {
    appleId: app.id || "",
    App_ID: app.appId || "",
    App_Name: app.title || "",
    url: app.url || "",
    Is_relevant: app.is_relevant ?? "",
    Purpose: app.purpose ?? "",
    Stakeholder: app.stakeholder ?? "",
    Sport_Type: app.sport_type ?? "",
    searchQuery: app.searchQuery || "",
    Platform: platform,
    score: app.score || "",
    reviews: app.reviews || "",
    genreIds_appStore: app.genreIds || "",
    primaryGenre_appStore: app.primaryGenre || "",
    primaryGenreId: app.primaryGenreId || "",
    genre_playStore: app.genre || "",
    genreId_playStore: app.genreId || "",
    contentRating: app.contentRating || "",
    released: app.released || "",
    updated: app.updated || "",
    price: app.price || "",
    currency: app.currency || "",
    free: app.free != null ? (app.free ? "TRUE" : "FALSE") : "",
    ratings: app.ratings || "",
    developer: app.developer || "",
    developerId: app.developerId || "",
    sourceMethod: app.sourceMethod || "",
    sourceCollection: app.sourceCollection || "",
    targetCategory: app.targetCategory || "",
    sourceCountry: app.sourceCountry || "",
  };
}

// Play Store-specific JSON export with all available fields
export async function exportPlayStoreToJSON(apps, filename, logToFile) {
  try {
    const exportData = {
      exportInfo: {
        platform: "Google Play Store",
        exportDate: new Date().toISOString(),
        totalApps: apps.length,
      },
      apps: apps.map((app) => ({
        title: app.title,
        url: app.url,
        installs: app.installs,
        minInstalls: app.minInstalls,
        maxInstalls: app.maxInstalls,
        score: app.score,
        scoreText: app.scoreText,
        ratings: app.ratings,
        reviews: app.reviews,
        histogram: app.histogram,
        price: app.price,
        free: app.free,
        currency: app.currency,
        priceText: app.priceText,
        offersIAP: app.offersIAP,
        IAPRange: app.IAPRange,
        androidVersion: app.androidVersion,
        androidMaxVersion: app.androidMaxVersion,
        developer: app.developer,
        developerId: app.developerId,
        genre: app.genre,
        genreId: app.genreId,
        previewVideo: app.previewVideo,
        contentRating: app.contentRating,
        adSupported: app.adSupported,
        released: app.released,
        updated: app.updated,
        preregister: app.preregister,
        earlyAccessEnabled: app.earlyAccessEnabled,
        isAvailableInPlayPass: app.isAvailableInPlayPass,
        editorsChoice: app.editorsChoice,
        appId: app.appId,
        // Existing source fields
        sourceMethod: app.sourceMethod,
        sourceCollection: app.sourceCollection || null,
        sourceCountry: app.sourceCountry || null,
        searchQuery: app.searchQuery || null,
        subCategory: app.subCategory || app.searchQuery || null,
        targetCategory: app.targetCategory,
      })),
    };
    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    logToFile(`\n📁 Play Store JSON data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export Play Store JSON: ${error.message}`);
  }
}

// Play Store-specific CSV export with all available fields
export async function exportPlayStoreToCSV(apps, filename, logToFile) {
  try {
    const headers = [
      "title",
      "url",
      "installs",
      "minInstalls",
      "maxInstalls",
      "score",
      "scoreText",
      "ratings",
      "reviews",
      "histogram_1",
      "histogram_2",
      "histogram_3",
      "histogram_4",
      "histogram_5",
      "price",
      "free",
      "currency",
      "priceText",
      "offersIAP",
      "IAPRange",
      "androidVersion",
      "androidMaxVersion",
      "developer",
      "developerId",
      "developerInternalID",
      "genre",
      "genreId",
      "contentRating",
      "adSupported",
      "released",
      "updated",
      "preregister",
      "earlyAccessEnabled",
      "isAvailableInPlayPass",
      "editorsChoice",
      "appId",
      // Existing source fields
      "sourceMethod",
      "sourceCollection",
      "sourceCountry",
      "searchQuery",
      "subCategory",
      "targetCategory",
    ];
    const csvRows = [headers.join(",")];
    apps.forEach((app) => {
      const row = [
        (app.title || "").replace(/"/g, '""'),
        app.url || "",
        app.installs || "",
        app.minInstalls || "",
        app.maxInstalls || "",
        app.score || "",
        app.scoreText || "",
        app.ratings || "",
        app.reviews || "",
        app.histogram && app.histogram["1"] !== undefined
          ? app.histogram["1"]
          : "",
        app.histogram && app.histogram["2"] !== undefined
          ? app.histogram["2"]
          : "",
        app.histogram && app.histogram["3"] !== undefined
          ? app.histogram["3"]
          : "",
        app.histogram && app.histogram["4"] !== undefined
          ? app.histogram["4"]
          : "",
        app.histogram && app.histogram["5"] !== undefined
          ? app.histogram["5"]
          : "",
        app.price || "",
        app.free ? "TRUE" : "FALSE",
        app.currency || "",
        app.priceText || "",
        app.offersIAP ? "TRUE" : "FALSE",
        app.IAPRange || "",
        app.androidVersion || "",
        app.androidMaxVersion || "",
        (app.developer || "").replace(/"/g, '""'),
        app.developerId || "",
        app.developerInternalID || "",
        app.genre || "",
        app.genreId || "",
        app.contentRating || "",
        app.adSupported ? "TRUE" : "FALSE",
        app.released || "",
        app.updated || "",
        app.preregister ? "TRUE" : "FALSE",
        app.earlyAccessEnabled ? "TRUE" : "FALSE",
        app.isAvailableInPlayPass ? "TRUE" : "FALSE",
        app.editorsChoice ? "TRUE" : "FALSE",
        app.appId || "",
        // Existing source fields
        app.sourceMethod || "",
        app.sourceCollection || "",
        app.sourceCountry || "",
        app.searchQuery || "",
        app.subCategory || app.searchQuery || "",
        app.targetCategory || "",
      ]
        .map((field) => `"${field}"`)
        .join(",");
      csvRows.push(row);
    });
    await fs.writeFile(filename, csvRows.join("\n"));
    logToFile(`📊 Play Store CSV data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export Play Store CSV: ${error.message}`);
  }
}

/**
 * Export combined apps data to JSON file
 */
export async function exportCombinedToJSON(apps, filename, logToFile) {
  try {
    // Superset schema: all App Store and Play Store fields
    const exportData = {
      exportInfo: {
        platforms: ["Apple App Store", "Google Play Store"],
        exportDate: new Date().toISOString(),
        totalApps: apps.length,
        searchScope: "Global - Multiple Countries and Platforms",
        categoriesSearched: ["SPORTS", "HEALTH_AND_FITNESS"],
        deduplicationMethod: "appId and title matching across platforms",
      },
      apps: apps.map((app) => ({
        // App Store fields
        id: app.id || "",
        appId: app.appId || "",
        title: app.title || "",
        url: app.url || "",
        genres: app.genres || "",
        genreIds: app.genreIds || "",
        primaryGenre: app.primaryGenre || "",
        primaryGenreId: app.primaryGenreId || "",
        contentRating: app.contentRating || "",
        languages: app.languages || "",
        size: app.size || "",
        requiredOsVersion: app.requiredOsVersion || "",
        released: app.released || "",
        updated: app.updated || "",
        price: app.price || "",
        currency: app.currency || "",
        free: app.free != null ? app.free : "",
        developerId: app.developerId || "",
        developer: app.developer || "",
        score: app.score || "",
        reviews: app.reviews || "",
        currentVersionScore: app.currentVersionScore || "",
        currentVersionReviews: app.currentVersionReviews || "",
        supportedDevices: app.supportedDevices || "",
        // Play Store fields

        installs: app.installs || "",
        minInstalls: app.minInstalls || "",
        maxInstalls: app.maxInstalls || "",
        ratings: app.ratings || "",
        histogram: app.histogram || "",
        priceText: app.priceText || "",
        offersIAP: app.offersIAP != null ? app.offersIAP : "",
        IAPRange: app.IAPRange || "",
        androidVersion: app.androidVersion || "",
        androidMaxVersion: app.androidMaxVersion || "",
        developerInternalID: app.developerInternalID || "",
        genre: app.genre || "",
        genreId: app.genreId || "",
        adSupported: app.adSupported != null ? app.adSupported : "",
        preregister: app.preregister != null ? app.preregister : "",
        earlyAccessEnabled:
          app.earlyAccessEnabled != null ? app.earlyAccessEnabled : "",
        isAvailableInPlayPass:
          app.isAvailableInPlayPass != null ? app.isAvailableInPlayPass : "",
        editorsChoice: app.editorsChoice != null ? app.editorsChoice : "",
        // Existing source fields
        sourceMethod: app.sourceMethod || "",
        sourceCollection: app.sourceCollection || "",
        sourceCountry: app.sourceCountry || "",
        searchQuery: app.searchQuery || "",
        subCategory: app.subCategory || app.searchQuery || "",
        targetCategory: app.targetCategory || "",
      })),
    };
    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    logToFile(`\n📁 Combined JSON data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export combined JSON: ${error.message}`);
  }
}

/**
 * Export combined apps data to CSV file
 */
export async function exportCombinedToCSV(apps, filename, logToFile) {
  try {
    const csvRows = [OUTPUT_COLUMNS.join(",")];
    apps.forEach((app) => {
      const rowObj = buildOutputRow(app);
      const row = OUTPUT_COLUMNS.map((column) => {
        const field = String(rowObj[column] ?? "").replace(/"/g, '""');
        return `"${field}"`;
      }).join(",");
      csvRows.push(row);
    });

    await fs.writeFile(filename, csvRows.join("\n"));
    logToFile(`📊 Enhanced CSV data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export combined CSV: ${error.message}`);
  }
}

/**
 * Export combined apps data to XLSX file.
 */
export async function exportCombinedToXLSX(apps, filename, logToFile) {
  try {
    const dataRows = apps.map((app) => {
      const rowObj = buildSchemaXlsxRow(app);
      return XLSX_SCHEMA_COLUMNS.map((column) => rowObj[column] ?? "");
    });
    const worksheetData = [XLSX_SCHEMA_COLUMNS, ...dataRows];

    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    XLSX.utils.book_append_sheet(workbook, worksheet, "Apps");
    XLSX.writeFile(workbook, filename);
    logToFile(`📗 Combined XLSX data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export combined XLSX: ${error.message}`);
  }
}
