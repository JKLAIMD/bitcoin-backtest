#!/bin/bash
# Fetch Bitcoin data using curl and Yahoo Finance

DATA_DIR="data"
mkdir -p "$DATA_DIR"

echo "Fetching Bitcoin historical data..."

# Get BTC-USD symbol info first
SYMBOL_INFO=$(curl -s "https://query1.finance.yahoo.com/v7/finance/quote?symbols=BTC-USD" | jq -r '.quoteResponse.result[0].symbol')
if [ "$SYMBOL_INFO" = "null" ]; then
    echo "Failed to get symbol info"
    exit 1
fi

echo "Symbol: $SYMBOL_INFO"

# Fetch historical data (this might not give minute data without proper session)
# For minute data, we need to use the chart endpoint
CHART_DATA=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=7d&interval=5m&indicators=quote&includeTimestamps=true")

# Extract timestamps and prices
TIMESTAMPS=$(echo "$CHART_DATA" | jq -r '.chart.result[0].timestamp[]')
OPEN_PRICES=$(echo "$CHART_DATA" | jq -r '.chart.result[0].indicators.quote[0].open[]')
HIGH_PRICES=$(echo "$CHART_DATA" | jq -r '.chart.result[0].indicators.quote[0].high[]')
LOW_PRICES=$(echo "$CHART_DATA" | jq -r '.chart.result[0].indicators.quote[0].low[]')
CLOSE_PRICES=$(echo "$CHART_DATA" | jq -r '.chart.result[0].indicators.quote[0].close[]')
VOLUMES=$(echo "$CHART_DATA" | jq -r '.chart.result[0].indicators.quote[0].volume[]')

# Create CSV header
echo "timestamp,open,high,low,close,volume" > "$DATA_DIR/btc_5min.csv"

# Combine data into CSV (this is simplified - real implementation needs array handling)
echo "$CHART_DATA" | jq -r '
.chart.result[0] as $result |
($result.timestamp | length) as $len |
range(0; $len) as $i |
"\($result.timestamp[$i]),\($result.indicators.quote[0].open[$i]),\($result.indicators.quote[0].high[$i]),\($result.indicators.quote[0].low[$i]),\($result.indicators.quote[0].close[$i]),\($result.indicators.quote[0].volume[$i])"
' >> "$DATA_DIR/btc_5min.csv"

echo "Data saved to $DATA_DIR/btc_5min.csv"
wc -l "$DATA_DIR/btc_5min.csv"