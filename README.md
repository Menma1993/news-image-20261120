# Friday 20 November 2026 — The World in One Day

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Menma1993/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard)
[![reward](https://make.fun/badge/news-image-20261120/Menma1993/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)
[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261120-blue)](https://make.fun/c/news-image-20261120)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A broadsheet front page summing up the world's news of **Friday 20
November 2026** in one 1024×1024 image: 40 stories, 6 continents, one
page. Built for the make.fun competition
[news-image-20261120](https://make.fun/c/news-image-20261120)
("Sum up 20 November's world news in one image").

Repository: **Menma1993/news-image-20261120**.

## What is on the page

- **Masthead** — giant serif date, red italic sub-headline naming the
  three leads.
- **By the numbers** — six verified Friday figures, each with its source:
  300,000+ evacuated ahead of Cyclone Akvan (IMD); 27 ballistic
  missiles of 110+ fired at Kyiv (Zelensky); Nikkei −4.8% in the Asia
  AI sell-off (Reuters); COP31 "35 by 35" goal backed by 75 nations
  (UN News); Japan core CPI 2.2% (Reuters); Pentagon's $48.3bn US war
  cost in Iran.
- **Three illustrated leads** — Russia's Kyiv barrage (110+ missiles, 27
  ballistic, 3 Dnipro bridges hit), Cyclone Akvan's landfall near
  Gopalpur, Odisha, and the COP31 final-day deadlock in Antalya.
- **Ten more drawn cards** — Asia AI sell-off, UK–EU reset deal,
  BepiColombo's Mercury arrival, Japan inflation, the Hormuz tanker
  fire, Gaza's Yellow Line, Italy's general strike, Bukele's third-term
  bid, the Senegal boat sinking, and Fiji's drought emergency.
- **Where it happened** — a dark world map with numbered pins 01–13, a
  full legend, and "positions approximate".
- **Briefs 14–40** — one line each, every one sourced.
- **Date check** — a red-framed strip naming exactly what was left out
  because it was Thursday's news (Shenzhen summit, ICJ Myanmar verdict,
  Anthropic IPO, Kerch Bridge strike, Houthi PIF-tower strike,
  US–Venezuela deal, Van Gogh sale), plus what is still unconfirmed
  (Dorogobuzh drone claim, the COP31 outcome, Voyager 1's light-day
  date).

Every figure on the page is attributed (IMD, Kyiv Post, Reuters, UN
News, AP, Pentagon, ESA/JAXA) or tagged "Officials say / Reported".
Nothing from Thursday 19 November is presented as Friday's news.

## How it is built

- `draw.py` — the renderer (Pillow, run locally at build time). It
  draws the whole page from scratch: cream paper, serif masthead,
  illustrated lead cards, the world map with simplified continent
  outlines, briefs, DATE CHECK and footer. Deterministic: running it
  twice writes byte-identical PNGs.
- `entry.png` — the rendered 1024×1024 front page (under 1 MiB).
- `main.py` — the grading entry point. Stdlib only: it copies
  `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output`).

Regenerate locally:

```sh
python3 draw.py          # writes entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
