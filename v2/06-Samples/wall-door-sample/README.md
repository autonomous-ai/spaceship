# Wall and door sample: what the factory builds and tests

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-SMP-WD (proposed; the control pack adds it to `document-register.csv`) | P01 | DRAFT | 2026-10-31 | Layout Engineer |

Spaceship is the working name of v2 (FocusPod v2, the team's "Indoor Pod"). The factory's wall-and-door sample is the project's physical check (D-32). Sound, weight, fixings and assembly time get measured on it instead of trusted to a calculation. This folder is the package the factory needs to build that sample and test it.

Nothing here is released for production. Every physical test stays PLANNED until real data exists (guideline §10). Agents don't contact suppliers or order parts (REQ-DOC-02); where a part isn't named yet, it is on HOLD and the question goes on the factory's list.

## Read in this order

1. [build-list.md](build-list.md): what the factory builds. The sample items S1 to S7 and the test rigs R1 to R4, with sizes, layers, and the tests each one serves.
2. [parts-list.md](parts-list.md): every material and part, with its quantity, maker and product where one is picked, the status of each number, and its source.
3. [test-plan.md](test-plan.md): the 13 tests T01 to T13. For each: the method, who measures, the pass or fail limit and the requirement it ties to.
4. [hold-list.md](hold-list.md): what can't be built or tested until a part is named, a joint is designed or a drawing exists. Each item has an owner and a release condition.
5. [drawings-needed.md](drawings-needed.md): the Fusion drawings the factory needs from Milestone 2 before it cuts anything.

`python3 check_package.py` (from this folder) checks the package. It checks the status words, that every cited decision, requirement and issue exists, and that tests, items and HOLDs refer to each other correctly.

## The sample on one page

- **What gets built** (build list): one full lower side wall panel, L1, with its lining cassette (S1, S2); one ceiling cassette, C1, with its safety catch (S3); the door unit (S4), on HOLD until its hinges and lock are named. The tests also need the air sample, meaning both fan cartridges and the riser in a box the size of the right decor block (S5), a felt specimen for the absorption test (S6), and coupons (S7).
- **What gets measured** (test plan): wall sound transmission from 100 Hz (T01); the lighter fill next to the 32 kg/m³ one (T02); felt absorption on its 25 mm gap (T03); the 12 V fans' flow and octave noise in their cartridges (T04); recirculation at boost (T05); rivnut spin-out in the real 1.2 mm tube (T06); clip pull-out (T07); the ceiling catch's drop test (T08); the ACP-to-aluminium bond (T09); weight per m² (T10); timed assembly of the panel (T11); taking a cartridge out into the pod and back (T12). The door's tests (T13) wait for its hardware.
- **What it decides:**
  - whether the pod lands at or under the 420 kg cap (D-54). The layout study's estimate is 426.7 kg, open against the cap.
  - whether the 24 kg/m³ fill can replace the 32, saving 4.3 kg (D-54).
  - the real sound figure: 19.3 dB calculated, with 24 dB as the best case (D-53).
  - the rivnut tightening torque (D-48).
  - whether the clips and the ceiling catch hold their loads (D-47).
  - whether the fans meet 26 dB(A) at 53 l/s and 30 dB(A) at boost (D-52), without breathing their own exhaust (D-58).
  - whether a cartridge comes out into the pod in one piece or splits in two with a sealed slip joint (D-59).

## Where the numbers come from

| Key | Source |
|---|---|
| LS | Layout study, `v2/05-Engineering/layout-study/`, as updated by PR #20 (revision 16ea081): part sizes, weights, joint counts, assembly times |
| HW-SEL | Hardware selection, `v2/05-Engineering/hardware/selection.md` (PR #11, merged): products, interface data, clip loads, sample tests |
| HW-AA | Sound and air check, `v2/05-Engineering/acoustics-air/report.md` and `calc.py` (PR #11, merged): stack, R per band, felt data, fan duty, noise |
| SKL | Pod skeleton P03, `v2/01-CAD-Native/skeleton/BUILD-RECORD.md` and its parameter register: envelopes |
| DL | Decision log, `v2/00-Control/decision-log.md`. D-01 to D-48 are merged; D-49 to D-58 come from the control pack's PR #19, which wasn't merged when this was written |
| REQ | Requirements, `v2/00-Control/requirements.md` |
| ISS | Issue register, `v2/00-Control/issue-register.csv`. ISS-074 to ISS-080 come from PR #19 |
| GL | Engineering guideline, `docs/engineering-guideline.md` |

Every number in a table carries one of the five status words: confirmed, source, calculation, assumption or unverified. A value the PM decided is confirmed and cites its decision. Test results don't exist yet, so nothing here is "measured" (conventions §9).
