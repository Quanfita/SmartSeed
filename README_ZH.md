# SmartSeed

这是一个开源的图像处理软件，仿照了Adobe Photoshop的功能及结构特点。我希望可以使用尽可能多的AI算法把它的功能完善。目前，项目还在初步阶段，尽情期待。

## 环境要求

- Python 3.6
- PyQt 5.9
- OpenCV 3.4
- TensorFlow 1.4
- Keras 2.1

## 进展

### v 1.0

下列功能已被完成：

- 新建画板
- 打开图片
- 保存图片
- 铅笔
- 直线
- 10种常规滤镜
- 自动白平衡

### v 1.1

修复之前存在的一些bug，添加新功能：

- 锐化滤镜
- 模糊滤镜
- 撤销与重做操作
- 滤镜库中的一些特殊滤镜
- 矩形工具
- 椭圆工具
- 图层结构

### v 1.2

修复图层上的一些bug，添加新功能：

- 画布大小
- 图像大小

## 使用方法

### 使用命令行打开

#### 1. 下载

```shell
git clone https://github.com/Quanfita/SmartSeed.git
cd SmartSeed
```

#### 2. 依赖库

```shell
pip install -r requirements.txt
```

#### 3. 开始使用

```shell
python main.py
```

### 可执行文件

我们之后将在Releases中提供Windows版本的可执行文件。

## 预训练模型

使用到深度学习来实现的一些功能已提供，预训练模型已上传到[谷歌云端硬盘](https://drive.google.com/open?id=1IIernzA0viaP3rJmZCB4uO7QF077aUk0)。

## 参考

[1] [Style2Paints](https://github.com/lllyasviel/style2paints)

[2] [DeblurGAN-tf](https://github.com/dongheehand/DeblurGAN-tf)