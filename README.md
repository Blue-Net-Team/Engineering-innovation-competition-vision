# 2025年全国大学生工程实践与创新能力大赛（工创）--视觉识别部分

本代码是该比赛智慧物流搬运赛道的视觉识别部分，该方案
- 将色相重构，使用中心点色相和容差的方式识别色相，然后轻微对饱和度和亮度进行调整，基本可以保证参数的鲁棒性。
- 不再提供圆环的定位，而是使用圆环旁边的T型路口的直角进行定位，全场的定位可以完全依赖这个。
- 函数设计上，将所有的顶层需求都使用固定参数传入，固定类型传出，从而实现顶层的多态，底层的单一职责，这样可以保证代码的可维护性和可扩展性。

## 泰山派的环境配置

### 系统烧录
参考嘉立创官方，烧录提供的Ubuntu固件（镜像）。

[泰山派系统烧录](https://wiki.lckfb.com/zh-hans/tspi-rk3566/system-usage/img-download.html#loader%E5%8D%87%E7%BA%A7%E6%A8%A1%E5%BC%8F)

### ADB的使用

完成了系统烧录，应该也知道了loader和adb模式，直接用typeC将泰山派连接到电脑，连接后直接用adb连接

```shell
adb shell su lckfb
```

后面的`su lckfb`是以lckfb的身份登录，如果不用，就是以root的身份登录

### wifi连接

使用命令`nmcli`连接wifi

```bash
nmcli device wifi connect "wifi名" password "密码"
```

使用`ifconfig`查看ip地址

其中，wlan0是无线网卡，eth0是有线网卡，没有使用底部扩展板是没有eth0的。此外，lo是本地回环接口，不用管。

### apt更新

板子默认使用了清华源，**一般来说是不用改的**，但是如果遇到无法使用，可以换成阿里源。使用编辑器编辑`/etc/apt/sources.list`文件，将清华源注释掉，加入阿里源。如果是**adb只能使用vim**，要使用nano需要配置好ssh，并且额外安装。

```bash
# 默认注释了源码仓库，如有需要可自行取消注释
deb http://mirrors.aliyun.com/ubuntu-ports/ focal main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu-ports/ focal-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu-ports/ focal-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu-ports/ focal-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-backports main restricted universe multiverse

# 预发布软件源，不建议启用
# deb http://mirrors.aliyun.com/ubuntu-ports/ focal-proposed main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-proposed main restricted universe multiverse
```

然后使用`apt update`更新源

在使用`apt upgrade`升级软件的时候会提示有217个软件包保持了原来的版本(hold back)，是因为嘉立创的系统将这些软件进行了锁定，不允许升级，如果需要升级，可以使用`apt-mark unhold`命令解锁。**这一步也可以不做**，因为这些软件的版本是没有问题的。

```bash
sudo apt-mark unhold accountsservice apparmor base-files bind9-host bind9-libs bluez bluez-cups bluez-obexd bsdutils bubblewrap ca-certificates cpp-9 cups cups-browsed cups-bsd cups-client cups-common cups-core-drivers cups-daemon cups-filters cups-filters-core-drivers cups-ipp-utils cups-ppdc cups-server-common distro-info-data dns-root-data dnsmasq-base e2fsprogs fdisk ffmpeg fonts-opensymbol gcc-9-base ghostscript ghostscript-x gir1.2-accountsservice-1.0 gir1.2-gdkpixbuf-2.0 gir1.2-gtk-3.0 gir1.2-nm-1.0 gir1.2-soup-2.4 gir1.2-vte-2.91 gnome-control-center gnome-control-center-data gnome-control-center-faces gnome-shell gnome-shell-common gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-good gstreamer1.0-pulseaudio gstreamer1.0-tools gstreamer1.0-x gtk-update-icon-cache gtk2-engines-pixbuf hplip hplip-data krb5-locales libaccountsservice0 libapparmor1 libarchive13 libavcodec-dev libavcodec58 libavdevice-dev libavdevice58 libavfilter-dev libavfilter7 libavformat-dev libavformat58 libavresample-dev libavresample4 libavutil-dev libavutil56 libblkid1 libbluetooth3 libc-bin libc6 libcdio18 libcom-err2 libcups2 libcupsfilters1 libcupsimage2 libcurl3-gnutls libde265-0 libdvbv5-0 libexpat1 libext2fs2 libfdisk1 libfontembed1 libgail-common libgail18 libgd3 libgdk-pixbuf2.0-0 libgdk-pixbuf2.0-bin libgdk-pixbuf2.0-common libglib2.0-0 libglib2.0-bin libglib2.0-data libgnutls30 libgs9 libgs9-common libgssapi-krb5-2 libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 libgstreamer1.0-0 libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk2.0-0 libgtk2.0-bin libgtk2.0-common libharfbuzz-icu0 libharfbuzz0b libhpmud0 libk5crypto3 libkrb5-3 libkrb5support0 libldap-2.4-2 libldap-common libmount1 libmpg123-0 libmpv1 libmysqlclient21 libndp0 libnghttp2-14 libnm0 libnspr4 libnss-systemd libnss3 libopenjp2-7 liborc-0.4-0 libpam-modules libpam-modules-bin libpam-runtime libpam-s
```

解锁后再次使用`apt upgrade`升级软件

如果这一步没有做的话，后续使用apt安装的时候使用 `--allow-change-held-packages`参数。

### 安装必要的软件包

安装gcc的原因是luma.oled库依赖于RPi.GPIO库，这个需要gcc编译，所以需要安装gcc。

```bash
# --allow-change-held-packages是没有解锁软件包的时候使用的参数
sudo apt install git nano openssh-server openssh-client gcc g++ cmake make -y # --allow-change-held-packages
```

**安装openssh-server、openssh-client之前需要使用adb连接泰山派**

### 使用sd卡，扩展根目录

sd卡速度慢的话无法把miniconda装进去，这边指定使用[闪迪32G V30红黑卡](https://item.taobao.com/item.htm?id=853736888042&pisk=gxQb1ST9cxDj1ODli-FyNJkUK6T6lOaUWfOOt13q6ELvfVCVdCuwboAs5L1LiKrgmOs5BTx2Hd-w5C6eEsuaisP_51CpHFS23CBPCTmV3NJNUP1hdnuV6Nlcq95KuZrD7VTDSFeULyzUisYMWNPaABHm2IAY7V39BEY-LKG4vyzFi_G2MW588ZWBzAOnXVB9D3nJsLdxkVdTN3de6F3vXqn-eLA9WFKtWbCJ1IOxHd3YNbdesx3v6Vh-wCAp6FLOB3FWsvVgFQqXHsNxJh4FrcThMLgtWZUMcpGkeQAPPatvpn9oW_7WGn9dMZPM-cRRzate4frHy6jPHQTQzmLdNGBCvOqEqE1ODOx5n8mWUgQc6dKj6215OsIpyNPtt36J1HL9Vf3ONEv1dZTLJYOl2sSOotGsWIbV8h9HV53MbUQevMBjsWfJkCBMxNynoKCOtwjeRzovJ_sOdGszb2JBGbisNH06NpP7NcmGzvn16eRV2nxvZQ7UN7MjjndkNp7aN0iMDQAyY7NShcf..&spm=tbpc.boughtlist.suborder_itemtitle.1.16822e8doOytxb&skuId=5654524389321)

插入卡后，使用`dmesg | grep mmc`查看系统日志中包含`mmc`的信息，找到对应的设备名，会找到类似于`mmcblk1`的设备名，这个就是sd卡的设备名。使用`lsblk`可以查看这个sd卡下有没有分区，如果类似于以下情况，说明没有分区。

```bash
mmcblk1     179:0    0  29.7G  0 disk
```

如果是以下情况，说明有分区

```bash
mmcblk1     179:0    0  29.7G  0 disk
└─mmcblk1p1 179:1    0  29.7G  0 part
```

如果没有分区需要创建分区，使用`fdisk`命令，输入`n`，然后输入`p`，然后输入`1`，然后两次回车，最后输入`w`保存。

fdisk是一个交互式的命令行工具，所以需要输入`fdisk /dev/mmcblk1`进入交互模式。

```bash
sudo fdisk /dev/mmcblk1
```

- 输入n：新建分区
- 输入p：新建主分区(primary)
- 输入1：分区号
- 两次回车：默认起始扇区和结束扇区
- w：保存。

然后使用`lsblk`查看分区是否创建成功。

```bash
mmcblk1     179:0    0  29.7G  0 disk
└─mmcblk1p1 179:1    0  29.7G  0 part
```

然后需要格式化分区，使用`mkfs.ntfs`命令，将sd卡格式化为ntfs格式。

```bash
sudo mkfs.ntfs /dev/mmcblk1p1
```

等待完成，然后将sd卡挂在到泰山派上。

创建`/media/sdcard`文件夹，使用mkdir命令创建。

```bash
sudo mkdir /media/sdcard
```

使用`mount`命令挂载。

```bash
sudo mount /dev/mmcblk1p1 /media/sdcard
```

但是这个方法并不会开机自动挂载，需要将挂载信息写入`/etc/fstab`文件中。

1. 方法1 可以使用编辑器
    ```bash
    sudo nano /etc/fstab
    ```

    然后再文件末尾添加以下内容。

    ```bash
    /dev/mmcblk1p1 /media/sdcard auto defaults,uid=1000,gid=1000 0 0
    ```

2. 方法2 可以使用echo

    ```bash
    sudo echo "/dev/mmcblk1p1 /media/sdcard auto defaults,uid=1000,gid=1000 0 0" >> /etc/fstab
    ```

修改了`/etc/fstab`文件之后，使用`mount -a`命令重新挂载。

```bash
sudo mount -a
```

### 安装miniconda3

可以先下载了安装包后使用sftp将文件传到泰山派（需要ssh），也可以直接下载

使用`wget`命令下载安装包

```bash
# 创建Downloads文件夹，并且将安装包放在里面
mkdir Downloads && cd Downloads
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
```

下载完成后，运行安装脚本

```bash
# -p后面的参数是安装目录
bash Miniconda3-latest-Linux-aarch64.sh -b -p /media/sdcard/miniconda3
```

完成安装之后，要对conda进行初始化

```bash
/media/sdcard/miniconda3 init
source ~/.bashrc
```

建议关掉自动base环境激活

```bash
conda config --set auto_activate_base false
```

然后修改全局pip源，这边采用阿里源

```bash
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

### 自启动的脚本

**下面的内容需要创建了gpio组，并且将当前用户(这里是`lckfb`)添加到gpio组中在运行**

```bash
sudo groupadd gpio
sudo usermod -a -G gpio $USER
```

可以使用`groups`命令查看当前用户所在的用户组，**确保当前用户在`gpio`用户组中**

环境配置的时候我提供了一个开机自动配置GPIO的脚本，用于修改GPIO芯片的权限，位于目录`run_auto`下，里面的`gpio-setup.service`需要复制到`/etc/systemd/system/`下，然后使用`systemctl enable gpio-setup.service`命令开机自启动。

```bash
# 确保脚本有执行权限
sudo chmod +x run_auto/gpio-setup.sh
# 复制服务文件到systemd目录
sudo cp run_auto/gpio-setup.service /etc/systemd/system/
# 修改权限
sudo chmod 644 /etc/systemd/system/gpio-setup.service
# 重新加载服务
sudo systemctl daemon-reload
# 开机自启动
sudo systemctl enable gpio-setup.service
# 启动服务
sudo systemctl start gpio-setup.service
# 检查服务状态
sudo systemctl status gpio-setup.service
```

**`gpio-setup.service`里面的`ExecStart`需要修改到`run_auto`文件夹下`gpio-setup.sh`文件的绝对路径**

## 项目结构

下面不会在讲到非必要文件，例如.gitignore，LICENSE等文件

```
detector
    |___ __init__.py        检测器的初始化文件
    |___ Detector.py        检测器的基类
    |___ LineDetector.py    直线检测器
    |___ CircleDetector.py  圆环检测器
    |___ ColorDetector.py   颜色检测器
utils                       用于存放工具代码的文件夹
    |___ __init__.py        工具代码的初始化文件
    |___ _cap.py            关于摄像头的代码
    |___ typingCheck.py     用于检查函数的的形参和实参是否匹配
    |___ UART.py            串口通信的代码
    |___ ImgTrans.py        用于远程图传的代码
    |___ gpio.py            有关于GPIO的代码，主要是开关,LED,OLED的抽象
    |___ tspi_boaed_info.py 用于获取泰山派的信息
    |___ wifi_connect.py    用于连接wifi的代码

AdjustConfig.py             用于调整配置的调试代码
Solution.py                 用于存放解决方案的代码，包括颜色识别，圆环识别，直线识别以及串口等使用的函数
test_Solution.py            用于测试Solution或者detector的功能
img_trans.py                用于远程图传的代码，主要用于调试过程方便在电脑上得到图像
main.py                     主程序，直接在Jetson或者树莓派上运行的代码
requirements.txt            依赖的库,可以使用pip install -r requirements.txt一键安装依赖
config.json                 用于存放参数的文件
environment.sh              用于一键配置泰山派环境的脚本，还没用过，不建议使用，可以参考里面的内容，手动配置
```

## 当前电控可以直接调用的接口

即返回值封装成了字符，可以直接串口进行发送返回值

- 物料的运动检测，即物料所在位号发生变化认为物料运动

```
"1" 代表物料运动
```

- 获取物料位置，返回位号

```
"R1G2B3"代表红色在1号位，绿色在2号位，蓝色在3号位
如果有物料没识别到位号（可能被夹走），对应的数字变为0
```

- 直角(圆环)检测

```
返回角度大于0的直线(参与直角的组成)角度和直角的交点坐标

str的结果会表示为
    'LHXXXxxxyyy'，
        其中：
        * L(location),表示定位
        * XXX是角度的十倍(如果是圆环，此处为000)
        * H代表正负号（0和1）(如果是圆环，此处为000)
        * xxx和yyy代表交点的坐标
```

## 完成的功能

即返回值没有进行封装，只是方便其他方法的使用，不能使用串口直接发送

- 物料追踪

## 外部调节的参数(config.json)

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

### 颜色阈值

该参数尽量固定

```json
{
    "color": {
        "R": {
            "centre": 0,
            "error": 17,
            "L_S": 60,
            "U_S": 255,
            "L_V": 30,
            "U_V": 255
        },
        "G": {
            "centre": 65,
            "error": 21,
            "L_S": 25,
            "U_S": 255,
            "L_V": 31,
            "U_V": 255
        },
        "B": {
            "centre": 109,
            "error": 17,
            "L_S": 60,
            "U_S": 255,
            "L_V": 30,
            "U_V": 255
        }
    },
    "min_material_area": 2000,
    "max_material_area": 40000,
}
```

### 目标角度

该参数尽量固定

```json
{
    "target_angle": 46
}
```

## 调参(AdjustConfig.py)

该文件末尾已经封装了需要调整的参数的对应函数，需要向内传入一个摄像头或者图传接收器，此处的图传接收器与OpenCV摄像头形成多态。

在图传接收器中，将ip地址改为树莓派的ip地址，端口号改为图传的端口号，即可在电脑上调整参数。**但是需要先在树莓派上运行图传文件**

完成本地调参之后，将`config.json`文件复制到树莓派上。

## 测试(test_Solution.py)

在测试文件中，主要用于测试顶层需求，类`TestSolution`继承了`Solution`类，然后在`TestSolution`中实现了`test`函数，该函数中手动传入电控发送的信号，然后调用`Solution`中的函数，最后将返回值打印出来。

同时也提供了串口测试，物料追踪的测试

## 远程图传(img_trans.py)

在树莓派和本地电脑的文件是不同的，对应不同的仓库分支，分支`developing`是本地电脑的开发版本，分支`master`是树莓派的正式版本。

在树莓派的版本中，所有图传都是向外发送;在本地版本中，所有图传都是接收。

**所有图传都要树莓派(服务端)先运行**，然后本地电脑(客户端)再运行，否则会出现`地址已被占用`的错误。如果已经排除了这个问题仍然出现这个错误，检查ip是否是**服务端的ip**，端口号在**两端中是否一致**。
