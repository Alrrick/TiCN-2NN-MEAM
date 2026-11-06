"""Optional historical histogram helpers; inputs are absent from the archive.

These helpers are retained for compatibility, not validated for new research.
Use ticn_analysis.layers for the supplied coordinate exports.
"""

import statistics as stats
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


def read_two_columns(filename: str | Path) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Read a two-column export after its two header lines."""
    xs = []
    ys = []

    with open(filename, "r") as dat:
        line = dat.readline().strip()
        line = dat.readline().strip()
        line = dat.readline().strip()
        while line:
            d = line.split()
            xs.append(float(d[0]))
            ys.append(float(d[1]))

            line = dat.readline().strip()
    return np.asarray(xs, dtype=np.float64), np.asarray(ys, dtype=np.float64)


def gauss(x: NDArray[np.float64], a: float, mu: float, s: float) -> NDArray[np.float64]:
    return a * np.exp(-((x - mu) ** 2) / (2 * s**2))


def layer_analysis_basic(filename: str, lim: float = 0) -> list[float]:
    xs, ys = read_two_columns(filename)

    st = 200
    ed = -150

    plt.figure()
    plt.rcParams.update({"font.size": 12})
    ax = plt.subplot(111)
    plt.plot(xs[st:ed], ys[st:ed], label="")

    mus: list[float] = []
    print(filename)
    peaks, _ = find_peaks(ys[st:ed], prominence=60, distance=4)
    for p in peaks:
        pup = p + 2
        pdw = p - 2
        a = max(ys[st:ed][pdw:pup])
        mu = stats.mean(ys[st:ed][pdw:pup])
        s = stats.stdev(ys[st:ed][pdw:pup])

        popt, pcov = curve_fit(
            gauss, xs[st:ed][pdw:pup], ys[st:ed][pdw:pup], p0=[a, mu, s], maxfev=10000
        )

        a = popt[0]
        mu = popt[1]
        s = popt[2]
        residuals = ys[st:ed][pdw:pup] - gauss(xs[st:ed][pdw:pup], *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((ys[st:ed][pdw:pup] - np.mean(ys[st:ed][pdw:pup])) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        print(p, a, mu, s, r_squared)
        mus.append(float(mu))

        plt.plot(xs[st:ed][pdw:pup], ys[st:ed][pdw:pup], "-")

    plt.xlabel("a (Å)", fontsize=13, fontweight="bold")
    plt.ylabel("Counts a.u.", fontsize=13, fontweight="bold")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.minorticks_on()
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    plt.savefig(filename.split(".")[0] + ".png", bbox_inches="tight")
    plt.show()

    return mus


def surface_analysis(folder: str) -> None:
    mu_1 = layer_analysis_basic(folder + "/" + "coor_1.txt")
    layer_analysis_basic(folder + "/" + "coor_2.txt")
    mu_bulk = layer_analysis_basic(folder + "/" + "coor_bulk.txt")

    a0 = mu_bulk[0]
    d1Ti2X = 100 * (mu_1[2] - a0) / a0
    d1X2Ti = 100 * (mu_1[0] - a0) / a0

    print(a0, d1Ti2X, d1X2Ti)


def analyze_rippling(folder: str) -> None:
    """Historical optional exports; retain signed widths, fix species reporting."""
    from .analysis import layer_statistics
    from .io import read_coordinates

    results = [
        layer_statistics(read_coordinates(Path(folder) / f"r{i}data.txt")) for i in range(1, 5)
    ]
    means = []
    with open(folder + "result.txt", "w", encoding="utf-8") as output:
        for i, result in enumerate(results, 1):
            ti, an = result.titanium_mean_angstrom, result.anion_mean_angstrom
            sd_ti, sd_an = result.titanium_sd_angstrom, result.anion_sd_angstrom
            if ti == 0 or an == 0:
                raise ValueError("legacy width error is undefined at a zero species mean")
            width = ti - an
            error = width * sd_ti / ti + width * sd_an / an
            text = (
                f"----------\nlayer_r{i}:\n"
                f"z_ti: {ti} {sd_ti}\nz_xs: {an} {sd_an}\n"
                f"width: {width} {error}\n"
            )
            output.write(text)
            print(text)
            means.append((ti + an) / 2)
    for i, (upper, lower) in enumerate(zip(means, means[1:], strict=False), 1):
        print(f"z{i}-z{i + 1}:", upper - lower)


def analyze_rippling_coordinates(folder: str) -> None:
    mu_1 = layer_analysis_basic(folder + "/" + "r1coord.txt")
    mu_2 = layer_analysis_basic(folder + "/" + "r2coord.txt")
    mu_3 = layer_analysis_basic(folder + "/" + "r3coord.txt")
    mu_4 = layer_analysis_basic(folder + "/" + "r4coord.txt")
    mu_b = layer_analysis_basic(folder + "/" + "rbcoord.txt")

    print(mu_1)
    print(mu_2)
    print(mu_3)
    print(mu_4)
    print(mu_b)
