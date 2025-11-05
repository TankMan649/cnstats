# Proxy Setup Guide for stats.gov.cn API Access

## Problem

The stats.gov.cn API blocks requests from non-Chinese IP addresses with **403 Forbidden** errors. This prevents direct API access for discovering all available variables.

## Investigation Results

We tested multiple approaches to bypass the blocking:

| Method | Result | Notes |
|--------|--------|-------|
| Different User-Agents | ✗ Failed | Tried Chrome, Firefox, Safari, Chinese browsers |
| Session/Cookie management | ✗ Failed | Cannot establish session without valid IP |
| HTTP Headers modification | ✗ Failed | Application-level blocking, not header-based |
| Direct curl requests | ✗ Failed | Command-line tools also blocked |

**Conclusion:** The blocking is **IP-based geofencing**, likely implemented via a Web Application Firewall (WAF). A proxy or VPN with a Chinese IP address is required.

## Solutions

### Option 1: Paid Proxy Services (Recommended)

Professional proxy services offer reliable Chinese IP addresses with high uptime.

#### Recommended Providers

**International Providers:**

1. **Bright Data (formerly Luminati)** - https://brightdata.com
   - ✓ Residential & datacenter IPs in China
   - ✓ Rotating and sticky sessions
   - ✓ Good documentation
   - Price: ~$500/month for residential, ~$250/month for datacenter
   - Setup: HTTP/SOCKS5 proxy with authentication

2. **Oxylabs** - https://oxylabs.io
   - ✓ Chinese residential IPs
   - ✓ Good for web scraping
   - Price: ~$300-600/month
   - Setup: HTTP/SOCKS5 proxy

3. **Smartproxy** - https://smartproxy.com
   - ✓ Chinese residential IPs
   - ✓ Lower cost option
   - Price: ~$75-150/month
   - Setup: HTTP/SOCKS5 proxy

**Chinese Providers (May require Chinese business registration):**

1. **快代理 (Kuaidaili)** - https://www.kuaidaili.com
   - ✓ Domestic Chinese proxy service
   - ✓ Lower latency for Chinese sites
   - Price: ¥200-500/month (~$30-75)

2. **芝麻代理 (Zhima Proxy)** - http://www.zhimaruanjian.com
   - ✓ Popular Chinese proxy service
   - ✓ Good for government sites
   - Price: ¥100-300/month (~$15-45)

3. **阿布云 (Abuyun)** - https://www.abuyun.com
   - ✓ Dynamic residential IPs
   - ✓ Good coverage in China
   - Price: ¥200+/month

#### Setup Example (Bright Data):

```python
# After purchasing Bright Data service
proxy_url = "http://brd-customer-USERNAME:PASSWORD@brd.superproxy.io:22225"

# Test the proxy
python test_with_proxy.py --proxy $proxy_url

# Use with discovery script
python build_master_variables_list_with_proxy.py --proxy $proxy_url
```

### Option 2: VPN with Chinese Servers

Some VPN services offer Chinese server locations.

**Providers:**
- **ExpressVPN** - Has Hong Kong servers (may work)
- **NordVPN** - No mainland China servers
- **Private Internet Access** - Limited China access

**Limitations:**
- Government websites may block known VPN IP ranges
- Connection may be slower and less reliable
- Some VPNs are blocked in China

**Setup:**
1. Connect to VPN with Chinese/Hong Kong server
2. Run discovery script normally (no proxy parameter needed)

### Option 3: Cloud VM in China

Deploy the script on a cloud server hosted in China.

**Providers:**
- **Alibaba Cloud** - https://www.alibabacloud.com
- **Tencent Cloud** - https://intl.cloud.tencent.com
- **Huawei Cloud** - https://www.huaweicloud.com

**Pros:**
- Native Chinese IP address
- No proxy configuration needed
- Fast connection to government sites

**Cons:**
- Requires Chinese business registration for some services
- Monthly VM costs (~$5-20/month for small instance)
- Need to set up Python environment on VM

**Setup:**
```bash
# On the Chinese VM
git clone https://github.com/TankMan649/cnstats.git
cd cnstats
pip install -r requirements.txt
python build_master_variables_list.py  # No proxy needed!
```

### Option 4: SSH Tunnel (If you have access to a server in China)

If you have SSH access to any server in China, you can create a SOCKS proxy.

**Setup:**
```bash
# On your local machine, create SSH tunnel
ssh -D 1080 -N user@your-server-in-china.com

# In another terminal, use the local SOCKS proxy
python test_with_proxy.py --proxy socks5://localhost:1080

# If it works, use with discovery
python build_master_variables_list_with_proxy.py --proxy socks5://localhost:1080
```

**Note:** Requires PySocks library for SOCKS support:
```bash
pip install pysocks
```

### Option 5: Free Proxies (Not Recommended)

