// The workshop, slide by slide. index.html draws these, edit this file to change what's on screen.
//
// Slide kinds:
//   title    { h, sub, qr }                        big title, optional QR code of the repo
//   points   { h, items: [...], foot }             a heading and a few short lines (HTML allowed)
//   agenda   {}                                    the lesson table, built from LESSONS
//   mermaid  { h, code, side: [...] }              a mermaid diagram, optional notes on the right
//   diagram  { src }                               one of the animated diagrams in ../diagrams/, → steps through it
//   page     { src }                               another page full screen, e.g. replay.html (the recorded lesson 05 run)
//   run      { h, cmds: [...], note, alt: [...] }  the command to run, big, with a copy button
//   output   { h, cmd, out, side: [...], label }  real terminal output (label replaces '$ cmd' in the title bar, e.g. for code), notes on the right. 00-04 recorded 2026-11-09,
//                                                  05 is data/sample-run.db (the 2026-11-06 run) at real speed
//   table    { h, rows: [[a, b], ...], foot }      two columns, e.g. files and what they are
//   grid     { h, head: [...], rows: [[...]], pick: [i], foot }   a table with a header row, rows in pick are green
//
// Output markup: <b> bold, <c> cyan, <g> green, <m> grey, same colours as the scripts print.

const REPO = 'https://github.com/zytedata/extract-summit-26-browser-workshop';

const INTRO = [
  { kind: 'title', h: 'Building browser agents',
    sub: 'Driving a remote browser over CDP and WebSockets<div class="event">Extract Summit 2026 · Dublin · hands-on, 90 min</div>', qr: true },
  { kind: 'points', h: 'The question',
    items: [
      '<big>"Who are our competitors, what do they charge, and what do you get for it?"</big>',
      'Find them in "best X companies" articles',
      'Send a small browser agent to each website: it looks, decides where to click, finds the plans',
      'Turn what it found into a table: every plan, its price, what it includes',
    ] },
  { kind: 'points', h: 'How we do it',
    items: [
      '<b>You don\'t write code.</b> Every lesson: I explain, you run one command, we look at the output',
      'This deck is in the repo: open <code>deck/index.html</code> and follow along on your laptop',
      'Lost? The bar at the bottom always shows the lesson and the command to run',
      'Wifi gone? Lessons 05 and 06 replay a recorded run, no network needed',
    ] },
  { kind: 'agenda' },
];

