## for 6 Antenna

## load data for RFID csv file
## input: csv file, timestamp for interpolating
## return: resampled phase and RSSI data 
## currently only surport single RFID tag
## offline processing
## bug fixed!!

import os
import time
import datetime
import math
import csv
import numpy as np
from utils.basic import *
from utils.fusion_SAR import *
from scipy.stats import multivariate_normal

class RFID_dataloader_v2:
    def __init__(self, csv_filename, rfid_wanted):#rfid_list_wanted = ['E280 1160 6000 0209 F811 7224'] #  ['E280 1160 6000 0209 F811 7224']['E280 6894 0000 500E 73D4 548C']
        ###  RFID csv file   ###
        # [Timestamp    Antenna     RFID     Freq    RSSI    Phase] #
        ids = []
        det_data = []
        self.rfid_list = []
        with open( csv_filename, 'r') as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            for row in f_csv:
                if row[2] == rfid_wanted:
                    if row[2] not in self.rfid_list and row[2] != '':
                        self.rfid_list.append(row[2])
                    if row[1] != '':
                        if row[1] not in ids:
                            ids.append(row[1])
                            det_data.append([])
                        det_data[ids.index(row[1])].append(row)
            f.close()
        print(ids)
        print(self.rfid_list)
        
        ## basic operation ## 
        ####phase ==> [antenna idx][RFid]==>[phase0,phase1,phase2...]
        ####ptime ==> [antenna idx][RFid]==>[time0,time1,time2...]

        self.antenna_list = ids
        self.phase = [[[] for j in self.rfid_list] for i in self.antenna_list]
        self.ptime = [[[] for j in self.rfid_list] for i in self.antenna_list]
        self.rssi = [[[] for j in self.rfid_list] for i in self.antenna_list]
        for i, antenna in enumerate(self.antenna_list):
            for j, rfid in enumerate(self.rfid_list):
                self.phase[i][j] = np.array([eval(k[5]) for k in det_data[ids.index(antenna)] if k[2] == rfid])
                self.ptime[i][j] = np.array([str2timestamp(k[0],'%Y-%m-%d %H:%M:%S.%f') for k in det_data[ids.index(antenna)] if k[2] == rfid])
                self.rssi[i][j] = np.array([eval(k[4]) for k in det_data[ids.index(antenna)] if k[2] == rfid])
        #print(self.ptime)
        print('Finish RFID data loading')
        print('Start time: %.4f, stop time: %.4f' % (self.ptime[0][0][0],self.ptime[0][0][-1]))
        # print(self.phase)
        # print(self.rssi)
    def get_data(self, time_temp): ## get ONE data 
        T_polyfit = 0
        T_valid = 0.2
        order = 2 # linear spline interpolation
        self.phase_fit = []
        self.rssi_fit = []

        self.a_1_idx = self.antenna_list.index('25')
        self.a_2_idx = self.antenna_list.index('26')
        self.a_3_idx = self.antenna_list.index('27')
        self.a_4_idx = self.antenna_list.index('28')
        self.a_5_idx = self.antenna_list.index('29')
        self.a_6_idx = self.antenna_list.index('30')

        # phase polynomial regression
        for i, antenna in enumerate(self.antenna_list):
            idx_f_i, idx_l_i = BinarySearch(self.ptime[i][0], time_temp)
            if len(self.phase[i][0][idx_f_i:idx_l_i]) == 0:
                self.phase_fit.append(0)
            else:
                phase_temp = phase_wrap(holograph_poly_fit(self.ptime[i][0][idx_f_i:idx_l_i], self.phase[i][0][idx_f_i:idx_l_i], time_temp, 0, order = order, new_x = True))[0]
                self.phase_fit.append(phase_wrap(phase_temp))
        # rssi linear fitting
        for i, antenna in enumerate(self.antenna_list):    
            idx_f_i, idx_l_i = BinarySearch(self.ptime[i][0], time_temp)
            if len(self.rssi[i][0][idx_f_i:idx_l_i]) == 0:
                self.rssi_fit.append(-80)
            else:
                self.rssi_fit.append(Linear_fitting_2pnts(self.ptime[i][0][idx_f_i], self.ptime[i][0][idx_l_i], self.rssi[i][0][idx_f_i], self.rssi[i][0][idx_l_i], time_temp))
        
        self.phase_list = [self.phase_fit[self.a_1_idx], self.phase_fit[self.a_2_idx], self.phase_fit[self.a_3_idx], self.phase_fit[self.a_4_idx] , self.phase_fit[self.a_5_idx], self.phase_fit[self.a_6_idx]]
        self.rssi_list = [self.rssi_fit[self.a_1_idx], self.rssi_fit[self.a_2_idx], self.rssi_fit[self.a_3_idx], self.rssi_fit[self.a_4_idx] , self.rssi_fit[self.a_5_idx], self.rssi_fit[self.a_6_idx]]
        return self.phase_list, self.rssi_list
    
    def get_data_segment(self, time_array): 
        ## get data segment according to the time_list argument 
        T_polyfit = 0
        T_valid = 0.2
        order = 2 # linear spline interpolation

        self.phase_list = np.zeros((len(time_array), 4))
        self.rssi_list =  np.zeros((len(time_array), 4))
        self.a_1_idx = self.antenna_list.index('1')
        self.a_2_idx = self.antenna_list.index('2')
        self.a_3_idx = self.antenna_list.index('3')
        self.a_4_idx = self.antenna_list.index('4')
        self.antenna_list_reorder = [self.a_1_idx, self.a_2_idx, self.a_3_idx, self.a_4_idx]

        for idx, time_temp in enumerate(time_array):
            self.phase_fit = []
            self.rssi_fit = []
        # phase polynomial regression
            for i, antenna in enumerate(self.antenna_list):
                idx_f_i, _ = BinarySearch(self.ptime[i][0], time_temp - T_polyfit / 2)
                _, idx_l_i = BinarySearch(self.ptime[i][0], time_temp + T_polyfit / 2)
                if len(self.ptime[i][0][idx_f_i:idx_l_i]) == 0:
                    self.phase_fit.append(0)
                else:
                    phase_temp = phase_wrap(holograph_poly_fit(self.ptime[i][0][idx_f_i:idx_l_i], self.phase[i][0][idx_f_i:idx_l_i], time_temp, 0, order = order, new_x = True))[0]
                    self.phase_fit.append(phase_wrap(phase_temp))
            # rssi linear fitting
            for i, antenna in enumerate(self.antenna_list):    
                idx_f_i, idx_l_i = BinarySearch(self.ptime[i][0], time_temp)
                if len(self.rssi[i][0][idx_f_i:idx_l_i]) == 0:
                    self.rssi_fit.append(-80)
                else:
                    self.rssi_fit.append(Linear_fitting_2pnts(self.ptime[i][0][idx_f_i], self.ptime[i][0][idx_l_i], self.rssi[i][0][idx_f_i], self.rssi[i][0][idx_l_i], time_temp))
            
            self.phase_list[idx,:] = np.array([self.phase_fit[self.a_1_idx], self.phase_fit[self.a_2_idx], self.phase_fit[self.a_3_idx], self.phase_fit[self.a_4_idx] ])
            self.rssi_list[idx,:]= np.array([self.rssi_fit[self.a_1_idx], self.rssi_fit[self.a_2_idx], self.rssi_fit[self.a_3_idx], self.rssi_fit[self.a_4_idx] ])
        return self.phase_list, self.rssi_list

    def get_data_segment_for_LSTM(self, start_time, length = 5, window_size = 20, step_size = 1/50, T = [0.85,0.8]):
        ## the length can be 2,4 and 10 second 
        stop_time = start_time + length * window_size * step_size
        ptime_fit = np.linspace(start_time, stop_time, round((stop_time-start_time) / step_size))
        self.phase_list, self.rssi_list = self.get_data_segment(ptime_fit)
        # print('ptime_fit',len(ptime_fit),ptime_fit)

        def get_rssi_cdf_v1(rssi_list, percentile):
            # if there is no RSSI data pnt in the data window, return [ -75 db for all antennas ].
            if len(rssi_list) == 0:
                return [-75.0 for i in range(len(percentile))]
            # if there is at least one data, then sort them and return the 0,25,50,75,100 percentiles
            rssi_sorted = np.sort(rssi_list)
            value_list = []
            for percent in percentile:
                value_list.append(np.percentile(rssi_sorted,percent))
            return value_list

        writer = []
        row_write = []
        phase_graph = np.zeros((len(ptime_fit),200))
        for idx, time_temp in enumerate(ptime_fit):
            _, phase_graph[idx,:] = self.get_pdf(self.phase_list[idx,:], offset = [0, 4.47, 3.30, 5.75], T1 = 0) ## set T1 = 0 here, we apply thresholding later.
            if idx % window_size == 0 and idx <= len(ptime_fit) - window_size:
                # print(idx)
                ############## accumulate the 200 pnt's phase_pdf #################
                phase_pdf_acc = np.zeros(200)
                window_cnt = 0
                for i in range(idx,idx+window_size):
                    ########################## We apply the data selection here. if the phase_pdf constructed from all phases has a high peak, #####################
                    ########################## then it means the all phases 'agree with' each other, then the whole phase_pdf is valid. ############################
                    if np.max(phase_graph[i])>=T[0]:# threshold parameter 1
                        window_cnt += 1
                        phase_pdf_acc += phase_graph[i]
                ############### take average if the phase_pdf accumulated is not a empty list ##################
                if  window_cnt != 0:
                    phase_pdf_acc /= window_cnt

                ################ return the peak's location and peak's value. We generated this feature but did not use it at last. ##################
                max_value, max_idx =0,0
                row = [time_temp + window_size * step_size, idx, max_value, max_idx] # stop time for each time window

                ################# get rssi cdf ######################
                for i in self.antenna_list_reorder:
                    ################# align two sequences by finding the idx for each antenna ######################
                    _, idx_f = BinarySearch(self.ptime[i][0], ptime_fit[idx])
                    idx_l, _ = BinarySearch(self.ptime[i][0], ptime_fit[idx + window_size - 1])
                    ################# get rssi cdf for each antenna ######################
                    row.extend(get_rssi_cdf_v1(self.rssi[i][0][idx_f: idx_l + 1], [0,25,50,75,100]))
                    ################# get data pnts in the time window for each antenna ######################
                    num_pnt = idx_l-idx_f+1
                    row.append(num_pnt)
                
                row.extend(phase_pdf_acc)
                row.append(0)##gt aoa

                ########## We apply the data selection here again. if the accumulated phase_pdf has a high peak, #####################
                ########## then it means the all phase_pdfs in the time window 'agree with' each other, then the whole data in this window is valid. ###############
                ########## if it is valid, use the new data, if not, use the previous data except the timestamp needs to update#################
                if np.max( phase_pdf_acc ) >= T[1]:# threshold parameter 2
                    row_write = row

                if len(row_write) != 0:# just in case it is a empty list. sometimes, at the beginning of an experiment, empty list occurs.
                    row_write[0] = time_temp
                    row_write[1] = idx
                    writer.append(row_write)
        return writer

    def get_pdf(self, phase_received, offset = [0, 4.47, 3.30, 5.75], T1 = 0.85): ## T1 is for threshold 1

        use_data = [True, True, True, True]
        antenna_enable = [int(use_data[self.a_1_idx]), int(use_data[self.a_2_idx]), int(use_data[self.a_3_idx]), int(use_data[self.a_4_idx])]
        ############### A simplified function that computes 200 points' phase_pdf ###############
        phase_pdf = fusion_SAR_simplify(phase_received, offset = offset, antenna_enable = antenna_enable, num_of_search = 200)

        if np.max(phase_pdf)>= T1:
            return True, np.array(phase_pdf)
        else:
            return False, np.zeros(200)

    def get_RSSIpdf(self, F = 3.5, base = 0.4, dev = 2, prop_model = [-44,-6.8]):
        #######
        RSSI_received = self.rssi_list
        d_rssi = ((RSSI_received[0] +  RSSI_received[1] ) - (RSSI_received[2] +  RSSI_received[3] )) / 4
        avg_rssi = np.mean(RSSI_received)  
        log_dis_center = 10 * np.log10(2.5)
        cos_est_rssi = F * d_rssi / prop_model[1] / 80 * np.log10(math.e) * np.exp((avg_rssi-prop_model[0]) / prop_model[1] + np.log(2.5))
        aoa_est_rssi = np.arccos( -1 * np.minimum(abs( cos_est_rssi) * 2 / 0.25, 1) * np.sign( cos_est_rssi) )
        gaussian_pdf = multivariate_normal.pdf(np.linspace(0,np.pi,200), mean=aoa_est_rssi, cov=dev) + base
        return np.array(gaussian_pdf)

if __name__ == '__main__':
    RFID_data = RFID_dataloader_v2('/home/zihaow/Experiments/Experi13/Data/test1.csv','E280 1160 6000 0209 F811 72C4')
    data = RFID_data.get_data(1655539004.6987)
    data, _ = RFID_data.get_data_segment(np.linspace(1655539014.6987, 1655539014.6987+2, round(2*50)))
    data = RFID_data.get_data_segment_for_LSTM(1655539014.6987)
    print(len(data))
    print(data)
    # pdf = RFID_data.get_pdf()
    # print(pdf)