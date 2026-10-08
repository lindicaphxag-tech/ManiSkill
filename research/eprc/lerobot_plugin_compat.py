from __future__ import annotations

from pathlib import Path
import re
import tomllib
import zipfile


LEROBOT_PLUGIN_PR = 4592
LEROBOT_PLUGIN_HEAD = "a37961cb098cf3d0cb9fc18603e7922b09b4e311"
LEROBOT_DISCOVERY_PREFIX = "lerobot_processor_"
EXPECTED_DISTRIBUTION = "lerobot_processor_eprc"
EXPECTED_IMPORT_PACKAGE = "lerobot_processor_eprc"
EXPECTED_REGISTRY_NAME = "eprc_contract_gate"


def read_project_name(pyproject: Path) -> str:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return str(data["project"]["name"])


def validate_source_layout(plugin_root: Path) -> None:
    pyproject = plugin_root / "pyproject.toml"
    distribution = read_project_name(pyproject)
    if distribution != EXPECTED_DISTRIBUTION:
        raise ValueError(
            f"distribution must exactly match {EXPECTED_DISTRIBUTION!r}; got {distribution!r}"
        )
    if not distribution.startswith(LEROBOT_DISCOVERY_PREFIX):
        raise ValueError("distribution does not satisfy LeRobot processor discovery prefix")

    package = plugin_root / "src" / EXPECTED_IMPORT_PACKAGE
    if not package.is_dir() or not (package / "__init__.py").is_file():
        raise ValueError("distribution name is not backed by an identically named import package")

    step_text = (package / "step.py").read_text(encoding="utf-8")
    pattern = rf'ProcessorStepRegistry\.register\(name="{re.escape(EXPECTED_REGISTRY_NAME)}"\)'
    if re.search(pattern, step_text) is None:
        raise ValueError("expected EPRC ProcessorStep registration is missing")


def validate_built_wheel(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
        package_prefix = EXPECTED_IMPORT_PACKAGE + "/"
        if not any(name.startswith(package_prefix) for name in names):
            raise ValueError("wheel does not contain the expected import package")

        metadata_names = [n for n in names if n.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain exactly one METADATA file")
        metadata = zf.read(metadata_names[0]).decode("utf-8")
        name_lines = [line for line in metadata.splitlines() if line.startswith("Name: ")]
        if name_lines != [f"Name: {EXPECTED_DISTRIBUTION}"]:
            raise ValueError(
                "wheel metadata distribution name does not preserve the underscore discovery contract"
            )