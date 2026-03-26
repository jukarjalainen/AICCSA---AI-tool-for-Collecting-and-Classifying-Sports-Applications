/**
 * Exporters module.
 * Writes platform-specific and combined scraping results to JSON and CSV formats.
 */
import fs from "fs/promises";

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
        developerInternalID: app.developerInternalID,
        genre: app.genre,
        genreId: app.genreId,
        categories: app.categories,
        previewVideo: app.previewVideo,
        contentRating: app.contentRating,
        adSupported: app.adSupported,
        released: app.released,
        updated: app.updated,
        version: app.version,
        preregister: app.preregister,
        earlyAccessEnabled: app.earlyAccessEnabled,
        isAvailableInPlayPass: app.isAvailableInPlayPass,
        editorsChoice: app.editorsChoice,
        appId: app.appId,
        // Existing cross-platform and source fields
        platform: app.platform,
        platforms: app.platforms || [app.platform],
        availableOnBothPlatforms: app.availableOnBothPlatforms || false,
        crossPlatformMethod: app.crossPlatformMethod || null,
        crossPlatformAppIds: app.crossPlatformAppIds || null,
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
      "categories",
      "contentRating",
      "adSupported",
      "released",
      "updated",
      "preregister",
      "earlyAccessEnabled",
      "isAvailableInPlayPass",
      "editorsChoice",
      "appId",
      // Existing cross-platform and source fields
      "platform",
      "platforms",
      "availableOnBothPlatforms",
      "crossPlatformMethod",
      "crossPlatformAppIds",
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
        Array.isArray(app.categories)
          ? app.categories.map((c) => `${c.name}:${c.id}`).join("; ")
          : app.categories || "",
        app.contentRating || "",
        app.adSupported ? "TRUE" : "FALSE",
        app.released || "",
        app.updated || "",
        app.preregister ? "TRUE" : "FALSE",
        app.earlyAccessEnabled ? "TRUE" : "FALSE",
        app.isAvailableInPlayPass ? "TRUE" : "FALSE",
        app.editorsChoice ? "TRUE" : "FALSE",
        app.appId || "",
        // Existing cross-platform and source fields
        app.platform || "",
        Array.isArray(app.platforms)
          ? app.platforms.join("; ")
          : app.platforms || "",
        app.availableOnBothPlatforms ? "TRUE" : "FALSE",
        app.crossPlatformMethod || "",
        Array.isArray(app.crossPlatformAppIds)
          ? app.crossPlatformAppIds.join("; ")
          : app.crossPlatformAppIds || "",
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
        categories: app.categories || "",
        adSupported: app.adSupported != null ? app.adSupported : "",
        preregister: app.preregister != null ? app.preregister : "",
        earlyAccessEnabled:
          app.earlyAccessEnabled != null ? app.earlyAccessEnabled : "",
        isAvailableInPlayPass:
          app.isAvailableInPlayPass != null ? app.isAvailableInPlayPass : "",
        editorsChoice: app.editorsChoice != null ? app.editorsChoice : "",
        // Existing cross-platform and source fields
        platform: app.platform || "",
        platforms: app.platforms || [app.platform],
        availableOnBothPlatforms: app.availableOnBothPlatforms || false,
        crossPlatformMethod: app.crossPlatformMethod || null,
        crossPlatformAppIds: app.crossPlatformAppIds || null,
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
    // Superset schema: all App Store and Play Store fields
    const headers = [
      // App Store fields
      "id",
      "appId",
      "title",
      "genres",
      "genreIds",
      "primaryGenre",
      "primaryGenreId",
      "contentRating",
      "languages",
      "size",
      "requiredOsVersion",
      "released",
      "updated",
      "price",
      "currency",
      "free",
      "developerId",
      "developer",
      "score",
      "reviews",
      "currentVersionScore",
      "currentVersionReviews",
      "supportedDevices",
      // Play Store fields
      "installs",
      "minInstalls",
      "maxInstalls",
      "ratings",
      "histogram_1",
      "histogram_2",
      "histogram_3",
      "histogram_4",
      "histogram_5",
      "priceText",
      "offersIAP",
      "IAPRange",
      "androidVersion",
      "androidMaxVersion",
      "developerInternalID",
      "genre",
      "genreId",
      "categories",
      "adSupported",
      "preregister",
      "earlyAccessEnabled",
      "isAvailableInPlayPass",
      "editorsChoice",
      // Existing cross-platform and source fields
      "platform",
      "platforms",
      "availableOnBothPlatforms",
      "crossPlatformMethod",
      "crossPlatformAppIds",
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
        // App Store fields
        app.id || "",
        app.appId || "",
        (app.title || "").replace(/"/g, '""'),
        Array.isArray(app.genres) ? app.genres.join("; ") : app.genres || "",
        Array.isArray(app.genreIds)
          ? app.genreIds.join("; ")
          : app.genreIds || "",
        app.primaryGenre || "",
        app.primaryGenreId || "",
        app.contentRating || "",
        Array.isArray(app.languages)
          ? app.languages.join("; ")
          : app.languages || "",
        app.size || "",
        app.requiredOsVersion || "",
        app.released || "",
        app.updated || "",
        app.price || "",
        app.currency || "",
        app.free ? "TRUE" : "FALSE",
        app.developerId || "",
        (app.developer || "").replace(/"/g, '""'),
        app.score || "",
        app.reviews || "",
        app.currentVersionScore || "",
        app.currentVersionReviews || "",
        Array.isArray(app.supportedDevices)
          ? app.supportedDevices.join("; ")
          : app.supportedDevices || "",
        // Play Store fields
        app.installs || "",
        app.minInstalls || "",
        app.maxInstalls || "",
        app.ratings || "",
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
        app.priceText || "",
        app.offersIAP ? "TRUE" : "FALSE",
        app.IAPRange || "",
        app.androidVersion || "",
        app.androidMaxVersion || "",
        app.developerInternalID || "",
        app.genre || "",
        app.genreId || "",
        Array.isArray(app.categories)
          ? app.categories.map((c) => `${c.name}:${c.id}`).join("; ")
          : app.categories || "",
        app.adSupported ? "TRUE" : "FALSE",
        app.preregister ? "TRUE" : "FALSE",
        app.earlyAccessEnabled ? "TRUE" : "FALSE",
        app.isAvailableInPlayPass ? "TRUE" : "FALSE",
        app.editorsChoice ? "TRUE" : "FALSE",
        // Existing cross-platform and source fields
        app.platform || "",
        Array.isArray(app.platforms)
          ? app.platforms.join("; ")
          : app.platforms || "",
        app.availableOnBothPlatforms ? "TRUE" : "FALSE",
        app.crossPlatformMethod || "",
        Array.isArray(app.crossPlatformAppIds)
          ? app.crossPlatformAppIds.join("; ")
          : app.crossPlatformAppIds || "",
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
    logToFile(`📊 Enhanced CSV data exported to ${filename}`);
  } catch (error) {
    logToFile(`Failed to export combined CSV: ${error.message}`);
  }
}