const LESSONS = [
  { id: '00', title: 'Setup', time: 10, cmd: 'python lessons/00-setup/check.py', slides: [
    { kind: 'run', h: 'Check you can open a Zyte browser',
      cmds: ['python lessons/00-setup/check.py'],
      note: 'Setup steps are in the main README: venv, <code>pip install -r requirements.txt</code>, keys in <code>.env</code>' },
    { kind: 'output', h: 'You\'re through', cmd: 'python lessons/00-setup/check.py',
      out: `your laptop:      Dublin, IE
connected in 2.5s
the Zyte browser: Leesburg, US
session closed. You're ready.`,
      side: ['Two different places: the website sees the Zyte browser, not your laptop',
             'Errors? Check <code>ZYTE_API_KEY</code> in <code>.env</code> and that the account is verified for the browser'] },
  ] },

  { id: '01', title: 'First session', time: 10, cmd: 'python lessons/01-first-session/first_session.py', slides: [
    { kind: 'diagram', src: '../diagrams/01-model.html' },
    { kind: 'diagram', src: '../diagrams/01-session.html' },
    { kind: 'points', h: 'Four things to remember',
      items: [
        '<b>The first page decides the proxy.</b> Same proxy for the rest of the session',
        '<b>Close the session.</b> <code>browser.close()</code> only disconnects, send <code>Browser.close</code> over CDP',
        '<b><code>ttl</code> is the safety net.</b> The session dies after ttl seconds anyway',
        '<b>Cost:</b> whichever is higher, page loads or 15 second blocks. One quick page = 1 unit',
      ] },
    { kind: 'run', h: 'One session, step by step',
      cmds: ['python lessons/01-first-session/first_session.py'],
      note: 'Opens quotes.toscrape.com/js, a page that is empty until JavaScript runs. Every step prints the CDP messages it caused: <code>►</code> we sent, <code>◀</code> the browser sent back' },
    { kind: 'output', h: 'Connect, then go to the page', cmd: 'python lessons/01-first-session/first_session.py',
      out: `<b>[  0.0s] 1. Connect to browser.zyte.com over CDP (ttl=120, proxy_type=auto)</b>
      connected. A Chrome is now running for you on Zyte's side. Billing started.
      <c>► Browser.getVersion</c>
      ◀ Browser.getVersion Chrome/151.0.7922.76, user agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
      <c>► Target.createTarget</c> {"url":"about:blank"}
      ◀ Target.attachedToTarget page about:blank
      <c>► Page.enable</c>
      <c>► Runtime.enable</c>
      <m>... 7 more, 22 other messages (network data, lifecycle) in output/01/cdp_trace.log</m>

<b>[  3.1s] 2. Go to https://quotes.toscrape.com/js/ (first page: Zyte picks the proxy now)</b>
      status 200, title: 'Quotes to Scrape'
      <c>► Page.navigate</c> {"url":"https://quotes.toscrape.com/js/", ...}
      ◀ Network.requestWillBeSent GET https://quotes.toscrape.com/js/
      ◀ Network.responseReceived 200 https://quotes.toscrape.com/js/
      ◀ Page.frameNavigated https://quotes.toscrape.com/js/
      ◀ Network.requestWillBeSent GET https://quotes.toscrape.com/static/bootstrap.min.css
      ◀ Network.requestWillBeSent GET https://quotes.toscrape.com/static/jquery.js
      ◀ Network.responseReceived 200 https://quotes.toscrape.com/static/jquery.js
      <m>... 9 more, 68 other messages (network data, lifecycle) in output/01/cdp_trace.log</m>`,
      side: ['<b>Browser.getVersion</b>: the Chrome running for you. That user agent is not your laptop',
             'One command, <b>Page.navigate</b>. Everything after it is the browser fetching CSS, JS, fonts on its own',
             'Your laptop never talks to the website'] },
    { kind: 'output', h: 'Look, read, close', cmd: 'python lessons/01-first-session/first_session.py',
      out: `<b>[  5.7s] 4. Screenshot (what the model will look at)</b>
      98.6 KB saved to output/01/screenshot.jpg
      <c>► Page.captureScreenshot</c> {"format":"jpeg","quality":70, ...}
      ◀ Page.captureScreenshot 98 KB jpeg, sent back as base64

<b>[  8.1s] 5. Get the HTML and turn it into markdown (what the model will read)</b>
      HTML 8.7 KB -> markdown 1.6 KB, about 405 tokens

<b>[  8.3s] 6. List what can be clicked (so the model can say 'click 7')</b>
      5 links and buttons, first few:
        1. Quotes to Scrape -> https://quotes.toscrape.com/
        2. Login -> https://quotes.toscrape.com/login
        3. Next → -> https://quotes.toscrape.com/js/page/2/

<b>[  8.7s] 7. Where does the website think you are? (new tab, same session, same proxy)</b>
      Washington, US, that's where the proxy is

<b>[ 10.3s] 8. Close the session (Browser.close over CDP, not just disconnect)</b>
      <c>► Browser.close</c>
      ◀ Browser.close ok
      session closed. Billing stopped.

<b>Done in 10.9s.</b>`,
      side: ['HTML vs markdown size: markdown is what the model reads, you pay per token',
             'Numbered links: in lesson 04 the model answers "click 3", no selectors',
             'Step 7: where the website thinks you are. Try <code>--region IE</code> and it moves'] },
    { kind: 'table', h: 'Open output/01/',
      rows: [['screenshot.jpg', 'what the browser saw'], ['page.md', 'the page as text, what the model reads'],
             ['links.txt', 'numbered list of clickable things'], ['page.html', 'the HTML after JavaScript ran'],
             ['cdp_trace.log', 'every CDP message, raw']],
      foot: 'Try: <code>first_session.py --proxy-type residential --region IE</code> and compare step 7' },
  ] },

  { id: '02', title: 'Find the competitors', time: 5, cmd: 'python lessons/02-find-competitors/discover.py "web scraping"', slides: [
    { kind: 'mermaid', h: 'Where the list comes from',
      code: `flowchart LR
  q["web scraping"] --> bing["Bing search<br/>best X companies"]
  bing --> art["list articles<br/>Zyte API article extraction"]
  art --> names["names from the<br/>numbered headings"]
  names --> home["homepage"]
  home --> json["data/web-scraping.json"]`,
      side: ['Plain HTTP through Zyte API, <b>no browser</b>. Nothing here needs one, and HTTP is cheaper and faster',
             '<b>Mentions:</b> named in all 3 articles is more likely a real player',
             '<b>Search is not stable,</b> so the list is saved and every lesson reads the saved copy'] },
    { kind: 'table', h: 'data/web-scraping.json: 20 companies from 3 articles',
      rows: [['Apify', '3 mentions · apify.com'], ['Bright Data', '2 · brightdata.com'], ['Diffbot', '2 · diffbot.com'],
             ['Import.io', '2 · import.io'], ['Octoparse', '2 · octoparse.com'], ['Oxylabs', '2 · oxylabs.io'],
             ['Zyte', '2 · zyte.com'], ['...', '13 more']],
      foot: 'Optional: <code>discover.py "web scraping"</code>, about 30s, writes to output/02/ so the saved list stays as it is' },
  ] },

  { id: '03', title: 'Describe a page', time: 15, cmd: 'python lessons/03-describe-a-page/describe.py', slides: [
    { kind: 'diagram', src: '../diagrams/03-describe.html' },
    { kind: 'run', h: 'Describe zyte.com',
      cmds: ['python lessons/03-describe-a-page/describe.py'],
      alt: ['python lessons/03-describe-a-page/describe.py Apify',
            'python lessons/03-describe-a-page/describe.py Oxylabs',
            'python lessons/03-describe-a-page/describe.py https://www.zyte.com/pricing/'],
      note: 'Watch the <code>[browser OPEN]</code> / <code>[browser closed]</code> tag on every step' },
    { kind: 'output', h: 'The browser closes before the model is asked', cmd: 'python lessons/03-describe-a-page/describe.py',
      out: `<b>[  0.0s]</b> <m>[browser closed]</m> <b>Connect to browser.zyte.com</b>
        connected in 3.0s. A Chrome is running for you at Zyte now, billing started.

<b>[  3.0s]</b> <g>[browser OPEN]</g> <b>Go to https://zyte.com/ (wait for the load event)</b>
        status 200, title: 'Web Data Collection: APIs and Managed Data Delivery | Zyte'
        redirected to https://www.zyte.com/

<b>[ 12.1s]</b> <g>[browser OPEN]</g> <b>Screenshot (top of the page, what the model will look at)</b>
        101 KB jpeg

<b>[ 18.2s]</b> <g>[browser OPEN]</g> <b>HTML -> markdown (what the model will read)</b>
        HTML 580 KB -> markdown 58 KB

<b>[ 20.1s]</b> <g>[browser OPEN]</g> <b>List links and buttons, numbered</b>
        125 links and buttons

<b>[ 21.0s]</b> <g>[browser OPEN]</g> <b>Close the session (Browser.close over CDP)</b>
        closed in 0.7s. The browser was open for 18.7s.
        1 page load, 19s = 2 x 15s block(s) -> billed as 2 unit(s), whichever is higher
        From here on no browser is running. The model only sees what we captured.

<b>[ 21.7s]</b> <m>[browser closed]</m> <b>Send it to OpenRouter -> anthropic/claude-haiku-5.5</b>
        3.8s, 24159 tokens in, 231 out, $0.0025`,
      side: ['The browser opens on connect, not on page load',
             'No "wait until quiet" step: busy sites never go quiet, every second is billed',
             'Open 18.7s, past 15s: billed as 2 units',
             'A slow model doesn\'t keep a browser running',
             'Tokens in: mostly the page text and the image. Remember it for lesson 05'] },
    { kind: 'output', h: 'The answer', cmd: 'python lessons/03-describe-a-page/describe.py',
      out: `<b>[ 25.6s]</b> <m>[browser closed]</m> <b>The answer, as JSON (exactly what the model sent back)</b>
        <c>{</c>
        <c>  "company": "Zyte",</c>
        <c>  "description": "This is the home page of Zyte, a web data company, with a cookie</c>
        <c>    consent banner and a promotion for its ExtractSummit 2026 conference. ...",</c>
        <c>  "page_type": "home",</c>
        <c>  "prices": [],</c>
        <c>  "why": "The link labeled \\"Pricing\\" under the top navigation (link 76, ...)</c>
        <c>    ... so the direct pricing URL link 76 is the best choice.",</c>
        <c>  "pricing_link": 76</c>
        <c>}</c>

<b>[ 25.6s]</b> <m>[browser closed]</m> <b>What our code does with it</b>
        <b>Zyte</b>, page type: home, 0 price(s)
        pricing_link 76 -> 'Pricing' https://www.zyte.com/pricing/
        <m>that's the click lesson 04 will make</m>

<b>Timeline</b> <m>(each mark = 0.5s)</m>
  connect       <m>######                                            </m>   0.0s ->   3.0s
  browser open  <g>      #####################################       </g>   3.0s ->  21.7s
  model         <c>                                          ########</c>  21.7s ->  25.6s`,
      side: ['<b>why</b> comes before <b>pricing_link</b> in the schema: number first gave wrong links',
             'Our code looks up 76 in its own list. The model never makes up a URL',
             'Is the page type right? The link?'] },
    { kind: 'points', h: 'Replay the session',
      items: [
        '<code>playwright show-trace output/03/zyte.com/trace.zip</code>',
        'or drop the file on <b>trace.playwright.dev</b>, it stays in your browser',
        'Filmstrip, every action with the DOM before and after, network, console',
        'Try another model: <code>--model google/gemini-3.5-flash-lite</code>. Compare answer, time, cost',
      ] },
    { kind: 'output', h: 'Another way to show a page: the accessibility snapshot', label: 'page.aria_snapshot(mode="ai") on apify.com/pricing',
      out: `  - main [ref=e46]:
      - heading <c>"Flexible plan + pay as you go"</c> [level=1] [ref=e56]
      - generic [ref=e57]:
        - <b>button</b> [ref=e59]:
          - paragraph [ref=e60]: Bill monthly
        - <b>button</b> <c>"-10% Bill annually"</c> <g>[ref=e61]</g> [cursor=pointer]:
          - generic [ref=e62]: "-10%"
          - paragraph [ref=e63]: Bill annually
      - generic [ref=e66]:
        - heading <c>"Free"</c> [level=2] [ref=e67]
        - paragraph [ref=e69]: $0
        - paragraph [ref=e70]: $5 to spend in Apify Store or on your own Actors
        - paragraph [ref=e75]: $0.2 per compute unit
        - paragraph [ref=e79]: Community support
        - <b>link</b> <c>"Start for free"</c> [ref=e84] [cursor=pointer]:
          - /url: https://console.apify.com
      - generic [ref=e86]:
        - heading <c>"Starter"</c> [level=2] [ref=e87]
        <m>...</m>`,
      side: ['The <b>accessibility tree</b>: the page the way a screen reader reads it. No styles, no layout',
             'One line per element: <b>role</b>, <b>"name"</b>, state, and a <b>ref</b>',
             'Roles tell the model what it can do: a <code>button</code> is clicked, a <code>heading</code> is read',
             'The ref is a handle: the model answers <code>e61</code>, our code clicks it'] },
    { kind: 'output', h: 'The Playwright API', label: 'Python, Playwright 1.64',
      out: `<m># the whole page as YAML text. mode="ai" adds a [ref=...] to everything you can act on</m>
snapshot = page.<b>aria_snapshot</b>(mode=<c>"ai"</c>)

<m># the model answers with a ref, Playwright finds the element again</m>
page.<b>get_by_ref</b>(<c>"e61"</c>).click()

<m># just one part of the page, only a few levels deep</m>
page.locator(<c>"main"</c>).<b>aria_snapshot</b>(mode=<c>"ai"</c>, depth=<c>4</c>)

<m># add where each element is on screen: [box=x,y,width,height]</m>
page.<b>aria_snapshot</b>(mode=<c>"ai"</c>, boxes=<c>True</c>)

<m># trimmed for a model in this repo: 30-45% smaller, same tree</m>
<b>from</b> shared.capture <b>import</b> snapshot
text = snapshot(page)`,
      side: ['<code>aria_snapshot</code> since Playwright 1.59, <code>get_by_ref</code> since 1.64',
             'Refs belong to the latest snapshot. Page changed? Take a new one before you click',
             'Without <code>mode="ai"</code>: the same tree, no refs. That\'s the format Playwright tests assert against',
             'Works over CDP like everything else: the tree is built in the Zyte browser'] },
    { kind: 'grid', h: 'Research: what should the model see?',
      head: ['What we sent', 'Right click', 'Prices right', 'Tokens in', '$ / call', 'Seconds / step'],
      rows: [
        ['Screenshot + markdown + links <span style="color:var(--muted)">(this lesson)</span>', '8 / 10', '6 / 6', '19.2K', '0.0022', '9.0'],
        ['Accessibility snapshot', '9 / 10', '4 / 6', '17.3K', '0.0019', '3.8'],
        ['Snapshot + screenshot', '9 / 10', '6 / 6', '19.6K', '0.0021', '7.3'],
        ['Markdown + links', '7 / 10', '4 / 6', '16.8K', '0.0021', '6.4'],
        ['Screenshot only', '10 / 10*', '6 / 6*', '3.0K', '0.0004', '5.6'],
      ],
      pick: [2],
      foot: '5 pages (Apify, Zyte, Octoparse, Bright Data, Oxylabs) × 2 runs, Haiku. Seconds = capture in the browser + the answer. * clicks by visible text, only sees what\'s on screen. Details and the script: <code>research/</code>' },
    { kind: 'points', h: 'What we learned',
      items: [
        '<b>Images are cheap in tokens, slow in the browser.</b> A screenshot is ~2K tokens but 2-4 s to capture, and the browser is billed by the second',
        '<b>Text is the token cost.</b> 15-20K per page, markdown or snapshot alike',
        '<b>Markdown can\'t click.</b> Toggles and tabs often aren\'t links: Octoparse\'s "Billed monthly" never made our list',
        '<b>Some prices are only pixels.</b> Bright Data animates "$499" digit by digit. Markdown: <code>$ /month</code>. Snapshot: <code>$ 4 9 9</code>, read as $49. Screenshot: $499',
      ] },
    { kind: 'points', h: 'When to send what',
      items: [
        '<b>Snapshot, to act.</b> Roles, states, refs: <code>page.get_by_ref("e61").click()</code>. Same idea as Playwright MCP',
        '<b>Screenshot, to read what\'s drawn.</b> Prices, charts, popups, what\'s above the fold',
        '<b>Markdown, to read long text.</b> Articles and docs. Lesson 02 doesn\'t even open a browser',
        'For finding prices: snapshot + screenshot. For speed on plain-text pages: snapshot alone',
      ] },
  ] },

  { id: '04', title: 'Agent loop', time: 20, cmd: 'python lessons/04-agent-loop/agent.py', slides: [
    { kind: 'points', h: 'Let the model drive',
      items: [
        'Lesson 03 in a loop: capture, ask the model, act, again',
        'One extra field in the answer: what to do next. <code>click 48</code>, <code>scroll</code>, <code>done</code>',
        'Our code does the clicking, the model only says which number',
        'Stops when it has the prices, or after 6 steps',
      ] },
    { kind: 'diagram', src: '../diagrams/04-agent-loop.html' },
    { kind: 'points', h: 'One browser for the whole run',
      items: [
        'The browser stays open while the model thinks. Different from lesson 03',
        '<b>State.</b> A "Bill annually" toggle has no URL. A new browser shows monthly again, the cookie banner comes back, the IP can change',
        '<b>Cost.</b> In a loop time sets the bill. Apify: 1 page load but ~37s open = 3 units. A new browser per step: at least as many units, plus ~3s to connect each time',
        'A faster model is how you cut the waiting',
      ] },
    { kind: 'run', h: 'Find Apify\'s prices',
      cmds: ['python lessons/04-agent-loop/agent.py'],
      note: 'Goal: "find the pricing, capture every price set and what each plan includes". A good run: click Pricing, flip the monthly/annual toggle, done' },
    { kind: 'output', h: 'Step 2: the model saved the prices, then flips the toggle', cmd: 'python lessons/04-agent-loop/agent.py',
      out: `<b>[  9.8s]</b> <g>[browser OPEN]</g> <b>Step 1: ask anthropic/claude-haiku-5.5  <m>(browser waits, same page, same cookies)</m></b>
        3.1s, 19510 tokens in, 106 out, $0.0020
        <c>"why": "The Pricing link in the top navigation leads directly to the plan and</c>
        <c>        price sets, so I'll open it.",  "action": "click",  "link": 48</c>

<b>[ 12.9s]</b> <g>[browser OPEN]</g> <b>Step 1: click 48 'Pricing'</b>
        now on https://apify.com/pricing

<b>[ 21.1s]</b> <g>[browser OPEN]</g> <b>Step 2: ask anthropic/claude-haiku-5.5  <m>(browser waits, same page, same cookies)</m></b>
        4.5s, 20756 tokens in, 689 out, $0.0024
        <c>"page_type": "pricing",</c>
        <c>"prices": [ Free 0, Starter 19, Scale 199, Business 999  (USD/month, billed monthly) ],</c>
        <c>"why": "The monthly prices are captured, so I'll flip the toggle to 'Bill annually'</c>
        <c>        to capture the annual price set.",  "action": "click",  "link": 54</c>

<b>[ 25.5s]</b> <g>[browser OPEN]</g> <b>Step 2: click 54 '-10% Bill annually'</b>
        same URL, the page changed in place <m>(a new browser would lose this)</m>

<b>[ 33.5s]</b> <g>[browser OPEN]</g> <b>Step 3: ask anthropic/claude-haiku-5.5</b>
        <c>"why": "Both the monthly and annual price sets are now captured ... the goal is reached.",</c>
        <c>"action": "done"</c>`,
      side: ['Each call gets the steps so far, <b>with the prices already saved</b>. Without them it flips the toggle back to double check',
             'A click that times out on a hidden menu link falls back to opening its URL'] },
    { kind: 'output', h: 'What it found, what it cost', cmd: 'python lessons/04-agent-loop/agent.py',
      out: `<b>Prices found</b>
  step 2  Starter                        19 USD  / month, billed monthly, + pay as you go
  <m>...</m>
  step 3  Starter                        17 USD  / month + pay as you go, billed annually
  <m>                               includes: $19 prepaid usage, $0.2 per compute unit, Chat support,</m>
  <m>                                         Bronze Apify Store discount</m>
  step 3  Scale                         179 USD  / month + pay as you go, billed annually
  <m>                               includes: $199 prepaid usage, $0.16 per compute unit, Priority chat support</m>
  step 3  Business                      899 USD  / month + pay as you go, billed annually
  <m>                               includes: $999 prepaid usage, $0.13 per compute unit, Account manager</m>

<b>Cost</b>
  browser: 1 session, open 41s = 3 x 15s blocks, 1 full page load(s) -> 3 units (time set the bill)
  model:   3 calls, 61785 tokens in, 2245 out, $0.0073
  17s of the 41s the browser was open, the model was thinking
  a new browser per step: 3 sessions -> at least 3 units, 3 x ~3s to connect,
  and 1 in-page change(s) lost (toggle, menu, banner)

<b>Timeline</b> <m>(0s -> 45s)</m>
  browser open  <g>    ####################################################### </g>
  model         <c>         ######           ########           #########  </c>

<b>Done in 44.5s.</b> Journey in output/04/apify.com/:
  01_home.jpg      click  Pricing
  02_pricing.jpg   click  -10% Bill annually
  03_pricing.jpg   done`,
      side: ['<b>includes</b>: what the plan gets you, in Apify\'s own unit. Prepaid dollars and compute units',
             'The green bar runs the whole way, the model calls sit inside it',
             'Replay: <code>playwright show-trace output/04/apify.com/trace.zip</code>. Look at the gap while the model thinks'] },
    { kind: 'points', h: 'Try',
      items: [
        '<code>agent.py Oxylabs</code>: pricing is under a menu. Does it get there?',
        '<code>agent.py Zyte --goal "find out if there is a free trial and what it includes"</code>',
        '<code>--model google/gemini-3.5-flash-lite</code>: more steps or fewer? Cheaper overall?',
        '<code>--max-steps 2</code>: what does the journey look like when it runs out?',
      ] },
  ] },

  { id: '05', title: 'Explore competitors', time: 15, cmd: 'python lessons/05-explore-competitors/explore.py', slides: [
    { kind: 'diagram', src: '../diagrams/05-explore.html' },
    { kind: 'run', h: 'Two terminals',
      cmds: ['streamlit run lessons/06-report/app.py', 'python lessons/05-explore-competitors/explore.py'],
      alt: ['python lessons/05-explore-competitors/explore.py --replay   # no wifi, recorded run'],
      note: 'Dashboard first, it waits for data. Then the agents, about a minute and a half. Next slide: a recorded run, if yours fails or the wifi is gone' },
    { kind: 'page', src: 'replay.html' },
    { kind: 'points', h: 'What to look at',
      items: [
        'Three green edges at once: three browsers open, three bills running',
        'Wall time vs the sum of browser times: that\'s what running in parallel saved',
        'Which one took the most steps? Bright Data: a cookie modal hid the plan amounts',
        'Open its <code>trace.zip</code> in <code>output/05/&lt;site&gt;/</code> and see where it went',
      ] },
  ] },

  { id: '06', title: 'Report', time: 10, cmd: 'streamlit run lessons/06-report/app.py', slides: [
    { kind: 'points', h: 'Answer the boss',
      items: [
        'Every price came from one step of one agent, on one page, with a reason. Nothing typed by hand',
        '<b>Price:</b> as shown, plus USD per month, monthly or annual. That\'s what makes the charts possible',
        '<b>Includes:</b> what the plan gets you, in the company\'s own unit',
        'Credits, queries, tasks, prepaid dollars: no common "price per request", so compare what you get',
      ] },
    { kind: 'run', h: 'Open the dashboard',
      cmds: ['streamlit run lessons/06-report/app.py'],
      alt: ['python lessons/05-explore-competitors/explore.py --replay --fast   # nothing ran? fill it from the recording'],
      note: 'Still open from lesson 05? Just switch to it' },
    { kind: 'page', src: 'replay.html?view=plans' },
    { kind: 'points', h: 'What to look at',
      items: [
        '<b>Entry price:</b> the cheapest paid plan. Who\'s the cheap way in?',
        '<b>Plan ladder:</b> who stops at a few hundred a month, who goes straight to "talk to sales"?',
        '<b>Annual discount:</b> the toggle from lesson 04 paying off',
        '<b>What each plan includes:</b> what $19 buys at Apify vs $9 at Import.io',
        '<b>The table:</b> check a few against the screenshots before it goes to your boss',
        '<b>What it cost:</b> units, dollars, minutes. Compare with doing it by hand',
      ] },
    { kind: 'points', h: 'Run it again next week',
      items: [
        'Every run adds to the same database, nothing is replaced',
        'Weekly runs turn the dashboard into price history: new tiers, dropped free plans',
        'That\'s the step from one-off research to monitoring',
      ] },
  ] },
];

const OUTRO = [
  { kind: 'title', h: 'Thanks', sub: 'Take the repo home, the code is short enough to read end to end', qr: true },
];
