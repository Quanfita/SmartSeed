import os
import tensorflow as tf
from PIL import Image
import numpy as np
import time
import util
import cv2
from skimage.measure import compare_ssim as ssim

def test_only(args, ele, model, sess, saver):
    
    saver.restore(sess,args.pre_trained_model)
    print("saved model is loaded for test only!")
    print("model path is %s"%args.pre_trained_model)

    blur = np.expand_dims(ele, axis = 0)
    output = sess.run(model.output, feed_dict = {model.blur : blur})
    cv2.imwrite('res.jpg',output[0].astype(np.uint8))
    #output = Image.fromarray(output[0])

    #output.save('res.jpg')
