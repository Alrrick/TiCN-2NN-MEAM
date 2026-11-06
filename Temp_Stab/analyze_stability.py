"""Analyze archived composition logs from the current working directory.

See docs/reproduction.md for retained sampling and slab-volume limitations.
"""

import numpy as np
import matplotlib.pyplot as plt
import statistics as stats
from pathlib import Path
from scipy.optimize import curve_fit

def data_reader(archive_name, curve_number = 3):
    """Read the first curve_number - 1 thermo blocks (legacy selection).

    The first block is minimization. This selection is retained for comparison
    with the archived analysis; it does not select the final production run.
    """
    data_start_text = "Step         PotEng         KinEng          Temp          Volume         Press"
    divisor = "  "
    endin = "Loop"
    ## Per-property data lists
    steps = []
    pots  = []
    temps = []
    vols  = []
    press = []
    ##
    current_number = 1   
    data_matrix = []
    
    current_data = []
    #print("Reading:", archive_name, "Started!\n", "-"*10)
    with open(archive_name, "r") as dat: 
          
        while current_number <  curve_number:
            # Find the start of the next thermo block.
            l = dat.readline().strip()
            while data_start_text not in l :
                if not l and dat.tell() == Path(archive_name).stat().st_size:
                    raise ValueError(f"{archive_name}: missing thermo block {current_number}")
                l = dat.readline().strip()

            l = dat.readline().strip()
     
            # Store the thermo data.
            
            while endin not in l:
                if not l:
                    raise ValueError(f"{archive_name}: incomplete thermo block {current_number}; expected Loop terminator")
                li = l.replace(",", ".").split(divisor)
                aux = []
                for i in range(len(li)):
                    if li[i].strip() != "":
                        aux.append(float(li[i].strip()))

                current_data.append(aux.copy())
                steps.append(aux[0])
                pots.append(aux[1])
                temps.append(aux[3])
                vols.append( aux[4])
                press.append(aux[5])

                l = dat.readline().strip()
        # Append the completed block to the data matrix.
            data_matrix += current_data.copy()
            current_data = []
            current_number += 1

    #print("Done!\n", "-"*10)
    return data_matrix, steps, temps, vols, press, pots
 
def analyze_folder(folder_name, archive_name):
    # Analyze the folder for one composition.
    n = 1
    nf = 1

    composition_values = []
    volume_series  = []
    pressure_series  = []
    temperature_series = []
    potential_energy_series  = []
    while n <= nf:
        #print(archive_name +  f"{n}.log" + " reading")
        matrix,steps,temps,vols,press,pots = data_reader(folder_name + "/" + archive_name + f"{n}.log")
        #print(archive_name +  f"{n}.log" +  " read\n")
        composition_values = steps
        volume_series.append(vols) 
        pressure_series.append(press) 
        temperature_series.append(temps)
        potential_energy_series.append(pots)
        n += 1
   

    #plt.figure()
    #plt.rcParams.update({'font.size': 12})
    #ax = plt.subplot(111)

    #plt.plot(cs, p1s, 'o', color="darkviolet", label= 'Peaks at 609 nm', lw=1, ms=3)
    #plt.plot(cs, p2s, 's', color="limegreen", label= 'Peaks at 665 nm', lw=1, ms=3)
    st = 150
    ed = -1
    #plt.plot(xses[st:ed], volses[0][st:ed], '-', label= '1', lw=1, ms=3)
    #plt.plot(xses[st:ed], volses[1][st:ed], '-', label= '2', lw=1, ms=3)
    #plt.plot(xses[st:ed], volses[2][st:ed], '-', label= '3', lw=1, ms=3)
    #plt.plot(xses[st:ed], volses[3][st:ed], '-', label= '4', lw=1, ms=3)
    
    auxs = [(np.asarray(volume_series[0][st:ed]) /(8*8*8))**(1/3)]#, 
           #(stats.mean(volses[1][st:ed])/(8*8*8))**(1/3),
           #(stats.mean(volses[2][st:ed])/(8*8*8))**(1/3),
           #(stats.mean(volses[3][st:ed])/(8*8*8))**(1/3)]

    aux = [stats.mean(auxs[0])]#, 
           #(stats.mean(volses[1][st:ed])/(8*8*8))**(1/3),
           #(stats.mean(volses[2][st:ed])/(8*8*8))**(1/3),
           #(stats.mean(volses[3][st:ed])/(8*8*8))**(1/3)]
    
    aux_er = [stats.stdev(auxs[0])]#, 
           #(stats.stdev(volses[1][st:ed])/(8*8*8))**(1/3),
           #(stats.stdev(volses[2][st:ed])/(8*8*8))**(1/3),
           #(stats.stdev(volses[3][st:ed])/(8*8*8))**(1/3)]
    
    av_a = stats.mean(aux)
    err_a = stats.mean(aux_er)
    pre = stats.mean(pressure_series[0][st:ed])
    
    
    aux_pot = [(stats.mean(potential_energy_series[0][st:ed]))]
    aux_pot_err = [stats.stdev(potential_energy_series[0][st:ed])]
    
    pot =  stats.mean(aux_pot)
    err_pot = stats.mean(aux_pot_err)
    
    print(folder_name, "\n  a :", av_a, err_a, "\n pot:", pot, err_pot)
    #plt.xlabel('Steps', fontsize=13, fontweight='bold')
    #plt.ylabel('Volume', fontsize=13, fontweight='bold')
    #plt.legend(bbox_to_anchor=(1.03, 0.8), loc='upper left')
    #plt.legend(loc='upper left')
    #plt.title("", fontsize=13, fontweight='bold')

    #ax.spines['right'].set_visible(False)
    #ax.spines['top'].set_visible(False)
    #ax.yaxis.set_ticks_position('left')
    #ax.xaxis.set_ticks_position('bottom')

    #plt.savefig("calibration.png", bbox_inches="tight")
    #plt.show()

    return av_a, err_a, pot, err_pot

