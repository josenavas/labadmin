# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The LabAdmin Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import TestCase, main

import numpy as np
import numpy.testing as npt

from knimin.lib.pm_shotgun import compute_shotgun_normalization_values


class TestShotgun(TestCase):
    def test_compute_shotgun_normalization_values(self):
        input_vol = 3.5
        input_dna = 10
        plate_layout = []
        for i in range(4):
            row = []
            for j in range(4):
                row.append({'dna_concentration': 10,
                            'sample_id': "S%s.%s" % (i, j)})
            plate_layout.append(row)

        obs_sample, obs_water = compute_shotgun_normalization_values(
            plate_layout, input_vol, input_dna)

        exp_sample = np.zeros((4, 4), dtype=np.float)
        exp_water = np.zeros((4, 4), dtype=np.float)
        exp_sample.fill(1000)
        exp_water.fill(2500)

        npt.assert_almost_equal(obs_sample, exp_sample)
        npt.assert_almost_equal(obs_water, exp_water)

        # Make sure that we don't go abaove the limit
        plate_layout[1][1]['dna_concentration'] = 0.25
        obs_sample, obs_water = compute_shotgun_normalization_values(
            plate_layout, input_vol, input_dna)

        exp_sample[1][1] = 3500
        exp_water[1][1] = 0

        npt.assert_almost_equal(obs_sample, exp_sample)
        npt.assert_almost_equal(obs_water, exp_water)


if __name__ == '__main__':
    main()
