from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

Matrix: TypeAlias = NDArray[np.floating]  # shape: (m, n)

Vector: TypeAlias = NDArray[np.floating]  # shape: (n,)
BoolVector: TypeAlias = NDArray[np.bool_]
IntVector = NDArray[np.int_]

