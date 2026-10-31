# Working in this repo

This repo holds the FocusPod design (the team calls it "Indoor Pod"): the v1 source files and the v2 work. v2 has the working name Spaceship.

Before any design, CAD, drawing or BOM work, read and follow `docs/engineering-guideline.md`. It's the hardware team's engineering guideline for every version of the pod, not just one. It's in Vietnamese.

## Layout

- `docs/engineering-guideline.md`: engineering guideline for all versions.
- `sources/v1/`: v1 files as received (Indoor Pod V3). Reference only. Never edit them.
- `v2/`: v2 work. `v2/00-Control/v2-build-plan.pdf` is the plan to build v2, from the indoor pod lead engineer.

## Rules that matter most

The guideline has the full list. These are the ones that bite most often:

- Use mm everywhere. 3D uses X, Y and Z; 2D views and hole tables use X and Y only. The one exception: Fusion's STEP export always writes cm. Keep the file as Fusion wrote it, with its declared unit; don't convert it (decision D-13).
- Every number carries a status: confirmed, source, calculation, assumption or unverified.
- Don't edit `sources/`. Don't contact suppliers or order anything.
- The PM (the Swarm Lead) makes product and design decisions and records each one, with its reason, in `v2/00-Control/decision-log.md`. Nothing waits for outside approval. Follow the guideline's engineering rules, but its approval steps are replaced by this log. The one hard rule on the look: it stays exactly as the team designed it.
- The repo is public, so leave out supplier quotes, margins and personal data.
