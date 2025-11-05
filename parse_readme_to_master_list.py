#!/usr/bin/env python3
"""
Parse README.md to create a comprehensive master variables list.

This script extracts all documented indicator codes, region codes, and city codes
from the README and combines them with database codes to create a flat JSON
metadata structure.
"""

import re
import json
from datetime import datetime

# Database codes mapping
DATABASE_CODES = {
    'hgyd': {
        'scope': 'national',
        'frequency': 'monthly',
        'scope_cn': '宏观',
        'scope_en': 'National',
        'frequency_cn': '月度',
        'frequency_en': 'Monthly'
    },
    'hgjd': {
        'scope': 'national',
        'frequency': 'quarterly',
        'scope_cn': '宏观',
        'scope_en': 'National',
        'frequency_cn': '季度',
        'frequency_en': 'Quarterly'
    },
    'hgnd': {
        'scope': 'national',
        'frequency': 'annual',
        'scope_cn': '宏观',
        'scope_en': 'National',
        'frequency_cn': '年度',
        'frequency_en': 'Annual'
    },
    'fsyd': {
        'scope': 'provincial',
        'frequency': 'monthly',
        'scope_cn': '分省',
        'scope_en': 'Provincial',
        'frequency_cn': '月度',
        'frequency_en': 'Monthly'
    },
    'fsjd': {
        'scope': 'provincial',
        'frequency': 'quarterly',
        'scope_cn': '分省',
        'scope_en': 'Provincial',
        'frequency_cn': '季度',
        'frequency_en': 'Quarterly'
    },
    'fsnd': {
        'scope': 'provincial',
        'frequency': 'annual',
        'scope_cn': '分省',
        'scope_en': 'Provincial',
        'frequency_cn': '年度',
        'frequency_en': 'Annual'
    },
    'csyd': {
        'scope': 'city',
        'frequency': 'monthly',
        'scope_cn': '城市',
        'scope_en': 'City',
        'frequency_cn': '月度',
        'frequency_en': 'Monthly'
    },
    'csjd': {
        'scope': 'city',
        'frequency': 'quarterly',
        'scope_cn': '城市',
        'scope_en': 'City',
        'frequency_cn': '季度',
        'frequency_en': 'Quarterly'
    },
    'csnd': {
        'scope': 'city',
        'frequency': 'annual',
        'scope_cn': '城市',
        'scope_en': 'City',
        'frequency_cn': '年度',
        'frequency_en': 'Annual'
    },
}


def parse_readme_table(content, start_marker, end_marker=None):
    """
    Parse a markdown table from README content.

    Parameters:
    -----------
    content : str
        The README content
    start_marker : str
        The line that marks the start of the table section
    end_marker : str, optional
        The line that marks the end of the table section

    Returns:
    --------
    list : List of tuples (code, description)
    """
    lines = content.split('\n')
    table_data = []
    in_table = False
    table_started = False

    for i, line in enumerate(lines):
        # Check if we've reached the start marker
        if start_marker in line:
            in_table = True
            continue

        # Check if we've reached the end marker
        if end_marker and end_marker in line:
            break

        # Skip until we find the table header separator
        if in_table and not table_started:
            if '---|---' in line or '--- | ---' in line:
                table_started = True
                continue

        # Parse table rows
        if table_started:
            # Stop if we hit a blank line or another section
            if line.strip() == '' or line.startswith('#'):
                break

            # Parse the table row
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                # Remove empty first/last elements from split
                parts = [p for p in parts if p]
                if len(parts) == 2:
                    code, desc = parts
                    if code and desc:  # Skip empty rows
                        table_data.append((code, desc))

    return table_data


def parse_indicator_hierarchy(indicators):
    """
    Parse indicator codes to determine parent-child relationships.

    Parameters:
    -----------
    indicators : list
        List of (code, description) tuples

    Returns:
    --------
    list : List of indicator dictionaries with hierarchy information
    """
    indicator_list = []

    for code, desc in indicators:
        # Determine the level based on code pattern
        # A01 -> level 1 (top level)
        # A0101 -> level 2
        # A010101 -> level 3, etc.

        # Find parent code
        parent_code = None
        parent_desc = None

        if len(code) > 3:  # Has a parent
            # Try to find parent by removing last part
            for test_len in range(len(code) - 1, 2, -1):
                potential_parent = code[:test_len]
                for parent_candidate_code, parent_candidate_desc in indicators:
                    if parent_candidate_code == potential_parent:
                        parent_code = potential_parent
                        parent_desc = parent_candidate_desc
                        break
                if parent_code:
                    break

        indicator_list.append({
            'code': code,
            'desc': desc,
            'parent_code': parent_code,
            'parent_desc': parent_desc,
            'level': len(code) - 2  # Rough estimate of hierarchy level
        })

    return indicator_list


