import tensorflow as tf
import numpy as np
import os


class dataloader():
    
    def __init__(self, args):
        
        self.patch_size = args.patch_size
        self.batch_size = args.batch_size
        self.train_Sharp_path = args.train_Sharp_path
        self.train_Blur_path = args.train_Blur_path
        self.test_Sharp_path = args.test_Sharp_path
        self.test_Blur_path = args.test_Blur_path
        self.test_with_train = args.test_with_train
        self.test_batch = args.test_batch
        self.load_X = args.load_X
        self.load_Y = args.load_Y
        self.augmentation = args.augmentation
        self.channel = args.channel
        
    def build_loader(self):
            
        blur_imgs = sorted(os.listdir(self.test_Blur_path))
        blur_imgs = [os.path.join(self.test_Blur_path, ele) for ele in blur_imgs]
            
        self.te_dataset = tf.data.Dataset.from_tensor_slices(blur_imgs)
        self.te_dataset = self.te_dataset.map(self._parse_Blur_only, num_parallel_calls = 4).prefetch(32)
        self.te_dataset = self.te_dataset.batch(1)
            
        iterator = tf.data.Iterator.from_structure(self.te_dataset.output_types, self.te_dataset.output_shapes)
        self.next_batch = iterator.get_next()
        self.init_op = {}
        self.init_op['te_init'] = iterator.make_initializer(self.te_dataset)
            
            
    def _parse(self, image_blur, image_sharp):
        
        image_blur = tf.read_file(image_blur)
        image_sharp = tf.read_file(image_sharp)
        
        image_blur = tf.image.decode_png(image_blur, channels = self.channel)
        image_sharp = tf.image.decode_png(image_sharp, channels = self.channel)
        
        image_blur = tf.cast(image_blur, tf.float32)
        image_sharp = tf.cast(image_sharp, tf.float32)
        
        return image_blur, image_sharp
    
    def _resize(self, image_blur, image_sharp):
        
        image_blur = tf.image.resize_images(image_blur, (self.load_Y, self.load_X), tf.image.ResizeMethod.BICUBIC)
        image_sharp = tf.image.resize_images(image_sharp, (self.load_Y, self.load_X), tf.image.ResizeMethod.BICUBIC)
        
        return image_blur, image_sharp
    
    
    def _parse_Blur_only(self, image_blur):
        
        image_blur = tf.read_file(image_blur)
        image_blur = tf.image.decode_image(image_blur, channels = self.channel)
        image_blur = tf.cast(image_blur, tf.float32)
        
        return image_blur
        
    def _get_patch(self, image_blur, image_sharp):
        
        shape = tf.shape(image_blur)
        ih = shape[0]
        iw = shape[1]
        
        ix = tf.random_uniform(shape = [1], minval = 0, maxval = iw - self.patch_size + 1, dtype = tf.int32)[0]
        iy = tf.random_uniform(shape = [1], minval = 0, maxval = ih - self.patch_size + 1, dtype = tf.int32)[0]
        
        img_sharp_in = image_sharp[iy:iy + self.patch_size, ix:ix + self.patch_size]        
        img_blur_in = image_blur[iy:iy + self.patch_size, ix:ix + self.patch_size]
        
        return img_blur_in, img_sharp_in
    
    def _data_augmentation(self, image_blur, image_sharp):
        
        rot = tf.random_uniform(shape = [1], minval = 0, maxval = 3, dtype = tf.int32)[0]
        flip_rl = tf.random_uniform(shape = [1], minval = 0, maxval = 3, dtype = tf.int32)[0]
        flip_updown = tf.random_uniform(shape = [1], minval = 0, maxval = 3, dtype = tf.int32)[0]
        
        image_blur = tf.image.rot90(image_blur, rot)
        image_sharp = tf.image.rot90(image_sharp, rot)
        
        rl = tf.equal(tf.mod(flip_rl, 2),0)
        ud = tf.equal(tf.mod(flip_updown, 2),0)
        
        image_blur = tf.cond(rl, true_fn = lambda : tf.image.flip_left_right(image_blur), false_fn = lambda : (image_blur))
        image_sharp = tf.cond(rl, true_fn = lambda : tf.image.flip_left_right(image_sharp), false_fn = lambda : (image_sharp))
        
        image_blur = tf.cond(ud, true_fn = lambda : tf.image.flip_up_down(image_blur), false_fn = lambda : (image_blur))
        image_sharp = tf.cond(ud, true_fn = lambda : tf.image.flip_up_down(image_sharp), false_fn = lambda : (image_sharp))
        
        return image_blur, image_sharp