def reference_lattice_parameter(x):
    return 0.0857 * x + 4.2417

def linear(x, m, n):
    return m * x + n

def analyze_stability():
    
    log_prefix = "temp_v"
    composition_labels = ["A", "B", "C", "D", "E"]
    composition_values = ["1.0", "0.75", "0.5", "0.25", "0.0"]
 
    xs = []
    lattice_parameters     = []
    er_as    = []
    pots     = [] 
    err_pots = []
    
    ref = []  
  
    for i in range(5):
        a, er_a, pot, err_pot = analyze_folder(f"{composition_labels[i]}-Ti(C{composition_values[i]},N{composition_values[::-1][i]})", log_prefix)
        xs.append(float(composition_values[i]))
        lattice_parameters.append(a)
        er_as.append(er_a)
        pots.append(pot)
        err_pots.append(err_pot)
        ref.append(reference_lattice_parameter(float(composition_values[i])))
    
    with open("results.txt", "w") as dat:
        dat.write("x a err_a en_pot err_en_pot\n")
        
        for i in range(len(xs)):
            s = str(xs[i]) + " " + str(lattice_parameters[i]) + " " + str(er_as[i])
            s += " " + str(pots[i]) + " " + str(err_pots[i])
            dat.write(s.replace(".", ",") + "\n")
    
    xs =  np.asarray(xs)
    lattice_parameters = np.asarray(lattice_parameters)
      
    param1, covariance1 = curve_fit(linear, xs, lattice_parameters)

    #print(param1[0], 100* (param1[0] - 0.0857)/0.0857)
   
    plt.figure()
    plt.rcParams.update({'font.size': 12})
    ax = plt.subplot(111)

    #plt.plot(cs, p1s, 'o', color="darkviolet", label= 'Peaks at 609 nm', lw=1, ms=3)
    #plt.plot(cs, p2s, 's', color="limegreen", label= 'Peaks at 665 nm', lw=1, ms=3)
    st = 500
    ed = -1
    plt.errorbar(xs, lattice_parameters, yerr=er_as, fmt="o", label= 'Simulated', lw=1, ms=3)
    plt.plot(xs, ref, '-', label= 'Reference', lw=1, ms=3)
    
    plt.xlabel('x', fontsize=13, fontweight='bold')
    plt.ylabel('a (Å)', fontsize=13, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.03, 0.8), loc='upper left')
    plt.legend(loc='upper left')
    plt.title("Lattice parameter", fontsize=13, fontweight='bold')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.savefig("lattice_parameter.png", bbox_inches="tight")
    plt.show()
if __name__ == "__main__":
    analyze_stability()

