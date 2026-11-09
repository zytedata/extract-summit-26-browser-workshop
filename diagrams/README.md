# Animated diagrams

The diagrams from the lessons, built up step by step. Open one in your browser, straight from the folder, no server needed:

| Diagram | Lesson | What it shows |
|---|---|---|
| [01-session.html](01-session.html) | [01 First session](../lessons/01-first-session/) | one Zyte browser session from connect to `Browser.close`, the proxy pick, a challenge handled, the billing |
| [04-agent-loop.html](04-agent-loop.html) | [04 Agent loop](../lessons/04-agent-loop/) | a recorded run on zyte.com with its real screenshots: capture, ask Claude, act, four times (Pricing, reject cookies, scroll, done), with the steps so far, the model time inside the browser time, and what it cost |

Keys: space, → or a click for the next step. ← goes back one, `r` starts again. Add `?auto=1` to the URL and it plays through by itself, which is handy for recording.

They load GSAP and two fonts from a CDN, so open them once while you're online. After that the browser has them cached.

`diagram.js` and `diagram.css` are the shared parts: the colours, arrows, labels, icons and the step controls. A new diagram is one HTML file that calls `D.run()` with its steps, see the two above.
