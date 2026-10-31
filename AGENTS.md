# Working in this repo

This repo holds the FocusPod design (the team calls it "Indoor Pod"): the v1 source files and the v2 work. v2 has the working name Spaceship.

Before any design, CAD, drawing or BOM work, read and follow `docs/engineering-guideline.md`. It's the hardware team's engineering guideline for every version of the pod, not just one. It's in Vietnamese.

## Layout

- `docs/engineering-guideline.md`: engineering guideline for all versions.
- `sources/v1/`: v1 files as received (Indoor Pod V3). Reference only. Never edit them.
- `v2/`: v2 work. `v2/00-Control/v2-build-plan.pdf` is the plan to build v2, from the indoor pod lead engineer.

## Rules that matter most

The guideline has the full list. These are the ones that bite most often:

- Use mm everywhere. 3D uses X, Y and Z; 2D views and hole tables use X and Y only.
- Every number carries a status: confirmed, source, calculation, assumption or unverified.
- Don't edit `sources/`. Don't contact suppliers or order anything.
- A change to the look, overall size, architecture, main materials or key joints needs a change proposal for the hardware engineering lead. Don't wait for the answer: keep working with the change marked PROPOSED until he approves it.
- The repo is public, so leave out supplier quotes, margins and personal data.
