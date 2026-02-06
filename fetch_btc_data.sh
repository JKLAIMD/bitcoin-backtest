#!/bin/bash
# Fetch Bitcoin minute data using curl and Yahoo Finance API

OUTPUT_DIR="data"
mkdir -p "$OUTPUT_DIR"

echo "Fetching Bitcoin minute data..."

# Yahoo Finance API endpoint for BTC-USD
# This gets the last 7 days of 1-minute data
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?interval=1m&range=7d" | \
jq -r '[
  .chart.result[0].timestamp[],
  (.chart.result[0].indicators.quote[0].open // []),
  (.chart.result[0].indicators.quote[0].high // []),
  (.chart.result[0].indicators.quote[0].low // []),
  (.chart.result[0].indicators.quote[0].close // []),
  (.chart.result[0].indicators.quote[0].volume // [])
] | transpose[] | @csv' > "$OUTPUT_DIR/btc_minute.csv"

echo "Data saved to $OUTPUT_DIR/btc_minute.csv"
echo "Lines: $(wc -l < "$OUTPUT_DIR/btc_minute.csv")"