# Yemi Genderson — React Portfolio

React + Vite single-page portfolio with Spanish/English toggle, responsive layout and JSON-driven content.

## Local development

```bash
cd portfolio
npm install
npm run dev
npm run build
```

Edit `src/content.json` to update projects, skills, and copy. Vite's base path is `/yegecali/` for the GitHub Pages project URL `https://yegecali.github.io/yegecali/`.

## Deployment

Push to `gp-portfolio-build`. GitHub Actions builds `portfolio/dist` and commits only the generated static site to `gp-portfolio`. Set **Settings → Pages → Build and deployment → Deploy from a branch → gp-portfolio / (root)** once. The site is not published until that setting is enabled. No GitHub Pages workflow is required in the publishing branch.
