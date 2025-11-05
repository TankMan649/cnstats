#!/usr/bin/env python3
"""
Test script to validate the discovery approach on a single database.
This will help us verify the approach works before running the full discovery.
"""

import json
import sys
import os

# Add the cnstats package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cnstats.common import easyquery

def test_get_tree():
    """Test retrieving the indicator tree for hgyd (national monthly)."""
    print("Testing indicator tree retrieval for hgyd (宏观月度)...")
    print("-" * 60)

    try:
        # Get root level indicators
        response = easyquery(m='getTree', dbcode='hgyd', wdcode='zb', id='zb')

        if response and isinstance(response, list):
            print(f"✓ Successfully retrieved {len(response)} root-level indicators")
            print("\nSample indicators:")
            for i, node in enumerate(response[:5]):  # Show first 5
                print(f"  {i+1}. ID: {node.get('id')}, Name: {node.get('name')}, "
                      f"IsParent: {node.get('isParent')}, Code: {node.get('code', 'N/A')}")

            # Test getting children of first parent node
            first_parent = next((n for n in response if n.get('isParent')), None)
            if first_parent:
                print(f"\n\nTesting child retrieval for '{first_parent['name']}'...")
                child_response = easyquery(
                    m='getTree',
                    dbcode='hgyd',
                    wdcode='zb',
                    id=first_parent['id']
                )

                if child_response and isinstance(child_response, list):
                    print(f"✓ Successfully retrieved {len(child_response)} child indicators")
                    print("\nSample children:")
                    for i, node in enumerate(child_response[:3]):
                        print(f"  {i+1}. ID: {node.get('id')}, Name: {node.get('name')}, "
                              f"IsParent: {node.get('isParent')}, Code: {node.get('code', 'N/A')}")

            return True

        else:
            print(f"✗ Unexpected response format: {type(response)}")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_get_regions():
    """Test retrieving region codes for fsyd (provincial monthly)."""
    print("\n\n" + "=" * 60)
    print("Testing region retrieval for fsyd (分省月度)...")
    print("-" * 60)

    try:
        wds = [{"wdcode": "zb", "valuecode": "A01010101"}]
        response = easyquery(dbcode='fsyd', rowcode='reg', wds=wds)

        if response.get('returncode') == 200:
            wdnodes = response.get('returndata', {}).get('wdnodes', [])
            print(f"✓ Successfully retrieved response with {len(wdnodes)} wdnodes")

            # Find the region nodes
            for wdnode in wdnodes:
                if wdnode.get('wdcode') == 'reg':
                    regions = wdnode.get('nodes', [])
                    print(f"✓ Found {len(regions)} regions")
                    print("\nSample regions:")
                    for i, region in enumerate(regions[:5]):
                        print(f"  {i+1}. Code: {region.get('code')}, Name: {region.get('name')}")

                    return True

            print("✗ No region nodes found in response")
            return False

        else:
            print(f"✗ API returned error code: {response.get('returncode')}")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_metadata():
    """Test building metadata for a small sample."""
    print("\n\n" + "=" * 60)
    print("Testing metadata building...")
    print("-" * 60)

    try:
        # Get just the root indicators for hgyd
        response = easyquery(m='getTree', dbcode='hgyd', wdcode='zb', id='zb')

        if response and isinstance(response, list):
            # Build metadata for first non-parent indicator
            indicators = [n for n in response[:5] if not n.get('isParent')]

            if indicators:
                sample_indicator = indicators[0]
                metadata = {
                    'Key': sample_indicator.get('code', sample_indicator.get('id', '')),
                    'Desc': sample_indicator.get('name', ''),
                    'Component_Key': '',
                    'Component_Desc': '',
                    'Frequency_Key': 'hgyd',
                    'Frequency_Desc': '宏观月度',
                    'Frequency_EN': 'national monthly',
                    'full_variable': sample_indicator.get('name', ''),
                    'src': 'stats.gov.cn',
                    'source': 'National Bureau of Statistics of China',
                    'source_cn': '中华人民共和国国家统计局',
                    'dataset': 'hgyd',
                    'dataset_scope': 'national',
                    'dataset_frequency': 'monthly',
                    'Year': 'ALL',
                    'level': 1
                }

                print("✓ Sample metadata entry:")
                print(json.dumps(metadata, ensure_ascii=False, indent=2))
                return True

        return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("DISCOVERY APPROACH VALIDATION TEST")
    print("=" * 60)
    print()

    results = []

    # Test 1: Get indicator tree
    results.append(("Indicator Tree Retrieval", test_get_tree()))

    # Test 2: Get regions
    results.append(("Region Retrieval", test_get_regions()))

    # Test 3: Build metadata
    results.append(("Metadata Building", test_sample_metadata()))

    # Summary
    print("\n\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("✓ All tests passed! The approach is validated.")
        print("\nYou can now run the full discovery script:")
        print("  python build_master_variables_list.py")
    else:
        print("✗ Some tests failed. Please review the errors above.")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
