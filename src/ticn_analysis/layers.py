"""Layer-file selection and historical text reporting."""

from pathlib import Path

from .analysis import layer_statistics
from .io import read_coordinates
from .models import LayerResult


def layer_paths(directory: Path, name: str, start: int, stop: int, stride: int) -> list[Path]:
    if start < 0 or stop <= start or stride <= 0:
        raise ValueError("file range requires 0 <= start < stop and positive stride")
    return [directory / name / f"{name}_{index}.dat" for index in range(start, stop, stride)]


def analyze_layer(paths: list[Path], *, legacy: bool = False) -> LayerResult:
    coordinates = [row for path in paths for row in read_coordinates(path)]
    return layer_statistics(coordinates, legacy=legacy)


def legacy_layer_text(name: str, result: LayerResult) -> str:
    return (
        f"----------\nlayer: {name}\n"
        f"z_ti: {result.titanium_mean_angstrom} {result.titanium_sd_angstrom}\n"
        f"z_xs: {result.anion_mean_angstrom} {result.anion_sd_angstrom}\n"
        f"width: {result.width_angstrom} {result.legacy_width_error_angstrom}\n"
    )


def read_layer_info(
    folder: str, name: str, start: int, end: int, delta: int
) -> tuple[float, float, float, float]:
    """Compatibility API: append the historical report, returning species stats."""
    result = analyze_layer(layer_paths(Path(folder), name, start, end, delta), legacy=True)
    text = legacy_layer_text(name, result)
    with Path(folder + "result.txt").open("a", encoding="utf-8") as stream:
        stream.write(text)
    print(text)
    return (
        result.titanium_mean_angstrom,
        result.titanium_sd_angstrom,
        result.anion_mean_angstrom,
        result.anion_sd_angstrom,
    )


def analyze_all_layers(folder: str, start: int, end: int, delta: int) -> None:
    """Compatibility API; retains the original append behavior."""
    means = []
    for name in ("z1", "z2", "z3", "z4"):
        ti, _, anion, _ = read_layer_info(folder, name, start, end, delta)
        means.append((ti + anion) / 2)
    for index, (upper, lower) in enumerate(zip(means, means[1:], strict=False), 1):
        print(f"z{index}-z{index + 1}:", upper - lower)
