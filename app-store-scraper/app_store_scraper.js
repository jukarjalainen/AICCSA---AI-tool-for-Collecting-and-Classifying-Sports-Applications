import store from "app-store-scraper";
import gplay from "google-play-scraper";

store
  .app({ appId: "com.espn.fantasyFootball", country: "us", lang: "en" })
  .then(({ description }) => console.log(description))
  .catch(console.error);

gplay
  .app({
    appId: "com.yahoo.mobile.client.android.fantasyfootball",
    country: "us",
    lang: "en",
  })
  .then(({ description }) => console.log(description))
  .catch(console.error);

// --- Apple Lookup API example (prints description) ---
async function appleLookupDescription(appIdOrBundle, country = "us") {
  const params = new URLSearchParams({ country });
  if (/^\d+$/.test(String(appIdOrBundle))) {
    params.set("id", String(appIdOrBundle));
  } else {
    params.set("bundleId", String(appIdOrBundle));
  }
  const url = `https://itunes.apple.com/lookup?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Lookup failed ${res.status}`);
  const data = await res.json();
  const item = data?.results?.[0];
  return item?.description || item?.releaseNotes || "";
}

appleLookupDescription("com.espn.fantasyFootball", "us")
  .then((desc) => console.log(desc))
  .catch(console.error);
