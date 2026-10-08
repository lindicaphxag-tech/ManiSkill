from pathlib import Path
import subprocess
import sys

from research.eprc.lerobot_plugin_compat import (
    EXPECTED_DISTRIBUTION,
    LEROBOT_PLUGIN_HEAD,
    LEROBOT_PLUGIN_PR,
    validate_built_wheel,
    validate_source_layout,
)


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "research" / "eprc" / "lerobot_plugin"


def test_plugin_source_layout_matches_lerobot_4592_discovery_contract():
    assert LEROBOT_PLUGIN_PR == 4592
    assert LEROBOT_PLUGIN_HEAD == "a37961cb098cf3d0cb9fc18603e7922b09b4e311"
    validate_source_layout(PLUGIN)


def test_built_wheel_preserves_exact_distribution_import_identity(tmp_path):
    out = tmp_path / "dist"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            str(PLUGIN),
            "-w",
            str(out),
        ],
        check=True,
    )
    wheels = list(out.glob("*.whl"))
    assert len(wheels) == 1
    assert EXPECTED_DISTRIBUTION in wheels[0].name
    validate_built_wheel(wheels[0])