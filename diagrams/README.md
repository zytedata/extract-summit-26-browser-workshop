# Animated diagrams

The diagrams from the lessons, built up step by step. Open one in your browser, straight from the folder, no server needed:

| Diagram | Lesson | What it shows |
|---|---|---|
| [01-model.html](01-model.html) | [01 First session](../lessons/01-first-session/) | the mental model: your script on the laptop, CDP over a WebSocket to a Chrome in Zyte's cloud, unblocking, the proxy, the website, the model on the side |
| [01-session.html](01-session.html) | [01 First session](../lessons/01-first-session/) | one Zyte browser session from connect to `Browser.close`, the proxy pick, a challenge handled, the billing |
| [03-describe.html](03-describe.html) | [03 Describe a page](../lessons/03-describe-a-page/) | open Apify's homepage, capture screenshot + markdown + numbered links, close the browser, then ask the model. Numbers from a real run |
| [04-agent-loop.html](04-agent-loop.html) | [04 Agent loop](../lessons/04-agent-loop/) | a recorded run on zyte.com with its real screenshots: capture, ask the model, act, four times (Pricing, reject cookies, scroll, done), with the steps so far, the model time inside the browser time, and what it cost |
| [05-explore.html](05-explore.html) | [05 Explore competitors](../lessons/05-explore-competitors/) | the recorded top 5 run: a queue, three agents with their own browsers, every step into one database, the dashboard reading it |

Keys: space, → or a click for the next step. ← goes back one, `r` starts again. Add `?auto=1` to the URL and it plays through by itself, which is handy for recording.

They load GSAP and two fonts from a CDN, so open them once while you're online. After that the browser has them cached.

`diagram.js` and `diagram.css` are the shared parts: the colours, arrows, labels, icons and the step controls. A new diagram is one HTML file that calls `D.run()` with its steps, see the two above.
