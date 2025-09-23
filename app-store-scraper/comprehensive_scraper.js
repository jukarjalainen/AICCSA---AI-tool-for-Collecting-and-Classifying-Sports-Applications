import store from 'app-store-scraper';

// Combined strategy: Collections + Search queries for maximum coverage
const collections = [
  store.collection.TOP_FREE_IOS,
  store.collection.TOP_PAID_IOS, 
  store.collection.TOP_GROSSING_IOS,
  store.collection.TOP_FREE_IPAD,
  store.collection.TOP_PAID_IPAD,
  store.collection.TOP_GROSSING_IPAD
];

const searchQueries = [
  'football', 'soccer', 'basketball', 'tennis', 'golf', 'baseball',
  'running', 'fitness', 'workout', 'sports', 'hockey', 'volleyball',
  'swimming', 'cycling', 'marathon', 'gym', 'training'
];

const countries = ['us', 'gb', 'ca', 'au', 'de'];

async function comprehensiveScrape() {
  const allApps = [];
  const seenIds = new Set();
  
  // Step 1: Get apps from collections
  console.log('🔄 Phase 1: Scraping from collections...');
  for (const collection of collections) {
    try {
      const collectionName = Object.keys(store.collection).find(key => store.collection[key] === collection);
      console.log(`📱 ${collectionName}`);
      
      const apps = await store.list({
        collection: collection,
        category: store.category.SPORTS,
        num: 200
      });
      
      let newApps = 0;
      apps.forEach(app => {
        if (!seenIds.has(app.id)) {
          allApps.push({
            ...app,
            sourceMethod: 'collection',
            sourceCollection: collectionName
          });
          seenIds.add(app.id);
          newApps++;
        }
      });
      
      console.log(`  ✅ ${newApps} new apps, total: ${allApps.length}`);
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      console.error(`❌ Collection error:`, error.message);
    }
  }
  
  // Step 2: Search for additional apps
  console.log('\n🔍 Phase 2: Searching for additional apps...');
  for (const query of searchQueries) {
    for (const country of countries) {
      try {
        console.log(`🔍 Searching "${query}" in ${country.toUpperCase()}`);
        
        const apps = await store.search({
          term: query,
          country: country,
          num: 200 // Maximum per search
        });
        
        // Filter for sports apps only
        const sportsApps = apps.filter(app => 
          app.genre && (
            app.genre.toLowerCase().includes('sports') ||
            app.genre.toLowerCase().includes('health') ||
            app.genre.toLowerCase().includes('fitness')
          )
        );
        
        let newApps = 0;
        sportsApps.forEach(app => {
          if (!seenIds.has(app.id)) {
            allApps.push({
              ...app,
              sourceMethod: 'search',
              searchQuery: query,
              sourceCountry: country
            });
            seenIds.add(app.id);
            newApps++;
          }
        });
        
        console.log(`  ✅ ${newApps} new sports apps, total: ${allApps.length}`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        console.error(`❌ Search error for "${query}" in ${country}:`, error.message);
      }
    }
  }
  
  console.log(`\n🎯 COMPREHENSIVE RESULT: ${allApps.length} unique sports apps collected`);
  
  // Show breakdown
  const collectionApps = allApps.filter(app => app.sourceMethod === 'collection').length;
  const searchApps = allApps.filter(app => app.sourceMethod === 'search').length;
  console.log(`📊 Breakdown: ${collectionApps} from collections, ${searchApps} from search`);
  
  return allApps;
}

comprehensiveScrape()
  .then(apps => {
    console.log('\nSample results:');
    apps.slice(0, 5).forEach(app => {
      console.log(`- ${app.title} (${app.sourceMethod})`);
    });
  })
  .catch(console.error);
