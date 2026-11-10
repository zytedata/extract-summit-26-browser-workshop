# Workshop deck

The whole workshop in one page: open `index.html` in your browser, straight from the folder, no server needed. Same deck on the projector and on your laptop.

Keys: → or space for the next slide, ← back. On the animated diagrams → steps through the diagram first, then moves on. `0`-`6` jump to a lesson, `f` fullscreen, `r` restarts a diagram.

The bar at the bottom always shows the lesson and the command to run, with a copy button. The URL changes with the slide (`#03.2` is lesson 03, slide 2), so a reload keeps your place.

Content is in `slides.js`, the slide kinds are listed at the top. Terminal output on the slides is from real runs. Like the diagrams it loads fonts, mermaid and a QR code library from a CDN, so open it once while online.

## The recorded run

`replay.html` plays a real lesson 05 run (the one in `data/sample-run.db`) with its real timing: agents working 3 at a time, plans and what they include filling in. `replay.html?view=plans` is the end result, one column per company. Both are slides in the deck, so if a live run fails or the wifi is gone, the slide still shows a real run. Open on their own: space pauses, `s` changes speed, `r` restarts.

The data is in `run.js`, made from the recording:

```bash
python lessons/05-explore-competitors/explore.py               # a live run
python lessons/05-explore-competitors/explore.py --save-sample # keep it as data/sample-run.db
python deck/export_run.py                                      # -> deck/run.js
```

## Presenting

- Browser and terminal in two macOS fullscreen spaces, swipe between them (or ctrl+← / ctrl+→)
- A terminal profile for the projector: ~22pt font, dark, short prompt. `clear` before each run
- Run the command live, then come back to the "what you should see" slide if your run went sideways
