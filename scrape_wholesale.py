from oxylabs import RealtimeClient
import sys
import os

def scrape_wholesale_prices(query="wholesale bulk socks"):
    """
    Search Google Shopping for wholesale queries using Oxylabs RealtimeClient.
    """
    username = os.environ.get("OXYLABS_USERNAME", "YOUR_OXYLABS_USERNAME_HERE")
    password = os.environ.get("OXYLABS_PASSWORD", "YOUR_OXYLABS_PASSWORD_HERE")
    client = RealtimeClient(username=username, password=password)
    try:
        response = client.scrape_search(
            source="google_shopping",
            query=query,
            domain="com",
            locale="en_us",
            parse=True
        )
        
        results = []
        for item in response.get("results", {}).get("organic", []):
            title = item.get("title", "No Title")
            price = item.get("price", "N/A")
            seller = item.get("seller_name", "Unknown")
            print(f"[{seller}] {title} - {price}")
            results.append({"title": title, "price": price, "seller": seller})
            
        return results
    except Exception as e:
        print(f"Error scraping '{query}': {e}")
        return []

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "wholesale bulk ceramic mugs"
    scrape_wholesale_prices(query)
