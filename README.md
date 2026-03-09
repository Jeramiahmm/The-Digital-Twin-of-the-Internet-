# Digital Twin of the Internet

An interactive, real-time visualization of global internet infrastructure — data centers, ISPs, internet exchange points, CDN edges, DNS servers, and end users — rendered on an HTML5 canvas.

## Features

- Animated network topology with live packet traffic
- Drag nodes to rearrange the layout
- Click nodes to inspect details (type, latency, uptime, traffic)
- Add new nodes that auto-connect to nearby infrastructure
- Pulse traffic bursts across all links
- Fully client-side — no backend required

## Run Locally

Open `index.html` directly in any modern browser:

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

Or use a local dev server:

```bash
# Python
python3 -m http.server 8000

# Node.js (install first: npm i -g serve)
npx serve .
```

Then visit `http://localhost:8000`.

## Host for Free

### GitHub Pages
1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Set source to your branch (`main` or `master`), folder `/ (root)`
4. Your site will be live at `https://<username>.github.io/The-Digital-Twin-of-the-Internet-/`

### Netlify
1. Go to [netlify.com](https://www.netlify.com) and sign in with GitHub
2. Click **Add new site → Import an existing project**
3. Select this repo — no build command needed, publish directory is `/`
4. Deploy — you get a free `.netlify.app` URL

### Vercel
1. Go to [vercel.com](https://vercel.com) and import this repo
2. Framework preset: **Other**
3. Deploy — live at a free `.vercel.app` URL

### Cloudflare Pages
1. Go to [pages.cloudflare.com](https://pages.cloudflare.com)
2. Connect your GitHub repo
3. Build command: (leave blank), output directory: `/`
4. Deploy

## Tech Stack

- Vanilla HTML, CSS, JavaScript
- HTML5 Canvas for rendering
- No dependencies, no build step
