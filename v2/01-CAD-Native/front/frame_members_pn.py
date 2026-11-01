"""D-120 member part numbers for the three decor frames, as Control allocated them (#232, v2/04-BOM/number-allocation.csv).

Each tube of a welded frame is its own component with its own number; tubes that are the same part (same section,
wall, length, both end cuts and holes, never mirrored: the Lead's rule of 2026-11-01) share one number and are copies
of one component. frame_lib.member_parts() reads the names from the allocation list and checks every number against it.
"""

DL_FRAME = "351104"
DL_MEMBERS = {
    "B01": "352101", "B02": "352102", "B03": "352103", "B04": "352104",
    "R1D": "352105", "R2D": "352105", "R3D": "352105", "R4D": "352105",
    "R1K": "352106", "R2K": "352106", "R3K": "352106", "R4K": "352106",
    "R1O": "352107", "R1F": "352108",
    "R2O": "352109", "R3O": "352109", "R4O": "352109",
    "R2F": "352110", "R3F": "352110", "R4F": "352110",
    "H1": "352111", "P1": "352112", "H2": "352113", "P2": "352114", "H3": "352115", "P3": "352116",
}

DT_FRAME = "351204"
DT_MEMBERS = {
    "B01": "352201", "B02": "352202", "B03": "352203", "B04": "352204", "B05": "352205",
    "F01": "352206", "F02": "352207", "F03": "352208", "R01": "352209", "R02": "352210",
    "C01": "352211", "C02": "352211", "C03": "352211",
}

DR_FRAME = "351306"
DR_MEMBERS = {
    "F01": "352301", "F02": "352302", "F03": "352303", "F04": "352304", "F05": "352305", "F06": "352306",
    "B01": "352307", "B02": "352308", "B03": "352309", "B04": "352310", "B05": "352311", "B06": "352312",
    "B07": "352313", "F07": "352314", "F08": "352315", "B08": "352316",
    "F09": "352322",        # the front ring's cross tube over the fan box (D-131 skin spans; Control, #287)
    "C01": "352317", "C04": "352317", "C05": "352317", "C03": "352318",
    "C06": "352319", "C08": "352319", "C09": "352320",
    # 352321 (C10, the joint's straight end) cancelled: C09 runs on to the back ring (PM ruling 2026-11-01)
}

# DL's hinge-side stop 351103 splits into its pieces (D-120; 351103 cancelled): ST2 and ST3 are one shape
DL_STOP = {"ST1": "351105", "ST2": "351106", "ST3": "351106", "ST4": "351107"}