Free Chinese proxies can be found on various websites, but they are:
- ✗ Unreliable (frequent downtime)
- ✗ Slow (high latency)
- ✗ Often blocked
- ✗ Security risk (untrusted third parties)
- ✗ Limited availability

**Sources for free proxies:**
- https://www.proxy-list.download/HTTPS/CN
- https://free-proxy-list.net/
- https://spys.one/free-proxy-list/CN/

## Usage Instructions

### Testing Your Proxy

Before running the full discovery, test if your proxy works:

```bash
# Test proxy connection
python test_with_proxy.py --proxy http://your-proxy:port

# Expected output if successful:
# ✓ Main page accessible!
# ✓ SUCCESS! Valid JSON response received!
```

### Running Discovery with Proxy

Once your proxy is verified:

```bash
# Run full API discovery with proxy
python build_master_variables_list_with_proxy.py --proxy http://your-proxy:port

# Or with SOCKS5
python build_master_variables_list_with_proxy.py --proxy socks5://your-proxy:port

# With authentication
python build_master_variables_list_with_proxy.py --proxy http://username:password@proxy:port

# Custom output filename
python build_master_variables_list_with_proxy.py \
    --proxy http://your-proxy:port \
    --output my_variables_list.json
```

### Python Code Example

```python
from cnstats.common_proxy import easyquery, set_proxy

# Configure proxy
set_proxy('http://your-proxy:port')

# Now all API calls will use the proxy
response = easyquery(m='getTree', dbcode='hgyd', wdcode='zb', id='zb')
print(response)
```

## Cost Comparison

| Solution | Monthly Cost | Reliability | Setup Complexity |
|----------|-------------|-------------|------------------|
| Bright Data (residential) | $500+ | ★★★★★ | Low |
| Bright Data (datacenter) | $250+ | ★★★★☆ | Low |
| Oxylabs | $300-600 | ★★★★★ | Low |
| Smartproxy | $75-150 | ★★★★☆ | Low |
| Chinese proxies | $15-75 | ★★★★☆ | Medium |
| Cloud VM (Alibaba) | $5-20 | ★★★★★ | High |
| VPN | $5-15 | ★★☆☆☆ | Low |
| Free proxies | $0 | ★☆☆☆☆ | High |

## Recommendations

**For one-time use:**
- Use a cheap VPS in China for 1 month (~$5-10)
- Or try Smartproxy for 1 month (~$75)

**For regular updates:**
- Cloud VM in China (most cost-effective long-term)
- Or Chinese proxy service (~$30/month)

**For commercial/production use:**
- Bright Data or Oxylabs (most reliable)
- Includes support and SLA guarantees

## Troubleshooting

### "ProxyError: Cannot connect to proxy"
- Check if proxy URL is correct
- Verify proxy server is running
- Test with curl: `curl -x http://proxy:port https://www.google.com`

### "Timeout Error"
- Proxy may be slow or overloaded
- Increase timeout in script
- Try different proxy server

### Still getting 403 errors with proxy
- Proxy IP may be blacklisted
- Try different proxy server/location
- Ensure proxy is actually routing through China

### "DNS resolution failed"
- Use IP address instead of hostname
- Configure DNS to use proxy's DNS

### SOCKS proxy not working
- Install PySocks: `pip install pysocks`
- Use format: `socks5://host:port` (not `socks://`)

## Alternative: Using the README-based List

If proxy access is not feasible, you can use the master variables list generated from the README documentation (currently available in the repository):

```bash
# Extract the compressed file
gunzip master_variables_list.json.gz

# Or regenerate from README
python parse_readme_to_master_list.py
```

This gives you **all documented variables** (181,692 entries), but may miss any **undocumented variables** that only exist in the API.

## Security Considerations

**When using proxies:**
- ✓ Use HTTPS for proxy connection when possible
- ✓ Only use proxies from trusted providers
- ✓ Avoid sending sensitive data through free proxies
- ✓ Monitor for unusual billing or usage patterns
- ✓ Rotate credentials regularly

**When using cloud VMs:**
- ✓ Keep software updated
- ✓ Use SSH keys instead of passwords
- ✓ Configure firewall properly
- ✓ Don't store sensitive credentials on VM
- ✓ Delete VM when finished to avoid ongoing charges

## Support

If you encounter issues:

1. Run diagnostic: `python test_with_proxy.py --diagnostic`
2. Test proxy: `python test_with_proxy.py --proxy YOUR_PROXY`
3. Check proxy provider's documentation
4. Open an issue in the repository with details

## Files

- `test_with_proxy.py` - Test proxy connectivity to stats.gov.cn
- `build_master_variables_list_with_proxy.py` - Discovery script with proxy support
- `cnstats/common_proxy.py` - Proxy-enabled API client
- `investigate_api_access.py` - Diagnostic tool for API access issues

---

**Last Updated:** 2025-11-05
