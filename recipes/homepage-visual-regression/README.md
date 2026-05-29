# Homepage visual regression

> The page is "up." It's also blank, unstyled, or missing its hero image.
> Conversion drops to zero and your status board stays green.

## Symptoms

- Landing page renders unstyled and stays that way.
- Hero image is missing or shows a broken-image icon.
- Page is technically up but visually broken; conversion drops to zero.

## Failure modes

- CSS/JS bundle URL changed after deploy; the page references the old one.
- A CDN purge removed assets the page expects.
- A font/image CDN began returning 403 (referer policy / hotlink protection).
- Theme migration left orphan classes; rendered DOM no longer matches CSS.
- A no-code "publish" action half-completed and left the site mid-state.

## Checks

Three monitors, layered.

1. **`visual_snapshot` at desktop (1440x900)** — diffs against a baseline
   image. Catches "page renders but looks wrong."
2. **`visual_snapshot` at mobile (390x844)** — higher threshold (mobile has
   more layout noise).
3. **`http_keyword`** — asserts the HTML references the current bundle
   marker (e.g. a build SHA in a `<meta name="build">` tag, or the hashed
   bundle filename). Catches stale-HTML-from-cache cases the snapshot misses
   when the cached HTML happens to render OK.

**Re-baseline** the snapshots whenever you intentionally change the design.

## Triage

1. Side-by-side compare failing snapshot vs baseline.
2. Open the page in incognito; Network panel for 404/403 on assets.
3. Confirm deploy completed; look for half-finished publishes.
4. Verify CDN cache purged for the homepage.
5. Re-baseline only after confirming the change is intentional.

## False positives

- Marketing banners, A/B variants, seasonal hero changes trip the diff.
  Bake a tolerance into the threshold or mask the variable region.
- Mobile snapshots are noisier than desktop; expect a higher threshold.

## Alert routing

- **Severity:** ticket.
- **Channel:** marketing-ops.
- **Suppress:** scheduled deploy windows, active re-baselining.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=homepage-visual-regression) packages these monitors, incident matching, and diagnostic playbooks for no-code and AI-built apps — so this recipe runs continuously and pages you in plain English when the contract changes.
