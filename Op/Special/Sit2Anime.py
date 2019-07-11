# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 09:53:20 2019

@author: Quanfita
"""
import os
import cv2
import numpy as np
import logger

class Sit2Anime(object):
    def __init__(self,tablepath):
        #tablepath=os.path.dirname(os.path.abspath(__file__))
        self.local = cv2.imread(tablepath+'/lookup-table.png')
        self.transport = cv2.imread(tablepath+'/lookup-table_tmp1.jpg')
        self.lambda_res()

    def skyRegion(self,picname):
        iLow = np.array([100,43,46])
        iHigh = np.array([124,255,255])
        img = picname#cv2.imread(picname)
        #imgOriginal = picname#cv2.imread(picname)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        h,s,v = cv2.split(img)
        v = cv2.equalizeHist(v)
        hsv = cv2.merge((h,s,v))
        
        imgThresholded = cv2.inRange(hsv,iLow,iHigh)
        
        imgThresholded = cv2.medianBlur(imgThresholded,9)
        
        kernel = np.ones((5,5),np.uint8)
        imgThresholded = cv2.morphologyEx(imgThresholded,cv2.MORPH_OPEN,kernel,iterations=10)
        imgThresholded = cv2.medianBlur(imgThresholded,9)
        return imgThresholded
    
    def seamClone(self,skyname,picname,maskname):
        src = skyname#cv2.imread(skyname)
        dst = picname#cv2.imread(picname)
        
        src_mask = maskname#cv2.imread(maskname,0)
        src_mask0 = cv2.cvtColor(maskname,cv2.COLOR_GRAY2BGR)#cv2.imread(maskname)
        contours = cv2.findContours(src_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        
        x,y,w,h = cv2.boundingRect(cnt)
        if w==0 or h==0:
            return dst
        #dst_x = len(dst[0])
        #dst_y = len(dst[1])
        #src_x = len(src[0])
        #src_y = len(src[1])
        #scale_x = w*1.0/src_x
        src = cv2.resize(src,(dst.shape[1],dst.shape[0]),interpolation=cv2.INTER_CUBIC)
    
        center = ((2*x+w)//2,(2*y+h)//2)
        output = cv2.seamlessClone(src, dst, src_mask0, center, cv2.MIXED_CLONE)
        
        return output
    
    def shift(self,image):
        dst=cv2.pyrMeanShiftFiltering(image,10,30);
        return dst
    
    def custom_blur(self,image):
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32) #锐化
        dst = cv2.filter2D(image, -1, kernel=kernel)
        return dst
    
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

    def lambda_res(self):
        self.x = np.zeros((256,256),dtype=np.int32)
        self.y = np.zeros((256,256),dtype=np.int32)
        a = lambda x,y : y //4 + (x // 32)*64
        b = lambda x,z : z // 4 + ((x % 32) // 4)*64
        for i in range(256):
            for j in range(256):
                self.x[i,j] = a(i,j)
                self.y[i,j] = b(i,j)
    '''
    def myFilter(self,orimap,newmap,picname):
        ori = orimap#cv2.imread(orimap)
        new = newmap#cv2.imread(newmap)
        my = picname#cv2.imread(picname)
        for i in range(len(my)):
            for j in range(len(my[0])):
                pos = self.findPos(my[i][j],ori)
                my[i][j] = new[pos[0],pos[1]]
        return my
    '''

    def myFilter(self,orimap,newmap,picname):
        ori = orimap#cv2.imread(orimap)
        new = newmap#cv2.imread(newmap)
        my = picname#cv2.imread(picname)
        #z,y,x = my[:,:,0],my[:,:,1],my[:,:,2]
        #a = y // 4 + (x // 32)*64
        #b = z // 4 + ((x % 32) // 4)*64
        for i in range(len(my)):
            for j in range(len(my[0])):
                my[i,j] = new[self.x[my[i,j,0],my[i,j,1]],self.y[my[i,j,0],my[i,j,2]]]
                #my[i,j] = new[b[i,j],a[i,j]]
                #my[i][j] = new[self.findPos(my[i][j],ori)]
        return my

    def oilPainting(self,img, templateSize, bucketSize, step):#templateSize模板大小,bucketSize桶阵列,step模板滑动步长
     
        gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        gray = ((gray/256)*bucketSize).astype(int)                          #灰度图在桶中的所属分区
        h,w = img.shape[:2]
         
        oilImg = np.zeros(img.shape, np.uint8)                              #用来存放过滤图像
         
        for i in range(0,h,step):
            
            top = i-templateSize
            bottom = i+templateSize+1
            if top < 0:
                top = 0
            if bottom >= h:
                bottom = h-1
                
            for j in range(0,w,step):
                
                left = j-templateSize
                right = j+templateSize+1
                if left < 0:
                    left = 0
                if right >= w:
                    right = w-1
                    
                # 灰度等级统计
                buckets = np.zeros(bucketSize,np.uint8)                     #桶阵列，统计在各个桶中的灰度个数
                bucketsMean = [0,0,0]                                       #对像素最多的桶，求其桶中所有像素的三通道颜色均值
                #对模板进行遍历
                for c in range(top,bottom):
                    for r in range(left,right):
                        buckets[gray[c,r]] += 1                         #模板内的像素依次投入到相应的桶中，有点像灰度直方图
        
                maxBucket = np.max(buckets)                                 #找出像素最多的桶以及它的索引
                maxBucketIndex = np.argmax(buckets)
                
                for c in range(top,bottom):
                    for r in range(left,right):
                        if gray[c,r] == maxBucketIndex:
                            bucketsMean += img[c,r]
                bucketsMean = (bucketsMean/maxBucket).astype(int)           #三通道颜色均值
                
                # 油画图
                for m in range(step):
                    for n in range(step):
                        oilImg[m+i,n+j] = (bucketsMean[0],bucketsMean[1],bucketsMean[2])
        return  oilImg
    
    def DoProcess(self,img):
        #local = cv2.imread(tablepath+'/lookup-table.png')
        #transport = cv2.imread(tablepath+'/lookup-table_tmp1.jpg')
        logger.info("Start processing...")
        dst = self.shift(img)
        #oil = self.oilPainting(img,1,8,1)
        #dst = (0.4*oil + 0.6*dst).astype(np.uint8)
        #logger.info("Processing Sky Region.")
        #mask = self.skyRegion(dst)
        #clone = self.seamClone(sky,dst,mask)
        logger.info('Doing Filter.')
        res = self.myFilter(self.local,self.transport,dst)
        #cv2.imwrite(outputname,res)
        logger.info('Successful!')
        return res

if __name__ == '__main__':
    #main('./street/33.jpg','1.jpg','anime.jpg')
    app = Sit2Anime()
    app.DoProcess('../../samples/26.jpg','../../samples/2.jpg','../../tmp/anime.jpg')