# Google Play Store scraper using google_play_scraper package
from google_play_scraper import search, app

# Google Play Store scraper using google_play_scraper package
from google_play_scraper import search, app

def list_apps_by_category(category='SPORTS', num_apps=10):
    """
    Create a list of apps from a given category
    
    Args:
        category (str): The category to search for apps (e.g., 'GAME', 'BUSINESS', 'EDUCATION', 'SOCIAL', 'ENTERTAINMENT')
        num_apps (int): Number of apps to retrieve (default: 10)
    
    Returns:
        list: List of app dictionaries containing app information
    """
    
    # Category-specific search queries to improve results
    category_queries = {
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
    }
    
    try:
        # Use category-specific query if available, otherwise use the category name
        query = category_queries.get(category.upper(), category.lower())
        
        # Search for apps in the specified category
        apps = search(
            query=query,
            lang="en",  # Language
            country="us",  # Country
            n_hits=num_apps  # Number of results
        )
        
        app_list = []
        
        for app in apps:
            app_info = {
                'title': app.get('title', 'N/A'),
                'appId': app.get('appId', 'N/A'),
                'developer': app.get('developer', 'N/A'),
                'rating': app.get('score', 'N/A'),
                'installs': app.get('installs', 'N/A'),
                'free': app.get('free', 'N/A'),
                'category': app.get('genre', 'N/A')
            }
            app_list.append(app_info)
        
        return app_list
        
    except Exception as e:
        print(f"Error fetching apps: {e}")
        return []

def print_apps(apps):
    """
    Print the list of apps in a formatted way
    
    Args:
        apps (list): List of app dictionaries
    """
    if not apps:
        print("No apps found.")
        return
    
    print(f"\nFound {len(apps)} apps:")
    print("-" * 60)
    
    for i, app in enumerate(apps, 1):
        print(f"{i}. {app['title']}")
        print(f"   Package: {app['appId']}")
        print(f"   Developer: {app['developer']}")
        print(f"   Rating: {app['rating']}")
        print(f"   Installs: {app['installs']}")
        print(f"   Free: {app['free']}")
        print(f"   Category: {app['category']}")
        print("-" * 60)

# Example usage
if __name__ == "__main__":
    # Get a list of apps
    apps = list_apps_by_category(category='SPORTS', num_apps=200)
    
    # Print the apps
    print_apps(apps)