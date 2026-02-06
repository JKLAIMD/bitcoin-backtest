#!/bin/bash
# Fetch recent Bitcoin data with rate limiting

DATA_DIR="data"
mkdir -p "$DATA_DIR"

echo "Fetching recent Bitcoin data (last 7 days)..."
sleep 2

# Use a different approach - fetch from a public CSV source
# This is a fallback method
curl -s "https://api.coindesk.com/v1/bpi/historical/close.csv?start=$(date -d '7 days ago' +%Y-%m-%d)&end=$(date +%Y-%m-%d)" -o "$DATA_DIR/btc_daily.csv"

if [ -s "$DATA_DIR/btc_daily.csv" ]; then
    echo "Daily data fetched successfully"
    head -5 "$DATA_DIR/btc_daily.csv"
else
    echo "Failed to fetch daily data"
    # Create sample data for demonstration
    echo "date,price" > "$DATA_DIR/btc_daily.csv"
    for i in {1..30}; do
        date_val=$(date -d "$i days ago" +%Y-%m-%d)
        price=$(echo "30000 + $RANDOM % 10000" | bc)
        echo "$date_val,$price" >> "$DATA_DIR/btc_daily.csv"
    done
    echo "Created sample data for demonstration"
fi

echo "Data saved to $DATA_DIR/btc_daily.csv"
wc -l "$DATA_DIR/btc_daily.csv"