def build_flat_metadata(indicators, regions, cities):
    """
    Build comprehensive flat JSON metadata structure.

    Parameters:
    -----------
    indicators : list
        List of indicator dictionaries
    regions : list
        List of (code, name) tuples for provinces
    cities : list
        List of (code, name) tuples for cities

    Returns:
    --------
    list : Flat list of metadata dictionaries
    """
    flat_metadata = []
    entry_id = 1

    # For each database code
    for dbcode, db_info in DATABASE_CODES.items():
        scope = db_info['scope']

        # For each indicator
        for indicator in indicators:
            # Determine which regions to use based on scope
            if scope == 'national':
                # National data - no region
                entry = {
                    'id': entry_id,
                    'Key': indicator['code'],
                    'Desc': indicator['desc'],
                    'Component_Key': indicator.get('parent_code', ''),
                    'Component_Desc': indicator.get('parent_desc', ''),
                    'Frequency_Key': dbcode,
                    'Frequency_Desc': f"{db_info['scope_cn']}{db_info['frequency_cn']}",
                    'Frequency_EN': f"{db_info['scope_en']} {db_info['frequency_en']}",
                    'Scope': scope,
                    'Scope_CN': db_info['scope_cn'],
                    'Scope_EN': db_info['scope_en'],
                    'full_variable': indicator['desc'],
                    'full_variable_with_freq': f"{indicator['desc']} ({db_info['scope_cn']}{db_info['frequency_cn']})",
                    'src': 'stats.gov.cn',
                    'source': 'National Bureau of Statistics of China',
                    'source_cn': '中华人民共和国国家统计局',
                    'dataset': dbcode,
                    'dataset_scope': scope,
                    'dataset_frequency': db_info['frequency'],
                    'Year': 'ALL',
                    'level': indicator.get('level', 1)
                }
                flat_metadata.append(entry)
                entry_id += 1

            elif scope == 'provincial':
                # Provincial data - add each province
                for region_code, region_name in regions:
                    entry = {
                        'id': entry_id,
                        'Key': indicator['code'],
                        'Desc': indicator['desc'],
                        'Component_Key': indicator.get('parent_code', ''),
                        'Component_Desc': indicator.get('parent_desc', ''),
                        'Frequency_Key': dbcode,
                        'Frequency_Desc': f"{db_info['scope_cn']}{db_info['frequency_cn']}",
                        'Frequency_EN': f"{db_info['scope_en']} {db_info['frequency_en']}",
                        'Scope': scope,
                        'Scope_CN': db_info['scope_cn'],
                        'Scope_EN': db_info['scope_en'],
                        'Region_Key': region_code,
                        'Region_Desc': region_name,
                        'full_variable': f"{indicator['desc']} - {region_name}",
                        'full_variable_with_freq': f"{indicator['desc']} - {region_name} ({db_info['scope_cn']}{db_info['frequency_cn']})",
                        'src': 'stats.gov.cn',
                        'source': 'National Bureau of Statistics of China',
                        'source_cn': '中华人民共和国国家统计局',
                        'dataset': dbcode,
                        'dataset_scope': scope,
                        'dataset_frequency': db_info['frequency'],
                        'Year': 'ALL',
                        'level': indicator.get('level', 1)
                    }
                    flat_metadata.append(entry)
                    entry_id += 1

            elif scope == 'city':
                # City data - add each city
                for city_code, city_name in cities:
                    entry = {
                        'id': entry_id,
                        'Key': indicator['code'],
                        'Desc': indicator['desc'],
                        'Component_Key': indicator.get('parent_code', ''),
                        'Component_Desc': indicator.get('parent_desc', ''),
                        'Frequency_Key': dbcode,
                        'Frequency_Desc': f"{db_info['scope_cn']}{db_info['frequency_cn']}",
                        'Frequency_EN': f"{db_info['scope_en']} {db_info['frequency_en']}",
                        'Scope': scope,
                        'Scope_CN': db_info['scope_cn'],
                        'Scope_EN': db_info['scope_en'],
                        'Region_Key': city_code,
                        'Region_Desc': city_name,
                        'full_variable': f"{indicator['desc']} - {city_name}",
                        'full_variable_with_freq': f"{indicator['desc']} - {city_name} ({db_info['scope_cn']}{db_info['frequency_cn']})",
                        'src': 'stats.gov.cn',
                        'source': 'National Bureau of Statistics of China',
                        'source_cn': '中华人民共和国国家统计局',
                        'dataset': dbcode,
                        'dataset_scope': scope,
                        'dataset_frequency': db_info['frequency'],
                        'Year': 'ALL',
                        'level': indicator.get('level', 1)
                    }
                    flat_metadata.append(entry)
                    entry_id += 1

    return flat_metadata


