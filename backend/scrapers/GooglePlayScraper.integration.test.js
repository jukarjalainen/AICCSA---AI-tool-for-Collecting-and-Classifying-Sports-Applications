import test from "node:test";
import assert from "node:assert/strict";
import { GooglePlayScraper } from "./GooglePlayScraper.js";

const runIntegration = process.env.RUN_SCRAPER_INTEGRATION === "1";

test(
  "INTEGRATION: GooglePlayScraper fetches live padel results for one country",
  {
    timeout: 240000,
    skip:
      !runIntegration &&
      "Set RUN_SCRAPER_INTEGRATION=1 to run live network integration tests.",
  },
  async () => {
    const scraper = new GooglePlayScraper({
      countries: ["es"],
      searchQueries: ["padel"],
      logToFile: () => {},
      includeTopCollections: false,
    });

    const apps = await scraper.scrape();

    assert.ok(Array.isArray(apps), "scrape() should return an array");
    assert.ok(
      apps.length > 0,
      "Expected at least one live app result for country=es and query='padel'",
    );

    const app = apps[0];
    const expectedFields = [
      "title",
      "installs",
      "minInstalls",
      "maxInstalls",
      "score",
      "scoreText",
      "ratings",
      "reviews",
      "histogram",
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
      "previewVideo",
      "contentRating",
      "adSupported",
      "released",
      "updated",
      "version",
      "preregister",
      "earlyAccessEnabled",
      "isAvailableInPlayPass",
      "editorsChoice",
      "appId",
    ];

    for (const field of expectedFields) {
      assert.ok(
        field in app,
        `Expected field '${field}' to exist on live app object`,
      );
    }

    assert.equal(app.platform, "Google Play Store");
    assert.equal(app.sourceMethod, "search");
    assert.equal(app.sourceCountry, "es");
    assert.equal(app.searchQuery, "padel");
  },
);
