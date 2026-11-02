# Profile README generator v2.0

Edit `.readme/data.json` (Spanish/English descriptions, technology badges, projects and links) and optionally `.readme/README.md.j2`.

Run locally:

```bash
python -m pip install -r .readme/requirements-dev.txt
python .readme/build_readme.py --check
python -m pytest -q .readme/tests
python .readme/build_readme.py
```

The workflow on `build-readme` validates JSON, runs tests, generates the Markdown, and publishes **only** the generated root `README.md` to `main` if it changed. It does not merge source files into `main`. Branch protection or restricted token permissions may block publishing; review the workflow run for details.

The generated profile now shows only the Spanish introduction and technology
badges. English and featured-project data remain available in JSON but are not
rendered. Change the template to reintroduce them intentionally.

Pull requests targeting `build-readme` validate and generate an artifact without
publishing. A manual run with `create_release` enabled publishes the README and
creates a `readme-<run_id>.<attempt>` release targeting the source commit, with
`README.md` and SHA-256 checksums. Automatic pushes continue publishing to `main`
without creating releases. Releases require Actions Contents write permission;
protected branches can still prevent publishing.
