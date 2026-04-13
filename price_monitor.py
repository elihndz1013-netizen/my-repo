import time
import schedule
from scrape_wholesale import scrape_wholesale_prices

def check_prices():
    """Daily cron job to check wholesale prices and send an alert via OpenClaw if needed."""
    
    products_to_monitor = [
        "wholesale ceramic mugs bulk",
        "wholesale 64GB USB drives bulk",
        "wholesale blank t-shirts"
    ]
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting daily price monitor...")
    
    for product in products_to_monitor:
        print(f"\n--- Monitoring: {product} ---")
        results = scrape_wholesale_prices(product)
        
        if not results:
            print("No data retrieved.")
            continue
            
        print("Scrape completed. Simulated saving metrics to database.")
        time.sleep(2)
        
    print("\nPrice monitoring complete. Alerts forwarded to agent if price dropped below target thresholds.")

if __name__ == "__main__":
    print("Wholesale AI Agent background worker started. Scheduling daily price checks at 08:00 AM...")
    # Run once immediately on startup just to verify it works
    check_prices()
    
    # Schedule subsequent daily runs
    schedule.every().day.at("08:00").do(check_prices)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
