# Master Variables List for stats.gov.cn

## Overview

This directory contains a comprehensive master variables list for the Chinese National Bureau of Statistics (stats.gov.cn) API, generated from all documented indicator codes, regions, and database types.

## Files

### Generated Files

- **`master_variables_list.json.gz`** (181,692 entries, 4.2MB compressed)
  - Complete flat JSON metadata structure with all variable combinations
  - Format matches the requested BEA-style structure with Chinese descriptions
  - **Compressed** - Extract with: `gunzip master_variables_list.json.gz`
  - **Note:** The uncompressed JSON file (150MB) is not included in the repository due to GitHub's 100MB file size limit

- **`master_variables_stats.json`**
  - Statistics about the generated master list
  - Breakdown by scope, frequency, and database type

- **`master_variables_sample.json`**
  - Sample of first 10 entries for quick inspection
  - Useful for understanding the data structure

### Scripts

- **`parse_readme_to_master_list.py`**
  - Main script that parses README.md and generates the master variables list
  - Extracts indicator codes, provincial regions, and city codes
  - Builds comprehensive metadata with all combinations

- **`build_master_variables_list.py`**
  - API-based discovery script (currently blocked by 403 errors)
  - Designed to recursively discover ALL variables from the API
  - Can be used once API access is resolved

- **`test_discovery.py`**
  - Test script to validate API access and discovery approach
  - Useful for debugging API connectivity issues

- **`debug_api.py`**
  - Debug script to inspect raw API responses
  - Helps diagnose API access issues

## Master Variables List Structure

The master variables list follows a flat JSON structure with the following fields:

```json
{
  "id": 1,
  "Key": "A010101",
  "Desc": "全国居民消费价格分类指数(上年同月=100)(2016-)",
  "Component_Key": "A0101",
  "Component_Desc": "居民消费价格分类指数(上年同月=100)",
  "Frequency_Key": "hgyd",
  "Frequency_Desc": "宏观月度",
  "Frequency_EN": "National Monthly",
  "Scope": "national",
  "Scope_CN": "宏观",
  "Scope_EN": "National",
  "full_variable": "全国居民消费价格分类指数(上年同月=100)(2016-)",
  "full_variable_with_freq": "全国居民消费价格分类指数(上年同月=100)(2016-) (宏观月度)",
  "src": "stats.gov.cn",
  "source": "National Bureau of Statistics of China",
  "source_cn": "中华人民共和国国家统计局",
  "dataset": "hgyd",
  "dataset_scope": "national",
  "dataset_frequency": "monthly",
  "Year": "ALL",
  "level": 5
}
```

### For Provincial/City Data:

```json
{
  "id": 1765,
  "Key": "A01",
  "Desc": "价格指数",
  "Component_Key": "",
  "Component_Desc": "",
  "Frequency_Key": "fsyd",
  "Frequency_Desc": "分省月度",
  "Frequency_EN": "Provincial Monthly",
  "Scope": "provincial",
  "Scope_CN": "分省",
  "Scope_EN": "Provincial",
  "Region_Key": "110000",
  "Region_Desc": "北京市",
  "full_variable": "价格指数 - 北京市",
  "full_variable_with_freq": "价格指数 - 北京市 (分省月度)",
  "src": "stats.gov.cn",
  "source": "National Bureau of Statistics of China",
  "source_cn": "中华人民共和国国家统计局",
  "dataset": "fsyd",
  "dataset_scope": "provincial",
  "dataset_frequency": "monthly",
  "Year": "ALL",
  "level": 1
}
```

## Statistics

### Source Data
- **588 indicator codes** from README.md documentation
- **31 provincial regions** (including autonomous regions and municipalities)
- **71 cities** (major cities with statistical data)
- **9 database types** (3 scopes × 3 frequencies)

### Generated Metadata

| Breakdown | Count |
|-----------|-------|
| **Total Entries** | **181,692** |
| | |
| **By Scope** | |
| National entries | 1,764 |
| Provincial entries | 54,684 |
| City entries | 125,244 |
| | |
| **By Frequency** | |
| Monthly entries | 60,564 |
| Quarterly entries | 60,564 |
| Annual entries | 60,564 |

### Database Codes

| Code | Scope | Frequency | Scope (CN) | Frequency (CN) |
|------|-------|-----------|------------|----------------|
| `hgyd` | National | Monthly | 宏观 | 月度 |
| `hgjd` | National | Quarterly | 宏观 | 季度 |
| `hgnd` | National | Annual | 宏观 | 年度 |
| `fsyd` | Provincial | Monthly | 分省 | 月度 |
| `fsjd` | Provincial | Quarterly | 分省 | 季度 |
| `fsnd` | Provincial | Annual | 分省 | 年度 |
| `csyd` | City | Monthly | 城市 | 月度 |
| `csjd` | City | Quarterly | 城市 | 季度 |
| `csnd` | City | Annual | 城市 | 年度 |

## Usage

### Extracting the Compressed File

First, extract the compressed master variables list:

```bash
gunzip master_variables_list.json.gz
```

Or, if you want to keep the compressed file:

```bash
gunzip -k master_variables_list.json.gz
```

Alternatively, you can generate it from scratch:

```bash
python parse_readme_to_master_list.py
```

### Querying the Master List

