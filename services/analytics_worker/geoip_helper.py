"""
GeoIP 地理位置查詢模組

使用 MaxMind GeoLite2 數據庫查詢 IP 地理位置
"""

import logging
import os
from typing import Dict, Any, Optional
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)

# GeoLite2 數據庫路徑
GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH", "/app/data/geoip/GeoLite2-City.mmdb")

# 全局數據庫讀取器
_reader = None


def init_geoip_reader():
    """初始化 GeoIP 數據庫讀取器"""
    global _reader

    if _reader is not None:
        return _reader

    try:
        if os.path.exists(GEOIP_DB_PATH):
            _reader = geoip2.database.Reader(GEOIP_DB_PATH)
            logger.info(f"GeoIP database loaded from {GEOIP_DB_PATH}")
        else:
            logger.warning(f"  GeoIP database not found at {GEOIP_DB_PATH}")
            logger.warning("   Geographic location lookup will be disabled")
            logger.warning("   To enable GeoIP:")
            logger.warning("   1. Download GeoLite2-City.mmdb from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data")
            logger.warning(f"   2. Place it at {GEOIP_DB_PATH}")
    except Exception as e:
        logger.error(f"Error loading GeoIP database: {e}")

    return _reader


def lookup_ip_location(ip: str) -> Dict[str, Any]:
    """
    查詢 IP 地理位置

    Args:
        ip: IP 地址

    Returns:
        Dict: 地理位置信息
            - country: 國家名稱
            - country_code: 國家代碼 (ISO 3166-1 alpha-2)
            - city: 城市名稱
            - zip_code: 郵遞區號
            - latitude: 緯度
            - longitude: 經度
            - timezone: 時區
            - accuracy_radius: 位置精確度半徑（公里）
    """
    location = {
        'country': '',
        'country_code': '',
        'city': '',
        'zip_code': '',
        'latitude': None,
        'longitude': None,
        'timezone': '',
        'accuracy_radius': None
    }

    if not ip or ip == '0.0.0.0':
        return location

    # 檢查是否為私有 IP
    if is_private_ip(ip):
        logger.debug(f"Skipping GeoIP lookup for private IP: {ip}")
        return location

    # 初始化讀取器
    reader = init_geoip_reader()
    if reader is None:
        return location

    try:
        response = reader.city(ip)

        # 提取地理位置信息
        if response.country.name:
            location['country'] = response.country.name
        if response.country.iso_code:
            location['country_code'] = response.country.iso_code
        if response.city.name:
            location['city'] = response.city.name
        if response.postal.code:
            location['zip_code'] = response.postal.code
        if response.location.latitude:
            location['latitude'] = response.location.latitude
        if response.location.longitude:
            location['longitude'] = response.location.longitude
        if response.location.time_zone:
            location['timezone'] = response.location.time_zone
        if response.location.accuracy_radius:
            location['accuracy_radius'] = response.location.accuracy_radius

        logger.debug(f"✅ GeoIP lookup for {ip}: {location['country']}, {location['city']}")

    except geoip2.errors.AddressNotFoundError:
        logger.debug(f"GeoIP: Address not found in database: {ip}")
    except Exception as e:
        logger.warning(f"GeoIP lookup failed for {ip}: {e}")

    return location


def is_private_ip(ip: str) -> bool:
    """檢查是否為私有 IP 地址"""
    private_ranges = [
        '10.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
        '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
        '172.30.', '172.31.', '192.168.', '127.',
        'localhost', '::1', 'fe80:'
    ]
    return any(ip.startswith(prefix) for prefix in private_ranges)


def close_geoip_reader():
    global _reader
    if _reader is not None:
        try:
            _reader.close()
            logger.info("GeoIP database reader closed")
        except Exception as e:
            logger.error(f"Error closing GeoIP reader: {e}")
        finally:
            _reader = None
