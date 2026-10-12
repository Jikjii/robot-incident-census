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
