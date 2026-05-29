# Social preview

The repository's social-preview image (the card shown when the repo link is
shared on X/LinkedIn/Slack/Hacker News).

- `social-preview.png` — the rendered 1280×640 image.
- `card.html` — the self-contained source. Edit this to change the card.

## Set it on GitHub

GitHub has no API for this — a maintainer uploads it once via the UI:

**Repo → Settings → General → Social preview → Edit → upload `social-preview.png`.**

## Regenerate after editing `card.html`

Rendered with headless Chromium (any tool that screenshots HTML at a 1280×640
viewport works). Example using Playwright:

```sh
# from a checkout that has playwright + chromium available
node - <<'JS'
import { chromium } from "playwright";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 2 });
await p.goto("file://" + process.cwd() + "/.github/social-preview/card.html", { waitUntil: "networkidle" });
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: ".github/social-preview/social-preview@2x.png", clip: { x:0,y:0,width:1280,height:640 } });
await b.close();
JS
magick .github/social-preview/social-preview@2x.png -resize 1280x640 -strip .github/social-preview/social-preview.png
```

Fonts (Source Serif 4, IBM Plex Sans/Mono) load from Google Fonts at render
time, matching nightlamp.app.
