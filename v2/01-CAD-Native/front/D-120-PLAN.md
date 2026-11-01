# FRONT decor blocks: every part a component (D-120)

Status: PLAN (2026-11-01). Built on this drawings branch in one pass, after Control allocates the member numbers (the Lead passed FRONT's member list to Control on 2026-11-01). Method proved on one sample block first (DT, the smallest frame), then DR and DL.

## What D-120's check finds today (C06, on #105)

| Part | Today | After |
|---|---|---|
| 351104 DL frame, 351204 DT frame, 351306 DR frame | one component holding its 26, 13 and 24 tube bodies | a weldment assembly that keeps its number (D-123 (1)); each tube its own component with its member number |
| 351103 DL hinge-side stop | one component, 4 angle lengths | each length its own component (Control's numbers) |
| 368005 frame-stop seal in DL | one component, 4 pieces | each piece its own component of the bought part 368005 (bought by length) |

## Which tubes are the same part

The Lead's rule (2026-11-01): tubes share a number only if section, length, both end cuts (mitre angles included) and holes are all the same; a mirrored tube gets its own.

Checked on the model (the frame data evaluated on skeleton P04: each tube's solid compared with every other's under the 24 turns of the axis cube and a shift, never a mirror; the section, wall and holes compared too): **48 different tube parts in 63 tubes**.

| Frame | Tubes | Parts | Repeats (each a pure shift of the first) |
|---|---:|---:|---|
| DR 351306 | 24 | 21 | C01, C04, C05 (Z +1820, +2068.86); C06, C08 (X +541.85) |
| DT 351204 | 13 | 11 | C01, C02, C03 (X +555.28, +984.82) |
| DL 351104 | 26 | 16 | R1D to R4D and R1K to R4K (Z +612.25, +1366.75, +1988.75); R2O to R4O and R2F to R4F (Z +754.5, +1376.5) |

DR's glass-edge tubes F06 and B07 have the same length but different end cuts: two parts. DL's bottom ring tubes R1O and R1F carry the J-FRONT-02 spigot hole and slot: their own parts. The tubes with holes (DR B01, B02, B05, B08; DT B01, B03; DL B04, R1O, R1F) and the hinge posts (H1 to H3, hinge holes HOLD) are single parts; DT's F02 and R02 take the stop's and catch's screws (holes not modelled yet) and stay single.

## How the model changes (FRONT's files only)

- `frame_lib.build_members`: each member gets a new component under the frame's (identity placement, so its sketch keeps the frame's expressions and stays fully constrained), named `PARTNO NAME`, with its part number; its prism and shell are built inside it. A repeat is a second occurrence of the first copy's component, placed by a rigid joint from its origin to a sketch point at the shift (expressions of the parameters, so an edit moves it), as CEILING places its cross members.
- The block scripts cut each hole in its member's own component (today the cuts sit in the frame component).
- DL's stop lengths and seal pieces: one component each.
- Parts lists: the frame row becomes a weldment row (its mass the sum of its members) with one row per member part (quantity = its copies); the tube cut lists stay, keyed by member and part number.
- Edit test and clash check run per occurrence; the STEP keeps the assembly tree.
- Drawings: each frame's weldment drawing stays in Fusion; the member tubes are plain cut tubes for the drawing generator (D-112).

## Checks before the PR (D-118)

Every component has a part number; repeats are copies; quantities and masses follow the copies and match today's masses (DL 12.30, DT 7.84, DR 18.32 kg); 0 clashes; every sketch fully constrained; edit test PASS; the STEP opens with the assembly tree and re-reads exactly; C06 finds nothing for FRONT; master BOM clean; the roll-up and packing rerun.
