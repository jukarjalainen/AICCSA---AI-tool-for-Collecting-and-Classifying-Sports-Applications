import store from 'app-store-scraper';

// Maximum coverage strategy: Multiple collections + Multiple countries
const collections = [
  store.collection.TOP_FREE_IOS,
  store.collection.TOP_PAID_IOS, 
  store.collection.TOP_GROSSING_IOS,
  store.collection.TOP_FREE_IPAD,
  store.collection.TOP_PAID_IPAD,
  store.collection.TOP_GROSSING_IPAD,
  store.collection.NEW_IOS,
  store.collection.NEW_FREE_IOS,
  store.collection.NEW_PAID_IOS
];

const countries = [
  'us', 'gb', 'ca', 'au', 'de', 'fr', 'it', 'es', 'jp', 'kr'
];

async function scrapeMaximumApps() {
  const allApps = [];
  const seenIds = new Set();
  
  for (const country of countries) {
    console.log(`\n🌍 Scraping country: ${country.toUpperCase()}`);
    
    for (const collection of collections) {
      try {
        const collectionName = Object.keys(store.collection).find(key => store.collection[key] === collection);
        console.log(`  📱 Collection: ${collectionName}`);
        
        const apps = await store.list({
          collection: collection,
          category: store.category.SPORTS, // Change to your desired category
          country: country,
          num: 200 // Maximum per collection
        });
        
        // Add only unique apps
        let newApps = 0;
        apps.forEach(app => {
          if (!seenIds.has(app.id)) {
            allApps.push({
              ...app,
              sourceCountry: country,
              sourceCollection: collectionName
            });
            seenIds.add(app.id);
            newApps++;
          }
        });
        
        console.log(`    ✅ Found ${apps.length} apps, ${newApps} new, total unique: ${allApps.length}`);
        
        // Pause between requests to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1500));
        
      } catch (error) {
        console.error(`    ❌ Error with ${collection} in ${country}:`, error.message);
        // Continue with next collection even if one fails
      }
    }
  }
  
  console.log(`\n🎯 FINAL RESULT: ${allApps.length} unique apps collected`);
  return allApps;
}

scrapeMaximumApps()
  .then(apps => {
    console.log('Sample apps:', apps.slice(0, 3));
  })
  .catch(console.error);
