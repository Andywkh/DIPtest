## import the CV gt bbox file for post-matching
## 
## offline processing

import os
import time
import datetime
import math
import csv
import numpy as np
from utils.basic import *

class cv_dataloader:
    def __init__(self, box_filename, box_list_wanted = ['0 ', '1 ','2 ']):#rfid_list_wanted = ['E280 1160 6000 0209 F811 7224'] #  ['E280 1160 6000 0209 F811 7224']['E280 6894 0000 500E 73D4 548C']
        ## cv distance ##
        # [Timestamp	frame	id	block	distance	cx	cy	left	top	 w	h	coor_x	coor_y	coor_z] #
        self.box_ids = []
        self.box_data = []
        with open(box_filename, 'r') as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            for row in f_csv:
                if row[4] != 'nan ' and  row[4] != 'inf ' and row[2] in box_list_wanted:
                    if row[2] not in self.box_ids:
                        self.box_ids.append(row[2])
                        self.box_data.append([])
                    self.box_data[self.box_ids.index(row[2])].append([row[0],row[1],row[3],row[4],row[11],row[12],row[13]])
            f.close()
        print(self.box_ids)
        
        ####cdis ==> [antenna idx][person idx]==>[dis0,dis1,dis2,...]
        ####ctime ==> [person idx]==>[time0,time1,time1,...]
        # antenna_loc_list = [[-0.375,0.15,0.08],[-0.125,0.15,0.08],[0.125,0.15,0.08],[0.375,0.14,0.08]]
        wave_len = 0.1629247078010329
        self.ctime = [[] for i in self.box_ids]
        self.cx = [[] for i in self.box_ids]
        self.cz = [[] for i in self.box_ids]
        self.ctan = [[] for i in self.box_ids]
        self.cdis = [[] for i in self.box_ids]
        for k, person in enumerate(self.box_ids):
            self.ctime[k] = np.array([float(i[0]) for i in self.box_data[self.box_ids.index(person)] if i[-2] != 'nan '])
            self.c_x_temp = np.array([eval(i[-3]) for i in self.box_data[self.box_ids.index(person)] if i[-2] != 'nan ']) - 0
            self.c_z_temp = np.array([eval(i[-1]) for i in self.box_data[self.box_ids.index(person)] if i[-2] != 'nan ']) + 0.08
            self.ctan[k] = [self.c_x_temp[i]/self.c_z_temp[i] for i in range(len(self.c_x_temp))]
            self.cdis[k] = np.array([eval(i[3]) for i in self.box_data[self.box_ids.index(person)] if i[-2] != 'nan '])
            self.cx[k] =  self.c_x_temp * 1
            self.cz[k] =  self.c_z_temp * 1
        self.count = -1
        print('Finish CV data loading')
        print('Start time: %.4f, stop time: %.4f' % (self.ctime[0][0],self.ctime[0][-1]))
    def get_data(self, time_temp):
        # interpolation, length is in sec

        self.ctan_fit = [[] for i in self.box_ids]
        self.cx_fit =  [[] for i in self.box_ids]
        self.cz_fit = [[] for i in self.box_ids]
        self.c_aoa_fit = [[] for i in self.box_ids]
        self.cdis_fit = [[] for i in self.box_ids]

        for j, cvid in enumerate(self.box_ids):
            idx_f_i, idx_l_i = BinarySearch(self.ctime[j], time_temp)
            if len(self.ctime[j][idx_f_i:idx_l_i]) == 0:
                self.ctan_fit[j].append(self.ctan[j][idx_f_i])
                self.cx_fit[j].append(self.cx[j][idx_f_i])
                self.cz_fit[j].append(self.cz[j][idx_f_i])
                self.cdis_fit[j].append(self.cdis[j][idx_f_i])
            else:
                self.ctan_fit[j].append(Linear_fitting_2pnts(self.ctime[j][idx_f_i], self.ctime[j][idx_l_i], self.ctan[j][idx_f_i], self.ctan[j][idx_l_i], time_temp))
                self.cx_fit[j].append(Linear_fitting_2pnts(self.ctime[j][idx_f_i], self.ctime[j][idx_l_i], self.cx[j][idx_f_i], self.cx[j][idx_l_i], time_temp))
                self.cz_fit[j].append(Linear_fitting_2pnts(self.ctime[j][idx_f_i], self.ctime[j][idx_l_i], self.cz[j][idx_f_i], self.cz[j][idx_l_i], time_temp))
                self.cdis_fit[j].append(Linear_fitting_2pnts(self.ctime[j][idx_f_i], self.ctime[j][idx_l_i], self.cdis[j][idx_f_i], self.cdis[j][idx_l_i], time_temp))
            self.c_aoa_fit[j].append(np.arccos(self.cx_fit[j][-1]/(self.cz_fit[j][-1] ** 2 + self.cx_fit[j][-1] ** 2) ** 0.5))

        return self.box_ids, np.array(self.c_aoa_fit) / np.pi , ptime_fit
    def get_time_for_frame(self, frame_idx):
        self.count += 1
        return self.ctime[0][frame_idx]
if __name__ == '__main__':
    cv_data = cv_dataloader('/home/zihaow/Experiments/Experi13/Data/1.csv')
    ids, data,_ = cv_data.get_data(1655539017.9640)
    print(np.shape(data))
    print(data)
    # pdf = RFID_data.get_pdf()
    # print(pdf)
    
