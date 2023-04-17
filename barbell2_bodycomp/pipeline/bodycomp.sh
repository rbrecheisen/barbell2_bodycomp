#!/bin/bash
export PYTHONPATH=$HOME/barbell2_bodycomp:$PYTHONPATH
python bodycomp.py \
    "/mnt/localscratch/cds/rbrecheisen/raw/tlodewick-ct-noise-1/AL_100%/101816478/2-Abdomen" \
    "/mnt/localscratch/cds/rbrecheisen/processed/out" \
    "/mnt/localscratch/cds/rbrecheisen/models/v2/model.zip" \
    "/mnt/localscratch/cds/rbrecheisen/models/v2/contour_model.zip" \
    "/mnt/localscratch/cds/rbrecheisen/models/v2/params.json" \
    "PROBABILITIES" \
    --steps \
        "dicom2nifti" \
        "totalsegmentator" \
        "selectroi" \
        "selectslice" \
        "l3seg"