```python
import json

# Load the master variables list
with open('master_variables_list.json', 'r', encoding='utf-8') as f:
    variables = json.load(f)

# Filter by indicator code
cpi_vars = [v for v in variables if v['Key'].startswith('A01')]

# Filter by region
beijing_vars = [v for v in variables if v.get('Region_Key') == '110000']

# Filter by frequency
monthly_vars = [v for v in variables if v['dataset_frequency'] == 'monthly']

# Filter by scope
national_vars = [v for v in variables if v['Scope'] == 'national']
```

### Using with cnstats Package

```python
from cnstats.stats import stats

# Query using parameters from the master list
# Example: CPI for Beijing, January 2023
result = stats(
    zbcode='A01010101',  # From 'Key' field
    datestr='202301',
    regcode='110000',    # From 'Region_Key' field
    dbcode='fsyd'        # From 'dataset' field
)
```

## Data Coverage

### Major Indicator Categories (A-level codes)

| Code | Description (CN) | Description (EN) |
|------|------------------|------------------|
| A01 | 价格指数 | Price Indices |
| A02 | 工业 | Industry |
| A03 | 能源 | Energy |
| A04 | 固定资产投资(不含农户) | Fixed Asset Investment |
| A05 | 服务业生产指数 | Service Industry Production Index |
| A0E | 城镇调查失业率 | Urban Survey Unemployment Rate |
| A06 | 房地产 | Real Estate |
| A07 | 国内贸易 | Domestic Trade |
| A08 | 对外经济 | Foreign Trade |
| A09 | 交通运输 | Transportation |
| A0A | 邮电通信 | Postal & Telecom |
| A0B | 采购经理指数 | Purchasing Manager Index (PMI) |
| A0C | 财政 | Finance |
| A0D | 金融 | Monetary |

### Geographic Coverage

**Provincial Coverage:** All 31 provinces, autonomous regions, and municipalities directly under central government

**City Coverage:** 71 major cities including:
- 4 municipalities: Beijing, Tianjin, Shanghai, Chongqing
- 27 provincial capitals
- 40 other important cities

## Regenerating the Master List

To regenerate the master variables list from the latest README:

```bash
python parse_readme_to_master_list.py
```

This will:
1. Parse indicator codes from README.md
2. Parse provincial and city codes from README.md
3. Build hierarchy information for indicators
4. Generate all combinations of indicators × databases × regions
5. Save to `master_variables_list.json`

## Future: API-Based Discovery

### Current Issue

The stats.gov.cn API currently returns **403 Access Denied** errors when accessed from automated scripts. This prevents direct discovery of undocumented variables from the API.

### Resolution Steps

Once API access is resolved (through proper authentication, session management, or IP whitelisting):

1. **Run the test script:**
   ```bash
   python test_discovery.py
   ```
   This validates that the API is accessible.

2. **Run the full discovery script:**
   ```bash
   python build_master_variables_list.py
   ```
   This will:
   - Recursively discover ALL indicator codes from the API tree structure
   - Query all region codes for each database type
   - Discover potentially undocumented variables
   - Generate a more comprehensive master list

### Discovery Approach

The API-based discovery uses:
- **`getTree` method** - Recursively retrieves hierarchical indicator codes
- **Region queries** - Discovers all available regions for each database
- **Systematic iteration** - Covers all 9 database code combinations

### Potential for Undocumented Variables

The user correctly noted that there may be variables available through the API that are not documented in the README. The API discovery scripts are designed to find these by:

1. Recursively traversing the complete indicator tree for each database
2. Discovering region codes dynamically rather than relying on hardcoded lists
3. Identifying new indicators that may have been added since the README was last updated

## Limitations

### Current Limitations

1. **API Access Blocked** - Cannot currently discover undocumented variables due to 403 errors
2. **Static Source** - Master list is based on README documentation only
3. **No Data Validation** - Cannot verify which indicators actually return data
4. **No Date Range Info** - Cannot determine actual available date ranges for each variable

### Future Enhancements

Once API access is restored:

1. **Dynamic Discovery** - Automatically discover new indicators
2. **Data Availability Check** - Test which variables actually return data
3. **Date Range Detection** - Determine available date ranges for each variable
4. **Automatic Updates** - Scheduled regeneration of master list
5. **Change Detection** - Track additions and removals of variables over time

## API Authentication Notes

The stats.gov.cn API uses:
- **User-Agent** - Browser-like user agent required
- **Referer** - Proper referer header expected
- **Cookies** - Session cookies may be required
- **Rate Limiting** - May have rate limits or anti-scraping measures

To improve API access:
1. Consider using a proxy service based in China
2. Implement proper session management with cookie persistence
3. Add delays between requests to avoid rate limiting
4. Use browser automation (Selenium) if necessary to establish sessions

## Contributing

To add new indicator codes or regions:

1. Update README.md with new codes in the appropriate table
2. Run `python parse_readme_to_master_list.py` to regenerate
3. Validate the output in `master_variables_sample.json`
4. Commit both the README update and new master list

## License

This data structure is derived from public documentation of the Chinese National Bureau of Statistics API. See the main repository LICENSE file for details.

## Support

For issues or questions:
1. Check if the API is accessible: `python debug_api.py`
2. Review the generated statistics: `master_variables_stats.json`
3. Examine the sample output: `master_variables_sample.json`
4. Open an issue in the repository with details

---

**Generated:** 2025-11-05
**Version:** 1.0
**Total Variables:** 181,692
