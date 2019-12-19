# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 20:42:54 2019

@author: Quanfita
"""

import cv2
import numpy as np
import Op.Mixed as Mixed 
import math

class Ink(object):
    def __init__(self):
        pass
    def natural_histogram_matching(self,img):
        ho = np.zeros( 256)
        po = np.zeros( 256)
        for i in range(256):
            po[i] = np.sum(img == i)
        po = po / np.sum(po)
        ho[0] = po[0]
        for i in range(1,256):
            ho[i] = ho[i - 1] + po[i]
    
        #p1 = lambda x : (1 / 9.0) * np.exp(-(255 - x) / 9.0)
        #p2 = lambda x : (1.0 / (150 - 0)) * ((x >= 0 and x <= 150) or (x>250))
        #p3 = lambda x : (1.0 / np.sqrt(2 * math.pi *5) ) * np.exp(-((x - 240) ** 2) / float((2 * (5 **2))))
        p1 = lambda x : (1 / 9.0) * np.exp((-x) / 9.0)
        p2 = lambda x : (1.0 / (200-80)) * ((x >= 80 and x <= 200) or (x>250))
        p3 = lambda x : (1.0 / np.sqrt(2 * math.pi *9) ) * np.exp(-((x - 225) ** 2) / float((2 * (9 **2))))
        p = lambda x : (6 * p1(x) +22 * p2(x) + 72 * p3(x)) * 0.01
        #p = lambda x : (8 * p1(x) +42 * p2(x) + 50 * p3(x)) * 0.01
        prob = np.zeros(256)
        histo = np.zeros(256)
        total = 0
        for i in range(256):
            prob[i] = p(i)
            total = total + prob[i]
        prob = prob / np.sum(prob)
    
        histo[0] = prob[0]
        for i in range(1, 256):
            histo[i] = histo[i - 1] + prob[i]
    
        Iadjusted = np.zeros((img.shape[0], img.shape[1]))
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                histogram_value = ho[img[x,y]]
                i = np.argmin(np.absolute(histo - histogram_value))
                Iadjusted[x, y] = i
    
        Iadjusted = np.float64(Iadjusted) / 255.0
        return Iadjusted
    
    def Gaussian(self,scr,sigma,size):
        global SIGMA
        SIGMA = sigma/10.0
        KSIZE = size * 2 +3
        #print(KSIZE, SIGMA)
        dst = cv2.GaussianBlur(scr, (KSIZE,KSIZE), SIGMA, KSIZE) 
        #cv2.imwrite('./tmp/Gaussian_sigma.jpg',dst)
        return dst
    
    def rotate_img(self,img, angle):
        row, col = img.shape
        M = cv2.getRotationMatrix2D((row / 2, col / 2), angle, 1)
        res = cv2.warpAffine(img, M, (row, col))
        return res
    
    def get_eight_directions(self,l_len):    
        L = np.zeros((8, l_len, l_len))
        half_len = (l_len + 1) // 2
        for i in range(8):
            if i == 0 or i == 1 or i == 2 or i == 7:
                for x in range(l_len):
                        y = half_len - int(round((x + 1 - half_len) * math.tan(math.pi * i // 8)))
                        if y >0 and y <= l_len:
                            L[i, x, y - 1 ] = 1
                if i != 7:
                    L[i + 4] = np.rot90(L[i])
        L[3] = np.rot90(L[7], 3)
        return L
    
    def get_stroke(self,img, ks,  dirNum):
        height , width = img.shape[0], img.shape[1]
        img = np.float32(img) / 255.0
        img = cv2.medianBlur(img, 3)
        #print(img.shape)
        #cv2.imshow('blur', img)
        imX = np.append(np.absolute(img[:, 0 : width - 1] - img[:, 1 : width]), np.zeros((height, 1)), axis = 1)
        imY = np.append(np.absolute(img[0 : height - 1, :] - img[1 : height, :]), np.zeros((1, width)), axis = 0)
        #img_gredient = np.sqrt((imX ** 2 + imY ** 2))
        img_gredient = imX + imY
    
        kernel_Ref = np.zeros((ks * 2 + 1, ks * 2 + 1))
        kernel_Ref [ks, :] = 1
    
        response = np.zeros((dirNum, height, width))
        L = self.get_eight_directions(2 * ks + 1)
        for n in range(dirNum):
            ker = self.rotate_img(kernel_Ref, n * 180 / dirNum)
            response[n, :, :] = cv2.filter2D(img, -1, ker)
    
        Cs = np.zeros((dirNum, height, width))
        for x in range(width):
            for y in range(height):
                i = np.argmax(response[:,y,x])
                Cs[i, y, x] = img_gredient[y,x]
    
        spn = np.zeros((8, img.shape[0], img.shape[1]))
    
        kernel_Ref = np.zeros((2 * ks + 1, 2 * ks + 1))
        kernel_Ref [ks, :] = 1
        for n in range(width):
            if (ks - n) >= 0:
                kernel_Ref[ks  - n, :] = 1
            if (ks + n)  < ks * 2:
                kernel_Ref[ks + n, :] = 1
    
        kernel_Ref = np.zeros((2*ks + 1, 2 * ks + 1))
        kernel_Ref [ks, :] = 1
    
        for i in range(8):
            ker = self.rotate_img(kernel_Ref, i * 180 / dirNum)
            spn[i]= cv2.filter2D(Cs[i], -1, ker)
    
        sp = np.sum(spn, axis = 0)
        sp =  (sp - np.min(sp)) / (np.max(sp) - np.min(sp))
        S = 1 -  sp
    
        return S
    
    def scatter(self,img):
        dst = np.zeros_like(img)
    
        rows,cols = img.shape
        offsets = 1
        
        for y in range(rows - offsets):
            for x in range(cols - offsets):
                random_num = np.random.randint(0,offsets)
                dst[y,x] = img[y + random_num,x + random_num]
        return dst
    
    def skyRegion(self,img):
        iLow = np.array([100,43,46])
        iHigh = np.array([124,255,255])
        #imgOriginal = cv2.imread(picname)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        h,s,v = cv2.split(img)
        v = cv2.equalizeHist(v)
        hsv = cv2.merge((h,s,v))
        
        imgThresholded = cv2.inRange(hsv,iLow,iHigh)
        
        imgThresholded = cv2.medianBlur(imgThresholded,9)
        
        kernel = np.ones((5,5),np.uint8)
        imgThresholded = cv2.morphologyEx(imgThresholded,cv2.MORPH_OPEN,kernel,iterations=10)
        imgThresholded = cv2.medianBlur(imgThresholded,9)
        tmp = './tmp/ink-mask.jpg'
        #print(tmp)
        cv2.imwrite(tmp,imgThresholded)
        return imgThresholded
    
    def seamClone(self,skyname,picname,maskname):
        src = skyname.astype(np.uint8)
        dst = picname.astype(np.uint8)
        src_mask = maskname.astype(np.uint8)
        src_mask0 = cv2.merge([maskname,maskname,maskname])
    
        contours = cv2.findContours(src_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        
        x,y,w,h = cv2.boundingRect(cnt)
        #print(x,y,w,h)
        if w==0 or h==0:
            return dst
        dst_x = len(dst[0])
        dst_y = len(dst[1])
        src_x = len(src[0])
        src_y = len(src[1])
        scale_x = w*1.0/src_x
        src = cv2.resize(src,(dst.shape[1],dst.shape[0]),interpolation=cv2.INTER_CUBIC)
        #src = cv2.resize(src,(w,h),interpolation=cv2.INTER_CUBIC)
        #cv2.imwrite('src_sky.jpg',src)
        center = ((2*x+w)//2,(2*y+h)//2)
        #print(center)
        
        output = cv2.seamlessClone(src, dst, src_mask0, center, cv2.NORMAL_CLONE)
        
        return output
    
    def ink(self,img):
        img = cv2.pyrMeanShiftFiltering(img,15,30)
        h,w = img.shape[0],img.shape[1]
        img = cv2.resize(img,(512,512))
        mask = self.skyRegion(img)
        sky = np.ones((img.shape[0],img.shape[1],3))*255
        img = self.seamClone(sky,img,mask)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        '''
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if mask[i,j]:
                    img[i,j] = mask[i,j].astype(np.uint8)
        '''
        #img = Gaussian(img,15,1)
        nhm_img = self.natural_histogram_matching(img)
        cv2.imwrite('./tmp/ink_nhm.jpg',nhm_img*255)
        S = self.get_stroke(img, 2, 8)
        cv2.imwrite('./tmp/ink_s.jpg',S*255)
        nhm_stroke = self.natural_histogram_matching((S*255).astype(np.uint8))
        cv2.imwrite('./tmp/ink_nhm_str.jpg',nhm_stroke*255)
        
        img1 = self.Gaussian(nhm_img,10,1)
        cv2.imwrite('./tmp/ink_nhm_Gaus.jpg',img1*255)
        img2 = self.Gaussian(nhm_stroke,10,1)
        cv2.imwrite('./tmp/ink_nhm_str_Gaus.jpg',img2*255)
        img4 = img/255
        #img4 = scatter(img4)
        
        res = np.minimum(img1,img2)
        res = np.maximum(res,img4)
        #res = 0.7*res+0.3*img3
        #res = np.power(res,1/1.2)
        res = 0.7*res+0.3*img1
        res = cv2.resize(res,(w,h))
        #res = Gaussian(res,10,1)
        #print(res.shape)
        img = cv2.cvtColor((res*255).astype(np.uint8),cv2.COLOR_GRAY2BGR)
        h,w = img.shape[0],img.shape[1]
        img1 = cv2.resize(img,(512,512))
        dst=cv2.pyrMeanShiftFiltering(img,15,30)
        cv2.imwrite('./tmp/int_shift.jpg',dst)
        Gaus = self.Gaussian(dst,10,1)
        cd = Mixed.ColorDodge(Gaus,dst)
        cv2.imwrite('./tmp/int_CD.jpg',cd)
        cd = cv2.addWeighted(dst,0.3,cd,0.7,0)
        cdg = cv2.cvtColor(cd,cv2.COLOR_BGR2GRAY)
        img2 = cv2.imread('./tmp/ink_nhm.jpg')
        img2 = (img2/255)**2 * 255
        tmp = cv2.resize(cd,(512,512))
        dst = Mixed.Overlay(img2,tmp)
        dst = cv2.resize(dst,(w,h))
        dst = cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY)
        dst = 0.7*cdg + 0.3*dst
        dst = cv2.merge([dst,dst,dst])
        return dst.astype(np.uint8)

if __name__ == '__main__':
    img = cv2.imread('../../samples/26.jpg')
    ink = Ink()
    cv2.imwrite('../../tmp/ink.jpg',ink.ink(img))