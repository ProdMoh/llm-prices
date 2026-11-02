# LLM API prices

[![Validate](https://github.com/ProdMoh/llm-prices/actions/workflows/validate.yml/badge.svg)](https://github.com/ProdMoh/llm-prices/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Token prices for OpenAI, Anthropic Claude, Google Gemini, Perplexity and open models on Together AI, Fireworks, DeepInfra and Baseten, as JSON and CSV. Each model has its input, cached input and output price per million tokens, Batch and other service tiers, long-prompt rates, scheduled price changes and shutdown dates, with a link to the provider's pricing page.

Last generated: <!-- generated -->2026-11-02<!-- /generated -->

Maintained by [Ganivra](https://ganivra.com), which uses these same prices to work out what each customer of an AI product costs to serve.

## Current prices

USD per million tokens, standard tier, on each provider's own API.

<!-- prices:start -->
| Provider | Model | Input | Cached input | Output | Scheduled change |
|---|---|---:|---:|---:|---|
| Anthropic | `claude-fable-5-1` | $10.00 | $0.25 | $50.00 |  |
| Anthropic | `claude-opus-5-5` | $4.00 | $0.20 | $20.00 |  |
| Anthropic | `claude-sonnet-5-5` | $2.00 | $0.10 | $10.00 |  |
| Anthropic | `claude-haiku-5-5` | $0.10 | $0.01 | $0.50 |  |
| OpenAI | `gpt-6-astra` | $10.00 | $1.00 | $50.00 |  |
| OpenAI | `gpt-6.1-sol` | $2.00 | $0.10 | $10.00 |  |
| OpenAI | `gpt-6.1-terra` | $1.00 | $0.05 | $5.00 |  |
| OpenAI | `gpt-6-luna` | $0.10 | $0.01 | $0.50 |  |
| OpenAI | `gpt-5.6-sol` | $4.00 | $0.40 | $20.00 |  |
| Google Gemini | `gemini-4-argon` | $2.00 | $0.10 | $10.00 | $4.00 / $20.00 from 2026-12-01 |
| Google Gemini | `gemini-3.1-pro-preview` | $2.00 | $0.20 | $12.00 |  |
| Google Gemini | `gemini-3.8-flash` | $0.75 | $0.075 | $3.75 | $1.50 / $7.50 from 2027-01-01 |
| Google Gemini | `gemini-3.5-flash-lite` | $0.30 | $0.03 | $2.50 |  |
| Together AI | `deepseek-ai/DeepSeek-V4.1-Flash` | $0.30 | $0.006 | $1.20 |  |
<!-- prices:end -->

Every model is in [`data/prices.json`](data/prices.json). Browse them on [ganivra.com/supported-models](https://ganivra.com/supported-models), or compare two side by side at [ganivra.com/models/compare](https://ganivra.com/models/compare).

## Files

| File | What it holds |
|---|---|
| [`data/prices.json`](data/prices.json) | Every model with its current prices, service tiers, long-prompt rates, scheduled changes and shutdown date |
| [`data/prices.csv`](data/prices.csv) | The same models as one row each, for spreadsheets |
| [`data/providers/*.json`](data/providers) | `prices.json` split by provider |
| [`data/shutdowns.json`](data/shutdowns.json) | Every announced model shutdown from the OpenAI, Anthropic and Gemini deprecation pages, including audio, image and embedding models |
| [`schema/prices.schema.json`](schema/prices.schema.json) | JSON Schema for `prices.json` |

## Use it

Fetch the latest file straight from GitHub:

```bash
curl -s https://raw.githubusercontent.com/ProdMoh/llm-prices/main/data/prices.json
```

Price a request in Python:

```python
import json, urllib.request

URL = "https://raw.githubusercontent.com/ProdMoh/llm-prices/main/data/prices.json"
models = {(m["provider"], m["model"]): m for m in json.load(urllib.request.urlopen(URL))["models"]}

def cost(provider, model, input_tokens, output_tokens, cached_tokens=0):
    m = models[(provider, model)]
    p = m["price_per_million_tokens"]
    long = m.get("long_prompt")
    # Past the long-prompt threshold, the whole request is billed at the higher rates.
    if long and input_tokens > long["over_input_tokens"]:
        p = long
    cached_rate = p.get("cached_input") or p["input"]
    return ((input_tokens - cached_tokens) * p["input"] + cached_tokens * cached_rate + output_tokens * p["output"]) / 1_000_000

print(round(cost("anthropic", "claude-sonnet-5-5", 3_000, 500), 6))  # 0.011
```

Or in JavaScript:

```js
const { models } = await (await fetch("https://raw.githubusercontent.com/ProdMoh/llm-prices/main/data/prices.json")).json();
const sonnet = models.find(m => m.provider === "anthropic" && m.model === "claude-sonnet-5-5");
console.log(sonnet.price_per_million_tokens); // { input: 2, cached_input: 0.1, output: 10, ... }
```

## Fields

Each entry in `models`:

| Field | Meaning |
|---|---|
| `provider`, `provider_name` | Provider ID (`openai`, `anthropic`, `google`, `perplexity`, `together`, `fireworks`, `deepinfra`, `baseten`) and display name |
| `model`, `aliases` | The model ID you send to the API, and dated snapshots or aliases billed at the same price |
| `pricing_url` | The provider page the price comes from |
| `status` | `active`, `deprecated` (a shutdown date is announced) or `shut_down` (the date has passed). Shut-down models stay listed so older usage can still be priced |
| `price_per_million_tokens` | `input`, `cached_input` (cache reads; omitted when there is no cache discount), `output`, and cache write prices where the provider charges them: `cache_write_5m` and `cache_write_1h` (Anthropic), `cache_write` (OpenAI) |
| `long_prompt` | Rates for the whole request once the prompt passes `over_input_tokens` |
| `service_tiers` | Multipliers on the standard price: `batch`, `flex`, `priority`, `fast_mode`, `ultrafast`. A number applies to every token; an object gives `input`, `output` and `cached_input` separately |
| `fast_mode_price_per_million_tokens` | Absolute fast mode prices, where the provider publishes them instead of a multiplier |
| `scheduled_changes` | Announced future prices with their `effective` date |
| `retirement` | `shutdown_date`, the recommended `replacement`, and `earliest_date: true` when the provider (Google) gives the earliest date it may shut the model down |
| `notes` | Other charges in plain words, such as web search or grounding fees |

Prices are list prices for each provider's own API. Bedrock, Vertex AI, Azure and other resellers set their own prices and schedules. Taxes, regional surcharges and volume discounts are not included.

## How it is kept up to date

Prices are copied from each provider's pricing and deprecation pages and checked against them before each update. The `generated` field in every file is the date of the last export. A provider usually announces a price change weeks ahead, so `scheduled_changes` shows it before it takes effect.

Upcoming price changes and shutdowns across providers are also on [ganivra.com/models/price-changes](https://ganivra.com/models/price-changes), with an [RSS feed](https://ganivra.com/models/price-changes/feed.xml).

Found a wrong or missing price? [Open an issue](https://github.com/ProdMoh/llm-prices/issues/new) with a link to the provider's pricing page.

## License

The data is licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). You can use it in commercial and open-source projects. Credit it as:

> LLM API prices by [Ganivra](https://ganivra.com/supported-models), CC BY 4.0

The validation script is under the MIT license.
