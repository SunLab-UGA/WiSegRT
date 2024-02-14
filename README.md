# WiSegRT

WiSegRT (Wireless Segmented Ray Tracing) is a precise indoor radio dataset for channel modeling, as detailed in our paper [WiSegRT: Dataset for Site-Specific Indoor Radio Propagation Modeling with 3D Segmentation and Differentiable Ray-Tracing](https://arxiv.org/abs/2312.11245). 

### Download WiSegRT and Install Sionna
* To begin, download the WiSegRT code and extract it to your target path. Then download the [scene.zip](https://outlookuga-my.sharepoint.com/:u:/g/personal/lz90799_uga_edu/ERQgp55EGwhLj4eKJOSQUvoBs5AVTWb7I4KPt_gaYaUNag?e=e2KRdh) and extract it to the WiSegRT directory.

* Then you need to install Sionna, visit the official Sionna repository at [https://github.com/nvlabs/sionna](https://github.com/nvlabs/sionna) and follow the installation guide. For data generation with either our models or your own, we strongly recommend using the Docker installation. This document's instructions are based on the Docker method, which we have tested on Ubuntu 20.04 and 22.04.
   * The Docker-based sionna installation includes the NVIDIA Container Toolkit for GPU support. Ensure that Docker GPU support is functioning correctly. Based on our experience, you can use `sudo make docker` when creating the Sionna Docker Image and `sudo make run-docker gpus=all` when creating the corresponding container later. 

* Enter the WiSegRT directory and edit the Makefile, find this line
```
run-docker:
	docker run -itd -v {write_your_path_here}:/tf/WiSegRT -u $(id -u):$(id -g) -p 8887:8888 --privileged=true $(GPU) --env NVIDIA_DRIVER_CAPABILITIES=graphics,compute,utility sionna
```
* Write the path of WiSegRT directory as `/your/path/WiSegRT:/tf/WiSegRT`. This will mount the WiSegRT directory to the container as `/tf/WiSegRT`.

* Then, launch a terminal in the WiSegRT directory and execute `sudo make run-docker gpus=all` to initiate a Docker container which will run in the background. This will also start a JupyterLab server in that container , accessible at [`http://127.0.0.1:8887/lab/`](http://127.0.0.1:8887/lab/) in your browser. You can explore the Sionna RT tutorial Jupyter notebooks here to ensure the NVIDIA Container Toolkit operates as expected.
```
sudo make run-docker gpus=all
```

### Generating Paths
* After initiating a container, execute `sudo docker ps -a` to find your container's name and `sudo docker exec -it {container_name} /bin/bash` to open a virtual terminal in that container. (If there is only one container, you can use `tab` key to fill the name.)
```
sudo docker ps -a
```
```
sudo docker exec -it {container_name} /bin/bash
```

* Now, you are in the virtual terminal of the container and you can enter the WiSegRT directory in the virtual terminal by：
```
cd WiSegRT/
```
* and run the provided script by `bash generating.sh <transmitter_number> <GPU_index> <scene_name> <x_lim> <y_lim> <z_lim> <interval>`. Here are the default settings to run the simulations for our models. (GPU_index controls which GPU the simulations will run on):
```
bash generating.sh 30 0 scene_01 8 6 2.4 0.3
bash generating.sh 16 0 scene_02 4 3 2.4 0.2
bash generating.sh 18 0 scene_03 12 8 2.4 0.3
bash generating.sh 9 0 scene_04 12 8 2.4 0.3
bash generating.sh 18 0 scene_05 6 4 2.4 0.2
bash generating.sh 16 0 scene_06 16 8 2.4 0.3
```
* Or you can run a small scale simulations by setting the transmitter_number to 1.

* Upon completion, the generated path data and `.obj` models are stored within the `path` directory. For details on the data structure, refer to the `save_path` function in `generating.py`. Use the `load_path` function in `utilities.py` to access the stored paths. Note that outputs may include invalid receiver positions, which can be easily filterd out by their lack of valid path.

   * Notably, the attenuation (a) and delay (tau) of each path are from the `path.cir()` function, representing the baseband equivalent channel impulse response. Besides, the latest Sionna version (0.16.2) has introduced `path.to_dict()` and `path.from_dict()` methods, facilitating the export and import of path data for Sionna communication system simulations. We plan to adopt this feature in future releases.

### Conducting Multiple Simulations at One Time
* To run multiple simulations at one time, you have to open multiple terminals in the WiSegRT directory and open virtual container terminals by running `sudo docker exec -it {container_name} /bin/bash` in each of them. Then you can run the shell script in each of the virtual terminals.

* The feasible number of concurrent simulations depends on the hardware capabilities and the complexity of the scene model. For example, it's possible to run three simulations on GPU 0 and another three on GPU 1. Monitor system load with `nvidia-smi` and allocate resources with some redundancy to accommodate the variations in computational demand as receiver locations change.

### Creating Custom Scene Models with Blender
Follow the [Sionna RT tutorial](https://www.youtube.com/watch?v=7xHLDxUaQ7c) to learn how to create your custom scene for Sionna. Generally, you need to install [Blender 3.6 LTS](https://www.blender.org/download/releases/3-6/), Mitsuba `pip install mitsuba`, and then [Mitsuba-Blender add-on](https://github.com/mitsuba-renderer/mitsuba-blender)( we tested [v0.3.0](https://github.com/mitsuba-renderer/mitsuba-blender/releases/download/v0.3.0/mitsuba-blender.zip) with Blender 3.6 LTS). When creating your scene, ensure that materials are appropriately named (e.g., `itu_wood.001`, `itu_wood.002`... for diffrent Blender materials that are actually "wood", the `generating.py` will handle it). When exporting scenes to XML files, adhere to the specified export settings (export IDs, Y forward, Z up) and export them directly to the `./scene` directory. Execute `generating.sh` with your scene parameters.
