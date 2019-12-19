# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 13:56:28 2019

@author: Quanfita
"""
from common.singleton import SingletonIns
import numpy as np
import cv2

@SingletonIns
class Filter(object):
    def findPos(self,point,ori):
        l = []
        x = point[0]
        y = point[1]
        z = point[2]
        a = y // 4 + (x // 32)*64
        b = z // 4 + ((x % 32) // 4)*64
        l.append(a)
        l.append(b)
        return l
    
    def myFilter(self,orimap,newmap,picname):
        my = picname.astype(np.int16)
        x = my[:,:,1] // 4 + (my[:,:,0] // 32)*64
        y = my[:,:,2] // 4 + ((my[:,:,0] % 32) // 4)*64
        new = cv2.merge([x,y])
        
        for i in range(len(my)):
            for j in range(len(my[0])):
                #pos = self.findPos(my[i][j],orimap)
                #my[i][j] = newmap[pos[0],pos[1]]
                my[i][j] = newmap[new[i,j,0],new[i,j,1]]
        
        return my.astype(np.uint8)

if __name__ == '__main__':
    Filter.myFilter('lookup-table.png','lookup-table_anime.jpg','3.jpg')
