import numpy as np


def triangular_basis(domain_size, num_centers, radius):
        centers = np.linspace(0, domain_size - 1, num_centers)
        basis = np.zeros((num_centers, domain_size))
        for k, c in enumerate(centers):
            for i in range(domain_size):
                dist = abs(i - c)
                denom = radius if radius != 0 else 1e-10
                basis[k, i] = max(1 - dist / denom, 0)
    
        return basis