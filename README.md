# 2025年全国大学生工程实践与创新能力大赛（工创）---深度学习方案

本代码是该比赛智慧物流搬运赛道的视觉识别部分，该方案采用深度学习的方式进行颜色识别，对于圆环和直线的识别仍然采用传统的图像处理方法。

## 项目结构

下面不会在讲到非必要文件，例如.gitignore，LICENSE等文件

```
USART                       用于存放有关串口通信代码的包文件夹
    |___ __init__.py        串口通信代码的初始化文件
    |___ communicate.py     串口通信代码
detector
    |___ model              用于存放深度学习模型的文件夹
        |___ __init__.py    深度学习模型的初始化文件
        |___ cnn.py         深度学习模型
    |___ __init__.py        检测器的初始化文件
    |___ Detector.py        检测器的基类
    |___ LineDetector.py    直线检测器
    |___ CircleDetector.py  圆环检测器
    |___ ColorDetector.py   颜色检测器
utils                       用于存放工具代码的文件夹
    |___ __init__.py        工具代码的初始化文件
    |___ dataset.py         数据集类以及有关数据集的工具代码
AdjustConfig.py             用于调整配置的调试代码
Solution.py                 用于存放解决方案的代码，包括颜色识别，圆环识别，直线识别以及串口等使用的函数
test_Solution.py            用于测试Solution或者detector的功能
img_trans.py                用于远程图传的代码，主要用于调试过程方便在电脑上得到图像
main.py                     主程序，直接在Jetson或者树莓派上运行的代码
pth2onnx.py                 将pytorch模型转换为onnx模型的代码
train.py                    训练模型的代码
```

## 识别思路

对于物料的颜色识别，深度学习的模型是使用20x20的图像进行训练的，是一个纯CNN的分类网络。所以识别的时候需要有一个20x20的ROI区域，Debug文件就是用来确定这个ROI区域的。但是我们还需要对物料进行追踪，这种方案就不太可行。
所以我们使用圆环识别和深度学习结合的方式，现使用圆形识别确定物料的位置，然后在物料的位置上进行颜色识别。

对于圆环识别，我们使用的是霍夫变换，将识别到的圆环使用掩膜提取原图信息，进行重排序，在放进CNN颜色识别器进行颜色识别（正在开发）

对于直线识别，我们使用的是canny算子和霍夫直线。

## 备选方案

在颜色识别器文件中新增了传统颜色识别方案，使用中央阈值和容差的方式进行识别，可以修正红色色相的损失

为了能够快速调参，在树莓派或者Jetson上使用旋转编码器进行调整，同时使用应该开关切换调试模式，以及一个OLED显示状态和相关参数

## 当前电控可以直接调用的接口

即返回值封装成了字符，可以直接串口进行发送返回值

- 识别转盘中心坐标，xy各4位，01代表正负

```
"13320094" 代表偏差(332,-94)
```

- 地面圆环的矫正

```
"RFFFFFFFFG00421432B13450002"代表红色未检测到，绿色偏差-42,432，蓝色偏差345,2
```

- 物料的运动检测，即物料所在位号发生变化认为物料运动

```
"1" 代表物料运动
```

- 获取物料位置，返回位号

```
"R1G2B3"代表红色在1号位，绿色在2号位，蓝色在3号位
```

## 完成的功能

即返回值没有进行封装，只是方便其他方法的使用，不能使用串口直接发送

- 物料追踪
    根据更改solution的`多边形边数参数nums`(在config.json)选择对应的跟踪，默认为0
- 圆环的颜色检测
    可以识别圆环边的颜色
- 直角检测
    TODO:**本方法现在返回角度和交点，需要将其封装为电控可以调用的方法**

## 外部调节的参数(config.json)

### 地面圆环的基准坐标

```json
{
    ...
    "annulus_point": {
        "x": 0,
        "y": 0
    }
}
```

### 转盘中心的基准坐标

```json
{
    ...
    "rotator_centre_point":[
        0,  //转盘中心的x坐标
        0   //转盘中心的y坐标
    ]
}
```

### 地面圆环识别参数

该参数尽量固定

```json
{
    ...
    "annulus": {
        "dp": 1,        //累加器分辨率与图像分辨率的反比,值越大，检测时间越短，但是可能会丢失一些小圆
        "minDist": 52,  //两个圆心之间的最小距离
        "param1": 60,   //Canny边缘检测的高阈值
        "param2": 20,   //累加器的阈值,值越大，检测时间越短，但是可能会丢失一些小圆
        "minRadius": 48,    //圆的最小半径
        "maxRadius": 52     //圆的最大半径
    }
}
```

### 物料圆环识别参数

该参数尽量固定

```json
{
    ...
    "material": {
        "dp": 1,        //累加器分辨率与图像分辨率的反比,值越大，检测时间越短，但是可能会丢失一些小圆
        "minDist": 52,  //两个圆心之间的最小距离
        "param1": 60,   //Canny边缘检测的高阈值
        "param2": 20,   //累加器的阈值,值越大，检测时间越短，但是可能会丢失一些小圆
        "minRadius": 48,    //圆的最小半径
        "maxRadius": 52     //圆的最大半径
    }
}
```

### 多边形参数

```json
{
    ...
    "polygon":{
        "nums":3,   //多边形数,0为圆形
        // 下面的参数尽量固定
        "val_min": 50, //Canny边缘检测的低阈值
        "val_max": 150, //Canny边缘检测的高阈值
        "epsilon_factor": 0.02, //多边形近似的精度因子,值越小，近似的多边形越接近原始多边形
    }
}
```

### 直线识别参数

该参数尽量固定

```json
{
    ...
    "LineDetector": {
        "Min_val": 120,         //Canny边缘检测的低阈值
        "Max_val": 255,         //Canny边缘检测的高阈值
        "Hough_threshold": 48,  //霍夫变换的阈值,值越大，检测时间越短，但是可能会丢失一些直线
        "minLineLength": 41,    //线段的最小长度
        "maxLineGap": 49,       //线段之间的最大间隔
        "bias": 3               //允许的角度误差
    }
}
```

### 位号参数

该参数尽量固定

```json
{
    ...
    "area1_points":[
        [0,0],      //左上角
        [0,0]       //右下角
    ],
    "area2_points":[
        [0,0],      //左上角
        [0,0]       //右下角
    ],
    "area3_points":[
        [0,0],      //左上角
        [0,0]       //右下角
    ]
}
```
