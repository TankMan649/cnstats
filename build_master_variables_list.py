#!/usr/bin/env python3
"""
Master Variables List Builder for stats.gov.cn

This script systematically discovers all available variables from the Chinese National
Bureau of Statistics API and creates a comprehensive metadata list in flat JSON format.

The script:
1. Iterates through all database codes (national, provincial, city; monthly, quarterly, annual)
2. Recursively discovers all indicator codes using the getTree API method
3. Retrieves region codes for provincial and city databases
4. Builds a comprehensive flat JSON structure with metadata
"""

import json
import time
from datetime import datetime
from cnstats.common import easyquery

# Database codes mapping
DATABASE_CODES = {
    'hgyd': {'scope': 'national', 'frequency': 'monthly', 'scope_cn': '宏观', 'frequency_cn': '月度'},
    'hgjd': {'scope': 'national', 'frequency': 'quarterly', 'scope_cn': '宏观', 'frequency_cn': '季度'},
    'hgnd': {'scope': 'national', 'frequency': 'annual', 'scope_cn': '宏观', 'frequency_cn': '年度'},
    'fsyd': {'scope': 'provincial', 'frequency': 'monthly', 'scope_cn': '分省', 'frequency_cn': '月度'},
    'fsjd': {'scope': 'provincial', 'frequency': 'quarterly', 'scope_cn': '分省', 'frequency_cn': '季度'},
    'fsnd': {'scope': 'provincial', 'frequency': 'annual', 'scope_cn': '分省', 'frequency_cn': '年度'},
    'csyd': {'scope': 'city', 'frequency': 'monthly', 'scope_cn': '城市', 'frequency_cn': '月度'},
    'csjd': {'scope': 'city', 'frequency': 'quarterly', 'scope_cn': '城市', 'frequency_cn': '季度'},
    'csnd': {'scope': 'city', 'frequency': 'annual', 'scope_cn': '城市', 'frequency_cn': '年度'},
}

def get_indicator_tree_recursive(node_id='zb', dbcode='hgyd', parent_info=None):
    """
    Recursively retrieve all indicator codes from the API tree structure.

    Parameters:
    -----------
    node_id : str
        The node ID to start from (default 'zb' for root)
    dbcode : str
        Database code (e.g., 'hgyd', 'fsyd', etc.)
    parent_info : dict
        Information about the parent node (for building hierarchy)

    Returns:
    --------
    list : List of indicator dictionaries with metadata
    """
    indicators = []

    try:
        response = easyquery(m='getTree', dbcode=dbcode, wdcode='zb', id=node_id)

        if not response or not isinstance(response, list):
            return indicators

        for node in response:
            indicator = {
                'id': node.get('id', ''),
                'name': node.get('name', ''),
                'code': node.get('code', ''),
                'is_parent': node.get('isParent', False),
                'parent_id': parent_info['id'] if parent_info else None,
                'parent_name': parent_info['name'] if parent_info else None,
                'dbcode': dbcode,
                'level': (parent_info.get('level', 0) + 1) if parent_info else 1
            }

            indicators.append(indicator)

            # If this node has children, recursively get them
            if node.get('isParent', False):
                child_indicators = get_indicator_tree_recursive(
                    node_id=node['id'],
                    dbcode=dbcode,
                    parent_info={
                        'id': node.get('id'),
                        'name': node.get('name'),
                        'level': indicator['level']
                    }
                )
                indicators.extend(child_indicators)

            # Small delay to avoid overwhelming the API
            time.sleep(0.1)

    except Exception as e:
        print(f"Error retrieving tree for {node_id} in {dbcode}: {str(e)}")

    return indicators


def get_region_codes(dbcode='fsyd'):
    """
    Retrieve all region codes for a given database code.

    Parameters:
    -----------
    dbcode : str
        Database code (typically fsyd, fsnd, csyd, or csnd)

    Returns:
    --------
    list : List of region dictionaries with code and name
    """
    try:
        # Use a common indicator code to query regions
        wds = [{"wdcode": "zb", "valuecode": "A01010101"}]
        response = easyquery(dbcode=dbcode, rowcode='reg', wds=wds)

        if response.get('returncode') == 200:
            wdnodes = response.get('returndata', {}).get('wdnodes', [])
            # The region nodes are typically in the second wdnode (index 1)
            for wdnode in wdnodes:
                if wdnode.get('wdcode') == 'reg':
                    return wdnode.get('nodes', [])

        return []

    except Exception as e:
        print(f"Error retrieving regions for {dbcode}: {str(e)}")
        return []


