## Automate the sources
Automated pulls write candidates to `data/candidates/`; only verified rows go into `data/incidents.csv`.

- [ ] openFDA: adverse event reports for robot-assisted surgical systems → `data/candidates/openfda.csv`
  - Blocked 2026-10-12: api.fda.gov could not be reached from the weekly agent's environment (the fetch needs a permission nobody was there to grant), so the pull couldn't be built or checked against live data. Needs either network access to api.fda.gov for the agent or a GitHub Action to run the pull.
- [ ] NHTSA Standing General Order crash reports for automated driving systems (not driver assistance) → `data/candidates/nhtsa.csv`
- [ ] OSHA severe injury reports that mention robots → `data/candidates/osha.csv`
- [ ] EU Safety Gate alerts for robots and automated machinery → `data/candidates/eu_safety_gate.csv`
- [ ] Weekly GitHub Action that runs the pulls, commits candidates and opens an issue listing new ones for review (pattern: the BCI Census `weekly.yml`)
- [ ] Site in `docs/` (GitHub Pages): counts by robot type, harm and evidence status, every row linked to its sources
- [ ] Weekly X thread draft in `posts/YYYY-MM-DD.md`, every post under 280 characters
