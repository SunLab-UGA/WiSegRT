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

import argparse
parser = argparse.ArgumentParser(description = 'gpu_ind & scene_file')
parser.add_argument('gpu_ind', type=str)
parser.add_argument('scene_file',type =str)
parser.add_argument('x_lim',type = float)
parser.add_argument('y_lim',type = float)
parser.add_argument('z_lim',type = float)
parser.add_argument('interval',type = float)
parser.add_argument('tx_ind',type = int)

args = parser.parse_args()
import os

gpu_ind = args.gpu_ind 
os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ind
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print(gpus)
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError as e:
        print(e) 
tf.get_logger().setLevel('ERROR')

tf.random.set_seed(1) # Set global random seed for reproducibility


import matplotlib.pyplot as plt
import numpy as np
import time
import sionna

'''import Sionna RT components'''
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera,RadioMaterial


################################################################################
x_lim = args.x_lim
y_lim = args.y_lim
z_lim = args.z_lim
interval = args.interval

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

x_pos = generate_h_pos(x_lim,interval)
y_pos = generate_h_pos(y_lim,interval)
z_pos = generate_v_pos(z_lim,interval)

#Load scene

scene_name = args.scene_file
scene_path = './scene/'+scene_name+'.xml'
scene = load_scene(scene_path)

custom_plastic = RadioMaterial("custom_plastic",
                                relative_permittivity=2.3,
                                conductivity=0)

custom_leather = RadioMaterial("custom_leather",
                                relative_permittivity=1.8,
                                conductivity=0)

custom_cloth = RadioMaterial("custom_cloth",
                                relative_permittivity=1.8,
                                conductivity=0)

scene._radio_materials[custom_plastic.name] = custom_plastic
scene._radio_materials[custom_leather.name] = custom_leather
scene._radio_materials[custom_cloth.name] = custom_cloth

for i,obj in enumerate(scene.objects.values()):
    if f"{obj.radio_material.name}"[-4:-3] == ".":
        obj.radio_material = scene.get(f"{obj.radio_material.name}"[:-4])
    else:
        obj.radio_material = scene.get(f"{obj.radio_material.name}")



# Configure antenna array for all transmitters
scene.tx_array = PlanarArray(num_rows=1, 
                             num_cols=1,
                             vertical_spacing=0.5,
                             horizontal_spacing=0.5,
                             pattern="dipole",
                             polarization="V")

# Configure antenna array for all receivers
scene.rx_array = PlanarArray(num_rows=1,
                             num_cols=1,
                             vertical_spacing=0.5,
                             horizontal_spacing=0.5,
                             pattern="iso",
                             polarization="cross")

scene.frequency = 2.4e9 # in Hz; implicitly updates RadioMaterials

scene.synthetic_array = True # If set to False, ray tracing will be done per antenna element (slower for large arrays)

#######################################################################################

def save_path(path,tx_loc,rx_loc,output_path):
    a,tau = path.cir()
    path_dict = np.array([
                    tx_loc, 
                    rx_loc,
                    a.numpy(), #Channel coefficients//Attenuation
                    tau.numpy(), #delay
                    path.theta_t.numpy(), #Zenith  angles of departure
                    path.phi_t.numpy(),   #Azimuth angles of departure
                    path.theta_r.numpy(), #Zenith angles of arrival
                    path.phi_r.numpy(),     #Azimuth angles of arrival
                    path.types.numpy()
                    ],dtype=object)

    file_path = output_path+ '/tx_'+str(int(tx_loc[0]*10))+'_'+str(int(tx_loc[1]*10))+'_'+str(int(tx_loc[2]*10)) \
    +'/path/path_'+str(int(rx_loc[0]*10))+'_'+str(int(rx_loc[1]*10))+'_'+str(int(rx_loc[2]*10))

    np.save(file_path,path_dict)
    path.export(output_path+'/tx_'+str(int(tx_loc[0]*10))+'_'+str(int(tx_loc[1]*10))+'_'+str(int(tx_loc[2]*10))\
                +'/obj/path_'+str(int(rx_loc[0]*10))+'_'+str(int(rx_loc[1]*10))+'_'+str(int(rx_loc[2]*10))+'.obj')

def generate_paths(scene,tx_loc,output_path):
    start_time = time.time()
    count = 0
    
    tx = Transmitter(name="tx",
             position=tx_loc)
    scene.add(tx)

    dir_tx = output_path+ '/tx_'+str(int(tx_loc[0]*10))+'_'+str(int(tx_loc[1]*10))+'_'+str(int(tx_loc[2]*10))+'/path'
    if not os.path.exists(dir_tx):
        os.makedirs(dir_tx)
    dir_tx_obj = output_path+ '/tx_'+str(int(tx_loc[0]*10))+'_'+str(int(tx_loc[1]*10))+'_'+str(int(tx_loc[2]*10))+'/obj'
    if not os.path.exists(dir_tx_obj):
        os.makedirs(dir_tx_obj)
    
    
    for x in x_pos:
        curr_time = time.time()
        print(count,': ',curr_time-start_time,'seconds')
        for y in y_pos:

            for z in z_pos:
            
                rx_loc = [x,y,z]
                rx = Receiver(name='rx',
                              position=[x,y,z],
                              orientation=[0,0,0])
                scene.add(rx)
                paths = scene.compute_paths(max_depth=4,
                                      diffraction = True,
                                      num_samples=1e6)
          
            
                save_path(paths,tx_loc,rx_loc,output_path)
            
                scene.remove('rx')
                count+=1

    scene.remove('tx')

################################################################################################

output_path = './paths/'+f"{scene_name}"
tx_ind = args.tx_ind
tx_locs=np.load('./scene/'+ f"{scene_name}"+'_tx_locs.npy').tolist()

generate_paths(scene,tx_locs[tx_ind],output_path)







