import test from "node:test";
import assert from "node:assert/strict";
import gplay from "google-play-scraper";
import { GooglePlayScraper } from "./GooglePlayScraper.js";

test(
  "GooglePlayScraper returns expected Google Play fields for 'padel' search in one country",
  { timeout: 180000 },
  async () => {
    const originalSearch = gplay.search;

    gplay.search = async ({ term, country }) => {
      assert.equal(term, "padel");
      assert.equal(country, "es");

      return [
        {
          title: "Padel Pro Trainer",
          installs: "10,000+",
          minInstalls: 10000,
          maxInstalls: 50000,
          score: 4.6,
          scoreText: "4.6",
          ratings: 1200,
          reviews: 320,
          histogram: { 1: 10, 2: 20, 3: 50, 4: 200, 5: 920 },
          price: 0,
          free: true,
          currency: "USD",
          priceText: "Free",
          offersIAP: false,
          IAPRange: "",
          androidVersion: "8.0",
          androidMaxVersion: "",
          developer: "Padel Labs",
          developerId: "padel.labs",
          developerInternalID: "dev123",
          genre: "Sports",
          genreId: "SPORTS",
          categories: [{ name: "Sports", id: "SPORTS" }],
          previewVideo: "",
          contentRating: "Everyone",
          adSupported: false,
          released: "2023-01-01",
          updated: "2026-03-01",
          version: "1.2.0",
          preregister: false,
          earlyAccessEnabled: false,
          isAvailableInPlayPass: false,
          editorsChoice: false,
          appId: "com.padel.pro",
        },
      ];
    };

    const scraper = new GooglePlayScraper({
      countries: ["es"],
      searchQueries: ["padel"],
      logToFile: () => {},
      includeTopCollections: false,
    });

    let apps = [];
    try {
      apps = await scraper.scrape();
    } finally {
      gplay.search = originalSearch;
    }

    assert.ok(Array.isArray(apps), "scrape() should return an array");
    assert.ok(
      apps.length > 0,
      "Expected at least one app result for country=es and query='padel'",
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
        `Expected field '${field}' to exist on app object`,
      );
    }

    assert.equal(app.platform, "Google Play Store");
    assert.equal(app.sourceMethod, "search");
    assert.equal(app.sourceCountry, "es");
    assert.equal(app.searchQuery, "padel");
  },
);
