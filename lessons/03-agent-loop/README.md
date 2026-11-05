# 03 Agent loop

Goal: let Claude drive. On every page it describes what it sees and picks the next action. The loop runs in one browser session until Claude says it's done or hits the page limit.

Actions: click a link or button, scroll, toggle (monthly/yearly), done.

Each step is saved to `output/<site>/`:
- `NN_<slug>.jpg` screenshot
- `NN_<slug>.md` page markdown
- one line in `journey.jsonl`: url, description, action, why

The three places to make it yours are marked `# YOUR TURN` in `agent.py`:
1. the prompt that describes the page
2. which actions the agent is allowed to take
3. when to stop

Start on the fake shop (Browser Lab), then try a real site.

TODO: starter + solution
