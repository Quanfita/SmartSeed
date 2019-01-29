# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 22:06:21 2018

@author: Admin
"""

import cv2
import numpy as np
import random
import sys

class ACE(object):
    #饱和函数  
    def calc_saturation(self, diff, slope, limit):  
        ret = diff * slope  
        if ret > limit:  
            ret = limit  
        elif (ret < (-limit)):  
            ret = -limit  
        return ret  
     
    def automatic_color_equalization(self, nimg, slope=10, limit=1000, samples=500):  
     
        nimg = nimg.transpose(2, 0, 1)  
      
        #Convert input to an ndarray with column-major memory order(仅仅是地址连续，内容和结构不变)  
        nimg = np.ascontiguousarray(nimg, dtype=np.uint8)  
    
        width=nimg.shape[2]  
        height=nimg.shape[1]  
      
        cary=[]  
      
        #随机产生索引  
        for i in range(0,samples):  
            _x=random.randint(0,width)%width  
            _y=random.randint(0,height)%height  
     
            dict={"x":_x,"y":_y}  
            cary.append(dict)  
    
        mat = np.zeros((3,height,width),np.float32)  
    
        r_max = sys.float_info.min  
        r_min = sys.float_info.max  
    
        g_max = sys.float_info.min  
        g_min = sys.float_info.max  
    
        b_max = sys.float_info.min  
        b_min = sys.float_info.max  
      
        for i in range(height):  
            for j in range(width):  
                r=nimg[0,i,j]  
                g=nimg[1,i,j]  
                b=nimg[2,i,j]  
    
                r_rscore_sum = 0.0  
                g_rscore_sum = 0.0  
                b_rscore_sum = 0.0  
                denominator = 0.0  
      
                for _dict in cary:  
                    _x=_dict["x"] #width  
                    _y=_dict["y"] #height  
      
                    #计算欧氏距离  
                    dist=np.sqrt(np.square(_x-j)+np.square(_y-i))  
                    if (dist < height / 5):  
                        continue;  
     
                    _sr=nimg[0,_y,_x]  
                    _sg=nimg[1,_y,_x]  
                    _sb=nimg[2,_y,_x]  
      
                    r_rscore_sum +=self.calc_saturation(int(r) - int(_sr),slope,limit) / dist  
                    g_rscore_sum +=self.calc_saturation(int(g) - int(_sg),slope,limit) / dist  
                    b_rscore_sum +=self.calc_saturation(int(b) - int(_sb),slope,limit) / dist  
     
                    denominator += limit / dist  
     
                r_rscore_sum = r_rscore_sum / denominator  
                g_rscore_sum = g_rscore_sum / denominator  
                b_rscore_sum = b_rscore_sum / denominator  
      
                mat[0,i,j]=r_rscore_sum  
                mat[1,i,j]=g_rscore_sum  
                mat[2,i,j]=b_rscore_sum  
     
                if r_max<r_rscore_sum:  
                    r_max=r_rscore_sum  
                if r_min>r_rscore_sum:  
                    r_min=r_rscore_sum  
      
                if g_max<g_rscore_sum:  
                    g_max=g_rscore_sum  
                if g_min>g_rscore_sum:  
                    g_min=g_rscore_sum  
      
                if b_max<b_rscore_sum:
                    b_max=b_rscore_sum  
                if b_min>b_rscore_sum:  
                    b_min=b_rscore_sum  
      
        for i in range(height):  
            for j in range(width):  
               nimg[0, i, j] = (mat[0, i, j] - r_min) * 255 / (r_max - r_min)  
               nimg[1, i, j] = (mat[1, i, j] - g_min) * 255 / (g_max - g_min)  
               nimg[2, i, j] = (mat[2, i, j] - b_min) * 255 / (b_max - b_min)  
      
        return nimg.transpose(1, 2, 0).astype(np.uint8)

if __name__ == '__main__':
    img = cv2.imread('ouput.jpg')
    img = automatic_color_equalization(img)
    cv2.imwrite('ACE.jpg',img)