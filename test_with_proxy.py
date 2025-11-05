#!/usr/bin/env python3
"""
Test stats.gov.cn API access with proxy support

This script tests API access using proxy servers, which may be required
to bypass IP-based geographic restrictions.

Usage:
    # With HTTP proxy
    python test_with_proxy.py --proxy http://proxy.example.com:8080

    # With SOCKS proxy
    python test_with_proxy.py --proxy socks5://proxy.example.com:1080

    # With authentication
    python test_with_proxy.py --proxy http://user:pass@proxy.example.com:8080

    # Test with free proxy list
    python test_with_proxy.py --test-free-proxies
"""

import requests
import time
import json
import argparse

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

BASE_URL = 'https://data.stats.gov.cn/easyquery.htm'


def test_proxy_access(proxy_url):
    """
    Test API access through a proxy server.

    Parameters:
    -----------
    proxy_url : str
        Proxy URL in format: http://host:port or socks5://host:port
    """
    print("="*80)
    print(f"Testing API access with proxy: {proxy_url}")
    print("="*80)

    proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }

    session = requests.Session()
    session.proxies.update(proxies)
    session.verify = False

    # Set realistic headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })

    try:
        # Test 1: Access main page
        print("\nTest 1: Accessing main data page...")
        url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
        response = session.get(url, timeout=30)

        print(f"  Status: {response.status_code}")
        print(f"  Response length: {len(response.text)} bytes")
        print(f"  Cookies: {session.cookies.get_dict()}")

        if response.status_code != 200:
            print(f"  ✗ Failed to access main page")
            return False

        print(f"  ✓ Main page accessible!")

        time.sleep(2)

        # Test 2: Try API call
        print("\nTest 2: Attempting API call...")

        session.headers.update({
            'Referer': 'https://data.stats.gov.cn/easyquery.htm?cn=A01',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        })

        api_params = {
            'm': 'getTree',
            'dbcode': 'hgyd',
            'wdcode': 'zb',
            'id': 'zb',
            'k1': str(int(round(time.time() * 1000))),
            'h': '1',
        }

        api_response = session.post(BASE_URL, data=api_params, timeout=30)

        print(f"  Status: {api_response.status_code}")
        print(f"  Response length: {len(api_response.text)} bytes")
        print(f"  Response preview: {api_response.text[:200]}")

        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print(f"\n  ✓ SUCCESS! Valid JSON response received!")
                print(f"  Response structure: {list(data.keys()) if isinstance(data, dict) else 'List of items'}")

                if isinstance(data, list) and len(data) > 0:
                    print(f"  Number of items: {len(data)}")
                    print(f"  Sample item: {json.dumps(data[0], ensure_ascii=False)}")

                return True

            except Exception as e:
                print(f"  ✗ Response is not valid JSON: {str(e)}")
                return False
        else:
            print(f"  ✗ API call failed with status {api_response.status_code}")
            return False

    except requests.exceptions.ProxyError as e:
        print(f"\n✗ Proxy Error: {str(e)}")
        print(f"  The proxy server may be unreachable or invalid")
        return False

    except requests.exceptions.Timeout as e:
        print(f"\n✗ Timeout Error: {str(e)}")
        print(f"  The request timed out (proxy may be slow or blocked)")
        return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_free_proxy_list():
    """
    Get a list of free proxy servers to test.

    Note: Free proxies are often unreliable, slow, and may not work.
    For production use, consider paid proxy services.
    """
    # Some free public proxy lists (may or may not work)
    # WARNING: These are untrusted third-party services
    return [
        # Free proxy API services (these URLs would need to be actual proxy addresses)
        # Format: 'http://ip:port'
        # You would need to obtain actual working proxies from services like:
        # - proxy-list.download
        # - free-proxy-list.net
        # - spys.one
    ]


