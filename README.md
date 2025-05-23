# 2025年全国大学生工程实践与创新能力大赛（工创）--视觉识别部分

## 项目情况

本比赛已经结束，很遗憾这个方案没有进入决赛。我们赛后进行回顾和分析，得到一下结论

1. 指导老师没有买到官方地图，是本方案没能晋级的根本原因。在实验室的地图，中央4个黄色放个有黑色方框，识别直线的难度非常低，然而广工（广东工业大学）现场没有黑色边框，导致识别难度大大加大，再加上赛场灯光的多重阴影，最终定位效果并不如意
2. 本仓库在3月28的最后一次提交是实验室最稳定的版本，没有考虑到任何无线连接的干扰，在main中添加了无线图传，然而在赛场可能存在一些干扰，导致电脑的网卡频繁掉线，导致泰山派的main直接卡死，这个问题导致10分钟的调试时间没有发挥到最好的作用

在赛程一早上的10分钟调试时间，我们发现了实验室的地图与现场不同之后，从12:00开始想出新的识别方案，到13:00现场检录，我们更新了哈希为`37760572`的提交，此前，删除了main中的无线图传，避免卡死。

**值得注意的是，在哈希`37760572`提交之前，直角识别的参数bias工作一直不正常，都是介于还可以使用，在实验室就没有修改。**

接下来，本仓库将详细介绍思路以及相关改进思路；从泰山派的部署，到赛场的临时调试的注意事项，以及后续改比赛的思考。

## 分支说明

1. `master`分支：该分支同步泰山派的代码，与参赛时的代码和参数相同
2. `developing`分支：该分支用于开发新的功能，新的功能开发完成之后在这个分支进行测试，确保分支逻辑没有问题，会合并到`master`分支
3. `dev-329`分支：这个分支是3月29中午添加的分支，用于临时修改直线识别的逻辑和思路，虽然这个功能没有测试直接进行使用，但是可以确定的是，这个逻辑没有问题，。但是定位效果也一般般，也可能是参数调试过于仓促导致，也与底层的设计有关。初赛后曲儿该逻辑没问题后，这个分支也合并到了master分支，但是由于光线和其他问题，初赛后还是对其进行了修改，如果转盘物料转动后有物料没有识别到(包含0在结果中)会对0进行填补，自适应填补没有识别到的颜色；直角识别的角度两帧之间相差超过20°，认为是不应该出现的波动，就不会返回角度而是继续识别。但是这个功能最后没有在赛场进行 验证，也不知道其可行性。

## 项目简介

本代码是该比赛智慧物流搬运赛道的视觉识别部分，该方案

- 将色相重构，使用中心点色相和容差的方式识别色相，然后轻微对饱和度和亮度进行调整，基本可以保证参数的鲁棒性。
- 函数设计上，将所有的顶层需求都使用固定参数传入，固定类型传出，从而实现顶层的多态，底层的单一职责，这样可以保证代码的可维护性和可扩展性。

## 设备清单

