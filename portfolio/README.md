# Yemi Genderson — React Portfolio

React + Vite single-page portfolio with Spanish/English toggle, responsive layout and JSON-driven content.

## Local development

```bash
cd portfolio
npm ci
npm run dev
npm run build
```

Edit `src/content.json` to update projects, skills, and copy. Vite's base path is `/yegecali/` for the GitHub Pages project URL `https://yegecali.github.io/yegecali/`.

## Deployment

Push to `gp-portfolio-build`. GitHub Actions builds `portfolio/dist` and commits only the generated static site to `gp-portfolio`. Set **Settings → Pages → Build and deployment → Deploy from a branch → gp-portfolio / (root)** once. The site is not published until that setting is enabled. No GitHub Pages workflow is required in the publishing branch.


## Validation and releases

Pull requests targeting `gp-portfolio-build` build and upload an artifact without
publishing. Pushes retain the existing publication to `gp-portfolio`.
The workflow uses Node.js 22 and `npm ci` with the committed lockfile.

Run the workflow on `gp-portfolio-build` with `create_release` enabled to publish
and then create a `portfolio-<run_id>.<attempt>` release. It targets the exact
source commit and includes `portfolio.tar.gz` and `SHA256SUMS`. Releases are
optional and are not marked as the latest release of the repository.
The existing `PAGES_DEPLOY_TOKEN` remains necessary for branch-based Pages;
release creation uses `GITHUB_TOKEN` with Contents write permission.
