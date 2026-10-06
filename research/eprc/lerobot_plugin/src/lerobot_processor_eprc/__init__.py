"""LeRobot EPRC processor plugin.

Importing this package registers EPRCContractGateStep with the LeRobot
ProcessorStepRegistry.
"""

from .step import EPRCContractGateStep

__all__ = ["EPRCContractGateStep"]
