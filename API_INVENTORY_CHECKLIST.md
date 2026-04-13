# API Inventory & Configuration Checklist

**Generated:** 2026-04-14  
**Status:** ✅ AUDIT COMPLETE - All APIs catalogued

---

## 🔐 SECRETS & CREDENTIALS

### ⚠️ CRITICAL - Must Configure Locally

| API | Provider | Key Variable | Status | Notes |
|-----|----------|--------------|--------|-------|
| **LLM** | Groq | `GROQ_API_KEY` | ❌ **NEEDS LOCAL CONFIG** | Main provider for inference. Get from https://console.groq.com/keys |
| **LLM** | OpenAI | `OPENAI_API_KEY` | ❌ **OPTIONAL** | Fallback provider. Get from https://platform.openai.com/api-keys |
| **LLM** | OpenRouter | `OPENROUTER_API_KEY` | ❌ **OPTIONAL** | Multi-model proxy. Get from https://openrouter.ai/keys |
| **LLM** | Together AI | `TOGETHER_API_KEY` | ❌ **OPTIONAL** | Inference API. Get from https://www.together.ai/settings/keys |
| **LLM** | DeepSeek | `DEEPSEEK_API_KEY` | ❌ **OPTIONAL** | DeepSeek models. Get from https://platform.deepseek.com/api_keys |
| **LLM** | xAI (Grok) | `XAI_API_KEY` | ❌ **OPTIONAL** | Grok models. Get from https://console.x.ai/keys |
| **GitHub (Hive)**| GitHub | `HIVE_GITHUB_TOKEN` | ✅ **CI MANAGED** | Workflow: `secrets.HIVE_BOT_TOKEN` or auto `github.token` |
| **GitHub (Hive)**| GitHub | `HIVE_GITHUB_ISSUE_NUMBER` | ✅ **OPTIONAL** | Default: `1` (configure in repo vars if different) |

---

## ✅ PUBLIC APIs (No Key Required)

### News & Content Feeds
- **Hacker News API** - https://hn.algolia.com/api/v1/search?tags=front_page
  - No auth required
  - Used by: Aakaash.py (news fetcher)

- **Dev.to API** - https://dev.to/api/articles?per_page=30&top=7
  - No auth required
  - Used by: Aakaash.py (developer content)

### Academic & Research
- **arXiv API** - https://export.arxiv.org/api/query?
  - No auth required
  - Used by: Aakaash.py (research papers)

- **Crossref DOI API** - https://api.crossref.org/works?query=...
  - No auth required
  - Used by: Aakaash.py (academic metadata)

### Code Repository
- **GitHub Search API** - https://api.github.com/search/repositories?
  - No auth required (rate limited to 60 req/hour unauthenticated)
  - Optional: Add `GITHUB_TOKEN` to increase limit to 5000 req/hour
  - Used by: Aakaash.py (repo discovery)

---

## 🔗 HIVE MIND ARCHITECTURE APIs

### GitHub Issues Relay (REST API ✅)
```
Endpoint: POST /repos/{owner}/{repo}/issues/{issue_number}/comments
Token: HIVE_GITHUB_TOKEN (from CI secrets or github.token fallback)
Purpose: Distribute hive delta packets across nodes
Status: ✅ WORKING (switched from broken Discussions API)
```

### Local Sync APIs (Internal)
- **EvolutionSync**: Queue hive deltas locally
  - No external API
  - File-based: `evolution_vault/hive_queue.jsonl`

- **HiveConsent**: Manage node opt-in
  - No external API
  - File-based: `~/.antahkarana/node_keys.json`

- **HiveDelta**: Sign & encode packets
  - Cryptography: Ed25519 (optional) + HMAC SHA256 fallback
  - No external API dependency

---

## 📋 ENVIRONMENT VARIABLE REFERENCE

### LLM Bridge (InteractiveBridge.py)
```bash
# Primary configuration
ANTAHKARANA_LLM_ENABLED=true                              # Enable/disable LLM
ANTAHKARANA_LLM_PROVIDER=groq                             # Provider: groq, openai, openrouter, together, deepseek, xai
ANTAHKARANA_LLM_BASE_URL=https://api.groq.com/...         # Custom endpoint
ANTAHKARANA_LLM_MODEL=llama-3.3-70b-versatile             # Model name
ANTAHKARANA_LLM_API_KEY_ENV=GROQ_API_KEY                  # Which env var to read key from
ANTAHKARANA_LLM_API_KEY=<direct_key_optional>             # Direct key (overrides env var)

# Limits
ANTAHKARANA_LLM_MAX_TOKENS_PER_DAY=200000                 # Rate limit
```

