# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 16:30:12 2018

@author: Admin
"""

from .config import *

import os
import cv2
import datetime
import numpy as np

from .ai import *
from .tricks import *

def sketch_upload(sketch,method='colorization',room_path='./tmp'):
    if os.path.exists(room_path + '/tmp.improved.jpg'):
        improved_sketch = cv2.imread(room_path + '/tmp.improved.jpg')
        #print('lucky to find improved sketch')
    else:
        improved_sketch = sketch.copy()
        improved_sketch = min_resize(improved_sketch, 512)
        improved_sketch = cv_denoise(improved_sketch)
        improved_sketch = sensitive(improved_sketch, s=5.0)
        improved_sketch = go_tail(improved_sketch)
        cv2.imwrite(room_path + '/tmp.improved.jpg', improved_sketch)
    color_sketch = improved_sketch.copy()
    std = cal_std(color_sketch)
    #print('std = ' + str(std))
    need_de_painting = (std > 100.0) and method == 'rendering'
    if method=='recolorization' or need_de_painting:
        if os.path.exists(room_path + '/tmp.recolorization.jpg') or os.path.exists(room_path + '/tmp.de_painting.jpg'):
            print('lucky to find lined sketch')
        else:
            improved_sketch = go_passline(color_sketch)
            improved_sketch = min_k_down_c(improved_sketch, 2)
            improved_sketch = cv_denoise(improved_sketch)
            improved_sketch = go_tail(improved_sketch)
            improved_sketch = sensitive(improved_sketch, s=5.0)
            cv2.imwrite(room_path + '/tmp.recolorization.jpg', min_black(improved_sketch))
            if need_de_painting:
                cv2.imwrite(room_path + '/tmp.de_painting.jpg', min_black(improved_sketch))
                #print('In rendering mode, the user has uploaded a painting, and I have translated it into a sketch.')
            #print('sketch lined')
    cv2.imwrite(room_path + '/tmp.colorization.jpg', min_black(color_sketch))
    cv2.imwrite(room_path + '/tmp.rendering.jpg', eye_black(color_sketch))
    #print('sketch improved')
    return


def painting(imgname,reference=None,points=[],alpha=0,method='colorization',line = False,lineColor=np.array([0,0,0]),room_path='./tmp'):
    ID = datetime.datetime.now().strftime('H%HM%MS%S')
    if reference is not None:
        reference = s_enhance(reference)
    else:
        reference = None
    sketch = cv2.imread(room_path + '/tmp.' + method + '.jpg', cv2.IMREAD_GRAYSCALE)
    sketch_1024 = k_resize(sketch, 64)
    if os.path.exists(room_path + '/tmp.de_painting.jpg') and method == 'rendering':
        vice_sketch_1024 = k_resize(cv2.imread(room_path + '/tmp.de_painting.jpg', cv2.IMREAD_GRAYSCALE), 64)
        sketch_256 = mini_norm(k_resize(min_k_down(vice_sketch_1024, 2), 16))
        sketch_128 = hard_norm(sk_resize(min_k_down(vice_sketch_1024, 4), 32))
    else:
        sketch_256 = mini_norm(k_resize(min_k_down(sketch_1024, 2), 16))
        sketch_128 = hard_norm(sk_resize(min_k_down(sketch_1024, 4), 32))
    #print('sketch prepared')
    cv2.imwrite(room_path + '/tmp.128.jpg', sketch_128)
    cv2.imwrite(room_path + '/tmp.256.jpg', sketch_256)
    baby = go_baby(sketch_128, opreate_normal_hint(ini_hint(sketch_128), points, type=0, length=1))
    baby = de_line(baby, sketch_128)
    for _ in range(16):
        baby = blur_line(baby, sketch_128)
    baby = go_tail(baby)
    baby = clip_15(baby)
    cv2.imwrite(room_path + '/baby.tmp.' + ID + '.jpg', baby)
    #print('baby born')
    composition = go_gird(sketch=sketch_256, latent=d_resize(baby, sketch_256.shape), hint=ini_hint(sketch_256))
    if line:
        composition = emph_line(composition, d_resize(min_k_down(sketch_1024, 2), composition.shape), lineColor)
    composition = go_tail(composition)
    cv2.imwrite(room_path + '/composition.tmp.' + ID + '.jpg', composition)
    #print('composition saved')
    painting_function = go_head
    if method == 'rendering':
        painting_function = go_neck
    #print('method: ' + method)
    result = painting_function(
        sketch=sketch_1024,
        global_hint=k_resize(composition, 14),
        local_hint=opreate_normal_hint(ini_hint(sketch_1024), points, type=2, length=2),
        global_hint_x=k_resize(reference, 14) if reference is not None else k_resize(composition, 14),
        alpha=(1 - alpha) if reference is not None else 1
    )
    result = go_tail(result)
    cv2.imwrite(room_path + '/result.tmp.' + ID + '.jpg', result)
    return result

def run(imgname,reference=None,alpha=0.5,method='colorization',lineColor=np.array([0,0,0]),room_path='./tmp'):
    h,w,c = imgname.shape
    sketch_upload(imgname,method='colorization',room_path=room_path)
    tmp = painting(imgname,points=points,method=method,reference=reference,alpha=alpha,lineColor=lineColor)
    tmp = cv2.resize(tmp,(w,h))
    return tmp.astype(np.uint8)

if __name__ == '__main__':
    inputname = '007.jpg'
    outputname = inputname.split('.')[0]+'-res.jpg'
    run(inputname,outputname,True,0.9)
