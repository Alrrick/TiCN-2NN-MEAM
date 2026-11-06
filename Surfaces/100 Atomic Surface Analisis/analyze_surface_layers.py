"""Analyze archived TiC and TiN (100) surface-layer coordinate exports.

Run from this directory. Results append to TiCresult.txt and TiNresult.txt.
The optional histogram helpers require exports not included in this archive.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import statistics as stats
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

def read_two_columns(filename):
    """Read a two-column export after its two header lines."""
    xs = []
    ys = []
    
    with open(filename, "r") as dat:
        
        l = dat.readline().strip()
        l = dat.readline().strip()
        l = dat.readline().strip()
        while l:
            d = l.split(" ")
            xs.append(float(d[0]))
            ys.append(float(d[1]))
            
            l = dat.readline().strip()
    xs =  np.asarray(xs)
    ys =  np.asarray(ys)
    return xs, ys
    

def gauss(x, a, mu, s):
    
    return a* np.exp(-(x-mu)**2 / (2* s**2))
    
    
def layer_analysis_basic(filename, lim = 0):
    
    xs, ys = read_two_columns(filename)

    #plt.plot(cs, p1s, 'o', color="darkviolet", label= 'Peaks at 609 nm', lw=1, ms=3)
    #plt.plot(cs, p2s, 's', color="limegreen", label= 'Peaks at 665 nm', lw=1, ms=3)
    st = 200
    ed = -150
    
    plt.figure()
    plt.rcParams.update({'font.size': 12})
    ax = plt.subplot(111)
    plt.plot(xs[st:ed], ys[st:ed], label= '')
    
    mus =[]
    print(filename)
    peaks, _ = find_peaks(ys[st:ed], prominence=60, distance=4)
    for p in peaks:
        pup = p + 2
        pdw = p - 2
        a  = max(ys[st:ed][pdw:pup])
        mu = stats.mean(ys[st:ed][pdw:pup])
        s  = stats.stdev(ys[st:ed][pdw:pup])
        
        popt, pcov  = curve_fit(gauss, xs[st:ed][pdw:pup], ys[st:ed][pdw:pup], p0=[a, mu, s], maxfev=10000)
        
        a  = popt[0]
        mu = popt[1]
        s  = popt[2]
        residuals = ys[st:ed][pdw:pup] - gauss(xs[st:ed][pdw:pup], *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((ys[st:ed][pdw:pup] - np.mean(ys[st:ed][pdw:pup]))**2)
        r_squared = 1-(ss_res/ss_tot)
        
        print(p, a, mu, s, r_squared)
        mus.append(mu)
        fit = gauss(xs[st:ed][pdw:pup], *popt)
        
        plt.plot(xs[st:ed][pdw:pup], ys[st:ed][pdw:pup], '-')
    
    #a0 = mus[1]
    
    #d1Ti2X = mus[3]
    #d1X2Ti = mus[0]
    #d = mus[2]
    
    #plt.plot(xs, ases, yerr=er_as, fmt="o", label= 'Simulated', lw=1, ms=3)
    #plt.plot(xs, ref, '-', label= 'Reference', lw=1, ms=3)
    
    plt.xlabel('a (Å)', fontsize=13, fontweight='bold')
    plt.ylabel('Counts a.u.', fontsize=13, fontweight='bold')
    #plt.legend(bbox_to_anchor=(1.03, 0.8), loc='upper left')
    #plt.legend(loc='upper left')
    #plt.title("Lattice parameter", fontsize=13, fontweight='bold')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    
    plt.minorticks_on()
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    plt.savefig(filename.split(".")[0] + ".png", bbox_inches="tight")
    plt.show()
    
    return mus


def surface_analysis(folder):
    mu_1 = layer_analysis_basic(folder + "/" + "coor_1.txt")
    mu_2 = layer_analysis_basic(folder + "/" + "coor_2.txt")
    mu_bulk = layer_analysis_basic(folder + "/" + "coor_bulk.txt")
    
    a0 = mu_bulk[0]
    d1Ti2X = 100* (mu_1[2] - a0)/a0
    d1X2Ti = 100* (mu_1[0] - a0)/a0
    
    print(a0, d1Ti2X, d1X2Ti)
 

def analyze_rippling(folder):
    ts, ys = read_two_columns(folder + "/" + "r1data.txt")
    
    titanium_positions = []
    anion_positions  = []
    output_file = open(folder + "result.txt", "w")

    for i in range(len(ts)):
        if ts[i] == 1.0:
            titanium_positions.append(ys[i])
        else:
            anion_positions.append(ys[i])
    
    width = stats.mean(titanium_positions) - stats.mean(anion_positions)
    width_error = width *stats.stdev(titanium_positions)/stats.mean(titanium_positions) + width*stats.stdev(anion_positions)/stats.mean(anion_positions)
    s = "-"*10 + "\nlayer_r1:\n"
    s+= "z_ti: " + str(stats.mean(titanium_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "z_xs: " + str(stats.mean(anion_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "width: " + str(width) + " " + str(width_error) + "\n"
    output_file.write(s)

    print(s)

    z1 =  (stats.mean(titanium_positions) + stats.mean(anion_positions))/2
    
    ts, ys = read_two_columns(folder + "/" + "r2data.txt")
    
    titanium_positions = []
    anion_positions  = []

    for i in range(len(ts)):
        if ts[i] == 1.0:
            titanium_positions.append(ys[i])
        else:
            anion_positions.append(ys[i])
    
    width = stats.mean(titanium_positions) - stats.mean(anion_positions)
    width_error = width *stats.stdev(titanium_positions)/stats.mean(titanium_positions) + width*stats.stdev(anion_positions)/stats.mean(anion_positions)
    s = "-"*10 + "\nlayer_r2:\n"
    s+= "z_ti: " + str(stats.mean(titanium_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "z_xs: " + str(stats.mean(anion_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "width: " + str(width) + " " + str(width_error) + "\n"
    output_file.write(s)

    print(s)

    z2 =  (stats.mean(titanium_positions) + stats.mean(anion_positions))/2

    ts, ys = read_two_columns(folder + "/" + "r3data.txt")
    
    titanium_positions = []
    anion_positions  = []

    for i in range(len(ts)):
        if ts[i] == 1.0:
            titanium_positions.append(ys[i])
        else:
            anion_positions.append(ys[i])
    
    width = stats.mean(titanium_positions) - stats.mean(anion_positions)
    width_error = width *stats.stdev(titanium_positions)/stats.mean(titanium_positions) + width*stats.stdev(anion_positions)/stats.mean(anion_positions)
    s = "-"*10 + "\nlayer_r3:\n"
    s+= "z_ti: " + str(stats.mean(titanium_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "z_xs: " + str(stats.mean(anion_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "width: " + str(width) + " " + str(width_error) + "\n"
    output_file.write(s)

    print(s)
    z3 =  (stats.mean(titanium_positions) + stats.mean(anion_positions))/2

    

    ts, ys = read_two_columns(folder + "/" + "r4data.txt")
    
    titanium_positions = []
    anion_positions  = []

    for i in range(len(ts)):
        if ts[i] == 1.0:
            titanium_positions.append(ys[i])
        else:
            anion_positions.append(ys[i])
    
    width = stats.mean(titanium_positions) - stats.mean(anion_positions)
    width_error = width *stats.stdev(titanium_positions)/stats.mean(titanium_positions) + width*stats.stdev(anion_positions)/stats.mean(anion_positions)
    s = "-"*10 + "\nlayer_r4:\n"
    s+= "z_ti: " + str(stats.mean(titanium_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "z_xs: " + str(stats.mean(anion_positions)) + " " + str(stats.stdev(titanium_positions)) + "\n"
    s+= "width: " + str(width) + " " + str(width_error) + "\n"
    output_file.write(s)

    print(s)
    z4 =  (stats.mean(titanium_positions) + stats.mean(anion_positions))/2
    
    print("z1-z2:", z1- z2)
    print("z2-z3:", z2- z3)
    print("z3-z4:", z3- z4)
    output_file.close()


def analyze_rippling_coordinates(folder):
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


def read_layer_info(folder, name, start, end, delta):
    """Pool type/z exports over range(start, end, delta); type 1 is Ti.

    Other types are pooled as anions. The legacy width-error expression is
    retained; it is not a standard error or confidence interval.
    """
    k = start
    titanium_positions = []
    anion_positions  = []
    while k < end:
        ts, ys = read_two_columns(folder + "/" + name + "/" + name + "_" + str(k) + ".dat")

        for i in range(len(ts)):
            if ts[i] == 1.0:
                titanium_positions.append(ys[i])
            else:
                anion_positions.append(ys[i])   
        
        k += delta  
  
    output_file = open(folder + "result.txt", "a")
   
    z_ti = stats.mean(titanium_positions)
    er_z_ti = stats.stdev(titanium_positions)
    z_xs = stats.mean(anion_positions)
    er_z_xs = stats.stdev(anion_positions)
   
    width = abs(z_ti - z_xs)
    width_error = abs(width *er_z_ti/z_ti + width*er_z_xs/z_xs)
    
    s = "-"*10 + "\nlayer: " + name + "\n"
    s+= "z_ti: " + str(z_ti) + " " + str(er_z_ti) + "\n"
    s+= "z_xs: " + str(z_xs) + " " + str(er_z_xs) + "\n"
    s+= "width: " + str(width) + " " + str(width_error) + "\n"
    output_file.write(s)

    print(s)
    output_file.close()
    
    return (z_ti, er_z_ti, z_xs, er_z_xs)


def analyze_all_layers(folder, start, end, delta):
    #arch = open(folder + "result.txt", "w")
    #arch.close()

    l1 = read_layer_info(folder, "z1", start, end, delta)
    l2 = read_layer_info(folder, "z2", start, end, delta)
    l3 = read_layer_info(folder, "z3", start, end, delta)
    l4 = read_layer_info(folder, "z4", start, end, delta)
    
    z1 = (l1[0] + l1[2])/2
    z2 = (l2[0] + l2[2])/2
    z3 = (l3[0] + l3[2])/2
    z4 = (l4[0] + l4[2])/2
    
    print("z1-z2:", z1- z2)
    print("z2-z3:", z2- z3)
    print("z3-z4:", z3- z4)

if __name__ == "__main__":
    analyze_all_layers("TiC", 400, 451, 1)
    analyze_all_layers("TiN", 400, 451, 1)
#analyze_all_layers("TiC0,0N")
#r_analys("TiC1,0N")
#r_analys("TiC0,0N")
#r_coord("TiC1,0N")
#surface_analysis("TiC1,0N")





