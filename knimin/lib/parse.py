# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The LabAdmin Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

import numpy as np


def parse_plate_reader_output(fp):
    """Parses the output of a plate reader

    Parameters
    ----------
    fp : str
        The path to the file

    Returns
    -------
    np.array of floats
        A 2D array of floats
    """
    with open(fp, 'U') as f:
        data = []
        for line in f:
            line = line.strip()
            if not line or line.startswith('Curve'):
                continue
            data.append(line.split())

    return np.asarray(data, dtype=np.float)
