from oxylabs import RealtimeClient
import sys

def scrape_wholesale_prices(query="wholesale bulk socks"):
    """
    Search Google Shopping for wholesale queries using Oxylabs RealtimeClient.
    """
    client = RealtimeClient(api_key="YOUR_OXYLABS_KEY_HERE")
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
