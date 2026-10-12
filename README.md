# Robot Incident Census

How often do robots hurt people or break things? And when they do, can anyone prove what the robot
actually did? The Robot Incident Census is a public registry of robot incidents, with a source for every
row, updated every week.

The data lives in [`data/incidents.csv`](data/incidents.csv). The rules for what counts are in
[METHODOLOGY.md](METHODOLOGY.md).

## What each row holds

| Column | Meaning |
|---|---|
| `id` | `RIC-YYYY-NNN`, where `YYYY` is the year of the incident |
| `date` | When it happened: `YYYY-MM-DD`, or `YYYY-MM` / `YYYY` when only that much is known |
| `robot_type` | `surgical`, `robotaxi`, `warehouse`, `industrial`, `cobot`, `humanoid`, `delivery`, `service` or `other` |
| `company` | The company whose robot was involved (operator, maker, or both) |
| `location` | City or region, and country |
| `summary` | What happened, in one plain sentence (280 characters at most) |
| `harm` | `fatality`, `injury`, `property`, `near_miss`, `none` or `unknown` |
| `evidence` | Whether anyone could show what the robot did (see below) |
| `source_tier` | Best source: `A` official records, `B` the company, `C` reputable news |
| `sources` | Links, separated by spaces, primary source first |
| `added` | The date the row was added |

## The evidence column is the point

For every incident the census records what the sources say about the robot's own record of events:

| Value | Meaning |
|---|---|
| `logs_public` | The robot's data, logs or video were released publicly |
| `logs_cited` | An official source relied on the robot's data without publishing it |
| `logs_disputed` | Parties disagree about what the robot did or what its data shows |
| `logs_unavailable` | Data was reported missing, lost, overwritten or never recorded |
| `under_investigation` | An investigation is open and its findings aren't public yet |
| `unknown` | The sources don't say |

## How it's updated

Every week a research agent finds new incidents, opens every source, checks the facts and the privacy
rules, and proposes the new rows in a pull request titled "Census update DATE". CI validates every row
on every push. Nothing reaches `main` until it's been reviewed.

Next on the roadmap ([TODO.md](TODO.md)) are automated pulls from public records (openFDA, NHTSA,
OSHA, EU Safety Gate), a site, and a weekly thread, following the
[BCI Census](https://github.com/Jikjii/bci-census) design.

## Check the data locally

Python 3.11 or newer.

```bash
pip install -r requirements.txt
python -m census validate      # checks data/incidents.csv against the schema
python -m pytest -q
```

## Corrections

Spotted a mistake or a missing incident? Open an issue with a link to a source.

## Disclosure

The maintainer, Geraldo Grell, is building [robot-black-box](https://github.com/Jikjii/robot-black-box),
a tamper-evident incident recorder for robots. The census records what sources say; it doesn't assign
fault.
