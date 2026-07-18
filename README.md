<div align="center">
  <img src="./imgup.png" alt="imgup" width="150">

# imgup

一个轻量、自托管、跨平台使用的图床工具。部署一次服务端，Windows、Linux、macOS 都可以用同一套域名和 Token 上传图片，并获得稳定可长期引用的 HTTPS 链接。

[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Windows](https://img.shields.io/badge/Windows-GUI-2563eb?style=for-the-badge&logo=windows&logoColor=white)]()
[![Self Hosted](https://img.shields.io/badge/Self--Hosted-Yes-0ea5e9?style=for-the-badge)]()

`本地图片 -> imgup -> 自己的服务器 -> HTTPS 图片链接`

[快速开始](#-快速开始) · [项目配置下载说明](#-项目配置下载说明) · [常见问题](#-常见问题)

</div>

## ✨ 项目优点

| 能力 | 说明 |
| --- | --- |
| 🔒 自托管 | 图片保存在自己的服务器目录中，不依赖第三方图床。 |
| ⚡ 轻量 | 服务端使用 Python 标准库实现，不需要数据库。 |
| 🧩 易部署 | `install.sh` 会创建 systemd 服务、生成 Token，并尝试配置反向代理。 |
| 🖥️ Windows 友好 | 提供 `dist-utf8/imgup.exe`，双击运行，支持图形界面上传。 |
| 🧭 跨平台 | Windows 用 GUI，Linux / macOS 用命令行。 |
| 🔗 链接稳定 | 上传后按日期归档，返回可直接引用的 HTTPS 链接。 |
| 🛡️ 防覆盖 | 同名文件自动追加短 hash，避免覆盖旧图片。 |
| 🤖 自动化友好 | API 返回 JSON，适合脚本、Markdown 工具和自动化流程调用。 |

## 🚀 快速开始

### Step 1：部署服务端

在 Linux 服务器上执行：

```bash
git clone https://github.com/FeynmanNddbb/imgup.git
cd imgup
sudo bash install.sh
```

安装完成后保存脚本输出的两项信息：

- 图床域名，例如 `images.example.com`
- 上传 Token

### Step 2A：Windows 客户端上传

仓库中可直接使用的 Windows 客户端位于 `dist-utf8`：

```text
dist-utf8/
  imgup.exe
  imgup_config.json
```

使用方式：

1. 双击运行 `dist-utf8/imgup.exe`。
2. 首次启动时填写图床域名和上传 Token。
3. 点击“选择图片并上传”。
4. 上传成功后，图片链接会自动复制到剪贴板。

### Step 2B：Linux / macOS 命令行上传

如果是在刚刚执行过 `sudo bash install.sh` 的服务器本机，安装脚本已经创建了 `imgup` 命令，可以直接上传：

```bash
imgup photo.jpg
imgup "中文目录/截图.png"
imgup *.png *.jpg
```

如果是在另一台 Linux / macOS 电脑上使用，需要先安装并配置客户端：

```bash
chmod +x install-client.sh upload.sh
./install-client.sh
```

配置完成后再上传：

```bash
imgup photo.jpg
```

## 📦 项目配置下载说明

### 🛠️ 服务端部署

`install.sh` 用于在 Linux 服务器上部署 imgup 服务端。它会把上传服务安装为 systemd 服务，并在当前服务器本机顺带安装一个 `imgup` 命令，方便服务器本机直接测试上传。

执行命令：

```bash
git clone https://github.com/FeynmanNddbb/imgup.git
cd imgup
sudo bash install.sh
```

安装脚本会自动完成：

- 创建安装目录和图片存储目录
- 复制 `server.py`
- 创建并启动 `imgup.service`
- 生成随机上传 Token
- 在当前服务器本机安装命令行工具 `imgup`
- 尝试为 Caddy / Nginx / Apache 写入反向代理配置

安装完成后，请保存脚本输出的图床域名和上传 Token。Windows 客户端、其他 Linux / macOS 电脑都需要用这两个信息进行配置。

服务端默认监听：

```text
127.0.0.1:8765
```

对外访问通常由反向代理提供。

#### 🔧 服务管理

```bash
sudo systemctl status imgup
sudo systemctl restart imgup
sudo journalctl -u imgup -f
```

#### ⚙️ 主要环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `UPLOAD_DIR` | `/data/images` | 图片存储目录 |
| `UPLOAD_TOKEN` | 自动生成 | 上传鉴权 Token |
| `BASE_URL` | `https://images.example.com` | 返回链接使用的公网地址 |
| `PORT` | `8765` | 本地监听端口 |
| `MAX_SIZE_MB` | `20` | 单文件最大体积 |

### 🖥️ Windows 客户端

Windows 用户主要使用 `dist-utf8/imgup.exe`。

#### 📦 文件说明

| 文件 | 作用 |
| --- | --- |
| `dist-utf8/imgup.exe` | Windows 图形界面客户端，双击运行。 |
| `dist-utf8/imgup_config.json` | 客户端配置文件，用于保存上传地址和 Token。 |

#### ✅ 功能

- 首次启动配置域名和 Token
- 多选图片上传
- 上传日志显示
- 成功后自动复制链接到剪贴板
- 支持重新配置服务端地址和 Token

#### 🖼️ 支持格式

```text
.jpg .jpeg .png .gif .webp .svg .bmp .avif .ico
```

### 💻 Linux / macOS 客户端

Linux / macOS 客户端并不是系统自带命令，必须先安装。分两种情况：

#### 情况 1：服务器本机使用

如果这台机器已经执行过服务端部署命令：

```bash
sudo bash install.sh
```

安装脚本会顺带安装 `/usr/local/bin/imgup`，因此可以直接上传：

```bash
imgup photo.jpg
```

#### 情况 2：另一台 Linux / macOS 电脑使用

需要先安装客户端并填写图床域名和 Token：

```bash
chmod +x install-client.sh upload.sh
./install-client.sh
```

安装完成后再使用：

```bash
imgup photo.jpg
imgup "中文目录/截图.png"
imgup *.png *.jpg
```

客户端配置默认保存到：

```text
~/.config/imgup/imgup_config.json
```

配置示例：

```json
{
  "url": "https://images.example.com/upload",
  "token": "your_token_here",
  "version": "1.0"
}
```

### 🔌 API

#### 健康检查

```http
GET /health
```

响应示例：

```json
{
  "status": "ok",
  "upload_dir": "/data/images"
}
```

#### 上传图片

```http
POST /upload
X-Upload-Token: your_token_here
Content-Type: multipart/form-data
```

表单字段：

| 字段 | 说明 |
| --- | --- |
| `file` | 要上传的图片文件 |

成功响应示例：

```json
{
  "url": "https://images.example.com/2026-07-18/photo.jpg",
  "filename": "photo.jpg",
  "date": "2026-07-18",
  "size": 204800
}
```

### 📁 存储结构

上传后的图片会按日期归档：

```text
/data/images/
  2026-07-18/
    photo.jpg
    screenshot.png
    photo_a1b2c3d4.jpg
```

同名文件不会覆盖旧文件，服务端会自动追加短 hash。

### 🌐 反向代理

推荐把公网域名转发到本地 `127.0.0.1:8765`。

#### Caddy

```caddy
images.example.com {
    encode gzip zstd

    handle /upload {
        reverse_proxy 127.0.0.1:8765
    }

    handle /health {
        reverse_proxy 127.0.0.1:8765
    }

    handle {
        root * /data/images
        file_server browse
    }
}
```

#### Nginx

```nginx
server {
    listen 80;
    server_name images.example.com;

    location /upload {
        proxy_pass http://127.0.0.1:8765;
        client_max_body_size 20M;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8765;
    }

    location / {
        root /data/images;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
}
```

## ❓ 常见问题

### 上传返回 401 unauthorized

客户端 Token 和服务端 `UPLOAD_TOKEN` 不一致。请检查：

- Windows 客户端同目录下的 `imgup_config.json`
- 安装脚本输出的 Token
- systemd 服务里的 `UPLOAD_TOKEN`

### 返回链接没有 https

确认服务端 `BASE_URL` 带有协议：

```ini
Environment=BASE_URL=https://images.example.com
```

### 修改服务配置后没有生效

手动执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart imgup
```

## 📄 许可证

[MIT](LICENSE)
