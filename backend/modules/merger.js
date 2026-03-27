/**
 * Merger module.
 * Combines Apple and Google datasets.
 * Deduplication is handled upstream in scraper modules.
 */
export function combineApps(appStoreApps, googlePlayApps, logToFile) {
  logToFile("\n🔄 Combining apps (no deduplication in merger)...");

  const normalizePlatformFields = (apps, platformLabel) =>
    apps.map((app) => {
      const platform = app?.platform || platformLabel;
      return {
        ...app,
        platform,
        platforms: app?.platforms || [platform],
        availableOnBothPlatforms: app?.availableOnBothPlatforms || false,
        crossPlatformMethod: app?.crossPlatformMethod || null,
      };
    });

  const appleApps = normalizePlatformFields(appStoreApps, "Apple App Store");
  const googleApps = normalizePlatformFields(
    googlePlayApps,
    "Google Play Store",
  );

  const combinedApps = [...appleApps, ...googleApps];

  logToFile(`   📊 Merge summary (dedupe disabled in merger):`);
  logToFile(`   📱 Apple App Store input: ${appStoreApps.length}`);
  logToFile(`   📱 Apple kept: ${appleApps.length}`);
  logToFile(`   🤖 Google Play Store input: ${googlePlayApps.length}`);
  logToFile(`   🤖 Google kept: ${googleApps.length}`);
  logToFile("   🔁 Cross-platform entries are preserved as separate rows.");
  logToFile(`   🎯 Total combined apps: ${combinedApps.length}`);

  return combinedApps;
}
