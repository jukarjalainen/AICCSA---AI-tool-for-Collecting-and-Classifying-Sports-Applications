import gplay from "google-play-scraper";

/**
 * Create a list of apps from a given category
 * 
 * @param {string} category - The category to search for apps (e.g., 'GAME', 'BUSINESS', 'EDUCATION')
 * @param {number} numApps - Number of apps to retrieve (default: 10)
 * @returns {Promise<Array>} Promise that resolves to an array of app objects
 */
async function listAppsByCategory(category = 'GAME', numApps = 10) {
    // Category-specific search queries to improve results
    const categoryQueries = {
        'GAME': 'game',
        'BUSINESS': 'business productivity',
        'EDUCATION': 'education learning',
        'SOCIAL': 'social media',
        'ENTERTAINMENT': 'entertainment video',
        'HEALTH_AND_FITNESS': 'health fitness',
        'LIFESTYLE': 'lifestyle',
        'MUSIC_AND_AUDIO': 'music audio',
        'NEWS_AND_MAGAZINES': 'news magazine',
        'PHOTOGRAPHY': 'photo camera',
        'SHOPPING': 'shopping',
        'SPORTS': 'sports',
        'TOOLS': 'tools utility',
        'TRAVEL_AND_LOCAL': 'travel maps',
        'WEATHER': 'weather'
    };

    try {
        // Use category-specific query if available, otherwise use the category name
        const query = categoryQueries[category.toUpperCase()] || category.toLowerCase();
        
        // Search for apps in the specified category
        const apps = await gplay.search({
            term: query,
            lang: "en",     // Language
            country: "us",  // Country
            num: numApps    // Number of results
        });

        // Extract and structure app information
        const appList = apps.map(app => ({
            title: app.title || 'N/A',
            appId: app.appId || 'N/A',
            developer: app.developer || 'N/A',
            rating: app.score || 'N/A',
            installs: app.installs || 'N/A',
            free: app.free || false,
            category: app.genre || 'N/A',
            url: app.url || 'N/A'
        }));

        return appList;
        
    } catch (error) {
        console.error(`Error fetching apps: ${error.message}`);
        return [];
    }
}

/**
 * Print the list of apps in a formatted way
 * 
 * @param {Array} apps - Array of app objects
 */
function printApps(apps) {
    if (!apps || apps.length === 0) {
        console.log("No apps found.");
        return;
    }

    console.log(`\nFound ${apps.length} apps:`);
    console.log("=".repeat(80));

    apps.forEach((app, index) => {
        console.log(`\n${index + 1}. ${app.title}`);
        console.log(`   📱 Package: ${app.appId}`);
        console.log(`   👩‍💻 Developer: ${app.developer}`);
        console.log(`   ⭐ Rating: ${app.rating}`);
        console.log(`   📥 Installs: ${app.installs}`);
        console.log(`   💰 Free: ${app.free ? 'Yes' : 'No'}`);
        console.log(`   📂 Category: ${app.category}`);
        console.log("-".repeat(80));
    });
}

// Example usage
async function main() {
    try {
        console.log("Scraping apps...");
        const gameApps = await listAppsByCategory('SPORTS', 50);
        printApps(gameApps);

    } catch (error) {
        console.error("Error in main function:", error);
    }
}

// Run the example if this file is executed directly
main();
