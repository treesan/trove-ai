<div align="center">

# Trove AI — 拾遗

**Read-later + AI knowledge base, built for the Chinese internet.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![Frontend: Next.js 14](https://img.shields.io/badge/Frontend-Next.js%2014-black)](https://nextjs.org)
[![pgvector](https://img.shields.io/badge/Vector-pgvector-336791)](https://github.com/pgvector/pgvector)
[![Responsive: PC · Pad · Mobile](https://img.shields.io/badge/Responsive-PC%20·%20Pad%20·%20Mobile-007aff)]()
[![Status: active](https://img.shields.io/badge/status-active-success.svg)]()

> 🔥 **这是 Simonlin 优化版** ([simonlin000/trove-ai](https://github.com/simonlin000/trove-ai)) — 在原版 [weaiw/trove-ai](https://github.com/weaiw/trove-ai) 基础上增加了 B 站/YouTube 视频 ASR 语音转录、DeepSeek V4-Pro 驱动、UI 配置化等关键能力。详见下方 [Simon Fork 变更](#simon-fork-变更-v11)。

[中文 README](README.zh.md) · [Self-host guide](docs/SELF_HOST.md) · [Obsidian plugin](https://github.com/weaiw/trove-sync-obsidian)

</div>

---

## Why Trove AI?

You save 1000 articles. You re-read 5.

The problem isn't that you have too much — it's that your tools treat "save" and "read" as the same action. WeChat 收藏 buries them. **收藏 ≠ reading.** That gap is the entire problem.

**Pocket shut down in 2024. Omnivore shut down too.** Their users' carefully curated libraries vanished overnight.

**Trove AI is a self-hostable, AI-powered second brain** that turns "save for later" back into "actually read & remember." Built first-class for the Chinese internet (WeChat 公众号 / 知乎 / 抖音 / 小红书 / B 站 / 头条 / 掘金 / CSDN), with WeChat Bot ingress, automatic knowledge graph, and one-way Obsidian sync as built-in features.

It's yours to host. It's yours to keep.

---

## Highlights

<table>
<tr>
<td width="50%" valign="top">

#### 📥 Multi-platform capture
WeChat 公众号 · **视频号 (WeChat Channels)** · 头条 · 抖音 · 小红书 · B 站 · Medium · CSDN · 掘金 — and any OpenGraph-aware URL.
JS-rendered & no-parser pages (视频号, CSDN, Medium, …) are extracted via a *trafilatura → headless-Chromium render → BeautifulSoup* cascade for clean main-content.
Ingestion via: browser bookmark, WeChat Bot, paste, upload (PDF/DOCX/EPUB/etc), one-sentence Spark generation.

</td>
<td width="50%" valign="top">

#### 🧠 AI does the work, not you
Every article gets: AI-extracted title, 5-sentence summary, 3-5 key points, auto-tags, source-aware author extraction, 384-dim vector embedding, mind-map auto-generation. **B 站 / YouTube 视频自动字幕 + ASR 语音转录。**

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 🔍 Semantic search + RAG Q&A
Ask *"What did I read about prompt engineering?"* → get answer with citations to **your** library, not the public internet.

</td>
<td width="50%" valign="top">

#### 🕸 Auto-grown knowledge graph
Each new article finds its 3 closest siblings by semantic distance. Watch your knowledge connect itself.

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 🛤 Learning paths
One sentence → AI picks articles from your library, orders them, presents as a curriculum.

</td>
<td width="50%" valign="top">

#### 💬 WeChat Bot ingress
Forward an article URL to your bot → it's in your library 5 seconds later, with summary, tags, and "related to your earlier reads" suggestions.

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 📝 One-way Obsidian sync
Companion plugin writes a Markdown snapshot to your vault. Never overwrites your local edits. Your data survives any future Trove shutdown.

</td>
<td width="50%" valign="top">

#### 🏢 Multi-tenant, production-grade
JWT auth · per-user data isolation · revocable sync tokens · service-token impersonation for bots · admin user management.

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 📂 Real knowledge-base craftsmanship
Folder hierarchy · tag system · archive · favorite · recycle bin · weekly review reminder · related-articles recommender on every read view.

</td>
<td width="50%" valign="top">

#### 🌐 All content types
Web links · clipboard paste · PDF · Word · Excel · PPT · EPUB · CSV · plain notes · Spark (1-sentence → full article AI generation).

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 📱 Full-device responsive
**PC · iPad · mobile** all work natively. Touch-optimized reader, gesture-friendly knowledge graph, mobile-first layouts. Use Trove from any device, anywhere.

</td>
<td width="50%" valign="top">

#### 🌗 Light / dark / system theme
Auto-switching based on OS preference, or pin to your favorite mode. Eye-friendly serif reader font for long sessions.

</td>
</tr>
</table>

---

## Screenshots

> ⚠️ Add screenshots in `docs/screenshots/` — see open issues for placeholders.

| Dashboard | Reader | Knowledge graph | Settings |
|---|---|---|---|
| _(placeholder)_ | _(placeholder)_ | _(placeholder)_ | _(placeholder)_ |

---

## Who is it for?

- **Product managers and researchers** drowning in saved-but-never-read articles
- **Engineers and lifelong learners** who want their weekly tabs to compound into knowledge
- **Privacy-conscious users** who don't want their reading habits living in some startup's database
- **People burned by Pocket / Omnivore shutdowns** wanting data sovereignty
- **Content curators** building structured personal knowledge bases
- **Self-hosters** who run their own infrastructure for fun and survival
- **Cross-device readers** who switch between phone (commute) → iPad (couch) → laptop (desk) and want all three to feel native

---

## Compared to alternatives

|  | Trove AI | Pocket | Omnivore | Readwise | Hoarder/Karakeep | Memos |
|---|---|---|---|---|---|---|
| Open source | ✅ AGPL-3.0 | ❌ | ✅ (was) | ❌ | ✅ MIT | ✅ MIT |
| Self-host | ✅ Docker | ❌ | ✅ (defunct) | ❌ | ✅ Docker | ✅ Docker |
| **Chinese platforms** | **✅ 6+ deep parsers** | ❌ | Weak | ❌ | Weak | N/A |
| AI summary | ✅ Any provider | ❌ Basic | ✅ | ✅ | ✅ | ❌ |
| **Video ASR / transcription** | **✅ B站+YouTube** | ❌ | ❌ | ❌ | ❌ | ❌ |
| Knowledge graph | ✅ Auto | ❌ | ❌ | ❌ | ❌ | ❌ |
| Learning paths | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| WeChat Bot | ✅ Built-in | ❌ | ❌ | ❌ | ❌ | ❌ |
| Obsidian sync | ✅ Plugin | ❌ | ✅ | ✅ Paid | ❌ | ❌ |
| **Responsive (PC/pad/mobile)** | ✅ All native | ✅ | Limited | ✅ | Limited | Limited |
| Multi-tenant | ✅ | N/A | ✅ | N/A | Limited | Limited |
| Status | ✅ Active | ⛔ **Shut down 2024** | ⛔ **Shut down 2024** | ✅ Paid | ✅ Active | ✅ Active |

Trove AI is the **only** option that combines: deep Chinese platform support · WeChat Bot · auto knowledge graph · Obsidian sync · self-host · full-device responsive UI. If any one of those is critical to you, the alternatives don't cover it.

---

## Quick Start (5 minutes)

### Prerequisites

- **Docker** ≥ 24.0 with Compose v2 (`docker compose ...`, not `docker-compose`)
- ~ **4 GB RAM** free
- ~ **5 GB disk**

That's it. No Python or Node required on the host.

### Steps

```bash
# 1. Clone (Simon 优化版，含视频 ASR + YouTube + DeepSeek)
git clone https://github.com/simonlin000/trove-ai.git
cd trove-ai

# 或原版
# git clone https://github.com/weaiw/trove-ai.git

# 2. Configure secrets
cp .env.example .env
# Edit .env, at minimum:
#   POSTGRES_PASSWORD=$(openssl rand -base64 24)
#   SECRET_KEY=$(openssl rand -base64 48)

# 3. (Optional) Pre-fill LLM keys (or skip — configure via web UI later)
cp backend/app/config_store.example.json backend/app/config_store.json

# 4. Run
docker compose up -d

# 5. Open
open http://localhost
```

First-time setup creates an admin user. The credentials appear in backend logs:

```bash
docker compose logs backend | grep -i admin
```

Full self-host guide with troubleshooting: **[`docs/SELF_HOST.md`](docs/SELF_HOST.md)**.

### Cloud deployment

Any Docker-capable VM works. Battle-tested on:
- **腾讯云 Lighthouse / CVM** (recommended for China users)
- AWS EC2 t3.medium
- DigitalOcean 4GB droplet
- Hetzner CX22

Bring your own reverse proxy (**Caddy / Traefik / Nginx**) for HTTPS, or use Cloudflare Tunnel.

---

## Architecture

```
        ┌──────────────────────────────────────────────────────┐
        │       Any device — PC · iPad · mobile · browser       │
        │   • Web app   • WeChat Bot   • Obsidian plugin        │
        └─────────────────────────┬────────────────────────────┘
                                  │
                          ┌───────▼───────┐
                          │  Nginx :80    │
                          └───┬────────┬──┘
                              │        │
                  ┌───────────▼──┐  ┌──▼────────────┐
                  │  Frontend    │  │  Backend       │
                  │  (Next.js 14)│  │  (FastAPI)     │
                  │  Responsive  │  │  async         │
                  └──────────────┘  └───┬────────────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  │                     │                     │
        ┌─────────▼──────────┐ ┌────────▼───────┐  ┌──────────▼────────┐
        │  PostgreSQL 16     │ │  Redis 7       │  │ External APIs     │
        │  + pgvector        │ │  (cache)       │  │ LLM + embedding   │
        │  • articles        │ │                │  │ • DeepSeek        │
        │  • embeddings 1024d│ │                │  │ • 讯飞 / OpenAI   │
        │  • knowledge_edges │ │                │  │ • SiliconFlow     │
        │  • users + tokens  │ │                │  │ • any compatible  │
        └────────────────────┘ └────────────────┘  └───────────────────┘
```

### Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | **Next.js 14** + TypeScript + Tailwind | App router, server components, responsive-first |
| Backend | **FastAPI** + SQLAlchemy async + pydantic | Async-native, type-safe, auto OpenAPI docs |
| Database | **PostgreSQL 16** + **pgvector** | One DB for both relational data and vector search |
| Cache | **Redis 7** | Sessions, queues |
| Crawler | **Playwright** + **curl_cffi** + httpx | Defeats Chinese anti-bot (TLS fingerprint, XHR intercept, JS VM bypass) |
| LLM | Any **OpenAI-compatible** | DeepSeek, 讯飞星辰, OpenAI, SiliconFlow, MiniMax, 智谱, ... |
| Embedding | **fastembed bge-small-en-v1.5** (384-dim) or SiliconFlow bge-m3 (1024-dim) | Cloud quality with local fallback |
| Reverse proxy | **Nginx** | Single ingress, fast static serving |

---

## Configuration

Everything user-facing is configurable via the web UI:

**Settings page** → AI 对话模型 / 嵌入模型 / 缓存

| What | Where |
|------|-------|
| LLM provider + key + model | Settings → AI 对话模型 |
| Embedding provider + key + model | Settings → 嵌入模型 |
| Cache clearing / rebuilding | Settings → 系统缓存 |
| Obsidian sync token | Personal Settings → Obsidian 备份 |
| WeChat Bot binding | Personal Settings → WeChat |
| Review schedule | Personal Settings → 周期回顾 |

### Environment variables

| Var | Required | What |
|-----|----------|------|
| `POSTGRES_PASSWORD` | ✅ | DB password |
| `SECRET_KEY` | ✅ | JWT signing secret (≥ 32 random chars) |
| `OPENAI_API_KEY` | ❌ | Optional fallback if no UI config |
| `DEEPSEEK_API_KEY` | ❌ | Optional fallback |
| `SILICONFLOW_API_KEY` | ❌ | Optional fallback |
| `MINIMAX_API_KEY` | ❌ | Optional fallback |
| `SERVICE_TOKENS` | ❌ | `tokenA:userA,tokenB:userB` — for bots |
| `LINKMIND_PUBLIC_BASE` | ❌ | Public URL for bot deep links |

See `.env.example` for the complete template with comments.

---

## API endpoints (high-level)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/auth/login` | User login → JWT |
| `POST /api/articles` | Add article by URL |
| `POST /api/articles/upload` | Upload file (PDF / Word / EPUB / etc) |
| `POST /api/articles/notes` | Write a note |
| `POST /api/articles/spark` | One-sentence → AI-generated article |
| `POST /api/assistant/ask` | RAG Q&A on your library |
| `GET /api/knowledge/graph` | Knowledge graph data |
| `POST /api/learning/paths/generate` | Generate learning path |
| `POST /api/sync/issue-token` | Mint long-lived Obsidian sync token |
| `GET /api/sync/articles` | Paginated articles for sync |
| `POST /api/sync/revoke-all-tokens` | Revoke all sync tokens |

Full OpenAPI spec at `http://localhost/api/docs` once running.

---

## Obsidian Sync — companion plugin

Plugin repo: **[weaiw/trove-sync-obsidian](https://github.com/weaiw/trove-sync-obsidian)** (MIT)

**One-shot snapshot to your local vault.** Never overwrites your edits. Your data survives any future shutdown.

Setup:

1. Web app → **Personal Settings → Obsidian Backup → Generate Sync Token**
2. Download plugin from [Releases](https://github.com/weaiw/trove-sync-obsidian/releases/latest)
3. Drop into `<your-vault>/.obsidian/plugins/trove-sync/`
4. In Obsidian → Community plugins → enable **Trove AI Sync**
5. Paste token + server URL → click **Sync Now**

The plugin auto-detects already-synced articles via dual-OR (sync_state.json ∪ frontmatter scan), so it's safe to lose either side of the index.

---

## Documentation

- [`docs/SELF_HOST.md`](docs/SELF_HOST.md) — Full self-host guide with troubleshooting
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — How to contribute
- API docs at `/api/docs` (auto-generated from FastAPI)


---

## Simon Fork 变更 (v1.1)

本仓库 ([simonlin000/trove-ai](https://github.com/simonlin000/trove-ai)) 在原版 [weaiw/trove-ai](https://github.com/weaiw/trove-ai) 基础上增加了以下能力：

### 🎬 视频 ASR 语音转录

**B 站 & YouTube 视频 → 完整文字稿。** 三层处理：

1. **字幕抓取** — 有外挂字幕直接扒下来
2. **ASR 转录** — 没字幕？后台自动下载音频轨道，Whisper (faster-whisper tiny) 转文字
3. **智能限制** — 默认 30 分钟上限（可在设置页调），防止内存溢出

流程：贴链接 → 秒存文章 → 30 秒内后台扫到标记 → 几分钟后刷新，字幕已在文章底部。

### 📺 YouTube 完整支持

接入 yt-dlp：自动获取标题/频道/简介/封面，优先中文字幕，无字幕走 ASR。只需在设置页填代理地址（国内访问 YouTube 需要）。

### 🧠 DeepSeek V4-Pro 驱动

1.6 万亿参数 MoE 模型（490 亿激活），摘要质量显著提升。不是"本文介绍了XXX"的表面总结，而是提炼核心命题。

### ⚙️ UI 配置化

**设置 → 插件设置**，四个开关随时改：

- YouTube 解析（开/关）
- 代理地址
- 语音转录 ASR（开/关）
- 转录视频上限（默认 1800 秒）

改了立刻生效，不用重启容器。

### 🔄 Obsidian 双向同步

除原版 Trove → Obsidian 拉取外，新增 `POST /api/sync/articles` 端点：Obsidian vault 里的 Markdown 文件可推送回 Trove。按 obsidian_path 去重，支持更新。

### 🐛 关键修复

- **Embedding 向量化修复** — `TextEmbedding` 导入缺失、HuggingFace 国内不可达、向量维度不匹配（1024→384）
- **双 Worker 竞态条件** — `ASR_RUNNING` 锁防重复转录
- **临时文件堆积导致磁盘满** — 限制 30 分钟 + 及时清理
- **长视频 OOM** — 内存保护，超过上限不转录

### 从本仓库部署

```bash
git clone https://github.com/simonlin000/trove-ai.git
cd trove-ai
cp .env.example .env
# 编辑 .env，至少填 DEEPSEEK_API_KEY 和 SECRET_KEY
docker compose up -d
```

打开 http://localhost:80 → 设置 → AI 对话模型 配 DeepSeek → 设置 → 插件设置 配代理 → 开始用。

---

## Roadmap

### v1.1 — current
- ✅ WeChat Channels (视频号) capture
- ✅ Smart generic extraction (trafilatura → headless render → BeautifulSoup)
- ✅ Article-scoped Q&A (📄 this-article / 📚 whole-library toggle)

### v1.0
- ✅ Multi-platform capture (8+ sources)
- ✅ AI processing pipeline (summary / key-points / tags / embedding / mind-map)
- ✅ RAG Q&A + semantic search
- ✅ Auto knowledge graph + learning paths
- ✅ WeChat Bot ingress
- ✅ Obsidian sync plugin
- ✅ Multi-tenant + revocable sync tokens
- ✅ Self-host via Docker
- ✅ Responsive UI for PC / pad / mobile

### v1.1
- 🔜 Browser extension (one-click clip from any tab)
- 🔜 Image local download (offline-safe backup)
- 🔜 Pocket / Omnivore import
- 🔜 Better article deduplication
- 🔜 PWA support for "add to home screen" on mobile

### v1.2
- More LLM providers (Claude, Gemini, Doubao native)
- Per-user theme & language preferences
- Bulk re-process articles with new AI prompts
- Article version history

### v2 — research
- Obsidian community marketplace submission
- Multi-vault Obsidian sync
- Notion / Logseq / Reflect export
- Audio podcast generation from saved articles
- Daily / weekly digest emails

---

## FAQ

<details>
<summary><strong>Will Trove AI work without paying for an LLM API?</strong></summary>

Yes — embedding has a local CPU-only fallback (`BAAI/bge-small-en-v1.5`, 384-dim).
For LLM features (summary, tags, RAG), you need at least a free-tier API:
- **DeepSeek** — cheapest at ~$0.27 / 1M tokens
- **讯飞 / 智谱** — both offer free trial credits
- **OpenAI / Claude / Gemini** — pay-per-use
- **MiniMax / SiliconFlow** — generous free tiers
</details>

<details>
<summary><strong>How much does it cost to run?</strong></summary>

~ **$5-10/month** on a small VPS + LLM API usage.
At < 1000 articles/month with DeepSeek, expect ~$2-5/month in LLM costs.
For totally free, use local embedding + skip AI summary features.
</details>

<details>
<summary><strong>Can I migrate from Pocket / Omnivore / Readwise?</strong></summary>

Direct importer coming in v1.1. Workarounds:
- Pocket export → individual URL list → bulk paste via `/api/articles/batch`
- Omnivore → markdown export → use `/api/articles/upload`
</details>

<details>
<summary><strong>Is anything sent to third parties without my consent?</strong></summary>

Only to the LLM provider **you explicitly configure**. The API key and base URL are entirely under your control.
For air-gapped operation, use local embedding only and skip LLM-powered features.
No analytics, no telemetry, no third-party JS in the frontend.
</details>

<details>
<summary><strong>Does it work well on mobile?</strong></summary>

Yes — built mobile-first with responsive layouts. Reader, library, search, knowledge graph all touch-optimized.
v1.1 adds PWA so you can "add to home screen" on iOS / Android.
</details>

<details>
<summary><strong>Do I need to know coding to deploy?</strong></summary>

Basic Docker familiarity helps. [`docs/SELF_HOST.md`](docs/SELF_HOST.md) walks through every step.
If you're stuck, open an issue and the community usually responds within a day.
</details>

<details>
<summary><strong>How is data isolated between users?</strong></summary>

Every row in `articles`, `tags`, `folders`, `knowledge_edges`, `learning_paths`, `wechat_accounts` is tagged with `user_id`.
All queries filter on `current_user.id`. JWT auth + per-user revocable sync tokens.
Cross-tenant leaks are mechanically prevented at the ORM layer.
</details>

<details>
<summary><strong>What happens if I delete an article?</strong></summary>

It goes to a per-user recycle bin (`deleted_at` column). Auto-purge after 30 days, restorable before that.
The Obsidian plugin **never** propagates deletes — your local file stays unless you manually delete it.
</details>

<details>
<summary><strong>Can I run this commercially?</strong></summary>

Yes, under AGPL-3.0: you can charge users for hosting, **as long as you publish your modifications** to those users.
For closed-source SaaS deployment, contact the maintainer for a commercial license.
</details>

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

Especially welcome:
- New platform parsers (parser_service.py)
- Translations (English, 日本語, others)
- UI polish and accessibility
- Bug reports with reproduction
- Comparison tests with other LLM providers

---

## Acknowledgements

- Built with **[Hermes](https://hermes.ai)** AI coding agent + **[DeepSeek](https://www.deepseek.com)** as the LLM brain — over **2.7 billion tokens** spent in vibe-coding, 0 lines of human-written code
- Backend: [FastAPI](https://fastapi.tiangolo.com) · [SQLAlchemy](https://www.sqlalchemy.org) · [pgvector](https://github.com/pgvector/pgvector) · [Playwright](https://playwright.dev) · [curl_cffi](https://github.com/lexiforest/curl_cffi)
- Frontend: [Next.js](https://nextjs.org) · [Tailwind](https://tailwindcss.com) · [lucide-react](https://lucide.dev) · [react-flow](https://reactflow.dev)
- Embedding: [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) · [fastembed](https://github.com/qdrant/fastembed)
- Inspired by **Pocket**, **Omnivore**, **Readwise** — and frustrated by the first two shutting down

---

## License

Core: **[AGPL-3.0](LICENSE)**.
Obsidian plugin: [MIT](https://github.com/weaiw/trove-sync-obsidian/blob/main/LICENSE).

For commercial closed-source SaaS deployment, contact the maintainer for a separate commercial license.

---

<div align="center">

If Trove AI saves your knowledge from yet another startup shutdown,
**please drop a ⭐ — it costs you nothing and helps the project be discovered.**

</div>
