# 解锁包的禁止更新
sudo aptitude unhold accountsservice apparmor base-files bind9-host bind9-libs bluez bluez-cups bluez-obexd bsdutils bubblewrap ca-certificates cpp-9 cups cups-browsed cups-bsd cups-client cups-common cups-core-drivers cups-daemon cups-filters cups-filters-core-drivers cups-ipp-utils cups-ppdc cups-server-common distro-info-data dns-root-data dnsmasq-base e2fsprogs fdisk ffmpeg fonts-opensymbol gcc-9-base ghostscript ghostscript-x gir1.2-accountsservice-1.0 gir1.2-gdkpixbuf-2.0 gir1.2-gtk-3.0 gir1.2-nm-1.0 gir1.2-soup-2.4 gir1.2-vte-2.91 gnome-control-center gnome-control-center-data gnome-control-center-faces gnome-shell gnome-shell-common gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-good gstreamer1.0-pulseaudio gstreamer1.0-tools gstreamer1.0-x gtk-update-icon-cache gtk2-engines-pixbuf hplip hplip-data krb5-locales libaccountsservice0 libapparmor1 libarchive13 libavcodec-dev libavcodec58 libavdevice-dev libavdevice58 libavfilter-dev libavfilter7 libavformat-dev libavformat58 libavresample-dev libavresample4 libavutil-dev libavutil56 libblkid1 libbluetooth3 libc-bin libc6 libcdio18 libcom-err2 libcups2 libcupsfilters1 libcupsimage2 libcurl3-gnutls libde265-0 libdvbv5-0 libexpat1 libext2fs2 libfdisk1 libfontembed1 libgail-common libgail18 libgd3 libgdk-pixbuf2.0-0 libgdk-pixbuf2.0-bin libgdk-pixbuf2.0-common libglib2.0-0 libglib2.0-bin libglib2.0-data libgnutls30 libgs9 libgs9-common libgssapi-krb5-2 libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 libgstreamer1.0-0 libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk2.0-0 libgtk2.0-bin libgtk2.0-common libharfbuzz-icu0 libharfbuzz0b libhpmud0 libk5crypto3 libkrb5-3 libkrb5support0 libldap-2.4-2 libldap-common libmount1 libmpg123-0 libmpv1 libmysqlclient21 libndp0 libnghttp2-14 libnm0 libnspr4 libnss-systemd libnss3 libopenjp2-7 liborc-0.4-0 libpam-modules libpam-modules-bin libpam-runtime libpam-s
# 更新软件
sudo apt-get update
sudo apt-get upgrade
# 安装ssh
sudo apt-get install openssh-client openssh-server
# 安装nano
sudo apt-get install nano
# 安装git
sudo apt-get install git
# 下载miniconda到Download文件夹
cd ~/Downloads
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# 安装miniconda
bash Miniconda3-latest-Linux-x86_64.sh
# 修改全局pip源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/