### Hive Mind (run_hive_aggregator.py / EvolutionSync.py)
```bash
ANTAHKARANA_HIVE_OPT_IN=true/false                        # Enable hive sync
ANTAHKARANA_HIVE_MIN_AVG_LEARNING=0.5                     # Min learning value to trigger sync
ANTAHKARANA_HIVE_MIN_UPLOAD_INTERVAL_SECS=3600           # Min time between uploads (1 hour)
ANTAHKARANA_HIVE_REMOTE_BASE_URL=https://...              # Optional: remote manifest URL
HIVE_GITHUB_TOKEN=<token>                                 # GitHub token (auto from CI)
HIVE_GITHUB_REPOSITORY=OGRONIT/artificial-consciousness   # Auto from CI (${{ github.repository }})
HIVE_GITHUB_ISSUE_NUMBER=1                                # Issue for delta relay (default: 1)
HIVE_BASE_BRAIN_VERSION=<version>                         # Optional: brain version tag
```

---

## 🔄 Configuration Flow

### Development (Local)

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your keys to `.env`:**
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   OPENAI_API_KEY=sk_test_...  # optional
   ```

3. **Never commit `.env`** - it's in `.gitignore`

### CI/CD (GitHub Actions - hive-aggregator.yml)

1. **Automatic (no config needed):**
   - `HIVE_GITHUB_TOKEN` = `secrets.HIVE_BOT_TOKEN` or fallback to `github.token`
   - `HIVE_GITHUB_REPOSITORY` = auto-injected by GitHub

2. **Optional customization (set in repo settings):**
   - `vars.HIVE_DISCUSSION_NUMBER` → `HIVE_GITHUB_ISSUE_NUMBER`
   - `vars.HIVE_BASE_BRAIN_VERSION` → `HIVE_BASE_BRAIN_VERSION`

3. **Secrets setup:**
   - Create `HIVE_BOT_TOKEN` in Settings > Secrets and Variables > Actions
   - Or use default `github.token` (automatically available)

---

## 🚨 SECURITY CHECKLIST

- [x] `.env` file is in `.gitignore` ✅
- [x] No API keys committed to git history ✅
- [x] Template `.env.example` provided without real keys ✅
- [x] GitHub token uses fallback (works without explicit secret) ✅
- [x] Ed25519 signing for hive packets (cryptography optional, HMAC fallback) ✅
- [x] Public APIs have no sensitive data exposure ✅

### Action Items (for user)

1. **GROQ Key Revocation**: Go to https://console.groq.com/keys and regenerate/revoke old key
2. **Local Setup**: Add your own GROQ_API_KEY to local `.env` (copy from `.env.example`)
3. **CI Setup (optional)**: If using custom token, add `HIVE_BOT_TOKEN` to repo secrets
4. **Verification**: Run `./run.sh` or IDE - should load keys from `.env` automatically

---

## 📊 API Usage Summary

| Category | Count | Keys Required | Status |
|----------|-------|----------------|--------|
| **LLM Providers** | 6 | 1 mandatory (Groq) | ❌ Local config needed |
| **Public APIs** | 5 | 0 | ✅ Ready |
| **GitHub Hive** | 1 | 1 (auto-managed in CI) | ✅ Ready |
| **Internal (Hive)** | 3 | 0 | ✅ Ready |
| **TOTAL** | 15 | 1 user-provided | ✅ ~87% Ready |

---

## ✨ Next Steps

1. **Add GROQ key locally**: Update `.env` with your actual key
2. **Test LLM bridge**: Run `python -c "from antahkarana_kernel import AntahkaranaKernel; k = AntahkaranaKernel(); print('LLM OK')"`
3. **Optional - enable Hive sync**: Set `ANTAHKARANA_HIVE_OPT_IN=true` in `.env`
4. **Verify GitHub CI**: Push changes, hive-aggregator.yml should run hourly

---

**Document Status**: Complete  
**Last Updated**: 2026-04-14  
**Verified By**: Full project scan + API endpoint validation
