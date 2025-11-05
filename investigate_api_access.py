#!/usr/bin/env python3
"""
Investigate API access solutions for stats.gov.cn

This script tests various approaches to overcome 403 Access Denied errors.
"""

import requests
import time
import json
from urllib.parse import urlencode

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

BASE_URL = 'https://data.stats.gov.cn/easyquery.htm'


def test_1_basic_get():
    """Test 1: Simple GET request to main page"""
    print("\n" + "="*80)
    print("TEST 1: Basic GET request to main page")
    print("="*80)

    try:
        url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
        response = requests.get(url, verify=False, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} bytes")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Cookies: {response.cookies.get_dict()}")

        if response.status_code == 200:
            print("✓ Main page accessible!")
            return True, response.cookies.get_dict()
        else:
            print(f"✗ Failed with status {response.status_code}")
            return False, {}

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False, {}


def test_2_different_user_agents():
    """Test 2: Try different User-Agent strings"""
    print("\n" + "="*80)
    print("TEST 2: Testing different User-Agent strings")
    print("="*80)

    user_agents = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Chrome on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        # Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        # Chinese Browser - 360 Browser
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 QIHU 360SE',
        # Chinese Browser - QQ Browser
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3861.400 QQBrowser/10.7.4313.400',
    ]

    for i, ua in enumerate(user_agents, 1):
        print(f"\n{i}. Testing: {ua[:60]}...")

        headers = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        try:
            url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            print(f"   Status: {response.status_code}, Length: {len(response.text)} bytes")

            if response.status_code == 200:
                print(f"   ✓ Success with this User-Agent!")
                return True, headers

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

        time.sleep(0.5)

    print("\n✗ All User-Agents failed")
    return False, {}


def test_3_session_with_cookies():
    """Test 3: Use session with proper cookie handling"""
    print("\n" + "="*80)
    print("TEST 3: Testing session with cookie persistence")
    print("="*80)

    session = requests.Session()
    session.verify = False

    # Set comprehensive headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    try:
        # Step 1: Visit main page
        print("Step 1: Visiting main stats.gov.cn page...")
        main_url = 'https://www.stats.gov.cn/'
        response = session.get(main_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Cookies after main page: {session.cookies.get_dict()}")

        time.sleep(1)

        # Step 2: Visit data portal
        print("\nStep 2: Visiting data portal...")
        portal_url = 'https://data.stats.gov.cn/'
        response = session.get(portal_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Cookies after portal: {session.cookies.get_dict()}")

        time.sleep(1)

        # Step 3: Visit easyquery page
        print("\nStep 3: Visiting easyquery page...")
        easyquery_url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
        response = session.get(easyquery_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Cookies after easyquery: {session.cookies.get_dict()}")

        if response.status_code == 200:
            time.sleep(1)

            # Step 4: Try API call with session
            print("\nStep 4: Attempting API call with established session...")

            session.headers.update({
                'Referer': 'https://data.stats.gov.cn/easyquery.htm?cn=A01',
                'X-Requested-With': 'XMLHttpRequest',
            })

            api_params = {
                'm': 'getTree',
                'dbcode': 'hgyd',
                'wdcode': 'zb',
                'id': 'zb',
                'k1': str(int(round(time.time() * 1000))),
                'h': '1',
            }

            api_response = session.post(BASE_URL, data=api_params, timeout=10)
            print(f"   API Status: {api_response.status_code}")
            print(f"   Response length: {len(api_response.text)} bytes")

            if api_response.status_code == 200:
                try:
                    data = api_response.json()
                    print(f"   ✓ Valid JSON response!")
                    print(f"   Response preview: {json.dumps(data, ensure_ascii=False)[:200]}")
                    return True, session
                except:
                    print(f"   Response text: {api_response.text[:200]}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    return False, None


def test_4_curl_equivalent():
    """Test 4: Try curl-like request"""
    print("\n" + "="*80)
    print("TEST 4: Testing curl-equivalent request")
    print("="*80)

    # Simulate exact curl behavior
    headers = {
        'User-Agent': 'curl/7.81.0',
        'Accept': '*/*',
    }

    try:
        url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
        response = requests.get(url, headers=headers, verify=False, timeout=10)

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")

    return False


def test_5_check_redirect():
    """Test 5: Check if there's a redirect we're missing"""
    print("\n" + "="*80)
    print("TEST 5: Checking for redirects")
    print("="*80)

    try:
        url = 'https://data.stats.gov.cn/easyquery.htm?cn=A01'
        response = requests.get(url, verify=False, timeout=10, allow_redirects=False)

        print(f"Status: {response.status_code}")
        print(f"Location: {response.headers.get('Location', 'None')}")

        if response.status_code in [301, 302, 303, 307, 308]:
            print(f"✓ Redirect detected to: {response.headers.get('Location')}")

            # Follow redirect manually
            redirect_url = response.headers.get('Location')
            if redirect_url:
                response2 = requests.get(redirect_url, verify=False, timeout=10)
                print(f"After redirect - Status: {response2.status_code}")
                return response2.status_code == 200

    except Exception as e:
        print(f"✗ Error: {str(e)}")

    return False


def test_6_get_with_query_params():
    """Test 6: Try GET instead of POST for API"""
    print("\n" + "="*80)
    print("TEST 6: Testing GET request with query parameters")
    print("="*80)

    params = {
        'm': 'getTree',
        'dbcode': 'hgyd',
        'wdcode': 'zb',
        'id': 'zb',
        'k1': str(int(round(time.time() * 1000))),
        'h': '1',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://data.stats.gov.cn/easyquery.htm?cn=A01',
        'X-Requested-With': 'XMLHttpRequest',
    }

    try:
        url = BASE_URL + '?' + urlencode(params)
        print(f"URL: {url}")

        response = requests.get(url, headers=headers, verify=False, timeout=10)

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ Valid JSON response!")
                return True
            except:
                pass

    except Exception as e:
        print(f"✗ Error: {str(e)}")

    return False


def main():
    """Run all tests"""
    print("="*80)
    print("INVESTIGATING API ACCESS SOLUTIONS FOR stats.gov.cn")
    print("="*80)

    results = []

    # Run all tests
    results.append(("Basic GET", test_1_basic_get()[0]))
    results.append(("Different User-Agents", test_2_different_user_agents()[0]))
    results.append(("Session with Cookies", test_3_session_with_cookies()[0]))
    results.append(("Curl-like request", test_4_curl_equivalent()))
    results.append(("Check redirects", test_5_check_redirect()))
    results.append(("GET with params", test_6_get_with_query_params()))

    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY OF TESTS")
    print("="*80)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    if any(r[1] for r in results):
        print("\n✓ At least one method worked! Review details above.")
    else:
        print("\n✗ All methods failed. This suggests:")
        print("  1. IP-based blocking (likely blocking non-Chinese IPs)")
        print("  2. Advanced bot detection")
        print("  3. Requires specific authentication/session token")
        print("\nRecommended next steps:")
        print("  - Try using a Chinese proxy server")
        print("  - Use browser automation (Selenium/Playwright)")
        print("  - Check if there's a captcha on first visit")


if __name__ == '__main__':
    main()
