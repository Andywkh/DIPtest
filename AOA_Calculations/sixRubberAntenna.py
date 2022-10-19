from doctest import OutputChecker
import cv2

import csv
import pandas as pd
import numpy as np
import math
import seaborn as sb
import matplotlib.pyplot as plt

import os
import time
import datetime

import sys
sys.path.append("../")

from utils.basic import * # note this file
from utils.fusion_SAR import * # note this file
from scipy.stats import multivariate_normal

from Dataloaders.dataloader_v3 import *
from Dataloaders.apriltag_loader_v2 import *

# E280 1160 6000 0209 F811 48C3
# MAC0 = str(input("Please Input MAC Address 1"))
MAC0 = "E280 1160 6000 0209 F811 48C3"

#RFID_data = RFID_dataloader_v2('../Datasets/rfid/testing4.csv',MAC0)
#cv_data = cv_dataloader('../Datasets/gtcsv/testing4.csv')### fill in later

RFID_data = RFID_dataloader_v2('./Datasets/rfid/testing4.csv',MAC0)
cv_data = cv_dataloader('./Datasets/gtcsv/testing4.csv')### fill in later

timeList = []
startingTime = 0
for x in np.arange(RFID_data.ptime[0][0][0], RFID_data.ptime[0][0][-1], 1/30):
    #y = startingTime + x 
    timeList.append(x)

AOAList_0 = []
timeList1 = []
data = RFID_data.get_data(1664952487.0483)
print(data)

from datetime import datetime

# Function for Time and phase difference calculation
def time_function(time_value, RFID_data):
    
    data = RFID_data.get_data(time_value)
    phase0_rad = data[0][0] + (1.24123098)
    phase1_rad = data[0][1] + (-1.22918835)
    phase2_rad = data[0][2] + (-0.78126601)
    phase3_rad = data[0][3] + (-0.01121657)
    phase4_rad = data[0][4] + (-0.43390704)
    phase5_rad = data[0][5] + (0.07594752)

    phaseDiff0 = -1 * (phase0_rad - phase1_rad)
    phaseDiff1 = -1 * (phase1_rad - phase2_rad)
    phaseDiff2 = -1 * (phase2_rad - phase3_rad)
    phaseDiff3 = -1 * (phase3_rad - phase4_rad) 
    phaseDiff4 = -1 * (phase4_rad - phase5_rad)
    phaseList = [phaseDiff0, phaseDiff1, phaseDiff2, phaseDiff3, phaseDiff4]

    return phaseList

# Function for AoA Calculation
def Aoa_calculation_function(phaseList):
    
    constant = (3*pow(10,8))/(4*3.141592654*919.75*pow(10,6)*0.1)
    AOA_0 = constant * phaseList[0]         
    AOA_1 = constant * phaseList[1]   
    AOA_2 = constant * phaseList[2]   
    AOA_3 = constant * phaseList[3]    
    AOA_4 = constant * phaseList[4]     
    # print('markkkk,',AOA_0, AOA_1, AOA_2, AOA_3, AOA_4)

    for k in range(-2,3):
        AOA_0_temp = AOA_0 + k * 2 * np.pi * constant
        print('test_in_loop',AOA_0_temp)
        if abs(AOA_0_temp) <= 0.9:
            AOA_0_result = np.arcsin(AOA_0_temp)
            print('k', k)
            # print('AOA_0_temp', AOA_0_temp)
    AOA_0 = AOA_0_result

    for k in range(-2,3):
        AOA_1_temp = AOA_1 + k * 2 * np.pi * constant
        if abs(AOA_1_temp) <= 0.9:
            AOA_1_result = np.arcsin(AOA_1_temp)
    AOA_1 = AOA_1_result

    for k in range(-2,3):
        AOA_2_temp = AOA_2 + k * 2 * np.pi * constant
        if abs(AOA_2_temp) <= 0.9:
            AOA_2_result = np.arcsin(AOA_2_temp)
    AOA_2 = AOA_2_result

    for k in range(-2,3):
        AOA_3_temp = AOA_3 + k * 2 * np.pi * constant
        if abs(AOA_3_temp) <= 0.9:
            AOA_3_result = np.arcsin(AOA_3_temp)
    AOA_3 = AOA_3_result

    for k in range(-2,3):
        AOA_4_temp = AOA_4 + k * 2 * np.pi * constant
        if abs(AOA_4_temp) <= 0.9:
            AOA_4_result = np.arcsin(AOA_4_temp)
    AOA_4 = AOA_4_result

    # try:
    #     AOA_0 = np.arcsin(AOA_0)
    #     print('t1',AOA_0)
    # except Exception:
    #     print('dsajgdagdj')
    #     pass

    # try:
    #     AOA_1 = np.arcsin(AOA_1)
    # except Exception:
    #     pass

    # try:
    #     AOA_2 = np.arcsin(AOA_2)
    # except Exception:
    #     pass

    # try:
    #     AOA_3 = np.arcsin(AOA_3)
    # except Exception:
    #     pass

    # try:
    #     AOA_4 = np.arcsin(AOA_4)
    # except Exception:
    #     pass

    calculatedAOA = statistics.median([ AOA_0, AOA_1, AOA_2, AOA_3, AOA_4])
    # calculatedAOA = AOA_0
    print(AOA_0, AOA_1, AOA_2, AOA_3, AOA_4,calculatedAOA)
    return calculatedAOA

