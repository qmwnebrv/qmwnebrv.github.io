# dannytsmith.com (2014), static rebuild

Live at https://qmwnebrv.github.io

A static HTML copy of the Adobe Muse site in `../dannytsmithcom.muse`, rebuilt so it can be viewed without Muse (discontinued 2018).

## Viewing the site

Serve this folder with any static web server, then open http://localhost:8765:

```bash
python -m http.server 8765
```

(Or `cd` into this folder and run `python -m http.server 8765`.)

Opening `index.html` straight from the file system mostly works too, but the embedded YouTube videos need the page to be served over http.

## Contents

| File | Page |
|---|---|
| `index.html` | Home |
| `photo.html` | Photo (links to the two galleries) |
| `varanassi.html` | Varanassi gallery (slideshow, 14 images) |
| `black-and-white.html` | Black & White gallery (slideshow, 19 images) |
| `video.html` | Video (two YouTube embeds) |
| `about.html` | About |

`style.css` holds the shared styles, `slideshow.js` runs the gallery slideshows, and `images/` holds the images taken from the `.muse` file.

## Rebuilding

`_build_from_muse.py` regenerates the HTML pages and `images/` from `../dannytsmithcom.muse`. That file is a SQLite database holding the page layout as XML, with the images embedded. The script only uses the Python standard library:

```bash
python _build_from_muse.py
```

It doesn't touch `style.css` or `slideshow.js`. It writes to the `OUT` path set at the top of the script.

## Differences from the original

- The footer's Facebook "Like" widget is left out, because the 2014 embed code no longer works.
- The Gill Sans labels fall back to similar fonts if Gill Sans isn't installed.
- The slideshow is a simple rewrite, not Muse's own widget code, so the button styling is approximate.
