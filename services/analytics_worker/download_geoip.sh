#!/bin/bash
# 下載 MaxMind GeoLite2-City 數據庫

set -e

GEOIP_DIR="/app/data/geoip"
GEOIP_DB="$GEOIP_DIR/GeoLite2-City.mmdb"

echo "=== GeoLite2 Database Downloader ==="

# 創建目錄
mkdir -p "$GEOIP_DIR"

# 檢查數據庫是否已存在
if [ -f "$GEOIP_DB" ]; then
    echo "✅ GeoLite2 database already exists at $GEOIP_DB"
    echo "   File size: $(du -h "$GEOIP_DB" | cut -f1)"
    echo "   Last modified: $(stat -c %y "$GEOIP_DB" 2>/dev/null || stat -f %Sm "$GEOIP_DB")"
    exit 0
fi

echo "⚠️  GeoLite2 database not found"
echo ""
echo "To enable GeoIP location lookup, you need to download the GeoLite2-City database."
echo ""
echo "📋 Instructions:"
echo "1. Go to https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
echo "2. Sign up for a free account (if you haven't already)"
echo "3. Download GeoLite2-City.mmdb"
echo "4. Place it at: $GEOIP_DB"
echo ""
echo "Alternatively, if you have a MaxMind license key, set these environment variables:"
echo "  MAXMIND_LICENSE_KEY=your_license_key"
echo ""
echo "🔗 Quick download (requires MaxMind account):"
echo "  wget 'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=YOUR_KEY&suffix=tar.gz' -O GeoLite2-City.tar.gz"
echo "  tar -xzf GeoLite2-City.tar.gz"
echo "  mv GeoLite2-City_*/GeoLite2-City.mmdb $GEOIP_DB"
echo ""
echo "📌 Without the database, geographic location will show as empty."
echo "   All other features will continue to work normally."
