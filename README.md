<div align="center">

# imgup 🖼️

### 构建属于自己的安全图床服务

把本地图片变成在线链接，轻量、安全、完全自托管

<br>

[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)
[![Platform](https://img.shields.io/badge/客户端-Windows%20%7C%20Linux%20%7C%20macOS-6366f1?style=flat)]()
[![GitHub Stars](https://img.shields.io/github/stars/FeynmanNddbb/imgup?style=flat&logo=github)](https://github.com/FeynmanNddbb/imgup/stargazers)

<br>

```
📷 本地图片  →  imgup  →  https://your-domain.com/2026-07-18/photo.jpg  🔗
```

<br>

[🚀 快速部署](#-快速部署) ·
[💻 客户端下载](#-客户端使用) ·
[⚙️ 配置](#️-配置) ·
[📋 API](#-api-参考)

</div>

---

## 这是什么？

imgup 是一个**自托管图床服务**，部署在你自己的服务器上，帮你把本地图片一键上传并生成可分享的在线链接。

- 📁 图片存储在**你的服务器**，数据完全自主掌控
- 🔒 Token 认证，只有你能上传，图片可以公开访问
- 📅 自动按日期归档，整洁有序
- 🪶 **零依赖**，纯 Python 3 标准库，服务端开箱即用

**适合场景：** 博客写作、文档配图、团队内部图片分享、替代付费图床服务

---

## ✨ 核心特性

|  | 特性 | 说明 |
|--|------|------|
| 🪶 | **零依赖** | 纯 Python 3 标准库，无需 `pip install` 任何东西 |
| 🔒 | **私有安全** | Token 鉴权，图片只能由你上传 |
| 📅 | **日期归档** | 自动整理为 `YYYY-MM-DD/` 目录结构 |
| 🔁 | **防重名** | 同名文件自动追加 MD5 短 hash |
| 🌐 | **CORS 支持** | 可直接在网页前端调用 |
| 💻 | **多平台客户端** | Windows 图形界面 + Linux/macOS 命令行 |
| ⚡ | **轻量部署** | 单文件服务端，一条命令启动 |

---

## 🚀 快速部署

### 一键安装（推荐）

```bash
git clone https://github.com/FeynmanNddbb/imgup.git
cd imgup
sudo bash install.sh
```

**安装脚本会询问你：**
1. 图片存储目录（默认 `/data/images`）
2. 你的域名（例如 `https://images.mydomain.com`）
3. 监听端口（默认 `8765`）
4. 自动生成随机 Token

**安装脚本会自动完成：**
- ✅ 创建 systemd 服务并启动
- ✅ 自动检测并配置反向代理（按优先级：Caddy > Nginx > Apache > Traefik）
- ✅ 配置上传客户端命令 `imgup`

> **你只需要运行一次安装脚本，所有配置自动完成！**

---

### 手动安装

如果需要手动安装或自定义配置：

<details>
<summary><b>展开查看手动安装步骤</b></summary>

#### 1. 复制文件并配置服务

```bash
# 复制服务端文件
sudo cp server.py /opt/imgup/server.py
sudo cp imgup.service /etc/systemd/system/

# 编辑配置（修改域名和 Token）
sudo nano /etc/systemd/system/imgup.service

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable --now imgup
```

#### 2. 配置 Web 服务器

**Caddy：**

```caddy
# /etc/caddy/Caddyfile
images.your-domain.com {
    encode gzip zstd

    handle /upload {
        reverse_proxy 127.0.0.1:8765
    }

    handle {
        root * /data/images
        file_server browse
    }
}
```

```bash
sudo systemctl reload caddy
```

**Nginx：**

```nginx
# /etc/nginx/sites-available/imgup
server {
    listen 80;
    server_name images.your-domain.com;

    location /upload {
        proxy_pass http://127.0.0.1:8765;
        client_max_body_size 20M;
    }

    location / {
        root /data/images;
        autoindex on;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/imgup /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

</details>

---

## 💻 客户端使用

### 🖥️ Windows — 图形界面（推荐）

1. 在 [Releases](https://github.com/FeynmanNddbb/imgup/releases) 下载 `imgup.exe`，或自行[打包](打包说明.md)
2. 双击运行，首次启动自动弹出配置向导
3. 输入图床域名（自动补全 `https://`）和 Token
4. 点击 **"选择图片并上传"**，完成后链接自动复制到剪贴板

> 配置保存在 `imgup_config.json`，修改后重启程序生效

### 🐧 Linux / 🍎 macOS — 命令行

```bash
# 设置配置（加入 ~/.bashrc 或 ~/.zshrc，之后无需重复设置）
export IMGUP_URL="https://images.your-domain.com/upload"
export IMGUP_TOKEN="your_token_here"
source ~/.bashrc

# 上传单张图片
./upload.sh photo.jpg

# 批量上传
./upload.sh *.png *.jpg

# 上传后自动复制链接到剪贴板 ✓
```

**截图直传（macOS）：**

```bash
screencapture -i /tmp/shot.png && ./upload.sh /tmp/shot.png
```

**截图直传（Linux）：**

```bash
scrot -s /tmp/shot.png && ./upload.sh /tmp/shot.png
```

### 🌐 curl / 脚本集成

```bash
curl -X POST https://images.your-domain.com/upload \
  -H "X-Upload-Token: your_token" \
  -F "file=@photo.jpg"
```

```json
{
  "url": "https://images.your-domain.com/2026-07-18/photo.jpg",
  "filename": "photo.jpg",
  "date": "2026-07-18",
  "size": 204800
}
```

---

## ⚙️ 配置说明

### 📌 必须修改的配置项

**无论使用哪种方式部署，以下两个配置都必须修改为你自己的：**

| 配置项 | 默认占位符 | 你需要改成 | 说明 |
|--------|-----------|----------|------|
| **域名** | `https://images.example.com` | `https://images.你的域名.com` | 图床的公网访问地址 |
| **Token** | `change_me_please` | 随机字符串（建议32位以上） | 上传密钥，防止他人盗用 |

---

### 🖥️ 服务端配置（必须）

**方式一：使用安装脚本（推荐）**

运行 `bash install.sh` 时会交互式询问：
- 存储目录
- 你的域名（例如：`images.example.com`）
- 监听端口
- 脚本自动生成随机 Token

**方式二：手动修改配置文件**

编辑 `/etc/systemd/system/imgup.service`，找到以下两行：

```bash
Environment=UPLOAD_TOKEN=change_me_please      # ← 改成你的随机 Token
Environment=BASE_URL=https://images.example.com # ← 改成你的域名
```

**示例：**

```bash
Environment=UPLOAD_TOKEN=a7f3c9e2b8d14f6a95e8c7b3d2f1a9e4c6b8d5f2  # ← 你的随机Token
Environment=BASE_URL=https://images.mydomain.com                   # ← 你的域名
```

**生成安全 Token：**

```bash
openssl rand -hex 32
# 输出类似：a7f3c9e2b8d14f6a95e8c7b3d2f1a9e4c6b8d5f2a9c1e3b7d4f6a8c2e5b9d1f3
```

修改后重启服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart imgup
```

---

### 💻 客户端配置

#### Windows（imgup.exe）

**首次启动自动配置：**

1. 双击 `imgup.exe`
2. 弹出配置向导，输入：
   - **图床域名**：只输入域名部分（例如 `images.mydomain.com`），程序自动补全 `https://` 和 `/upload`
   - **Token**：从服务器配置中复制你设置的 Token

**后续修改配置：**

方式1：点击程序内 "⚙️ 重新配置" 按钮

方式2：编辑 `imgup_config.json` 文件（与 exe 同目录）：

```json
{
  "url": "https://images.mydomain.com/upload",  ← 改成你的域名
  "token": "a7f3c9e2b8d14f6a...",                ← 改成你的Token
  "version": "1.0"
}
```

修改后重启程序生效。

---

#### Linux / macOS（upload.sh）

编辑 `~/.bashrc` 或 `~/.zshrc`，添加：

```bash
export IMGUP_URL="https://images.mydomain.com/upload"   # ← 改成你的域名
export IMGUP_TOKEN="a7f3c9e2b8d14f6a..."                # ← 改成你的Token
```

保存后重新加载：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

之后直接使用 `./upload.sh photo.jpg` 上传。

---

### 🔍 配置检查清单

部署完成后，确认以下配置已修改：

- [ ] 服务端 `imgup.service` 中的 `UPLOAD_TOKEN` 已改为随机字符串
- [ ] 服务端 `imgup.service` 中的 `BASE_URL` 已改为你的域名
- [ ] 客户端配置中的域名和 Token 与服务端**完全一致**
- [ ] Web 服务器（Caddy/Nginx）中的域名已配置并解析生效
- [ ] 防火墙允许 80/443 端口访问

---

### 📋 完整环境变量列表

服务端 `imgup.service` 可配置的所有环境变量：

| 变量 | 默认值 | 说明 | 是否必改 |
|------|--------|------|---------|
| `UPLOAD_DIR` | `/data/images` | 图片存储目录 | 可选 |
| `UPLOAD_TOKEN` | `change_me_please` | 上传鉴权密钥 | ✅ **必须** |
| `BASE_URL` | `https://images.example.com` | 你的图床域名 | ✅ **必须** |
| `PORT` | `8765` | 监听端口（仅本地） | 可选 |
| `MAX_SIZE_MB` | `20` | 单文件最大体积（MB） | 可选 |

---

## 📁 存储结构

```
/data/images/
├── 2026-07-16/
│   └── logo.svg
├── 2026-07-17/
│   ├── banner.jpg
│   └── screenshot.png
└── 2026-07-18/
    ├── photo.jpg
    └── photo_a1b2c3d4.jpg   ← 重名时自动追加 hash
```

---

## 📋 API 参考

### `GET /health` — 健康检查

```json
{ "status": "ok", "upload_dir": "/data/images" }
```

### `POST /upload` — 上传图片

**请求头：**

```
X-Upload-Token: <your_token>
Content-Type: multipart/form-data
```

**表单字段：** `file` — 图片文件

**支持格式：** `.jpg` `.jpeg` `.png` `.gif` `.webp` `.svg` `.bmp` `.avif` `.ico`

**响应：**

```json
{
  "url": "https://images.your-domain.com/2026-07-18/photo.jpg",
  "filename": "photo.jpg",
  "date": "2026-07-18",
  "size": 204800
}
```

---

## 🔧 服务管理

```bash
sudo systemctl status imgup     # 查看运行状态
sudo systemctl restart imgup    # 重启服务
sudo journalctl -u imgup -f     # 实时查看日志
```

---

## 🔒 安全建议

- 使用 `openssl rand -hex 32` 生成强 Token，不要使用弱密码
- 生产环境必须启用 HTTPS（Caddy 可自动申请证书）
- 限制上传端口只允许本地访问：`ufw allow from 127.0.0.1 to any port 8765`

---

## 📄 License

[MIT](LICENSE) © 2026 [FeynmanNddbb](https://github.com/FeynmanNddbb)

---

<div align="center">

**[⬆ 回到顶部](#imgup-️)**

</div>
