#!/bin/zsh
# Make the BASE drawings, one at a time through the Fusion lock:
# a start (tools/fusion/start_drawing.py) and one annotate run per drawing,
# then the offline finish (name strip, notes as text, PNG).
#   zsh v2/02-Drawings/base/run_drawings.sh 111101 111103 ...   (default: all)
cd "$(dirname "$0")/../../.."
typeset -A DESIGN SHEET
DESIGN=(110000 110000_P01_BASE_CAD
        110101 110101_P01_BASE-BAND-ASSY-SIDE-LH_CAD
        110103 110103_P01_BASE-BAND-ASSY-BACK_CAD
        110102 110102_P01_BASE-BAND-ASSY-SIDE-RH_CAD
        110104 110104_P01_BASE-BAND-ASSY-FRONT-LH_CAD
        110106 110106_P01_BASE-BAND-ASSY-FRONT-FIXED-GLASS_CAD
        111101 111101_P01_BASE-BAND-TUBE-SIDE-LH_CAD
        111103 111103_P01_BASE-BAND-TUBE-BACK_CAD
        111106 111106_P01_BASE-BAND-TUBE-FRONT-FIXED-GLASS_CAD
        111301 111301_P01_BASE-SILL-FIXED-GLASS_CAD
        111104 111104_P01_BASE-BAND-TUBE-FRONT-FACET-1-LH_CAD
        111105 111105_P01_BASE-BAND-TUBE-FRONT-FACET-2-LH_CAD
        111602 111602_P01_BASE-LEVELLING-GLIDE-M10-D40_CAD)
SHEET=(110000 A2 110101 A2 110103 A1 110102 A2 110104 A3 110106 A2 111101 A2 111103 A1 111106 A3 111301 A3
       111104 A3 111105 A3 111602 A3)
# D-139/D-158: the generator draws BASE's parts and assemblies; Fusion only the three it can't draw yet,
# 111104, 111105 and 111602 (the Lead's ruling of 2026-11-01, v2/02-Drawings/base/DRAWING-RECORD.md)
# No drawing (D-89): 111601 the glide doubler (part 4: DXF and parts-list row). No floor (D-132).
# Not BASE's: the corner keys 111211 to 111214 (the Joints Engineer's tabulated drawing; PM ruling 2026-11-01).
pns=("$@")
(( ${#pns} )) || pns=(110101 110103 110000 111106 111301)
for pn in $pns; do
  # a part number listed in the skip file is skipped when its turn comes, e.g. while
  # its hole positions are about to change (read at run time, so a queued session can be trimmed)
  skip=${BASE_DRAWING_SKIP:-v2/02-Drawings/base/.raw/skip.txt}      # .raw is git-ignored
  if [ -f "$skip" ] && grep -qx "$pn" "$skip"; then
    echo "== $pn: skipped (listed in $skip)"; continue
  fi
  d=${DESIGN[$pn]}
  w=${d%_CAD}_DWG
  echo "== $pn: $d -> $w (${SHEET[$pn]})"
  # --keep-open: the annotate run activates the open drawing instead of opening it from
  # the cloud (a drawing opened from the cloud hung Fusion on 2026-10-31)
  python3 tools/fusion/start_drawing.py "$d" "$w" --sheet "${SHEET[$pn]}" --keep-open \
      --label "BASE Engineer: start $pn" --lock-wait 3600 || { echo "start failed for $pn"; continue; }
  python3 tools/fusion/run_script.py v2/02-Drawings/base/base_drawings.py --doc "$w" --arg pn=$pn \
      --save "views, dimensions, holes" --close --label "BASE Engineer: annotate $pn" --lock-wait 3600 \
      || { echo "annotate failed for $pn"; continue; }
  python3 v2/02-Drawings/base/finish_pdfs.py $pn || echo "finish failed for $pn"
done
