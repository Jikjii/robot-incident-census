# Working rules for agents in this repo

This is the Robot Incident Census: a public, sourced registry of robot incidents. Read
[METHODOLOGY.md](METHODOLOGY.md) before adding anything.

## Branches
- Agents push only to `census/next` and propose changes in a pull request titled "Census update DATE".
- Geraldo merges into `main`. Never push to `main`, never force-push, never delete branches.

## Adding incidents
- Open every source you cite and confirm the date, company, what happened and the harm. Never cite a page you didn't open.
- Prefer tier A sources (official records), then B (the company), then C (reputable news with named sources).
- Never include names or identifying details of private individuals: patients, workers, passengers or bystanders.
- Use `unknown` rather than guessing, especially for `evidence`.
- Say "reported" whenever the source is a report or allegation rather than a finding.
- Skip anything already in `data/incidents.csv`; check the same date, company and robot before adding.
- IDs are `RIC-YYYY-NNN`, where `YYYY` is the incident year and `NNN` continues after the highest number
  used that year. Never reuse a retired ID (listed under Corrections in METHODOLOGY.md).

## Checks
- Run `python -m census validate` and `python -m pytest -q` before every commit; commit only when both pass.
- Work from `TODO.md` one item per commit, ticking the item in the same commit.
- Append an entry to `BUILDLOG.md` at the end of every session: date (America/New_York), incidents added,
  total, TODO item done, anything that needs Geraldo's decision.
