# **Semantic Layering in Room Segmentation via LLMs (SeLRoS)**

[Taehyeon Kim](https://github.com/QualiaT) and Byung-Cheol Min.

[Project Page](https://sites.google.com/view/selros)

Code repository for Semantic Layering in Room Segmentation via LLMs (SeLRoS). This repository includes 2D Map generation code and Room Information Interpreter code, and a data set containing ground truth, object information file, top view image, and room segmentation results for each environment for an experiment in 30 environments.


## Setup
Install dependencies:
```
pip install -r requirments.txt
```
For more details, please check the following link [ProcTHOR](https://github.com/allenai/procthor).





## Running Script
Run the following command to interpret segmenation map and generate output. 

```
python3 room_info_interpreter.py --input1 {segmented_map.png} --input2 {related_information.txt}
```
Note: You can use the segmented_map.png and related_information.txt in ```data\vrf\```.


Run the following script to generate top view image and 2d map of environment.

```
python3 run_get_2d_map.py
```

Run the following script to get scenes of specific position.

```
python3 run_get_scenes.py
```
Note: If you want to change observation position, change x, z value in 52 line.


## Dataset
The repository contains ground truth, object information file, top view image, and room segmentation results for each environment. 

Refer to ```data\ground_truth\``` for the ground truth of each environment.

Refer to ```data\object_information\``` for the object information txt file of each room in each environment.

Refer to ```data\selros\``` for the final room segmentation results using SeLRoS.

Refer to ```data\top_view\``` for the top view image of each environment.

Refer to ```data\vrf\``` for the room segmentation results using Voronoi Random Field algorithm and related information (each segmented room's center coordinate and color).



## Citation
If you find this work useful for your research, please consider citing:
```
@article{kim2024semantic,
  title={Semantic Layering in Room Segmentation via LLMs},
  author={Kim, Taehyeon and Min, Byung-Cheol},
  journal={arXiv preprint arXiv:2403.12920},
  year={2024}
}
```