## Automate the sources
Automated pulls write candidates to `data/candidates/`; only verified rows go into `data/incidents.csv`.

- [x] openFDA: adverse event reports for robot-assisted surgical systems → `data/candidates/openfda.csv`
  - Done 2026-10-14: `python -m census openfda [--days N | --since DATE] [--until DATE]` pulls injury and death reports for product code NAY (computer-controlled surgical systems) and keeps identifiers, dates and a MAUDE link only, no narrative text.
- [x] NHTSA Standing General Order crash reports for automated driving systems (not driver assistance) → `data/candidates/nhtsa.csv`
  - Done 2026-10-21: `python -m census nhtsa [--days N | --since DATE] [--until DATE]` reads NHTSA's ADS crash-report file only (no Level 2 file), keeps the latest version of each report submitted in the window, and keeps identifiers, months, city, operator type, engagement status and the alleged injury level, with no narrative, VIN, address or coordinates.
- [ ] OSHA severe injury reports that mention robots → `data/candidates/osha.csv`
  - Blocked 2026-10-28: www.osha.gov (the Severe Injury Reports page and the IMIS accident search) answers 403 from CloudFront to the agent's environment, and data.dol.gov's enforcement API needs a registered API key. Needs network access to osha.gov or a DOL API key (for example as a GitHub Actions secret).
- [ ] EU Safety Gate alerts for robots and automated machinery → `data/candidates/eu_safety_gate.csv`
- [ ] Weekly GitHub Action that runs the pulls, commits candidates and opens an issue listing new ones for review (pattern: the BCI Census `weekly.yml`)
- [ ] Site in `docs/` (GitHub Pages): counts by robot type, harm and evidence status, every row linked to its sources
- [ ] Weekly X thread draft in `posts/YYYY-MM-DD.md`, every post under 280 characters
