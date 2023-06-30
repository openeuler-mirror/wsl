# WSL介绍

## WSL是什么

WSL 是 Windows Subsystem for Linux 的缩写，意思是 Windows 的一个子系统，可以在 Windows 下运行 Linux 操作系统。它的主要目标是提高文件系统性能，以及添加完全的系统调用兼容性。你可以在 Microsoft Store 中选择你偏好的 Linux 分发版，运行常用的命令行工具、服务、语言和图形应用程序。它不需要传统的虚拟机或双启动设置开销。

## WSL与虚拟机的区别

WSL 和虚拟机的区别主要有以下几点：

- WSL 1 是基于动态翻译的方式将 Linux 的系统调用翻译为 Windows NT 的系统调用，而 WSL 2 是基于虚拟机的，在 Windows 主系统之上创建完整的 Linux 内核；
- WSL 的启动时间短，资源占用量少，并且无需 VM 配置或管理，而虚拟机可能启动速度慢，是独立的，消耗大量资源，需要你花费时间进行管理；
- WSL 可以对 Windows 文件系统下的文件直接进行读写，文件传输更方便，而虚拟机需要通过共享文件夹或其他方式来实现文件交换；
- WSL 支持剪贴板互通，可以直接在 Windows 下复制文本内容，粘贴到 WSL，而虚拟机需要安装增强工具或其他插件来实现这一功能；
- WSL 有 Windows 和 Linux 之间的无缝集成，可以跨 OS 调用应用程序，而虚拟机需要在不同的操作系统之间切换；
- WSL 可以在 Microsoft Store 中选择你偏好的 Linux 分发版，而虚拟机可以运行更多的开源操作系统，如 BSDs 或 FreeDOS；
- WSL 支持完全的系统调用兼容性，可以运行更多的 Linux 应用程序，如 Docker 等，而虚拟机可能有一些兼容性问题；
- WSL 的跨 OS 文件系统的性能比虚拟机低，如果要使用 Windows 应用程序来访问 Linux 文件，则目前通过虚拟机可实现更快的性能；
- WSL 不支持访问串行端口或 USB 设备（除非使用 USBIPD-WIN 项目），而虚拟机可以直接连接外部设备；
- WSL 不支持图形界面应用（除非使用一些临时技术来解决它），而虚拟机可以直接显示 Linux 的桌面环境和窗口管理器。

## WSL的优势

WSL 的优势如下：

- 与在虚拟机下使用 Linux 相比，WSL 更加流畅；
WSL 可以对 Windows 文件系统下的文件直接进行读写，文件传输更方便；
- WSL 支持剪贴板互通，可以直接在 Windows 下复制文本内容，粘贴到 WSL；
- WSL 使用的是真正的 Linux 内核，支持完全的系统调用兼容性，可以运行更多的 Linux 应用程序；
- WSL 的启动时间短，资源占用量少，并且无需 VM 配置或管理；
- WSL 的内存使用量会随使用而缩放，并且当进程释放内存时，这会自动返回到 Windows；
- WSL 有 Windows 和 Linux 之间的无缝集成，可以跨 OS 调用应用程序。

## WSL目前支持的Linux分发版

wsl sideload是指在WSL中安装不在Microsoft Store中提供的Linux发行版的过程。有两种方法可以实现wsl sideload：

- 使用tar文件导入任何Linux发行版，例如CentOS。这需要先获取一个包含发行版所有Linux二进制文件的tar文件，然后使用wsl --import命令将其导入WSL。
- 创建自己的自定义Linux发行版，打包为UWP应用，其行为将与Microsoft Store中提供的WSL发行版完全一样。这需要使用Windows 10 SDK中的工具来创建和签名应用包，然后使用Add-AppxPackage命令将其安装到WSL。

## 构建一个sideload

首先在一个 terminal 中依次执行如下命令，从 docker 中导出一个 Linux 发行版容器：

```
docker pull openeuler/openeuler
docker run -td openeuler/openeuler
```

然后在另一个 terminal 中依次执行如下命令，导出openeuler：

```
docker ps
docker export $(docker ps -ql) > ./openeuler.tar
```

然后执行如下指令，使用WSL命令，导入openEuler包，并指明openEuler的安装目录。例如，设置D:\work\WSL\openEuler为WSL的安装目录。：

```
wsl --import openEuler D:\work\WSL\openEuler .\openEuler.tar
wsl -d openEuler
```

即可实现 sideload 方式加载自定义的 wsl

# 在wsl中实现图形化界面

在 openEuler 中，如果是启动一些需要图形化界面的应用，那么 openEuler 会自动启动一个窗口来显示图形化界面，例如在 openEuler 中输入 `gedit` ，就会启动一个文本编辑器。

## 安装适用于 openEuler 的 FireFox

依次输入如下命令：

```
wsl -d openEuler
yum update
yum upgrade
```

在 openEuler 中输入命令下载 firefox ：

```
yum install firefox
```

由于 openEuler 中默认是以 root 身份运行的，而要启动 firefox 浏览器则需要普通用户才行，因此这里需要创建一个新用户 euler ：

```
useradd euler
passwd euler
su euler
```

然后输入命令 `firefox` 即可启动 firefox 浏览器。
