"""Shared MNI152 2mm grid constants.

Split out from visualization.py so atlas_regions.py can depend on the same
grid without creating a circular import (visualization.py -> atlas_regions.py
-> visualization.py).
"""
import numpy as np

MNI_SHAPE = (91, 109, 91)
MNI_AFFINE = np.array([
    [2., 0., 0., -90.],
    [0., 2., 0., -126.],
    [0., 0., 2., -72.],
    [0., 0., 0., 1.],
])

# World-space (mm) extent of the MNI152 2mm template grid above - used to
# bound the "exact MNI coordinates" advanced input mode so a typo can't stamp
# a point clean outside the volume.
MNI_X_RANGE = (-90.0, 90.0)
MNI_Y_RANGE = (-126.0, 90.0)
MNI_Z_RANGE = (-72.0, 108.0)
