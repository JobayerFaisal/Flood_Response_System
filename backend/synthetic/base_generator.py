import random
import numpy as np


class BaseGenerator:
    def __init__(self, seed: int):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def random_float(self, low, high):
        return np.random.uniform(low, high)

    def random_int(self, low, high):
        return np.random.randint(low, high)