- [1080p60帧工业高清摄像头 2.6mm无畸变](https://item.taobao.com/item.htm?id=641851678217&pisk=gFtgs9MHfF7_2mGdJHssyYz87i0d6GsX0IEAMiCq865IhPUtCZW2nIxvWK5AmIADi1Qq1GKDtL9xCnH1bmX2wBjvB1CvtxA9hohslGE4iC9r1dCxCnfVtCRclA1AgsAv3FHK20p6CisVmbn-2QOvVQdguZ5q36WlhvBZdFo2zisqwj4L0NilcQiWMK4a895CntPN_IWULtCF3PS2g67FUTFN0IRVYDWfetza7NWUT6680OrVQMzFUOWVQlR2LvXRTsSV7IJEhq0N1n-eYXl3kHXhPqxFINfyQ1J9dHkVWP91t_1JYOvGidub0o-hINxffVYBWNL2Fat9bmqCXLYFYTpsjkjyQTAO9QozxMJpLIQWRjZRRBxcuh7a3v5ejBx1bC34qQjMia-N--rvEd5Nx9-rHz1px1d2jwk8qZIe2aSwJ2GOkGXkghOgnoRypLK1RncuTsTOFMWJCcqh4dWV4jaUz2y_c9kvYraf796hwHaubAGfc33KKv4rhNWCC_HnKzkf796hwvD3zm_NdO1R.&spm=tbpc.boughtlist.suborder_itemtitle.1.5af02e8dEH5Ldl&skuId=4613893837981)
- [嘉立创泰山派RK3566 2+16G版本](https://oshwhub.com/li-chuang-kai-fa-ban/li-chuang-tai-shan-pai-kai-fa-ban)
- [泰山派底部扩展板](https://item.szlcsc.com/44319751.html)
- [闪迪32G V30红黑卡](https://item.taobao.com/item.htm?id=853736888042&pisk=gxQb1ST9cxDj1ODli-FyNJkUK6T6lOaUWfOOt13q6ELvfVCVdCuwboAs5L1LiKrgmOs5BTx2Hd-w5C6eEsuaisP_51CpHFS23CBPCTmV3NJNUP1hdnuV6Nlcq95KuZrD7VTDSFeULyzUisYMWNPaABHm2IAY7V39BEY-LKG4vyzFi_G2MW588ZWBzAOnXVB9D3nJsLdxkVdTN3de6F3vXqn-eLA9WFKtWbCJ1IOxHd3YNbdesx3v6Vh-wCAp6FLOB3FWsvVgFQqXHsNxJh4FrcThMLgtWZUMcpGkeQAPPatvpn9oW_7WGn9dMZPM-cRRzate4frHy6jPHQTQzmLdNGBCvOqEqE1ODOx5n8mWUgQc6dKj6215OsIpyNPtt36J1HL9Vf3ONEv1dZTLJYOl2sSOotGsWIbV8h9HV53MbUQevMBjsWfJkCBMxNynoKCOtwjeRzovJ_sOdGszb2JBGbisNH06NpP7NcmGzvn16eRV2nxvZQ7UN7MjjndkNp7aN0iMDQAyY7NShcf..&spm=tbpc.boughtlist.suborder_itemtitle.1.16822e8doOytxb&skuId=5654524389321)

## 泰山派的环境配置

### 系统烧录

参考嘉立创官方，烧录提供的Ubuntu固件（镜像）。

[泰山派系统烧录](https://wiki.lckfb.com/zh-hans/tspi-rk3566/system-usage/img-download.html#loader%E5%8D%87%E7%BA%A7%E6%A8%A1%E5%BC%8F)

### ADB的使用

完成了系统烧录，应该也知道了loader和adb模式，直接用typeC将泰山派连接到电脑，连接后直接用adb连接

> ADB (Android Debug Brigade)即安卓调试桥，本来是用于进行安卓开发的真机调试工具，但是也可以用在其他的一些Linux开发板中，可以为开发者提供有线的命令行环境

```shell
adb shell su lckfb
```

后面的 `su lckfb`是以lckfb的身份登录，如果不用，就是以root的身份登录

### wifi连接

使用命令 `nmcli`连接wifi

```bash
nmcli device wifi connect "wifi名" password "密码"
```

使用 `ifconfig`查看ip地址

其中，wlan0是无线网卡，eth0是有线网卡，没有使用底部扩展板是没有eth0的。此外，lo是本地回环接口，不用管。

### apt更新

板子默认使用了清华源，**一般来说是不用改的**，但是如果遇到无法使用，可以换成阿里源。使用编辑器编辑 `/etc/apt/sources.list`文件，将清华源注释掉，加入阿里源。如果是**adb只能使用vim**，要使用nano需要配置好ssh，并且额外安装。

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

然后使用 `apt update`更新源

在使用 `apt upgrade`升级软件的时候会提示有217个软件包保持了原来的版本(hold back)，是因为嘉立创的系统将这些软件进行了锁定，不允许升级，如果需要升级，可以使用 `apt-mark unhold`命令解锁。**这一步也可以不做**，因为这些软件的版本是没有问题的。

```bash
sudo apt-mark unhold accountsservice apparmor base-files bind9-host bind9-libs bluez bluez-cups bluez-obexd bsdutils bubblewrap ca-certificates cpp-9 cups cups-browsed cups-bsd cups-client cups-common cups-core-drivers cups-daemon cups-filters cups-filters-core-drivers cups-ipp-utils cups-ppdc cups-server-common distro-info-data dns-root-data dnsmasq-base e2fsprogs fdisk ffmpeg fonts-opensymbol gcc-9-base ghostscript ghostscript-x gir1.2-accountsservice-1.0 gir1.2-gdkpixbuf-2.0 gir1.2-gtk-3.0 gir1.2-nm-1.0 gir1.2-soup-2.4 gir1.2-vte-2.91 gnome-control-center gnome-control-center-data gnome-control-center-faces gnome-shell gnome-shell-common gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-good gstreamer1.0-pulseaudio gstreamer1.0-tools gstreamer1.0-x gtk-update-icon-cache gtk2-engines-pixbuf hplip hplip-data krb5-locales libaccountsservice0 libapparmor1 libarchive13 libavcodec-dev libavcodec58 libavdevice-dev libavdevice58 libavfilter-dev libavfilter7 libavformat-dev libavformat58 libavresample-dev libavresample4 libavutil-dev libavutil56 libblkid1 libbluetooth3 libc-bin libc6 libcdio18 libcom-err2 libcups2 libcupsfilters1 libcupsimage2 libcurl3-gnutls libde265-0 libdvbv5-0 libexpat1 libext2fs2 libfdisk1 libfontembed1 libgail-common libgail18 libgd3 libgdk-pixbuf2.0-0 libgdk-pixbuf2.0-bin libgdk-pixbuf2.0-common libglib2.0-0 libglib2.0-bin libglib2.0-data libgnutls30 libgs9 libgs9-common libgssapi-krb5-2 libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 libgstreamer1.0-0 libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk2.0-0 libgtk2.0-bin libgtk2.0-common libharfbuzz-icu0 libharfbuzz0b libhpmud0 libk5crypto3 libkrb5-3 libkrb5support0 libldap-2.4-2 libldap-common libmount1 libmpg123-0 libmpv1 libmysqlclient21 libndp0 libnghttp2-14 libnm0 libnspr4 libnss-systemd libnss3 libopenjp2-7 liborc-0.4-0 libpam-modules libpam-modules-bin libpam-runtime libpam-s
```

解锁后再次使用 `apt upgrade`升级软件

如果这一步没有做的话，后续使用apt安装的时候使用 `--allow-change-held-packages`参数。

### 安装必要的软件包

安装gcc的原因是luma.oled库依赖于RPi.GPIO库，这个需要gcc编译，所以需要安装gcc。

ifupdown是用于配置静态ip的软件包，修改interfaces修改静态ip依赖于这个软件包

```bash
# --allow-change-held-packages是没有解锁软件包的时候使用的参数
sudo apt install git nano openssh-server openssh-client gcc g++ cmake make ifupdown i2c-tools -y # --allow-change-held-packages
```

**安装openssh-server、openssh-client之前需要使用adb连接泰山派**

### 使用sd卡，扩展根目录

sd卡速度慢的话无法把miniconda装进去，这边指定使用[闪迪32G V30红黑卡](https://item.taobao.com/item.htm?id=853736888042&pisk=gxQb1ST9cxDj1ODli-FyNJkUK6T6lOaUWfOOt13q6ELvfVCVdCuwboAs5L1LiKrgmOs5BTx2Hd-w5C6eEsuaisP_51CpHFS23CBPCTmV3NJNUP1hdnuV6Nlcq95KuZrD7VTDSFeULyzUisYMWNPaABHm2IAY7V39BEY-LKG4vyzFi_G2MW588ZWBzAOnXVB9D3nJsLdxkVdTN3de6F3vXqn-eLA9WFKtWbCJ1IOxHd3YNbdesx3v6Vh-wCAp6FLOB3FWsvVgFQqXHsNxJh4FrcThMLgtWZUMcpGkeQAPPatvpn9oW_7WGn9dMZPM-cRRzate4frHy6jPHQTQzmLdNGBCvOqEqE1ODOx5n8mWUgQc6dKj6215OsIpyNPtt36J1HL9Vf3ONEv1dZTLJYOl2sSOotGsWIbV8h9HV53MbUQevMBjsWfJkCBMxNynoKCOtwjeRzovJ_sOdGszb2JBGbisNH06NpP7NcmGzvn16eRV2nxvZQ7UN7MjjndkNp7aN0iMDQAyY7NShcf..&spm=tbpc.boughtlist.suborder_itemtitle.1.16822e8doOytxb&skuId=5654524389321)

插入卡后，使用 `dmesg | grep mmc`查看系统日志中包含 `mmc`的信息，找到对应的设备名，会找到类似于 `mmcblk1`的设备名，这个就是sd卡的设备名。使用 `lsblk`可以查看这个sd卡下有没有分区，如果类似于以下情况，说明没有分区。

```bash
mmcblk1     179:0    0  29.7G  0 disk
```

如果是以下情况，说明有分区

```bash
mmcblk1     179:0    0  29.7G  0 disk
└─mmcblk1p1 179:1    0  29.7G  0 part
```

如果没有分区需要创建分区，使用 `fdisk`命令，输入 `n`，然后输入 `p`，然后输入 `1`，然后两次回车，最后输入 `w`保存。

fdisk是一个交互式的命令行工具，所以需要输入 `fdisk /dev/mmcblk1`进入交互模式。

```bash
sudo fdisk /dev/mmcblk1
```

- 输入n：新建分区
- 输入p：新建主分区(primary)
- 输入1：分区号
- 两次回车：默认起始扇区和结束扇区
- w：保存。

然后使用 `lsblk`查看分区是否创建成功。

```bash
mmcblk1     179:0    0  29.7G  0 disk
└─mmcblk1p1 179:1    0  29.7G  0 part
```

然后需要格式化分区，使用 `mkfs.ntfs`命令，将sd卡格式化为ntfs格式。

```bash
sudo mkfs.ntfs /dev/mmcblk1p1
```

等待完成，然后将sd卡挂在到泰山派上。

创建 `/media/sdcard`文件夹，使用mkdir命令创建。

```bash
sudo mkdir /media/sdcard
```

使用 `mount`命令挂载。

```bash
sudo mount /dev/mmcblk1p1 /media/sdcard
```

但是这个方法并不会开机自动挂载，需要将挂载信息写入 `/etc/fstab`文件中。

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

修改了 `/etc/fstab`文件之后，使用 `mount -a`命令重新挂载。

```bash
sudo mount -a
```

### 安装miniconda3(选做)

> 笔者开发的环境是使用`conda`，conda可以更换python版本，本仓库是使用python3.13进行开发

可以先下载了安装包后使用sftp将文件传到泰山派（需要ssh），也可以直接下载

使用 `wget`命令下载安装包

```bash
# 创建Downloads文件夹并打开
mkdir Downloads && cd Downloads
# 下载conda安装包到当前文件夹
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
```

下载完成后，运行安装脚本

```bash
# -b代表安装到指定目录，-p后面的参数是安装目录，这样可以快速安装不需要阅读许可协议
bash Miniconda3-latest-Linux-aarch64.sh -b -p /media/sdcard/miniconda3
```

完成安装之后，要对conda进行初始化

```bash
/media/sdcard/miniconda3/bin/conda init
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

### github的ssh配置

在泰山派中生成ssh密钥对

```bash
ssh-keygen -t rsa -b 4096 -C "邮箱@qq.com" -f ~/.ssh/id_rsa -P ""
```

然后查看公钥内容，在github中添加公钥

```bash
cat ~/.ssh/id_rsa.pub
```

生成config，并且添加github的ssh代理

```bash
touch ~/.ssh/config
echo "Host github.com" >> ~/.ssh/config
echo "  HostName ssh.github.com" >> ~/.ssh/config
echo "  Port 22" >> ~/.ssh/config
echo "  User git" >> ~/.ssh/config
```

然后测试ssh是否可以连接到github

```bash
ssh git@github.com -vT
```

如果出现 `Hi xxx! You've successfully authenticated, but GitHub does not provide shell access.`说明连接成功。如果卡住，可以考虑用 `nano`编辑 `~/.ssh/config`文件，将 `Port 22`改为 `Port 443`。

### 解决普通用户无法访问串口和gpio的问题

在泰山派中，普通用户无法访问串口和gpio，需要将用户加入到 `dialout`组中。

```bash
sudo usermod -a -G dialout lckfb
```

gpio的芯片是root组，我们需要将gpio芯片转交到 `gpio`组中。

先新建 `gpio`组

```bash
sudo groupadd gpio
# 把用户加入到gpio组
sudo usermod -a -G gpio $USER
# 重新登录，这里要输入密码
su lckfb
```

然后将 `gpiochip0`转交给 `gpio`组，这里的 `gpiochip0`对应GPIO0，参考[泰山派40脚排针接口](https://wiki.lckfb.com/zh-hans/tspi-rk3566/system-usage/buildroot-system-usage.html#_40pin%E6%8E%92%E9%92%88%E6%8E%A5%E5%8F%A3)

```bash
sudo chown root:gpio /dev/gpiochip0
sudo chmod 660 /dev/gpiochip0
```

### 自启动的脚本

上个标题的步骤，重新之后可能会失效，所以需要做一个开机自启动脚本

**下面的内容需要创建了gpio组，并且将当前用户(这里是 `lckfb`)添加到gpio组中在运行**

```bash
sudo groupadd gpio
sudo usermod -a -G gpio $USER
```

可以使用 `groups`命令查看当前用户所在的用户组，**确保当前用户在 `gpio`用户组中**

环境配置的时候我提供了一个开机自动配置GPIO的脚本，用于修改GPIO芯片的权限，位于目录 `run_auto`下，里面的 `gpio-setup.service`需要复制到 `/etc/systemd/system/`下，然后使用 `systemctl enable gpio-setup.service`命令开机自启动。

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

**`gpio-setup.service`里面的 `ExecStart`需要修改到 `run_auto`文件夹下 `gpio-setup.sh`文件的绝对路径**

#### 解析

其实制作自启动脚本的流程基本都是一样的，在固定的位置写好需要运行的脚本，可以是python脚本也可以是bash脚本，然后创建对应的service文件，然后放到系统的服务文件中，刷新，然后打开服务自启动即可

可能很难理解说明的`服务`，其实并没有那么复杂，服务其实就是运行在后台的一个程序，只是说这个程序一般是用来服务用户的其他操作，所以叫做`服务`

**如果使用bash脚本，必须在脚本开头写上**

```bash
#!/bin/bash
```

用于表明解释器，使用bash解释器

如果创建service文件，标准的service文件如下

```
[Unit]
Description=Change Board LED
After=network.target

[Service]
ExecStart=/media/sdcard/code/Engineering-innovation-competition-vision/run_auto/change_board_led.sh
Type=simple
RemainAfterExit=true
User=root

[Install]
WantedBy=multi-user.target
```

- `Unit` 单元信息，定义服务的元信息和依赖关系。
  - `Description`：描述服务的功能，便于管理员了解服务的用途。
  - `After`：指定服务的启动顺序，表示该服务需要在某些目标或服务启动后再启动。
  - `Requires` 和 `Wants`：定义服务的依赖关系，Requires 表示强依赖，Wants 表示弱依赖。
  - `Before`：与 `After` 相反，表示该服务需要在指定目标或服务之前启动。
- `Service`: 服务，用于定义服务的行为和运行方式
  - `ExecStart`：指定服务启动时执行的命令或脚本。
  - `Type`：定义服务的启动类型，例如：
    - `simple`：默认类型，直接运行 ExecStart 中的命令。
    - `forking`：服务会派生出一个子进程，父进程退出后，子进程继续运行。
    - `oneshot`：服务运行一次后立即退出，通常用于初始化任务。
  - `RemainAfterExit`：如果设置为 true，即使服务的主进程退出，服务仍然被认为是“活动”状态。
  - `User`：指定运行服务的用户。
  - `Restart`：定义服务失败时的重启策略，例如 always 表示服务失败后总是重启。
- `Install` 安装行为，用于设置服务的启动目标
  - `WantedBy`：指定服务在哪些目标（target）下启用。例如：
    - `multi-user.target`：表示服务在多用户模式下启动。
    - `graphical.target`：表示服务在图形界面模式下启动。
  - `RequiredBy`：类似于 WantedBy，但表示强依赖关系。
  - `Alias`：为服务创建别名。

### 摄像头索引查询

不管是树莓派还是泰山派，摄像头的索引可能会被其他的USB设备替代，摄像头的索引就会发生改变，所以我们需要确认摄像头的索引编号

使用以下命令查看可用的摄像头

```bash
v4l2-ctl --list-devices
```

也可以通过一下的命令查看摄像头支持的分辨率和帧率

```bash
v4l2-ctl --list-formats-ext
```

找到我们使用的摄像头，一般有USB或者1080p、60等字样，泰山派比较特殊，摄像头的索引不是0。会得到类型于下面的输出

```
/dev/video0
/dev/video1
```

这种情况一般就是第一个，如果第一个不行就试一下第二个

### 引脚资源释放

`run_auto/cleanup.sh`脚本是用来释放引脚资源，如果程序被kill，没有关闭对应的LED灯和OLED模块，需要手动释放引脚资源

#### 创建快捷方式

> 下面的方法可以适用于任何比较长的命令

在 `~/.bashrc`文件中添加以下内容

```bash
alias cleanup="bash /media/sdcard/code/Engineering-innovation-competition-vision/run_auto/cleanup.sh"
```

也可以使用`echo`命令添加

```bash
echo "alias cleanup=\"bash /media/sdcard/code/Engineering-innovation-competition-vision/run_auto/cleanup.sh\"" >> ~/.bashrc
```

然后使用 `source ~/.bashrc`命令使其生效

```bash
source ~/.bashrc
```

### main的运行

在main中添加了命令行传参，方便传递处理图像是否使用图传以及config的路径，可以使用以下命令快速执行

```bash
/media/sdcard/miniconda3/envs/EIC/bin/python /media/sdcard/code/Engineering-innovation-competition-vision/main.py -c /media/sdcard/code/Engineering-innovation-competition-vision/config.yaml
```

- --config_path(-c): 表示配置文件的路径，默认是当前目录下的config.yaml

#### 快捷方式的创建

同样的，也可以设置快捷命令，与上面的 `cleanup`命令类似

```bash
# 正式版的main，不显示图像
alias run="/media/sdcard/miniconda3/envs/EIC/bin/python /media/sdcard/code/Engineering-innovation-competition-vision/main.py --config_path /media/sdcard/code/Engineering-innovation-competition-vision/config.yaml"
```

也可以使用`echo`命令添加

```bash
echo "alias run=\"/media/sdcard/miniconda3/envs/EIC/bin/python /media/sdcard/code/Engineering-innovation-competition-vision/main.py --config_path /media/sdcard/code/Engineering-innovation-competition-vision/config.yaml\"" >> ~/.bashrc
echo "alias run-debug=\"/media/sdcard/miniconda3/envs/EIC/bin/python /media/sdcard/code/Engineering-innovation-competition-vision/main.py --deal_method send --config_path /media/sdcard/code/Engineering-innovation-competition-vision/config.yaml\"" >> ~/.bashrc
```

然后使用 `source ~/.bashrc`命令使其生效

```bash
source ~/.bashrc
```

#### 自启动服务的创建

在文件夹`run_auto`下，有`run-main-auto.service`以及`run_main.sh`。将`service`服务单元文件复制到`/etc/systemd/system/`下，并且修改 `ExecStart`的路径为 `run_main.sh`的绝对路径。

```bash
# 复制服务文件到systemd目录
sudo cp run_auto/run-main-auto.service /etc/systemd/system/
# 更新服务
sudo systemctl daemon-reload
# 开启服务
sudo systemctl start run-main-auto.service
# 关闭服务
sudo systemctl stop run-main-auto.service
# 开机自启动
sudo systemctl enable run-main-auto.service
# 关闭开机自启动
sudo systemctl disable run-main-auto.service
```

## 项目结构

下面不会在讲到非必要文件，例如.gitignore，LICENSE等文件

```
run_auto                    用于自启动服务及其脚本的文件夹
PCB                         存放泰山派扩展板设计和layout文件夹
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
    |___ gpio.py            有关于GPIO的代码，主要是开关,LED,OLED的抽象
    |___ tspi_boaed_info.py 用于获取泰山派的信息
    |___ wifi_connect.py    用于连接wifi的代码
    |___ ConfigLoader.py    用于加载配置文件的代码
    |___ logger.py          用于打印日志的函数，主要是包含了时间戳和字体颜色
ImgTrans                    用于存放图传逻辑的文件夹
    |___ __init__.py        图传逻辑的初始化文件
    |___ IImgTrans.py       图传逻辑的基类(类似于接口)
    |___ ImgTrans.py        图传逻辑的实现类，包括TCP和UDP

AdjustConfig.py             用于调整配置的调试代码
Solution.py                 用于存放解决方案的代码，包括颜色识别，圆环识别，直线识别以及串口等使用的函数
test_Solution.py            用于测试Solution或者detector的功能
img_trans.py                用于远程图传的代码，主要用于调试过程方便在电脑上得到图像
main.py                     主程序，直接在Jetson或者泰山派上运行的代码
requirements.txt            依赖的库,可以使用pip install -r requirements.txt一键安装依赖
config.yaml                 用于存放参数的文件
environment.sh              用于一键配置泰山派环境的脚本，还没用过，不建议使用，可以参考里面的内容，手动配置
```

## 电控可以直接调用的接口

即返回值封装成了字符，可以直接串口进行发送返回值

- 物料的运动检测，即物料所在位号发生变化认为物料运动，直接返回物料位号

```
"C123E"代表红色在1号位，绿色在2号位，蓝色在3号位
如果有物料没识别到位号（可能被夹走），对应的数字变为0
```

- 获取物料位置，返回位号，这个是直接看当前位置，不等待运动，与上面的不同

```
"C123E"代表红色在1号位，绿色在2号位，蓝色在3号位
如果有物料没识别到位号（可能被夹走），对应的数字变为0
```

- 直角(圆环)检测

```
返回角度大于0的直线(参与直角的组成)角度和直角的交点坐标

str的结果会表示为
    'LHXXXxxxyyyE'，
        其中：
        * L(location),表示定位
        * XXX是角度的十倍(如果是圆环，此处为000)
        * H代表正负号（0和1）(如果是圆环，此处为0)
        * xxx和yyy代表交点的坐标
```

## 完成的功能

即返回值没有进行封装，只是方便其他方法的使用，不能使用串口直接发送

- 物料追踪(Solution.Solution.__detect_material_positions())

## 外部调节的参数(config.yaml)

### 直线识别参数

该参数尽量固定

```yaml
LineDetector:
  Min_val: 120          #Canny边缘检测的低阈值
  Max_val: 255          #Canny边缘检测的高阈值
  Hough_threshold: 48   #霍夫变换的阈值,值越大，检测时间越短，但是可能会丢失一些直线
  minLineLength: 70     #Hough变换的最小线段长度
  maxLineGap: 49        #Hough变换的最大线段间隔
  bias: 1               #允许的角度误差
  sigma: 0              #Canny边缘检测的sigma
  odd_index: 3          #kernel_size(滤波卷积核尺寸)是第几个奇数
  H_High: 57
  H_Low: 12
  S_High: 200
  S_Low: 5
  V_High: 240
  V_Low: 0
```

### 位号参数

该参数尽量固定，这个参数主要是机械臂距离圆盘的高度决定的

```yaml
area1_points:
  - [25, 0]        #左上角
  - [168, 118]     #右下角
area2_points:
  - [168, 0]       #左上角
  - [293, 118]     #右下角
area3_points:
  - [65, 118]      #左上角
  - [290, 237]     #右下角

```

### 颜色阈值

该参数尽量固定，但是现场可能仍要调整

```yaml
color:
  R:
    centre: 0
    error: 17
    L_S: 80
    U_S: 255
    L_V: 40
    U_V: 255

  G:
    centre: 65
    error: 20
    L_S: 80
    U_S: 255
    L_V: 40
    U_V: 255

  B:
    centre: 109
    error: 17
    L_S: 80
    U_S: 255
    L_V: 40
    U_V: 255

min_material_area: 2000     #目标颜色最小面积
max_material_area: 40000    #目标颜色最大面积
```

### 目标角度

该参数尽量固定，这个角度是直角定位产生的角度

```yaml
target_angle: 46
```

### 圆环参数

圆环参数是包含物料圆环（识别圆形物料的，**现已弃用**），和地面的圆环（现在以这个为例）

```yaml
annulus:
  dp: 1             #霍夫变换的分辨率
  minDist: 100      #俩个圆之间的最小距离
  param1: 100       #Canny边缘检测的高阈值，低阈值是高阈值的一半
  param2: 100       #累加器阈值，值越大，检测时间越短，识别到的
  minRadius: 40     #最小圆半径
  maxRadius: 97     #最大圆半径
  sigma: 0          #高斯滤波标准差
  odd_index: 3      #kernel_size(滤波卷积核尺寸)是第几个奇数
```

### 底部裁剪高度

在摄像头画面的底部可能包含车身部分，所以要对底部进行裁剪，这个高度有对应的参数，单位px

```yaml
need2cut_height: 20
```

## 代码解读

整体结构思路：

对于视觉，大部分的功能和代码在常见比赛里面都具有较高的重复性，例如**颜色识别**，**直线识别**，**圆环识别等**。所以整体项目结构要保证以下几点

1. 保证常用的功能具有较高的可移植性。
2. 各个底层功能应该彼此分离
3. 各种参数应该与源代码剥离
4. 具有清晰的层次结构

### 底层结构与多态函数的初步构建

在底层结构的设计中，将颜色识别，直线识别等互相独立的任务抽象成类，可以理解为**识别器**，在文件夹 `./detector`下，包含的是各种识别器的代码，并且将 `detector`封装成软件包（内部含有 `__init__.py`即可），软件包也是一个单独的模块，可以使用 `import detector`对识别器进行导入（在C++中，这种被称为命名空间 `namespace`）

为了实现较高的复用型和灵活性，也是为了在顶层调用的时候传入的参数和返回值更方便进行处理，在底层的函数都应该具有一样的传参和返回值类型，这里就是**面向对象编程的思想**中核心之一**面相接口编程**可以从Java中获取对应的灵感。其核心目的是为了规范函数的传参和返回值。

在三个识别器中的核心函数的传参都设计成，只传入一个图片，返回对应需要的结果。在这个位置还没有完成完全的多态，但是传参进行了第一步的规范，为后续多态的构建提供了基础。

![项目结构图](flow_chart/项目结构.png)

初步完成底层的函数之后，开始构建顶层的函数，将底层的功能结合起来，这个地方的函数会完成完全的多态结构（此处的多态是函数多态，也可以理解为用函数指针调用函数）。

在 `Solution.py`解决方案中，写了所有顶层函数，直角定位，圆环定位，物料追踪，运动检测等。这个部分的函数传参和返回值都规定为下面的形式

```python
def func(self, img:cv2.typing.MatLike) -> tuple[None|str, cv2.typing.MatLike]:...
```

用上面的这种函数，在 `main.py`下调用会更加灵活。

返回值包含了一个图片，这个图片方便调试的时候进行远程图传的图片，也方便查找问题。

所有的 `Solution.py`下的函数设计成这样的原因也是为了方便在 `test_Solution.py`进行测试。

此外，需要注意的是，`utils`命名空间软件包的测试都要在外部进行，避免发生回环导入或者无法导入的问题，这些软件包设计的时候就不是用来在内部使用的，所以从内部进行函数调用会出现一些问题

### 需求解析

分析需求确实才是编程最难的部分，语法以及语言只是工具而已。本次方案的需求相对于往年的方案，复杂度大大提升，主要是要对物料进行运动检测。接下来会依次介绍`物料位号识别`、`运动检测`需求。直线检测和圆环检测属于传统视觉，几乎不包含任何新东西，主要是对参数的调整和调试。

#### 物料位号识别

位号，是人为在外部定义的区域，就是物料转盘停下时有物料的的位置，这个参数对应到`config.yaml`文件中，`area1_points`，`area2_points`，`area3_points`。这个参数是摄像头与物料转盘的高度决定的

在调参文件`AdjustConfig.py`中，提供了一个函数用于调整位号的参数，函数名为 `adjust_area_points`，该函数会在摄像头的画面上显示出位号的区域，方便调参

得到位号之后，对画面进行颜色识别，颜色识别器`ColorDetector`有一个用于二值化的函数`binarization`,使用`update_range`函数进行颜色阈值的更新，调整到需要识别的颜色，然后使用`binarization`函数会返回一个二值化的图像，再将这个图像传入函数`get_material_positions`中，得到物料的中心点坐标。

如果对这个中心点坐标进行判断，如果在位号的区域内，就认为这个物料在这个位号上，返回值为`C123E`，其中C代表颜色，数字代表位号，E代表结束符，索引值就是颜色。再例如：`C321E`，代表红色在3号位，绿色在2号位，蓝色在1号位。

#### 运动检测

物料的运动检测是用于调整机械臂的夹取时间，取保机械臂在第一次夹取的时候可以一次夹两个物料。这个需求需要在顶层解决方案中设立一个栈结构用于存储上一帧的位号信息，函数每次被调用的时候都会将当前帧的位号信息与上一帧的位号信息进行对比，如果有变化，就认为物料发生了运动，返回值为新的位号，格式就是上面的位号识别。

但是值得注意的是，并不是变化了就代表物料停下来了，可能在运动过程中物料的位号也发生了变化，所以不能简单的就认为物料发生了运动就返回位号，如果三个物料有两个都在下面，形成正三角形，下面的两个物料都会认为在3位号，这个时候会返回不希望的值，**所以要判断这三个值没有重复**，考虑使用集合的特性，将三个值放入集合中，如果集合的长度为3，就认为物料发生了运动。

确实到此就可以了，在`Solution.py`中196行的判断是用于单个物料的运动检测，就是说两个物料被夹走之后，再等待最后一个物料变化。但是经过测试，本方案的机械臂最快可以夹取2个，夹取完后转盘刚好转，这个时候不需要再等待变化，直接识别到物料的位号就可以了。

但是每次电控发送调用这个函数的信号的时候，还需要清空栈结构，否则会跟上一次识别的值进行对比，导致误判。

### 调参(AdjustConfig.py)

该文件末尾已经封装了需要调整的参数的对应函数，需要向内传入一个摄像头或者图传接收器，此处的图传接收器与OpenCV摄像头形成多态。

在图传接收器中，将ip地址改为泰山派的ip地址，端口号改为图传的端口号，即可在电脑上调整参数。

完成本地调参之后，将 `config.yaml`文件复制到泰山派上。

泰山派的无线网卡延迟比较高，远程图传的体检较差，我用的是有线网口进行的有线网络连接，使用的是双机通信内环IP(169.254.0.0/16)

### 测试(test_Solution.py)

在测试文件中，主要用于测试顶层需求，类 `TestSolution`继承了 `Solution`类，然后在 `TestSolution`中实现了 `test`函数，该函数中手动传入电控发送的信号，然后调用 `Solution`中的函数，最后将返回值打印出来。

同时也提供了串口测试，物料追踪的测试

### 远程图传(img_trans.py)

图传文件在一开始在两个平台是不能混用的，但是到现在这个版本，做了平台的判断，如果是Linux平台，会执行发送图传的逻辑，反之执行接收图传的逻辑

### 主文件(main.py)

可以注意到，在主文件中有包含GPIO的操作，主要使用LED指示开发板状态，是否在识别，是否已经启动等，还有OLED显示相关的状态信息。这些信息在PCB文件夹中有对应扩展板的文件，使用`嘉立创EDA Pro`进行查看。

代码量大，主要是因为要对开关状态进行判断，不使用多线程是要避免资源争夺，避免在识别运算的过程中互斥锁闭其他线程夺取，导致识别速度降低

## 创新点

### 对颜色阈值的重构

我们关注到OpenCV的颜色阈值是用一个低值和一个高值进行二值化，这种的二值化方式我们注意到其在红色的表现较差，因为红色的部分在HSV空间中是分布在两个区域的，所以我们对颜色阈值进行了重构，使用中心点和容差的方式进行颜色识别。可以理解为将条形的颜色阈值改为了圆形的颜色阈值。

该灵感来源于ps中的色相偏移，我们注意到ps中进行颜色选取的时候使用的中心点和容差的方式，所以我们将这个思想引入到了颜色识别中。此外，我们深入思考了HSV的深层含义，HSV是一个圆柱体，H是圆柱体的角度，S是圆柱体的半径，V是圆柱体的高度。H本身就是一个角度，所以我们这种方式是合理的。

流程图懒得画了，核心函数在颜色识别器的`update_range`，自己看看吧，也不是很难

### 一种不同于传统的视觉开发板

与传统的树莓派和openmv不同，这次使用的是嘉立创开源的泰山派RK3566开发板，这个开发板的优势在于：

1. 价格便宜，性能强大，可以运行Linux系统，相对于树莓派更具性价比
2. 相对于树莓派，开机速度更快，功耗低于树莓派的情况，性能没有过多的损失
3. 相对于树莓派，泰山派的使用难度更大，其要手动编译Linux系统并且烧录，以及外部存储设备的挂载，这些的难度远高于树莓派的常规使用，其更能锻炼团队的技术水平
4. 在大小而言，泰山派的尺寸比树莓派更小，重量更轻
5. 相对于openmv，泰山派的性能更强，可以运行更多的算法，更适合于视觉识别，有更丰富的Python三方库
6. 使用最新的Python版本，3.13，引入了JIT，初步抛弃了GIL，性能方面比过往版本有了很大的提升
