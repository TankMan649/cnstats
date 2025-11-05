#!/usr/bin/env python3
"""
Debug script to inspect the actual API responses from stats.gov.cn
"""

import requests
import json
import time

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

def test_api_raw():
    """Test the API with raw requests to see what's being returned."""
    url = 'https://data.stats.gov.cn/easyquery.htm'

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://data.stats.gov.cn/easyquery.htm?cn=A01',
        'Host': 'data.stats.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36',
        'X-Requested-With': 'XMLHttpRequest',
        # Note: Removed hardcoded cookies to see if API works without them
    }

    # Test 1: getTree request
    print("=" * 80)
    print("TEST 1: getTree API call")
    print("=" * 80)

    params = {
        'm': 'getTree',
        'dbcode': 'hgyd',
        'wdcode': 'zb',
        'id': 'zb',
        'k1': str(int(round(time.time() * 1000))),
        'h': '1',
    }

    print(f"URL: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    print()

    try:
        response = requests.post(url, data=params, headers=headers, verify=False, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Length: {len(response.text)} bytes")
        print()
        print("Response Text (first 500 chars):")
        print("-" * 80)
        print(response.text[:500])
        print("-" * 80)
        print()

        if response.text:
            try:
                json_data = response.json()
                print("✓ Valid JSON response!")
                print("JSON structure:")
                print(json.dumps(json_data, ensure_ascii=False, indent=2)[:1000])
            except Exception as e:
                print(f"✗ Invalid JSON: {str(e)}")
        else:
            print("✗ Empty response!")

    except Exception as e:
        print(f"✗ Request failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test 2: Try QueryData instead
    print("\n\n" + "=" * 80)
    print("TEST 2: QueryData API call (query actual data)")
    print("=" * 80)

    params2 = {
        'm': 'QueryData',
        'dbcode': 'hgyd',
        'rowcode': 'zb',
        'colcode': 'sj',
        'wds': json.dumps([]),
        'dfwds': json.dumps([
            {"wdcode": "zb", "valuecode": "A010101"},
            {"wdcode": "sj", "valuecode": "202301"}
        ]),
        'k1': str(int(round(time.time() * 1000))),
        'h': '1',
    }

    print(f"Parameters: {json.dumps(params2, indent=2)}")
    print()

    try:
        response = requests.post(url, data=params2, headers=headers, verify=False, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} bytes")
        print()
        print("Response Text (first 500 chars):")
        print("-" * 80)
        print(response.text[:500])
        print("-" * 80)
        print()

        if response.text:
            try:
                json_data = response.json()
                print("✓ Valid JSON response!")
                print("JSON structure:")
                print(json.dumps(json_data, ensure_ascii=False, indent=2)[:1000])
            except Exception as e:
                print(f"✗ Invalid JSON: {str(e)}")

    except Exception as e:
        print(f"✗ Request failed: {str(e)}")

    # Test 3: Try accessing the main page first
    print("\n\n" + "=" * 80)
    print("TEST 3: Access main page to establish session")
    print("=" * 80)

    try:
        main_url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
        session = requests.Session()
        session.verify = False

        print(f"Accessing: {main_url}")
        response = session.get(main_url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Cookies received: {session.cookies.get_dict()}")
        print()

        # Now try the API call with the session
        print("Retrying getTree with session cookies...")
        params['k1'] = str(int(round(time.time() * 1000)))  # Update timestamp
        response = session.post(url, data=params, headers=headers, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} bytes")
        print()
        print("Response Text (first 500 chars):")
        print("-" * 80)
        print(response.text[:500])
        print("-" * 80)

        if response.text:
            try:
                json_data = response.json()
                print("\n✓ Valid JSON response with session!")
                print("JSON structure:")
                print(json.dumps(json_data, ensure_ascii=False, indent=2)[:1000])
                return True
            except Exception as e:
                print(f"\n✗ Still invalid JSON: {str(e)}")

    except Exception as e:
        print(f"✗ Request failed: {str(e)}")
        import traceback
        traceback.print_exc()

    return False


if __name__ == '__main__':
    test_api_raw()
