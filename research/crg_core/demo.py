import numpy as np

from core import certify


cases = {
    "repair": (np.eye(2), np.array([0.2, 0.1]), 0.02, 0.5, 0.05),
    "uncertain": (np.eye(2), np.array([0.45, 0.0]), 0.20, 0.5, 0.05),
    "impossible": (np.eye(2), np.array([2.0, 0.0]), 0.10, 0.5, 0.10),
}

for name, (G, d, eps, radius, tol) in cases.items():
    cert = certify(
        G,
        d,
        epsilon_G=eps,
        certified_radius=radius,
        tolerance=tol,
    )
    print(
        name,
        cert.decision.value,
        f"nominal={cert.nominal_residual:.4f}",
        f"worst={cert.worst_case_residual_upper:.4f}",
        f"best={cert.best_case_residual_lower:.4f}",
    )
