import csv
import pandas as pd
import numpy as np
import math
import seaborn as sb
import matplotlib.pyplot as plt

# for dynamic graphing
from IPython import display

# from AOA_Calculations.sixRubberAntenna1ppl import *

# Function for drawing of graph for AoA
def graph_plotting_per_unit_timefunction(calculatedAOA, time_value):
   
    AOAList_0.append(calculatedAOA) #AOA_k_0

    #appending stringed time
    dt_object = datetime.fromtimestamp(time_value)
    
    timeList1.append(str(dt_object.hour) + ":" + str(dt_object.minute) + ":" + str(dt_object.second) + ":" + str(dt_object.microsecond/1000000)[2:4])
    
    plt.xticks(rotation=90)
    
    plt.scatter(timeList1, AOAList_0, c='b', marker='x', label='AOAList_0')
    
    plt.show(block = False)
    
    #plt.pause()
    #fig.canvas.draw()
    #fig.canvas.flush_events()
    
    #display.display(plt.show())
    #display.clear_output(wait=True)
    #display.clear_output()
    #time.sleep(1) # comment out if you can take high refresh
    plt.pause(0.0001)
    plt.clf()