def main():
    """Main function to parse README and build master variables list."""
    print("=" * 80)
    print("PARSING README TO BUILD MASTER VARIABLES LIST")
    print("=" * 80)
    print()

    # Read README
    print("Reading README.md...")
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Parse indicator codes
    print("Parsing indicator codes...")
    indicators_raw = parse_readme_table(
        readme_content,
        start_marker='## 指标代码',
        end_marker='## 分省地区代码'
    )
    print(f"  Found {len(indicators_raw)} indicator codes")

    # Parse indicator hierarchy
    print("Building indicator hierarchy...")
    indicators = parse_indicator_hierarchy(indicators_raw)
    print(f"  Processed {len(indicators)} indicators with hierarchy")

    # Parse provincial region codes
    print("Parsing provincial region codes...")
    regions = parse_readme_table(
        readme_content,
        start_marker='## 分省地区代码',
        end_marker='## 主要城市代码'
    )
    print(f"  Found {len(regions)} provincial regions")

    # Parse city codes
    print("Parsing city codes...")
    cities = parse_readme_table(
        readme_content,
        start_marker='## 主要城市代码'
    )
    print(f"  Found {len(cities)} cities")

    # Build flat metadata
    print("\nBuilding comprehensive metadata...")
    metadata = build_flat_metadata(indicators, regions, cities)
    print(f"  Generated {len(metadata):,} total metadata entries")

    # Calculate statistics
    stats = {
        'generated_at': datetime.now().isoformat(),
        'total_entries': len(metadata),
        'total_indicators': len(indicators),
        'total_regions': len(regions),
        'total_cities': len(cities),
        'total_databases': len(DATABASE_CODES),
        'by_scope': {
            'national': len([m for m in metadata if m['Scope'] == 'national']),
            'provincial': len([m for m in metadata if m['Scope'] == 'provincial']),
            'city': len([m for m in metadata if m['Scope'] == 'city'])
        },
        'by_frequency': {
            'monthly': len([m for m in metadata if m['dataset_frequency'] == 'monthly']),
            'quarterly': len([m for m in metadata if m['dataset_frequency'] == 'quarterly']),
            'annual': len([m for m in metadata if m['dataset_frequency'] == 'annual'])
        }
    }

    # Save master variables list
    output_file = 'master_variables_list.json'
    print(f"\nSaving master variables list to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ Successfully saved {len(metadata):,} entries")

    # Save statistics
    stats_file = 'master_variables_stats.json'
    print(f"Saving statistics to {stats_file}...")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✓ Statistics saved")

    # Save a sample for inspection
    sample_file = 'master_variables_sample.json'
    print(f"Saving sample (first 10 entries) to {sample_file}...")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(metadata[:10], f, ensure_ascii=False, indent=2)
    print(f"✓ Sample saved")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total indicator codes:      {stats['total_indicators']:>6,}")
    print(f"Total provincial regions:   {stats['total_regions']:>6,}")
    print(f"Total cities:               {stats['total_cities']:>6,}")
    print(f"Total database types:       {stats['total_databases']:>6,}")
    print()
    print("Breakdown by scope:")
    print(f"  National entries:         {stats['by_scope']['national']:>6,}")
    print(f"  Provincial entries:       {stats['by_scope']['provincial']:>6,}")
    print(f"  City entries:             {stats['by_scope']['city']:>6,}")
    print()
    print("Breakdown by frequency:")
    print(f"  Monthly entries:          {stats['by_frequency']['monthly']:>6,}")
    print(f"  Quarterly entries:        {stats['by_frequency']['quarterly']:>6,}")
    print(f"  Annual entries:           {stats['by_frequency']['annual']:>6,}")
    print()
    print(f"Total metadata entries:     {stats['total_entries']:>6,}")
    print("=" * 80)

    return metadata, stats


if __name__ == '__main__':
    metadata, stats = main()
