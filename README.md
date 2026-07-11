# ydilwoods-site

Statische site voor **ydilwoods.com** (Ydil Woods — uplifting trance).

## Structuur

- `data/releases.json` — bron van waarheid: alle releases, links, covers, artist-info.
- `build.py` — genereert de complete site → `public/` (geen dependencies, python3).
- `assets/yw-logo.png` — logo (bron).
- `public/` — gegenereerde site; **dit is wat Cloudflare Pages serveert**.

## Werkwijze

1. Wijzig `data/releases.json` (nieuwe release, status presave→released, links).
2. `python3 build.py`
3. Commit + push → Cloudflare Pages deployt automatisch.

## Release-statussen

- `announced` — datum bekend, nog geen pre-save (badge "AUG 2026", knop = Follow).
- `presave` — pre-save-fase (knop = presave-link; ontbreekt die → Follow on Spotify).
- `released` — uit (knop = Spotify; Apple/YouTube als ingevuld).

Op releasedag: status op `released` zetten, `links.spotify` invullen, rebuilden.

## Cloudflare Pages-instellingen

- Build command: *(leeg)* · Output directory: `public`
- Custom domain: ydilwoods.com (+ www)
