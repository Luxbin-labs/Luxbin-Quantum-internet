# Wallet Logo Setup Guide - LUXBIN (LUX)

**Goal:** Make your golden dragon logo appear in MetaMask, Coinbase Wallet, Trust Wallet, and all other wallets

**Your Logo:** `/Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission/luxbin.png`
- Size: 192x192 (should be 200x200 ideally)
- Format: PNG ✅
- File size: 47KB ✅

---

## Where Token Logos Come From

Wallets pull token logos from multiple sources:

1. **Base Ecosystem** - Coinbase Wallet pulls from here
2. **Token Lists** - Uniswap, CoinGecko, CMC aggregators
3. **Trust Wallet Assets** - Trust Wallet, MetaMask Mobile
4. **Token Metadata** - Some wallets query contract

---

## ✅ Step 1: Base Ecosystem (Already Done!)

You already submitted to Base:
- File: `/Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission/`
- Status: Submitted ✅

**When it goes live:**
- Coinbase Wallet will show your logo
- Base ecosystem directory will display it
- Usually takes 1-2 weeks to appear

**To check status:**
Look for your submission PR at: https://github.com/base-org/web/pulls

---

## ⚠️ Step 2: Resize Logo to 200x200 (Recommended)

Most platforms want exactly 200x200. Let's create that:

```bash
# Resize your logo to 200x200
sips -z 200 200 /Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission/luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission/luxbin-200x200.png
```

This creates a 200x200 version without modifying your original.

---

## 📋 Step 3: Trust Wallet Assets Repository

Trust Wallet is the most widely used token list. MetaMask Mobile pulls from here.

### How to Submit:

**1. Fork the Repository**
```bash
cd ~
git clone https://github.com/trustwallet/assets.git
cd assets
git checkout master
```

**2. Create Your Token Directory**
```bash
# Base is network "8453"
mkdir -p blockchains/base/assets/0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0
```

**3. Copy Your Logo**
```bash
# Must be named "logo.png" and be 256x256
sips -z 256 256 /Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission/luxbin.png --out ~/assets/blockchains/base/assets/0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0/logo.png
```

**4. Create info.json**
```bash
cat > ~/assets/blockchains/base/assets/0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0/info.json << 'EOF'
{
  "name": "LUXBIN Quantum Token",
  "type": "ERC20",
  "symbol": "LUX",
  "decimals": 18,
  "website": "https://github.com/mermaidnicheboutique-code/luxbin-quantum-internet",
  "description": "First cryptocurrency backed by 445 qubits from IBM quantum computers. Quantum-secured DeFi with deflationary burns, auto-rewards, and provably fair lottery.",
  "explorer": "https://basescan.org/token/0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0",
  "status": "active",
  "id": "0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0",
  "links": [
    {
      "name": "github",
      "url": "https://github.com/mermaidnicheboutique-code/luxbin-quantum-internet"
    },
    {
      "name": "twitter",
      "url": "https://twitter.com/LuxbinQuantum"
    },
    {
      "name": "telegram",
      "url": "https://t.me/luxbinofficial"
    },
    {
      "name": "coinmarketcap",
      "url": "https://coinmarketcap.com/currencies/luxbin-quantum-token/"
    },
    {
      "name": "coingecko",
      "url": "https://www.coingecko.com/en/coins/luxbin-quantum-token"
    }
  ],
  "tags": [
    "defi",
    "staking",
    "quantum"
  ]
}
EOF
```

**5. Commit and Create PR**
```bash
cd ~/assets
git add blockchains/base/assets/0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0
git commit -m "Add LUXBIN Quantum Token (LUX) on Base"
git push origin master

# Then go to GitHub and create Pull Request to trustwallet/assets
```

**6. Wait for Approval**
- Usually takes 3-7 days
- They'll review logo quality and contract verification
- Once merged, logo appears in Trust Wallet, MetaMask Mobile, many others

**Repository:** https://github.com/trustwallet/assets

---

## 📋 Step 4: CoinGecko Logo (When Applying)

When you apply to CoinGecko, they ask for logo URL.

