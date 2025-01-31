#
# Copyright (C) 2024, SunLab (Lihao Zhang)
# SunLab Wireless Research Group, https://sunlab.uga.edu
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  hsun@uga.edu
#


import numpy as np
import matplotlib.pyplot as plt

#scene parameters
scene_name = 'scene_01'
x_lim = 8
y_lim = 6
z_lim = 2.4
interval = 0.3

tx_locs=np.load('./scene/'+ scene_name+'_tx_locs.npy').tolist()

# Generate the receiver grid
def generate_h_pos(x_lim,interval):
    x_pos_num = int(x_lim/interval)-1
    x_pos = np.zeros(x_pos_num)
    for i in range(0,x_pos_num):
        x_pos[i] = np.around((-x_lim/2 + interval*(i+1)),1)
    return x_pos

def generate_v_pos(x_lim,interval):
    x_pos_num = int(x_lim/interval)-1
    x_pos = np.zeros(x_pos_num)
    for i in range(0,x_pos_num):
        x_pos[i] = np.around((0 + interval*(i+1)),1)
    return x_pos

# Iterate all the combination of the following  i os, y_pos and z_pos
x_pos = generate_h_pos(x_lim,interval)
y_pos = generate_h_pos(y_lim,interval)
z_pos = generate_v_pos(z_lim,interval)


### Load the stored path_dict 
# path_dict = np.array([
#                 tx_loc, 
#                 rx_loc,
#                 a.numpy(), #Channel coefficients//Attenuation
#                 tau.numpy(), #delay
#                 path.theta_t.numpy(), #Zenith  angles of departure
#                 path.phi_t.numpy(),   #Azimuth angles of departure
#                 path.theta_r.numpy(), #Zenith angles of arrival
#                 path.phi_r.numpy(),     #Azimuth angles of arrival
#                 path.types.numpy()
#                 ],dtype=object)

def load_path(scene_name,tx_loc,rx_loc):
    tx_name = 'tx_'+str(int(tx_loc[0]*10))+'_'+str(int(tx_loc[1]*10))+'_'+str(int(tx_loc[2]*10))
    rx_name = str(int(rx_loc[0]*10))+'_'+str(int(rx_loc[1]*10))+'_'+str(int(rx_loc[2]*10))
    file_path = './paths/'+scene_name+'/'+ tx_name +'/path/path_'+rx_name+'.npy'
    path = np.load(file_path,allow_pickle=True)
    return path


### Plot the CIR of the path
def print_cir(a,tau):
    t = tau[0,0,0,:]/1e-9 # Scale to ns
    a_abs = np.abs(a)[0,0,0,0,0,:,0]
    a_max = np.max(a_abs)
    # Add dummy entry at start/end for nicer figure
    t = np.concatenate([(0.,), t, (np.max(t)*1.1,)])
    a_abs = np.concatenate([(np.nan,), a_abs, (np.nan,)])
    
    # And plot the CIR
    plt.figure()
    plt.title("Channel impulse response realization")
    
    plt.stem(t, a_abs)
    plt.xlim([0, np.max(t)])
    plt.ylim([-2e-6, a_max*1.1])
    plt.xlabel(r"$\tau$ [ns]")
    plt.ylabel(r"$|a|$");

### Plot the distribution of the generated paths
# !pip install seaborn #in jupyter notebook
import seaborn as sns

def get_a_samples(scene_name,sample_number=1e6):
    non_list = []
    all_a= np.array(non_list)
    count =0 
    for tx_loc in tx_locs:
        for x in x_pos:
            print('Sampled data:'all_a.shape[0],end = "\r")
            for y in y_pos:
                for z in z_pos:
                    count+=1
                    if count%10 != 0:
                        continue
                    rx_loc=[x,y,z]
                    path = load_path(scene_name,tx_loc,rx_loc) 
                    if not path[2].all(): #filiter invalid rx positions
                        continue
                    a_abs = np.abs(path[2])[0,0,0,0,0,:,0]
    
                    for temp_a in a_abs:
                        all_a = np.append(all_a,temp_a)
                    if all_a.shape[0] >= sample_number:
                        return all_a

fig, ax = plt.subplots()
all_a = get_a_samples(scene_name)
sns.ecdfplot(data=all_a,log_scale=True)







