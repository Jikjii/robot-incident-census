# Build log

## 2026-10-12 (America/New_York): setup
- Repo skeleton: methodology, schema, validator, tests and CI.
- Incidents: 0. The weekly keeper's first run backfills verified incidents since January 1, 2025.
- Next: the first backfill, then the first TODO item (openFDA).

## 2026-10-12 (America/New_York): first backfill
- Incidents added: 23 (RIC-2025-001 to 013, RIC-2026-001 to 010), covering January 2025 to September 2026. Total: 23.
- Mix: 12 robotaxi, 5 surgical, 3 delivery, 2 service (robotic pool cleaners), 1 industrial. 12 rows rest on tier A records (NHTSA, FDA, CPSC); 11 on tier C news.
- Not added for now: no humanoid, cobot or warehouse incident had a source with a confirmed date in range. The viral Unitree G1 "clown" kick of a child (Futurism, June 2026) has no incident date. The Figure AI whistleblower suit (Nov 2025) describes a risk, not a dated event. The Waymo "KitKat" cat death (Oct 2025) was skipped because the harm column has no category for animals.
- TODO: openFDA pull blocked. api.fda.gov couldn't be reached from the agent's environment, so I added a note under the item and didn't build it.
- Needs Geraldo's decision:
  1. Recalls whose sources report no injury are rows with harm `none`, dated to when the firm started the recall (FDA/CPSC) or to the first incident in the chronology (NHTSA). Is that the convention you want?
  2. `under_investigation` was set when the cited source said an investigation was open (NHTSA PE25013 and the Santa Monica PE, OSHA at Palermo's, Nevada Highway Patrol, Wuhan). Those statuses reflect the source date, so later runs should recheck them.
  3. Zoox's injuries to test-vehicle occupants (RIC-2025-001, -005) come from OSHA data as reported by TechCrunch and count as automated-driving testing. Do you want to keep them in scope?
  4. Some NHTSA, CNBC and news URLs that were linked from other pages, or built by hand, couldn't be opened from this environment. Only pages that opened are cited, so several rows cite news (tier C) even though an official record probably exists.

## 2026-10-12 (America/New_York): weekly run (manual fire)
- The trigger said `data/incidents.csv` held only a header. That's true on `main` but not on `census/next`, which already had the 23 backfill rows in open PR #1. So I didn't repeat the backfill and ran the 14-day window instead.
- Incidents added: 1 (RIC-2026-011, humanoid, Colombia, Oct 2026). Total: 24.
- Correction: RIC-2026-001 now cites NHTSA PE26001 first and is tier A.
- TODO: openFDA is still blocked (see the note under the item), so no TODO commit.
- Needs Geraldo's decision:
  1. Two verified incidents fell just outside the 14-day window and the backfill missed them, so I didn't add them. Should they go in? They are the DePuy Synthes/Medos Velys robotic-assist station FDA Class II recall (initiated 2026-07-23; the arm may move unintentionally; https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfres/res.cfm?id=221615) and a humanoid that kicked at a customer and staff at a store in Russia on 2026-08-31 with no injuries (Men's Journal).
  2. RIC-2026-011 cites only one Colombian outlet, and the robot's maker isn't named.

## 2026-10-12 (America/New_York): review decisions applied
- Geraldo's decisions are now in METHODOLOGY.md: recalls with no reported injury count, with harm `none`, dated to when the recall started (for NHTSA, the first incident in the chronology); injuries to people on board test vehicles are in scope, so RIC-2025-001 and -005 stay; recalls must concern how the robot senses, decides or moves.
- Removed: RIC-2025-003 and RIC-2026-006 (robotic pool-vacuum battery and charger recalls). Their IDs are retired.
- Added: RIC-2026-012, the VELYS robotic-assist station recall (FDA Z-3088-2026). Total: 23.
- RIC-2026-011 now has a second source (Noticias RCN).
- Not added: the Saratov store humanoid (video posted 2026-09-01). Its sources don't confirm the date, an injury or any damage, no regulator or operator documented a near miss, and Tom's Guide suggests the scene was staged, so it doesn't meet the incident definition.
- TODO: no item done; openFDA is still blocked.
- Needs Geraldo's decision: how to unblock openFDA (network access for the agent, or a GitHub Action that runs the pull), and whether weekly runs should recheck `under_investigation` rows.
