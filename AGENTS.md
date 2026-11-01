# Working in this repo

This repo holds the FocusPod design (the team calls it "Indoor Pod"): the v1 source files and the v2 work. v2 has the working name Spaceship.

Before any design, CAD, drawing or BOM work, read `v2/00-Control/v2-build-plan.pdf`, the plan to build v2 from the indoor pod lead engineer. It is the main guide (the owner's instruction, 2026-11-01). `docs/engineering-guideline.md` (in Vietnamese) is a secondary reference only: check a rule from it before you rely on it, and where it conflicts with the build plan, the build plan wins.

## Layout

- `docs/engineering-guideline.md`: a secondary reference; check before relying on it.
- `sources/v1/`: v1 files as received (Indoor Pod V3). Reference only. Never edit them.
- `v2/`: v2 work. `v2/00-Control/v2-build-plan.pdf` is the plan to build v2, from the indoor pod lead engineer, and the main guide.

## Rules that matter most

These are the ones that bite most often:

- Use mm everywhere. 3D uses X, Y and Z; 2D views and hole tables use X and Y only. The one exception: Fusion's STEP export always writes cm. Keep the file as Fusion wrote it, with its declared unit; don't convert it (decision D-13).
- Every number carries a status: confirmed, source, calculation, assumption or unverified.
- Don't edit `sources/`. Don't contact suppliers or order anything.
- The PM (the Swarm Lead) makes product and design decisions and records each one, with its reason, in `v2/00-Control/decision-log.md`. Nothing waits for outside approval. Follow the build plan; any approval step in either document is replaced by this log. The one hard rule on the look: it stays exactly as the team designed it.
- The repo is public, so leave out supplier quotes, margins and personal data.
