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

## 2026-10-14 (America/New_York): weekly run
- Window: incidents reported 2026-09-30 to 2026-10-14. About 40 web calls.
- Incidents added: 2. Total: 25.
  - RIC-2026-013: a driverless Waymo in Tampa reportedly turned into oncoming traffic on a temporary one-way street (2026-10-04). Waymo confirmed it entered the street. No collision. Coded `near_miss` because the operator documented it.
  - RIC-2026-014: NHTSA opened defect petition DP26010 (2026-10-09) on alleged Tesla robotaxi speeding in active school zones. No crashes.
- TODO done: openFDA pull. api.fda.gov is reachable now. `python -m census openfda` wrote 83 injury and death reports (product code NAY, received 2026-09-14 to 2026-10-14) to `data/candidates/openfda.csv` for review. None of them were added to the census.
- Not added:
  - Tesla Cybercab with a torn-off door panel in Philadelphia (around 2026-10-07): only Reddit photos, and Electrek says it was most likely human-driven.
  - Humanoid robot that touched a 16-year-old girl in Cologne (2026-10-10): police are investigating whether two young people were controlling it, the harm doesn't fit a harm class, and it involves a minor.
  - Statesman report of "Texas' first fatal autonomous vehicle collision": the page couldn't be opened, so the date and details are unverified.
- Needs Geraldo's decision:
  1. Dating a regulatory action that has no dated incident: RIC-2026-014 uses the date NHTSA opened the file. Is that the convention you want? It cites news (tier C) because the NHTSA PDF (INOA-DP26010) couldn't be opened from here.
  2. Should the openFDA pull also cover other product codes? OLO covers Mako, ROSA, Mazor and VELYS but also includes non-robotic navigation systems.
  3. A missed backfill candidate: a Coco delivery robot was hit by an LAFD ambulance in Hollywood (about 2026-01-23, no injuries, CBS LA). Should it be added?
  4. The Statesman fatality report needs a source that opens. Should a later run try again?

## 2026-10-21 (America/New_York): weekly run
- Window: incidents reported 2026-10-07 to 2026-10-21. About 45 web calls. `census/next` was already up to date with `main`, so the rebase was a no-op.
- Incidents added: 1. Total: 26.
  - RIC-2026-015: Tesla reported to NHTSA its first Cybercab crash (SGO report 13781-16672, August 2026, Austin): with the ADS engaged and a safety monitor aboard, it drove into a water-filled pothole at up to 5 mph. Property damage only. Tier A (NHTSA SGO ADS file, published in mid-October).
- TODO done: NHTSA pull. `python -m census nhtsa` reads only the ADS crash-report file and wrote 185 reports submitted August to October 2026 to `data/candidates/nhtsa.csv` for review. None of them were added to the census.
- Not added:
  - Tesla crashes while a remote operator was driving (Electrek, 2026-10-15; SGO 13781-16678 Dallas and 13781-16679 Austin, both August 2026, property damage only). A remote human was in control, which looks like "a human is driving" under the methodology, so I left them out.
  - Waymo Houston barrier-wall crash (SGO 30270-16552, September 2026, test driver hospitalized with minor injuries). The report says the test driver had switched to manual mode before impact.
  - Delivery-robot biometric lawsuits in Chicago (Block Club, 2026-10-16), a Philadelphia protester arrested for blocking a robot (2026-10-14), and the Cologne humanoid (already declined last week): no physical harm from the robot.
- Needs Geraldo's decision:
  1. Remote-operator crashes: are robotaxi crashes while a remote human drives in scope, or out like driver assistance?
  2. The SGO ADS file is a rolling download (it currently covers submissions from June 2025). RIC-2026-015 cites it with the report ID in the summary. Is that citation style OK, given that older periods move to archive files?
  3. Verified backfill candidates that fell outside the window (not added):
     - Waymo, Dallas, August 2026: a pedestrian struck by an SUV was thrown into a slowing Waymo and died (SGO 30270-16196). This is the Statesman's "Texas' first fatal autonomous vehicle collision" from last week's open question. The Waymo didn't cause the impact.
     - Waymo, Tempe, September 2025: a motorcycle fatality (SGO 30270-11713). Not yet reviewed in detail.
     - Avride: NHTSA PE26003, opened 2026-05-06, covering 16 crashes in Dallas and Austin, 1 alleged minor injury (https://static.nhtsa.gov/odi/inv/2026/INOA-PE26003-14280.pdf).
     - Hellobike robotaxi struck two pedestrians in Zhuzhou, China, December 2025 (Yicai, CarNewsChina). Not yet opened.
     - Västtrafik/Karsan autonomous bus rear-ended by a tram in Gothenburg, 2026-05-25, no injuries (Startup Fortune citing Reuters).

## 2026-10-28 (America/New_York): weekly run
- Window: incidents reported 2026-10-14 to 2026-10-28. About 30 web calls. `census/next` was already up to date with `main`, so the rebase was a no-op.
- Incidents added: 1. Total: 27.
  - RIC-2026-016: in Tallinn on 2026-10-26, a Bolt delivery robot made by Starship reportedly entered a crossing on a red light. A city bus braked hard and hit it, and up to nine passengers were hurt (per operator TLT). The robot left the scene, and Starship opened an internal investigation. Evidence is `under_investigation`. Tier C (ERR, DPA via Yahoo).
- TODO: OSHA pull blocked. www.osha.gov returns 403 (CloudFront) to this environment, and data.dol.gov's API needs a key. I added a note under the item and didn't build it.
- Not added:
  - Unitree H2-X lost a leg after a side flip at a Hangzhou demo (2026-10-22): no injury and no damage beyond the robot itself.
  - CMR Surgical Versius console recall Z-2717-2026 (Secure Boot not enabled): a cybersecurity issue that doesn't affect how the robot senses, decides or moves.
  - KXAN/Statesman "Austin hits 249 robotaxi wrecks" (2026-10-27): aggregate SGO counts. Its newest individual crashes (Zoox and Tesla, August 2026) are already in `data/candidates/nhtsa.csv`, and none has a causal account.
- Needs Geraldo's decision:
  1. OSHA: give the agent network access to osha.gov, or provide a DOL API key (for example as an Actions secret)?
  2. A verified candidate outside the window: a worker died on 2026-09-25 after an automatically operating robotic arm in a product-loading system struck him on 2026-09-21 at Ottogi SF's plant in Goseong, South Korea. A co-worker reportedly switched the arm's power back on. The Ministry of Employment and Labor and the police are investigating (Nocut News, 2026-09-29: https://en.nocutnews.co.kr/news/6584202). Should it be added?
  3. RIC-2026-016 cites Starship as the maker (DPA), while ERR calls it a Bolt robot. The company column shows both.
