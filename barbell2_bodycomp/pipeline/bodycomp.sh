#!/bin/bash

export PYTHONPATH=$HOME/barbell2_bodycomp:$PYTHONPATH
# export PYTHONPATH=$HOME/dev/barbell2_bodycomp:$PYTHONPATH

# python bodycomp.py \
#     --input_directories "/mnt/localscratch/cds/rbrecheisen/raw/tlodewick-ct-noise-1/AL_100%/101816478/2-Abdomen" \
#     --output_directory "/mnt/localscratch/cds/rbrecheisen/processed/florian" \
#     --mode "PROBABILITIES" \
#     --steps \
#         "dicom2nifti" \
#         "totalsegmentator" \
#         "selectroi" \
#         "selectslice" \
#         "l3seg"

python bodycomp.py \
    "/mnt/localscratch/cds/rbrecheisen/raw/HCCBC_Julia_Sonneveld_CT/HCC_004_before_raw" \
    "/mnt/localscratch/cds/rbrecheisen/processed/HCCBC_Julia_Sonneveld_CT" \
    --mode "ARGMAX" \
    --steps \
        "dicom2nifti" \
        "totalsegmentator" \
        "selectroi" \
        "selectslice" \
        "l3seg" \
        "calculate"
