import pandas as pd
import json
import os
import requests
from io import StringIO
from datetime import datetime, timezone

# --- CONFIGURATION ---
CSV_URL = "https://portal.ogc.org/services/srv_active_members_csv_new.php" 
OUTPUT_DIR = "public"
OUTPUT_GEOJSON = "OGC_Membership.geojson"
OUTPUT_CSV = "OGC_Membership.csv" 

def process_data():
    print(f"Fetching data from {CSV_URL}...")
    
    # Download raw content to save later
    response = requests.get(CSV_URL)
    response.raise_for_status()
    raw_csv_content = response.text
    
    # Process Data Frame (using the raw content string)
    df = pd.read_csv(StringIO(raw_csv_content), on_bad_lines='skip')
    
    features = []
    
    for _, row in df.iterrows():
        lat = row.get('latitude')
        lon = row.get('longitude')
        
        if pd.notna(lat) and pd.notna(lon):
            properties = row.drop(['latitude', 'longitude']).to_dict()
            properties = {k: (None if pd.isna(v) else v) for k, v in properties.items()}
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)]
                },
                "properties": properties
            }
            features.append(feature)

    # Create FeatureCollection with Timestamp
    current_time = datetime.now(timezone.utc).isoformat()
    
    geojson_collection = {
        "type": "FeatureCollection",
        "source": CSV_URL,
        "fetched": current_time,
        "features": features
    }
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Write GeoJSON
    with open(os.path.join(OUTPUT_DIR, OUTPUT_GEOJSON), 'w', encoding='utf-8') as f:
        json.dump(geojson_collection, f, indent=4, ensure_ascii=False)

    # Write Raw CSV Copy
    with open(os.path.join(OUTPUT_DIR, OUTPUT_CSV), 'w', encoding='utf-8') as f:
        f.write(raw_csv_content)
        
    print(f"Success! Generated GeoJSON and saved CSV copy.")

if __name__ == "__main__":
    process_data()