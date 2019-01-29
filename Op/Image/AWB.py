# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 23:24:31 2018

@author: Admin
"""

import cv2
import numpy as np

def whiteBalance(img):
    #rows = img.shape[0]
    #cols = img.shape[1]
    
    final = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
    
    avg_a = np.average(final[:,:,1])
    avg_b = np.average(final[:,:,2])
    
    for x in range(final.shape[0]):
        for y in range(final.shape[1]):
            l,a,b = final[x,y,:]

            l *= 100 / 255.0
            final[x,y,1] = a-((avg_a - 128) * (1 / 100.0))
            final[x,y,2] = b-((avg_b - 128) * (1 / 100.0))
    
    final = cv2.cvtColor(final,cv2.COLOR_LAB2BGR)
    
    return final
if __name__ == '__main__':
    img = cv2.imread('color.jpg')
    img = whiteBalance(img)
    cv2.imwrite('AWB.jpg',img)