def test_direct_connection_diagnostic():
    """
    Run diagnostics to understand why direct connection fails.
    """
    print("="*80)
    print("DIAGNOSTIC: Understanding the block")
    print("="*80)

    import socket

    # Test 1: DNS resolution
    print("\n1. Testing DNS resolution...")
    try:
        ip = socket.gethostbyname('data.stats.gov.cn')
        print(f"   ✓ Resolved to: {ip}")
    except Exception as e:
        print(f"   ✗ DNS resolution failed: {e}")
        return

    # Test 2: TCP connection
    print("\n2. Testing TCP connection to port 443...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((ip, 443))
        sock.close()

        if result == 0:
            print(f"   ✓ TCP connection successful")
        else:
            print(f"   ✗ TCP connection failed with error code: {result}")
            return
    except Exception as e:
        print(f"   ✗ TCP connection error: {e}")
        return

    # Test 3: HTTP response headers
    print("\n3. Analyzing HTTP response...")
    try:
        response = requests.get('https://data.stats.gov.cn/easyquery.htm?cn=A01',
                               verify=False, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Server: {response.headers.get('Server', 'Not disclosed')}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'None')}")
        print(f"   Response body: '{response.text}'")

        if response.status_code == 403:
            print(f"\n   Analysis: 403 Forbidden error indicates:")
            print(f"   - Server is reachable and responding")
            print(f"   - Application-level blocking (not firewall)")
            print(f"   - Likely IP-based geofencing or WAF (Web Application Firewall)")

    except Exception as e:
        print(f"   ✗ HTTP request error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Test stats.gov.cn API access with proxy support'
    )
    parser.add_argument(
        '--proxy',
        help='Proxy URL (e.g., http://proxy.com:8080 or socks5://proxy.com:1080)'
    )
    parser.add_argument(
        '--test-free-proxies',
        action='store_true',
        help='Test with a list of free public proxies (unreliable)'
    )
    parser.add_argument(
        '--diagnostic',
        action='store_true',
        help='Run diagnostic tests on the direct connection'
    )

    args = parser.parse_args()

    if args.diagnostic:
        test_direct_connection_diagnostic()
        return

    if args.proxy:
        # Test with specified proxy
        success = test_proxy_access(args.proxy)

        if success:
            print("\n" + "="*80)
            print("✓ SUCCESS! This proxy works!")
            print("="*80)
            print(f"\nYou can now use this proxy with the discovery script:")
            print(f"  python build_master_variables_list.py --proxy {args.proxy}")
        else:
            print("\n" + "="*80)
            print("✗ This proxy did not work")
            print("="*80)

    elif args.test_free_proxies:
        print("Testing free proxies...")
        print("Note: Free proxies are often unreliable and may be blocked")
        print()

        proxies = get_free_proxy_list()

        if not proxies:
            print("No free proxies available in the hardcoded list.")
            print("\nTo use this feature, you need to:")
            print("1. Obtain proxy addresses from free proxy websites")
            print("2. Add them to the get_free_proxy_list() function")
            print("\nRecommended paid proxy services for Chinese sites:")
            print("  - Bright Data (luminati.io)")
            print("  - Oxylabs (oxylabs.io)")
            print("  - Smartproxy (smartproxy.com)")
            print("  - Chinese providers: 快代理 (kuaidaili.com), 芝麻代理 (zhimaruanjian.com)")
            return

        for i, proxy in enumerate(proxies, 1):
            print(f"\nTesting proxy {i}/{len(proxies)}: {proxy}")
            if test_proxy_access(proxy):
                print(f"\n✓ Found working proxy: {proxy}")
                return

        print("\n✗ None of the free proxies worked")

    else:
        print("No proxy specified. Running diagnostic instead...\n")
        test_direct_connection_diagnostic()

        print("\n\n" + "="*80)
        print("PROXY REQUIREMENTS")
        print("="*80)
        print("""
The stats.gov.cn API requires access from Chinese IP addresses.

RECOMMENDED SOLUTIONS:

1. PAID PROXY SERVICES (Most Reliable):
   - Bright Data: https://brightdata.com (has Chinese residential IPs)
   - Oxylabs: https://oxylabs.io
   - Smartproxy: https://smartproxy.com
   - Chinese services: 快代理 (kuaidaili.com), 芝麻代理 (zhimaruanjian.com)

2. VPN SERVICES:
   - Use a VPN with Chinese servers
   - May still be blocked if VPN IPs are blacklisted

3. CLOUD SERVICES:
   - Deploy on Alibaba Cloud, Tencent Cloud, or Huawei Cloud in China
   - Requires Chinese business registration for some services

4. SSH TUNNEL:
   - If you have access to a server in China
   - ssh -D 1080 user@server-in-china
   - Then use socks5://localhost:1080 as proxy

USAGE:
Once you have a proxy, test it with:
  python test_with_proxy.py --proxy http://your-proxy:port

Then use it with the discovery script:
  python build_master_variables_list.py --proxy http://your-proxy:port
""")


if __name__ == '__main__':
    main()
