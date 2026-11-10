# What should the model see?

Every step of the agent sends the model a picture of the page. There are three ways to describe a page, and they cost different things:

- **Screenshot**: a JPEG of what's on screen. What a person sees.
- **Markdown + numbered links**: the page text, plus a list of links and buttons our own JavaScript numbers. That's what lessons 03 and 04 send, with the screenshot.
- **Accessibility snapshot**: Playwright's `page.aria_snapshot(mode="ai")`. The page as a tree of roles and names (`button "-10% Bill annually" [ref=e61]`), with a ref on everything you can act on. Click with `page.get_by_ref("e61").click()`. It's what Playwright MCP gives agents. `shared/capture.py` has `snapshot(page)`, which trims it by 30-45% (drops unnamed wrapper divs, `[cursor=pointer]`, long URLs) without changing the tree.

We sent the same question five ways and checked the answers.

## The test

`python research/what_to_send.py`, run on 2026-11-10 with `anthropic/claude-haiku-5.5`. Five pages: Apify pricing, zyte.com, Octoparse pricing, Bright Data Web Unlocker pricing, Oxylabs homepage. One Zyte session per page captured everything. Then each setup was asked twice: "list the prices, and give the one element to click next" (the way to pricing, the billing toggle option that isn't selected, or the cookie button if a banner is in the way).

The raw answers are in [`results-2026-11-10.json`](results-2026-11-10.json). We graded them by hand against the screenshots.

| What we sent | Right click | Prices right | Tokens in | Cost per call | Seconds per step |
|---|---|---|---|---|---|
| A. Screenshot + markdown + links (lessons 03, 04) | 8 / 10 | 6 / 6 | 19.2K | $0.0022 | 9.0 |
| B. Snapshot | 9 / 10 | 4 / 6 | 17.3K | $0.0019 | 3.8 |
| C. Snapshot + screenshot | 9 / 10 | 6 / 6 | 19.6K | $0.0021 | 7.3 |
| D. Markdown + links | 7 / 10 | 4 / 6 | 16.8K | $0.0021 | 6.4 |
| E. Screenshot only | 10 / 10 * | 6 / 6 ** | 3.0K | $0.0004 | 5.6 |

Seconds per step = capturing in the browser + the model's answer, averaged. Prices: the three pricing pages, two runs each.

\* Answers with the visible text ("Billed monthly"), not an id, so your code has to find the element by text. \** Only what's on screen: it listed 1-3 "includes" per plan where the others found 7-15 further down the page.

Ten answers per setup is a small sample. Treat the differences of one as noise and the patterns below as the result.

## What we learned

**Images are cheap in tokens and slow in the browser.** A screenshot is about 2K tokens. Capturing it over a remote browser took 2-4 seconds every time, and the browser is billed by the second while it waits. Text is the opposite: 15-20K tokens per page whether it's markdown or the snapshot, but it's captured in about a second.

**Markdown can't click.** Toggles, tabs and switches often aren't links. Octoparse's "Billed monthly" isn't in our numbered list, so with markdown the model could only answer with text we couldn't click. The snapshot has it as an element with a ref.

**Some prices only exist as pixels.** Bright Data draws "$499" as one animated element per digit. Markdown got `$ /month`. The snapshot got `$`, `4`, `9`, `9` as separate items, and the model read it as $49. Every setup with the screenshot got $499.

**The snapshot names things.** `button "-10% Bill annually"` and `link "Pricing"` carry their role and state. The model picked the right element more often than from a flat list of link texts. A cookie dialog shows up at the top of the tree, so the model sees it's in the way.

**Both text forms lose what's hidden.** A link inside a closed dropdown menu isn't in the snapshot, and our link list only has visible ones. The model has to open the menu first, or you fall back to the link's URL.

## When to send what

- **Snapshot, to act.** Roles, states and refs make clicking reliable. It's the right default for an agent that has to click.
- **Screenshot, to read what's drawn.** Prices, charts, images, what's above the fold, popups covering the page. Cheap in tokens, but every capture keeps the browser open 2-4 seconds longer.
- **Markdown, to read long text.** Articles and docs, where the text is the point and nothing needs clicking. Lesson 02 reads list articles as plain HTTP, no browser at all.

For this workshop's job, clicking to the pricing page and reading prices, snapshot + screenshot (C) got everything right in our runs. Snapshot alone (B) is the fastest and cheapest, and fine on pages where the prices are plain text.

## Run it yourself

```bash
python research/what_to_send.py
python research/what_to_send.py --runs 1 --model google/gemini-3.5-flash-lite
```

About 5 browser units and $0.10 with the default model. Everything it captured lands in `output/research/`: the screenshot, markdown, link list and trimmed snapshot of each page, plus `results.json`. Open the snapshots next to the screenshots and see what each one misses.
