# SmartSeed

This is an open source image editing software modeled after Adobe Photoshop.  I hope that I can use as many AI algorithms as possible to make it feature rich. Currently, this project is still in production, so stay tuned.

## Environment

- Python 3.6
- PyQt 5.9
- OpenCV 3.4
- TensorFlow CPU/GPU 1.4
- Keras 2.1

## Progress

### v 1.0

Currently, the functions that have been implemented are as follows:

- New artboard
- Open picture
- Save picture
- Pencil tool
- Straight line tool
- 10 filters
- Automatic white balance

### v 1.1

Fix some bugs, add new features:

- Blurry filters
- Sharp filters
- Undo & Redo
- Some other filters
- Rectangle tool
- Ellipse tool
- Layer structure

### v 1.2

fix the bug of Layer structure, add new features:

- Canvas size
- Image size

## Usage

### Use shell

#### 1. Clone and Download

```shell
git clone https://github.com/Quanfita/SmartSeed.git
cd SmartSeed/
```

#### 2. Environment Configure

```shell
pip install -r requirements.txt
```

#### 3. Get Start

```shell
python main.py
```

### Executable file

We will provide executable file in the future, please wait.

## Pre-trained model

The Pre-trained models is uploaded to [Google Drive](https://drive.google.com/open?id=1IIernzA0viaP3rJmZCB4uO7QF077aUk0) in the future.

## Reference

[1] [Style2Paints](https://github.com/lllyasviel/style2paints)

[2] [DeblurGAN-tf](https://github.com/dongheehand/DeblurGAN-tf)