**Option A: Host on GitHub**
```bash
# Add to your repo
mkdir -p /Users/nicholechristie/luxbin-quantum-internet/assets
cp /Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission/luxbin.png /Users/nicholechristie/luxbin-quantum-internet/assets/logo-200x200.png

# Commit to GitHub
cd /Users/nicholechristie/luxbin-quantum-internet
git add assets/logo-200x200.png
git commit -m "Add token logo for CoinGecko"
git push

# Use this URL in CoinGecko application:
# https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png
```

**Option B: Upload Directly**
CoinGecko allows direct upload during application. Use your 200x200 version.

**Requirements:**
- 200x200 pixels
- PNG format
- Transparent background (yours has dark purple, that's OK)
- Under 200KB (yours is 47KB ✅)

---

## 📋 Step 5: CoinMarketCap Logo (When Applying)

Similar to CoinGecko.

**Logo URL for CMC:**
```
https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png
```

Or upload directly when applying.

**Requirements:**
- 200x200 pixels (minimum)
- PNG format
- Transparent background recommended
- Under 5MB (yours is 47KB ✅)

---

## 📋 Step 6: Uniswap Token List (Optional)

Uniswap has its own token list system.

**Create a token list JSON:**

```bash
cat > /Users/nicholechristie/luxbin-quantum-internet/luxbin-tokenlist.json << 'EOF'
{
  "name": "LUXBIN Token List",
  "timestamp": "2026-01-10T00:00:00.000Z",
  "version": {
    "major": 1,
    "minor": 0,
    "patch": 0
  },
  "tags": {},
  "logoURI": "https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png",
  "keywords": ["luxbin", "quantum", "defi"],
  "tokens": [
    {
      "chainId": 8453,
      "address": "0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0",
      "name": "LUXBIN Quantum Token",
      "symbol": "LUX",
      "decimals": 18,
      "logoURI": "https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png"
    }
  ]
}
EOF

# Commit to GitHub
cd /Users/nicholechristie/luxbin-quantum-internet
git add luxbin-tokenlist.json
git commit -m "Add Uniswap token list"
git push
```

**Token list URL:**
```
https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/luxbin-tokenlist.json
```

Users can manually add this to Uniswap to see your token with logo.

---

## 🎨 Logo Versions You Should Create

Create multiple sizes for different platforms:

```bash
cd /Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission

# Create assets directory
mkdir -p /Users/nicholechristie/luxbin-quantum-internet/assets

# 200x200 (CoinGecko, CMC, most exchanges)
sips -z 200 200 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-200x200.png

# 256x256 (Trust Wallet requirement)
sips -z 256 256 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-256x256.png

# 512x512 (High resolution for websites)
sips -z 512 512 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-512x512.png

# 64x64 (Small icon version)
sips -z 64 64 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-64x64.png

# Original (keep for reference)
cp luxbin.png /Users/nicholechristie/luxbin-quantum-internet/assets/logo-original.png
```

---

## 📋 Quick Checklist - Do This Now

### Immediate (Before Twitter):
- [ ] **Resize logo to 200x200** for CoinGecko/CMC
- [ ] **Resize logo to 256x256** for Trust Wallet
- [ ] **Create assets directory** in your GitHub repo
- [ ] **Commit logos to GitHub** for hosting

### Within 24 Hours:
- [ ] **Submit to Trust Wallet** (biggest impact for MetaMask Mobile)
- [ ] **Apply to CoinGecko** (will pull your logo)
- [ ] **Create token list JSON** for Uniswap

### Within 1 Week:
- [ ] **Apply to CoinMarketCap** (logo displays after approval)
- [ ] **Check Base ecosystem PR** status
- [ ] **Monitor Trust Wallet PR** status

---

## 🔍 How to Verify Logo is Working

### MetaMask (Desktop)
- Import token: 0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0
- Logo won't show until CoinGecko or Trust Wallet approval

### MetaMask (Mobile)
- Uses Trust Wallet assets
- Shows after Trust Wallet PR merged

### Coinbase Wallet
- Uses Base ecosystem
- Shows after Base submission approved (1-2 weeks)

### Trust Wallet
- Shows after Trust Wallet PR merged (3-7 days)

### Uniswap Interface
- Shows if token is in a token list
- Or after CoinGecko lists you

---

## 🎯 Expected Timeline

| Platform | Submission Time | Approval Time | Total |
|----------|----------------|---------------|-------|
| **Base Ecosystem** | Done ✅ | 1-2 weeks | ~2 weeks |
| **Trust Wallet** | 30 min | 3-7 days | ~1 week |
| **CoinGecko** | 10 min | 1-2 weeks | ~2 weeks |
| **CoinMarketCap** | 10 min | 2-4 weeks | ~3 weeks |

**Fastest path to wallet logos:**
1. Trust Wallet submission (shows in MetaMask Mobile)
2. CoinGecko listing (shows in many aggregators)

---

## 🚨 Common Issues

### Issue: Logo not showing in MetaMask Desktop
**Solution:** MetaMask Desktop doesn't automatically pull logos. Users must:
1. Import token manually
2. Wait for CoinGecko/CMC listing
3. Or use token list

### Issue: Trust Wallet rejects PR
**Common reasons:**
- Logo not 256x256 exactly
- Logo file size too large (>100KB)
- Contract not verified
- Poor quality image

**Fix:** Resize to exact 256x256, compress if needed

### Issue: Logo shows as generic icon
**Solution:** Wait for approval from Trust Wallet or CoinGecko. Takes time.

---

## 📝 Commands to Run Now

Run these commands to set everything up:

```bash
# 1. Create assets directory
mkdir -p /Users/nicholechristie/luxbin-quantum-internet/assets

# 2. Create all logo sizes
cd /Users/nicholechristie/luxbin-quantum-internet/base-ecosystem-submission

sips -z 200 200 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-200x200.png
sips -z 256 256 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-256x256.png
sips -z 512 512 luxbin.png --out /Users/nicholechristie/luxbin-quantum-internet/assets/logo-512x512.png

# 3. Create token list
cat > /Users/nicholechristie/luxbin-quantum-internet/luxbin-tokenlist.json << 'EOF'
{
  "name": "LUXBIN Token List",
  "timestamp": "2026-01-10T00:00:00.000Z",
  "version": {
    "major": 1,
    "minor": 0,
    "patch": 0
  },
  "logoURI": "https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png",
  "keywords": ["luxbin", "quantum", "defi"],
  "tokens": [
    {
      "chainId": 8453,
      "address": "0xbB5bf2139CbACDeE52991cf32f9c4d558B9464d0",
      "name": "LUXBIN Quantum Token",
      "symbol": "LUX",
      "decimals": 18,
      "logoURI": "https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png"
    }
  ]
}
EOF

# 4. Commit to GitHub
cd /Users/nicholechristie/luxbin-quantum-internet
git add assets/ luxbin-tokenlist.json
git commit -m "Add token logos and Uniswap token list"
git push origin main

# 5. Get logo URLs for applications
echo "Your logo URLs:"
echo "200x200: https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png"
echo "256x256: https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-256x256.png"
echo "512x512: https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-512x512.png"
```

---

## ✅ After Running Commands

You'll have:
- ✅ Multiple logo sizes ready
- ✅ Logos hosted on GitHub (public URLs)
- ✅ Token list JSON for Uniswap
- ✅ Ready for Trust Wallet submission
- ✅ Ready for CoinGecko/CMC applications

**Logo URLs to use everywhere:**
- CoinGecko: `https://raw.githubusercontent.com/mermaidnicheboutique-code/luxbin-quantum-internet/main/assets/logo-200x200.png`
- CMC: Same URL
- Trust Wallet: You'll upload the 256x256 file directly
- Social media: Use 512x512 for high quality

---

## 🎯 Priority Order

**Do this in order for fastest wallet logo display:**

1. **NOW:** Run the commands above to create logo versions
2. **TODAY:** Submit to Trust Wallet (biggest impact)
3. **TODAY:** Apply to CoinGecko (include logo URL)
4. **TOMORROW:** Apply to CoinMarketCap (include logo URL)
5. **THIS WEEK:** Monitor PRs and respond to any feedback

---

## 📞 Need Help?

If Trust Wallet or other platforms reject your logo:
1. Check requirements (exact size, file format)
2. Compress if too large: `pngquant logo.png --output logo-compressed.png`
3. Verify contract is verified on BaseScan
4. Read rejection message carefully and fix issue

---

**Ready to set up your logos? Run the commands above, then we'll start the Twitter account! 🚀**
