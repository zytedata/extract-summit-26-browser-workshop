// Made by deck/export_run.py from a recorded lesson 05 run. Don't edit by hand.
const RUN = {
 "run_id": "20261109-185752-8076",
 "model": "anthropic/claude-haiku-5.5",
 "goal": null,
 "recorded": "20261109",
 "agents": [
  {
   "site": "diffbot.com",
   "company": "Diffbot",
   "start": 0.29,
   "end": 27.25,
   "status": "done",
   "steps": 2,
   "browser_seconds": 23.5,
   "units": 2,
   "model_usd": 0.002,
   "page_status": "200, 301"
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "start": 0.29,
   "end": 57.25,
   "status": "done",
   "steps": 4,
   "browser_seconds": 53.7,
   "units": 4,
   "model_usd": 0.0114,
   "page_status": "200"
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "start": 0.29,
   "end": 46.18,
   "status": "done",
   "steps": 3,
   "browser_seconds": 42.4,
   "units": 3,
   "model_usd": 0.00727,
   "page_status": "200"
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "start": 28.53,
   "end": 74.82,
   "status": "done",
   "steps": 3,
   "browser_seconds": 42.5,
   "units": 3,
   "model_usd": 0.00543,
   "page_status": "200, 301"
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "start": 47.15,
   "end": 84.4,
   "status": "done",
   "steps": 2,
   "browser_seconds": 33.8,
   "units": 3,
   "model_usd": 0.00402,
   "page_status": "200, 302"
  }
 ],
 "steps": [
  {
   "site": "brightdata.com",
   "step": 1,
   "t": 12.96,
   "url": "https://brightdata.com/",
   "page_type": "home",
   "action": "click",
   "link_text": null,
   "why": "The cookie banner blocks the page, so I'll accept cookies to get it out of the way before going to the pricing section.",
   "model_usd": 0.0024687
  },
  {
   "site": "diffbot.com",
   "step": 1,
   "t": 13.01,
   "url": "https://www.diffbot.com/",
   "page_type": "home",
   "action": "click",
   "link_text": "PRICING",
   "why": "Pricing lives on the dedicated pricing page, so clicking the PRICING link in the top navigation gets the plan details and billing toggles.",
   "model_usd": 0.0008195
  },
  {
   "site": "apify.com",
   "step": 1,
   "t": 15.43,
   "url": "https://apify.com/",
   "page_type": "home",
   "action": "click",
   "link_text": "Pricing",
   "why": "Pricing is not on the homepage, so I'll open the Pricing page from the top navigation to capture the plans and billing options.",
   "model_usd": 0.0020285
  },
  {
   "site": "brightdata.com",
   "step": 2,
   "t": 23.26,
   "url": "https://brightdata.com/",
   "page_type": "home",
   "action": "click",
   "link_text": "Unlocker API FREE TIER Starts from $1/1k req",
   "why": "The pricing pages are linked from the Pricing menu, so I'll open the Unlocker API pricing page to see the plans and their billing options.",
   "model_usd": 0.0028465
  },
  {
   "site": "diffbot.com",
   "step": 2,
   "t": 26.48,
   "url": "https://www.diffbot.com/pricing",
   "page_type": "pricing",
   "action": "done",
   "link_text": null,
   "why": "All plan prices are visible and there is no annual toggle; the FAQ confirms plans are monthly subscriptions, so the pricing is fully captured.",
   "model_usd": 0.0011792
  },
  {
   "site": "apify.com",
   "step": 2,
   "t": 31.0,
   "url": "https://apify.com/pricing",
   "page_type": "pricing",
   "action": "click",
   "link_text": "-10% Bill annually",
   "why": "The monthly set is captured, so I'll flip the toggle to 'Bill annually' to capture the annual prices for the same plans.",
   "model_usd": 0.0026677
  },
  {
   "site": "import.io",
   "step": 1,
   "t": 43.39,
   "url": "https://www.import.io/",
   "page_type": "home",
   "action": "click",
   "link_text": "Pricing",
   "why": "The full plan list with monthly and annual prices lives on the Pricing page, so I'll open it via the Pricing link in the header.",
   "model_usd": 0.0018108
  },
  {
   "site": "brightdata.com",
   "step": 3,
   "t": 43.46,
   "url": "https://brightdata.com/pricing/web-unlocker",
   "page_type": "pricing",
   "action": "click",
   "link_text": null,
   "why": "The cookie modal hides the plan amounts, so I need to dismiss it with Accept all before the monthly and annual prices can be read.",
   "model_usd": 0.0029622
  },
  {
   "site": "apify.com",
   "step": 3,
   "t": 44.84,
   "url": "https://apify.com/pricing",
   "page_type": "pricing",
   "action": "done",
   "link_text": null,
   "why": "Both the monthly and annual price sets are now captured across the steps, so the pricing research is complete.",
   "model_usd": 0.0025763
  },
  {
   "site": "brightdata.com",
   "step": 4,
   "t": 56.34,
   "url": "https://brightdata.com/pricing/web-unlocker",
   "page_type": "pricing",
   "action": "done",
   "link_text": null,
   "why": "All visible plans are already captured in the saved steps, and no monthly/annual toggle or readable Scale amount is on the page, so the pricing goal is reached.",
   "model_usd": 0.0031242
  },
  {
   "site": "import.io",
   "step": 2,
   "t": 58.74,
   "url": "https://www.import.io/pricing",
   "page_type": "pricing",
   "action": "click",
   "link_text": "Monthly",
   "why": "The annual set is captured, so I'll flip the toggle to Monthly to capture the monthly prices.",
   "model_usd": 0.0018512
  },
  {
   "site": "octoparse.com",
   "step": 1,
   "t": 61.17,
   "url": "https://www.octoparse.com/",
   "page_type": "home",
   "action": "click",
   "link_text": "Pricing",
   "why": "The pricing page is linked in the top navigation and will show the plans and billing toggles needed for the goal.",
   "model_usd": 0.0016203
  },
  {
   "site": "import.io",
   "step": 3,
   "t": 73.66,
   "url": "https://www.import.io/pricing",
   "page_type": "pricing",
   "action": "done",
   "link_text": null,
   "why": "Both the monthly and annual price sets are now captured (annual from the steps so far, monthly on this page), so the goal is reached.",
   "model_usd": 0.0017674
  },
  {
   "site": "octoparse.com",
   "step": 2,
   "t": 83.39,
   "url": "https://www.octoparse.com/pricing",
   "page_type": "pricing",
   "action": "done",
   "link_text": null,
   "why": "Both the monthly and annual price sets, plus the quarterly set, are visible on this page and captured above, so the goal is complete.",
   "model_usd": 0.002401
  }
 ],
 "prices": [
  {
   "site": "diffbot.com",
   "company": "Diffbot",
   "step": 2,
   "plan": "Free",
   "amount": "0",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 0.0,
   "billing": "monthly",
   "kind": "free",
   "includes": [
    "10,000 credits / month",
    "All four APIs included",
    "5 requests / min"
   ]
  },
  {
   "site": "diffbot.com",
   "company": "Diffbot",
   "step": 2,
   "plan": "Startup",
   "amount": "299",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 299.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "250,000 credits / month",
    "Overage at $0.001 / credit",
    "5 requests / sec"
   ]
  },
  {
   "site": "diffbot.com",
   "company": "Diffbot",
   "step": 2,
   "plan": "Plus",
   "amount": "899",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 899.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "1,000,000 credits / month",
    "Access to Crawl (25 active)",
    "3 user seats"
   ]
  },
  {
   "site": "diffbot.com",
   "company": "Diffbot",
   "step": 2,
   "plan": "Enterprise",
   "amount": "custom",
   "currency": "USD",
   "period": "custom, no fixed monthly price",
   "usd_month": null,
   "billing": "none",
   "kind": "custom",
   "includes": [
    "Custom credit allotment",
    "100+ active crawls",
    "Dedicated support"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 2,
   "plan": "Free",
   "amount": "0",
   "currency": "USD",
   "period": "free, no card required",
   "usd_month": 0.0,
   "billing": "none",
   "kind": "free",
   "includes": [
    "$5 prepaid usage",
    "$0.2 per compute unit",
    "Community support"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 2,
   "plan": "Starter",
   "amount": "19",
   "currency": "USD",
   "period": "month + pay as you go, billed monthly",
   "usd_month": 19.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "$19 prepaid usage",
    "$0.2 per compute unit",
    "Chat support",
    "Bronze Apify Store discount"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 2,
   "plan": "Scale",
   "amount": "199",
   "currency": "USD",
   "period": "month + pay as you go, billed monthly",
   "usd_month": 199.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "$199 prepaid usage",
    "$0.16 per compute unit",
    "Priority chat support",
    "Silver Apify Store discount"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 2,
   "plan": "Business",
   "amount": "999",
   "currency": "USD",
   "period": "month + pay as you go, billed monthly",
   "usd_month": 999.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "$999 prepaid usage",
    "$0.13 per compute unit",
    "Account manager",
    "Gold Apify Store discount"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 2,
   "plan": "Enterprise",
   "amount": "custom",
   "currency": "USD",
   "period": "custom",
   "usd_month": null,
   "billing": "none",
   "kind": "custom",
   "includes": [
    "Custom scraping solutions",
    "SLAs with guaranteed data",
    "Dedicated team of experts"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 3,
   "plan": "Free Tier",
   "amount": "0",
   "currency": "USD",
   "period": "month, free tier",
   "usd_month": 0.0,
   "billing": "none",
   "kind": "free",
   "includes": [
    "5K requests per month",
    "Expert support"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 3,
   "plan": "Pay as you go",
   "amount": "$/1K requests",
   "currency": "USD",
   "period": "per 1K requests",
   "usd_month": null,
   "billing": "none",
   "kind": "usage",
   "includes": [
    "Pay only for success",
    "Set monthly spend limits",
    "Unlimited concurrency"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 3,
   "plan": "Scale",
   "amount": "slider, amount not shown",
   "currency": "USD",
   "period": "month, billing toggle not visible",
   "usd_month": null,
   "billing": "none",
   "kind": "subscription",
   "includes": [
    "383K requests included",
    "$/1K additional requests",
    "Unlimited concurrency"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 3,
   "plan": "Enterprise",
   "amount": "custom",
   "currency": "USD",
   "period": "custom",
   "usd_month": null,
   "billing": "none",
   "kind": "custom",
   "includes": [
    "Volume discounts",
    "Account manager",
    "Premium SLA"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 3,
   "plan": "Free",
   "amount": "0",
   "currency": "USD",
   "period": "month, billed annually",
   "usd_month": 0.0,
   "billing": "none",
   "kind": "free",
   "includes": [
    "$5 prepaid usage",
    "$0.2 per compute unit",
    "Community support"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 3,
   "plan": "Starter",
   "amount": "17",
   "currency": "USD",
   "period": "month + pay as you go, billed annually",
   "usd_month": 17.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "$19 prepaid usage",
    "$0.2 per compute unit",
    "32 max concurrent runs",
    "Chat support"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 3,
   "plan": "Scale",
   "amount": "179",
   "currency": "USD",
   "period": "month + pay as you go, billed annually",
   "usd_month": 179.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "$199 prepaid usage",
    "$0.16 per compute unit",
    "128 max concurrent runs",
    "Priority chat support"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 3,
   "plan": "Business",
   "amount": "899",
   "currency": "USD",
   "period": "month + pay as you go, billed annually",
   "usd_month": 899.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "$999 prepaid usage",
    "$0.13 per compute unit",
    "256 max concurrent runs",
    "Account manager"
   ]
  },
  {
   "site": "apify.com",
   "company": "Apify",
   "step": 3,
   "plan": "Enterprise",
   "amount": "custom",
   "currency": "USD",
   "period": "custom, billed annually",
   "usd_month": null,
   "billing": "none",
   "kind": "custom",
   "includes": [
    "Custom scraping solutions",
    "SLAs with guaranteed data",
    "Dedicated team of experts"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 4,
   "plan": "Free Tier",
   "amount": "0",
   "currency": "USD",
   "period": "month, free tier",
   "usd_month": 0.0,
   "billing": "none",
   "kind": "free",
   "includes": [
    "5K requests per month",
    "Expert support"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 4,
   "plan": "Pay as you go",
   "amount": "per 1K requests",
   "currency": "USD",
   "period": "per 1K requests",
   "usd_month": null,
   "billing": "none",
   "kind": "usage",
   "includes": [
    "Pay only for success",
    "Set monthly spend limits",
    "Unlimited concurrency",
    "Expert support"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 4,
   "plan": "Scale",
   "amount": "not shown (slider)",
   "currency": "USD",
   "period": "month, slider",
   "usd_month": null,
   "billing": "none",
   "kind": "subscription",
   "includes": [
    "383K requests included",
    "$/1K additional requests",
    "Unlimited concurrency",
    "Cancel anytime"
   ]
  },
  {
   "site": "brightdata.com",
   "company": "Bright Data",
   "step": 4,
   "plan": "Enterprise",
   "amount": "custom",
   "currency": "USD",
   "period": "custom",
   "usd_month": null,
   "billing": "none",
   "kind": "custom",
   "includes": [
    "Volume discounts",
    "Account manager",
    "Premium SLA",
    "Priority support"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 2,
   "plan": "Starter",
   "amount": "9",
   "currency": "USD",
   "period": "month, billed annually",
   "usd_month": 9.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "5,000 successful queries/mo",
    "hard stop, no overage",
    "up to 5 extractors",
    "daily CSV and JSON delivery"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 2,
   "plan": "Standard",
   "amount": "199",
   "currency": "USD",
   "period": "month, billed annually",
   "usd_month": 199.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "50,000 successful queries/mo",
    "$7 per 1K overage",
    "unlimited extractors and concurrent jobs",
    "webhook delivery"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 2,
   "plan": "Professional",
   "amount": "399",
   "currency": "USD",
   "period": "month, billed annually",
   "usd_month": 399.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "200,000 successful queries/mo",
    "$3.50 per 1K overage",
    "full API access and webhooks",
    "S3 and SFTP delivery"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 2,
   "plan": "Advanced",
   "amount": "699",
   "currency": "USD",
   "period": "month, billed annually",
   "usd_month": 699.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "500,000 successful queries/mo",
    "$2.50 per 1K overage",
    "premium and residential proxies",
    "multi-user with team management"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 3,
   "plan": "Starter",
   "amount": "11",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 11.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "5,000 successful queries/mo",
    "hard stop, no overage",
    "up to 5 extractors"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 3,
   "plan": "Standard",
   "amount": "249",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 249.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "50,000 successful queries/mo",
    "$7 per 1K overage",
    "unlimited extractors and concurrent jobs"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 3,
   "plan": "Professional",
   "amount": "499",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 499.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "200,000 successful queries/mo",
    "$3.50 per 1K overage",
    "regional proxies",
    "delivery to S3 and SFTP"
   ]
  },
  {
   "site": "import.io",
   "company": "Import.io",
   "step": 3,
   "plan": "Advanced",
   "amount": "899",
   "currency": "USD",
   "period": "month, billed monthly",
   "usd_month": 899.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "500,000 successful queries/mo",
    "$2.50 per 1K overage",
    "premium and residential proxies",
    "multi-user team management"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Free",
   "amount": "Free",
   "currency": "USD",
   "period": "free plan, no billing",
   "usd_month": 0.0,
   "billing": "none",
   "kind": "free",
   "includes": [
    "10 tasks",
    "Local extraction only",
    "Up to 50K rows exported per month",
    "1 device"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Standard",
   "amount": "69",
   "currency": "USD",
   "period": "month, billed annually (From $69/MO card, yearly toggle on)",
   "usd_month": 69.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "100 tasks",
    "Up to 3 concurrent cloud processes",
    "500+ preset scraping templates",
    "Residential proxies and IP rotation"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Standard",
   "amount": "83",
   "currency": "USD",
   "period": "month, billed monthly (comparison table)",
   "usd_month": 83.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "100 tasks",
    "Up to 3 concurrent cloud processes",
    "500+ preset scraping templates",
    "Residential proxies and IP rotation"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Standard",
   "amount": "239",
   "currency": "USD",
   "period": "total per 3 months, billed quarterly (comparison table)",
   "usd_month": 79.67,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "100 tasks",
    "Up to 3 concurrent cloud processes",
    "500+ preset scraping templates",
    "Residential proxies and IP rotation"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Professional",
   "amount": "249",
   "currency": "USD",
   "period": "month, billed annually (card $249/MO, yearly toggle on)",
   "usd_month": 249.0,
   "billing": "annual",
   "kind": "subscription",
   "includes": [
    "250 tasks",
    "Up to 20 concurrent cloud processes",
    "Save data to Google Sheets, Drive, Dropbox and S3",
    "Priority support and 1-on-1 training"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Professional",
   "amount": "299",
   "currency": "USD",
   "period": "month, billed monthly (comparison table)",
   "usd_month": 299.0,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "250 tasks",
    "Up to 20 concurrent cloud processes",
    "Save data to Google Sheets, Drive, Dropbox and S3",
    "Priority support and 1-on-1 training"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Professional",
   "amount": "779",
   "currency": "USD",
   "period": "total per 3 months, billed quarterly (comparison table)",
   "usd_month": 259.67,
   "billing": "monthly",
   "kind": "subscription",
   "includes": [
    "250 tasks",
    "Up to 20 concurrent cloud processes",
    "Save data to Google Sheets, Drive, Dropbox and S3",
    "Priority support and 1-on-1 training"
   ]
  },
  {
   "site": "octoparse.com",
   "company": "Octoparse",
   "step": 2,
   "plan": "Enterprise",
   "amount": "custom",
   "currency": "USD",
   "period": "custom, contact sales",
   "usd_month": null,
   "billing": "none",
   "kind": "custom",
   "includes": [
    "750+ tasks",
    "40+ concurrent cloud processes",
    "High-performance cloud servers",
    "Dedicated success manager"
   ]
  }
 ]
};
