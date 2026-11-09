#!/usr/bin/env python3
"""Generate matching Gazebo Classic world and ROS2 occupancy map for a TurtleBot3 maze."""
from pathlib import Path
import math

OUT=Path(__file__).resolve().parent
RES=0.05
W=160; H=120  # 8m x 6m
# 0=free, 1=occupied
occ=[[0]*W for _ in range(H)]
# World frame: centered at (0,0). Pixel origin lower-left for logical grid.
def paint(cx,cy,sx,sy):
    for j in range(H):
        y=(j+0.5)*RES-3
        if abs(y-cy)>sy/2: continue
        for i in range(W):
            x=(i+0.5)*RES-4
            if abs(x-cx)<=sx/2: occ[j][i]=1
walls=[]
def wall(x,y,sx,sy):
    walls.append((x,y,sx,sy)); paint(x,y,sx,sy)
# boundary walls
wall(0,2.9,8,0.2);wall(0,-2.9,8,0.2);wall(-3.9,0,0.2,6);wall(3.9,0,0.2,6)
# staggered vertical partitions: openings alternate at top and bottom
wall(-2.3,-0.65,0.16,4.1) # opening at top
wall(-0.7,0.65,0.16,4.1)  # opening at bottom
wall(0.9,-0.65,0.16,4.1)
wall(2.5,0.65,0.16,4.1)
# dead-end branches / obstacles (stay out of required route)
wall(-3.15,0.7,0.65,0.16)
wall(-1.5,-1.3,0.55,0.16)
wall(0.1,1.3,0.55,0.16)
wall(1.7,-1.3,0.55,0.16)
# PGM pixels from top to bottom, 0=occupied, 254=free
with (OUT/'maze.pgm').open('w') as f:
    f.write(f'P2\n# generated matching Gazebo maze\n{W} {H}\n255\n')
    for row in reversed(occ): f.write(' '.join('0' if v else '254' for v in row)+'\n')
(OUT/'maze.yaml').write_text('image: maze.pgm\nmode: trinary\nresolution: 0.05\norigin: [-4.0, -3.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n')
models=[]
for idx,(x,y,sx,sy) in enumerate(walls):
    models.append(f'''<model name="wall_{idx}"><static>true</static><pose>{x} {y} 0.45 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>{sx} {sy} 0.9</size></box></geometry></collision><visual name="visual"><geometry><box><size>{sx} {sy} 0.9</size></box></geometry><material><ambient>0.5 0.55 0.65 1</ambient><diffuse>0.5 0.55 0.65 1</diffuse></material></visual></link></model>''')
world='''<?xml version="1.0"?><sdf version="1.6"><world name="default"><include><uri>model://ground_plane</uri></include><include><uri>model://sun</uri></include><physics type="ode"><real_time_update_rate>1000</real_time_update_rate><max_step_size>0.001</max_step_size></physics>'''+''.join(models)+'''</world></sdf>'''
(OUT/'maze.world').write_text(world)
print('Generated:', OUT/'maze.world',OUT/'maze.yaml',OUT/'maze.pgm')
print('Start: x=-3.25, y=-2.0 | Goal: x=3.25, y=-2.0')
