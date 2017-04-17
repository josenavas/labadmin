# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The LabAdmin Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

import numpy as np


def compute_shotgun_normalization_values(plate_layout, input_vol, input_dna):
    """Computes the normalization variables and stores them in the DB

    Parameters
    ----------
    plate_layout : list of list of dicts
        The shotgun plate layout in which each well contains this information
        {'sample_id': None, 'dna_concentration': None} in which the
        dna_concentration is represented in nanograms per microliter
    input_vol : float
        The maximum input volume in microliters
    input_dna : float
        The desired DNA for library prep in nanograms

    Returns
    -------
    2d numpy array, 2d numpy array, 2d numpy array
        The water volume and the sample volume per well, represented in
        nanoliters as well as the original dna concentrartion in ng/nL
    """
    input_dna = float(input_dna)
    input_vol = float(input_vol)
    rows = len(plate_layout)
    cols = len(plate_layout[0])
    dna_conc = np.zeros((rows, cols), dtype=np.float)
    for i in range(rows):
        for j in range(cols):
            dna_conc[i][j] = plate_layout[i][j]['dna_concentration']

    # Compute how much sample do we need
    # ng / (ng/uL) -> uL
    vol_sample = input_dna / dna_conc

    # If a sample didn't have enough concentration simple put the totally of
    # the volume from the sample
    vol_sample[vol_sample > input_vol] = input_vol

    # Compute how much water do we need
    vol_water = input_vol - vol_sample

    # Transform both volumes to nanoliters
    vol_sample = vol_sample * 1000
    vol_water = vol_water * 1000

    return vol_sample, vol_water
