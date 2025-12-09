import os
import time
import pandas as pd
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
INPUT_CSV = 'Açaí_no_ponto_-_all_versions_-_labels_-_2025-11-26-17-29-38.csv'
OUTPUT_FILE = 'output_enderecos.xlsx'
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
DRY_RUN = False  # Set to True to test without API calls or limit records

def get_address(gmaps, lat, lng):
    """
    Reverse geocode a set of coordinates.
    Returns the first formatted address found.
    """
    if not API_KEY or API_KEY == 'your_api_key_here':
        return "API_KEY_ERROR"

    try:
        # Rate limiting: simple sleep. 
        # Free tier is generous but good practice to not hammer.
        time.sleep(0.1) 
        
        results = gmaps.reverse_geocode((lat, lng))
        if results:
            return results[0].get('formatted_address', 'No address found')
        return "No results"
    except Exception as e:
        return f"Error: {str(e)}"

def process_data():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Input file '{INPUT_CSV}' not found.")
        return

    print("Loading CSV...")
    try:
        df = pd.read_csv(INPUT_CSV, delimiter=';') # CSV seems to use semicolon based on view_file output
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Check if necessary columns exist
    # Based on file inspection: "_Localização_latitude", "_Localização_longitude"
    if "_Localização_latitude" not in df.columns or "_Localização_longitude" not in df.columns:
        print("Error: Latitude/Longitude columns not found.")
        print(f"Available columns: {df.columns.tolist()}")
        return

    print(f"Loaded {len(df)} records.")

    if not API_KEY or API_KEY == 'your_api_key_here':
        print("WARNING: Valid Google Maps API Key not found in .env file.")
        print("Geocoding will be skipped or fai.")
        if not DRY_RUN:
             print("Please set GOOGLE_MAPS_API_KEY in .env")
             return

    # Initialize Google Maps client
    gmaps = None
    if API_KEY and API_KEY != 'your_api_key_here':
        gmaps = googlemaps.Client(key=API_KEY)

    # List to store addresses
    addresses = []
    
    # Iterate and geocode
    total = len(df)
    limit = 5 if DRY_RUN else total
    
    print(f"Processing {limit} records (DRY_RUN={DRY_RUN})...")

    for index, row in df.iterrows():
        if index >= limit:
            addresses.append("DRY_RUN_SKIPPED")
            continue

        lat = row.get('_Localização_latitude')
        lng = row.get('_Localização_longitude')

        # Basic validation
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
             addresses.append("Invalid Coordinates")
             continue
        
        if pd.isna(lat) or pd.isna(lng) or (lat == 0 and lng == 0):
             addresses.append("Empty/Zero Coordinates")
        else:
            if gmaps:
                print(f"Geocoding {index+1}/{limit}: ({lat}, {lng})")
                addr = get_address(gmaps, lat, lng)
                addresses.append(addr)
            else:
                addresses.append("Mock Address (No API Key)")

    # Assign column
    # Ensure length matches if we cut short (should be handled by loop logic above but let's be safe)
    if len(addresses) < total:
        addresses.extend(["Skipped"] * (total - len(addresses)))
    
    df['Endereço_Google'] = addresses

    # Save output
    print(f"Saving to {OUTPUT_FILE}...")
    try:
        df.to_excel(OUTPUT_FILE, index=False)
        print("Done!")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

if __name__ == '__main__':
    process_data()