def build_flat_metadata(indicators, regions, db_info):
    """
    Build flat JSON metadata structure from indicators and regions.

    Parameters:
    -----------
    indicators : list
        List of indicator dictionaries
    regions : list
        List of region dictionaries
    db_info : dict
        Database information (scope, frequency, etc.)

    Returns:
    --------
    list : Flat list of metadata dictionaries
    """
    flat_metadata = []

    for indicator in indicators:
        # Skip parent-only nodes that don't have actual data
        if indicator.get('is_parent') and not indicator.get('code'):
            continue

        # Base metadata for this indicator
        base_entry = {
            'Key': indicator.get('code', indicator.get('id', '')),
            'Desc': indicator.get('name', ''),
            'Component_Key': indicator.get('parent_id', ''),
            'Component_Desc': indicator.get('parent_name', ''),
            'Frequency_Key': db_info['dbcode'],
            'Frequency_Desc': f"{db_info['scope_cn']}{db_info['frequency_cn']}",
            'Frequency_EN': f"{db_info['scope']} {db_info['frequency']}",
            'full_variable': indicator.get('name', ''),
            'src': 'stats.gov.cn',
            'source': 'National Bureau of Statistics of China',
            'source_cn': '中华人民共和国国家统计局',
            'dataset': db_info['dbcode'],
            'dataset_scope': db_info['scope'],
            'dataset_frequency': db_info['frequency'],
            'Year': 'ALL',
            'level': indicator.get('level', 1)
        }

        # If this is a national database or if there are no regions, add single entry
        if db_info['scope'] == 'national' or not regions:
            flat_metadata.append(base_entry.copy())
        else:
            # For provincial/city databases, create entry for each region
            for region in regions:
                entry = base_entry.copy()
                entry['Region_Key'] = region.get('code', '')
                entry['Region_Desc'] = region.get('name', '')
                entry['full_variable'] = f"{indicator.get('name', '')} - {region.get('name', '')}"
                flat_metadata.append(entry)

    return flat_metadata


def main():
    """
    Main function to build the master variables list.
    """
    print("=" * 80)
    print("Building Master Variables List for stats.gov.cn")
    print("=" * 80)
    print()

    all_metadata = []
    stats = {
        'total_indicators': 0,
        'total_entries': 0,
        'by_database': {}
    }

    # Iterate through all database codes
    for dbcode, db_info in DATABASE_CODES.items():
        print(f"\nProcessing {dbcode} ({db_info['scope_cn']}{db_info['frequency_cn']})...")
        db_info_with_code = db_info.copy()
        db_info_with_code['dbcode'] = dbcode

        # Get all indicators for this database
        print(f"  - Discovering indicator codes...")
        indicators = get_indicator_tree_recursive(node_id='zb', dbcode=dbcode)
        print(f"    Found {len(indicators)} indicators")

        # Get regions if applicable (provincial or city databases)
        regions = []
        if db_info['scope'] in ['provincial', 'city']:
            print(f"  - Discovering region codes...")
            regions = get_region_codes(dbcode=dbcode)
            print(f"    Found {len(regions)} regions")

        # Build flat metadata
        print(f"  - Building metadata entries...")
        metadata = build_flat_metadata(indicators, regions, db_info_with_code)
        all_metadata.extend(metadata)

        # Update statistics
        stats['total_indicators'] += len(indicators)
        stats['by_database'][dbcode] = {
            'indicators': len(indicators),
            'regions': len(regions),
            'entries': len(metadata)
        }
        stats['total_entries'] += len(metadata)

        print(f"    Generated {len(metadata)} metadata entries")

        # Small delay between database queries
        time.sleep(1)

    # Save to JSON file
    output_file = 'master_variables_list.json'
    print(f"\n\nSaving master variables list to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, ensure_ascii=False, indent=2)

    print(f"✓ Successfully saved {len(all_metadata)} entries to {output_file}")

    # Save statistics
    stats_file = 'master_variables_stats.json'
    stats['generated_at'] = datetime.now().isoformat()
    stats['total_databases'] = len(DATABASE_CODES)

    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✓ Statistics saved to {stats_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total databases processed: {stats['total_databases']}")
    print(f"Total unique indicators discovered: {stats['total_indicators']}")
    print(f"Total metadata entries generated: {stats['total_entries']}")
    print()
    print("Breakdown by database:")
    for dbcode, db_stats in stats['by_database'].items():
        db_info = DATABASE_CODES[dbcode]
        print(f"  {dbcode} ({db_info['scope_cn']}{db_info['frequency_cn']}): "
              f"{db_stats['indicators']} indicators × "
              f"{'1 (national)' if db_stats['regions'] == 0 else f\"{db_stats['regions']} regions\"} = "
              f"{db_stats['entries']} entries")
    print("=" * 80)


if __name__ == '__main__':
    main()
