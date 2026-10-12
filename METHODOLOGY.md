# Robot Incident Census methodology

The census answers two questions with receipts: when robots cause harm, what happened, and could anyone
prove what the robot did?

## What counts as a robot

A machine that senses, decides and moves in the physical world with some autonomy. In scope for version 1:

- **Surgical:** robot-assisted surgical systems
- **Robotaxi:** automated vehicles operating with no human driving (driverless service or automated-driving testing)
- **Warehouse:** autonomous mobile robots and automated storage systems in logistics
- **Industrial:** industrial robot arms and automated cells
- **Cobot:** collaborative robots designed to work beside people
- **Humanoid:** humanoid robots
- **Delivery:** sidewalk and road delivery robots
- **Service:** cleaning, hospitality, security and other service robots

Out of scope for version 1: drones and aircraft, driver-assistance systems where a human is driving,
software-only systems, and military systems.

## What counts as an incident

One event in which a robot:

- injured or killed someone,
- damaged property,
- caused a near miss that a regulator, court or the operator documented, or
- led to a safety recall or regulatory action.

Routine malfunctions with no safety impact are out.

## Sources and tiers

| Tier | Source |
|---|---|
| A | Official records: regulator reports and databases (for example NHTSA crash reports, OSHA records, FDA adverse event reports and recalls, EU Safety Gate alerts), court filings, official investigation reports |
| B | Statements from the company involved |
| C | Reputable news reporting with named sources |

Every row needs at least one source anyone can open, primary source first. Whoever adds a row must have
opened every source it cites and checked the date, company, what happened and the harm.

Some official records are allegations, not findings. FDA adverse event reports, for example, are
reports that a device may have been involved. Summaries say "reported" whenever the source does.

## The evidence column

It records only what sources say about the robot's own record of events: `logs_public`, `logs_cited`,
`logs_disputed`, `logs_unavailable`, `under_investigation` or `unknown`. When the sources are silent the
value is `unknown`. It's never inferred.

## Privacy

Never include names or identifying details of private individuals: patients, workers, passengers or
bystanders. Give no medical details beyond the harm class. Companies, agencies and public officials may
be named.

## What the census is not

- **Not a complete count.** Many incidents are never reported. The census is a floor.
- **Not a finding of fault.** Each row reports what its sources say, attributed to them.

## Corrections

Open an issue with a source. Corrections are made in the data, and the row's sources are updated to show
why.
