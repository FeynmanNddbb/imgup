<div align="center">
  <img src="./imgup.png" alt="imgup logo" width="150">

# imgup

### 一次安装配置，永久便捷上传的自托管图床

把图片上传到自己的服务器，返回稳定可长期引用的 HTTPS 链接。适合博客、Markdown、知识库、团队文档、截图分享和自动化脚本调用。

[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Client](https://img.shields.io/badge/Client-Windows%20%7C%20Linux%20%7C%20macOS-6366f1?style=for-the-badge)]()
[![Self Hosted](https://img.shields.io/badge/Self--Hosted-Yes-0ea5e9?style=for-the-badge)]()

```text
本地图片  ->  imgup  ->  https://images.example.com/2026-07-18/photo.jpg
```

[快速开始](#快速开始) ·
[客户端使用](#客户端使用) ·
[配置参考](#配置参考) ·
[API](#api-参考) ·
[常见问题](#常见问题)

</div>

---

## 为什么用 imgup

imgup 是一个轻量、安全、完全自托管的图片上传服务。服务端只依赖 Python 标准库，客户端覆盖 Windows、Linux 和 macOS，配置一次后就能长期稳定上传。

| 优点 | 说明 |
| --- | --- |
| 一次安装配置 | 服务端安装脚本自动配置 systemd、存储目录、Token 和反向代理 |
| 永久便捷上传 | Windows 双击上传，Linux/macOS 使用 `imgup photo.jpg`，无需每次填写 URL 和 Token |
| 稳定调用 | 上传接口固定、返回 JSON 稳定，适合脚本、CI、Markdown 工具和截图工作流 |
| 中文路径友好 | 客户端按文件原路径提交，支持中文文件名、中文目录和带空格路径 |
| 自托管存储 | 图片保存在自己的服务器目录，例如 `/data/images`，数据不托管给第三方 |
| Token 鉴权 | 只有携带正确 `X-Upload-Token` 的请求可以上传 |
| 自动日期归档 | 图片按 `YYYY-MM-DD/` 分目录保存，链接清晰可维护 |
| 防重名覆盖 | 同名文件自动追加短 hash，避免覆盖历史图片 |
| 多平台客户端 | Windows GUI、Linux/macOS 命令行、curl/API 都可用 |

---

## 快速开始

### 1. 准备域名

准备一个独立子域名作为图床域名：

```text
images.example.com
```

输入域名时不需要带 `https://`。安装脚本和客户端都会自动补全为：

```text
https://images.example.com/upload
```

### 2. 添加 DNS 解析

在域名服务商后台添加一条 `A` 记录：

| 类型 | 主机记录 | 记录值 |
| --- | --- | --- |
| `A` | `images` | 你的服务器公网 IP |

等待解析生效后检查：

```bash
ping images.example.com
```

### 3. 安装服务端

在服务器上执行：

```bash
git clone https://github.com/FeynmanNddbb/imgup.git
cd imgup
sudo bash install.sh
```

安装过程会询问：

| 项目 | 示例 | 说明 |
| --- | --- | --- |
| 图片存储目录 | `/data/images` | 图片最终保存位置 |
| 图床域名 | `images.example.com` | 不需要输入 `https://` |
| 监听端口 | `8765` | 只由本机反向代理访问 |
| 上传 Token | 自动生成 | 请保存，用于客户端上传 |

安装脚本会自动完成：

- 创建并启动 `imgup.service`
- 配置图片存储目录
- 生成随机上传 Token
- 检测并配置 Caddy / Nginx / Apache
- 安装命令行客户端 `imgup`
- 监听服务配置变更，修改后自动 reload 并重启服务

安装完成后会输出：

```text
图床地址 : https://images.example.com
Token    : <your_token>
配置文件 : /etc/systemd/system/imgup.service
```

保存好 Token，客户端上传必须使用同一个 Token。

---

## 客户端使用

### Windows 图形客户端

在 [Releases](https://github.com/FeynmanNddbb/imgup/releases) 下载 Windows 客户端，双击即可使用。新版 exe 已内置 `imgup.png` 作为应用图标。

```text
imgup-windows-x64-v1.0.0.exe
```

首次启动会弹出配置向导：

| 配置项 | 示例 |
| --- | --- |
| 图床域名 | `images.example.com` |
| Token | 安装脚本输出的 Token |

配置完成后，点击“选择图片并上传”，上传成功后链接会自动复制到剪贴板。需要更换服务器或 Token 时，在客户端内点击“重新配置”即可。

### Linux / macOS 命令行

首次使用先配置一次：

```bash
chmod +x configure.sh upload.sh
./configure.sh
```

配置脚本会写入与 Windows 客户端一致的 `imgup_config.json`：

```json
{
  "url": "https://images.example.com/upload",
  "token": "your_token_here",
  "version": "1.0"
}
```

之后永久便捷上传：

```bash
./upload.sh photo.jpg
./upload.sh "中文目录/测试图片.png"
./upload.sh *.png *.jpg
```

如果服务端安装脚本已把客户端安装为全局命令，也可以直接调用：

```bash
imgup photo.jpg
```

查看当前配置：

```bash
./configure.sh --show
```

临时覆盖配置：

```bash
IMGUP_URL="images.example.com" IMGUP_TOKEN="your_token_here" ./upload.sh photo.jpg
```

macOS 截图后上传：

```bash
screencapture -i /tmp/shot.png && imgup /tmp/shot.png
```

Linux 截图后上传：

```bash
scrot -s /tmp/shot.png && imgup /tmp/shot.png
```

### curl / 稳定 API 调用

```bash
curl -X POST https://images.example.com/upload \
  -H "X-Upload-Token: your_token_here" \
  -F "file=@photo.jpg"
```

成功响应：

```json
{
  "url": "https://images.example.com/2026-07-18/photo.jpg",
  "filename": "photo.jpg",
  "date": "2026-07-18",
  "size": 204800
}
```

---

## 配置参考

服务端配置文件：

```text
/etc/systemd/system/imgup.service
```

主要环境变量：

| 变量 | 示例 | 说明 |
| --- | --- | --- |
| `UPLOAD_DIR` | `/data/images` | 图片存储目录 |
| `UPLOAD_TOKEN` | `openssl rand -hex 32` 生成值 | 上传鉴权 Token |
| `BASE_URL` | `https://images.example.com` | 图片公开访问域名 |
| `PORT` | `8765` | Python 服务监听端口 |
| `MAX_SIZE_MB` | `20` | 单文件最大上传体积 |

手动修改示例：

```ini
Environment=UPLOAD_DIR=/data/images
Environment=UPLOAD_TOKEN=your_token_here
Environment=BASE_URL=https://images.example.com
Environment=PORT=8765
Environment=MAX_SIZE_MB=20
```

当前版本安装后会启用配置监听器。修改 `imgup.service` 后，系统会自动执行：

```bash
systemctl daemon-reload
systemctl restart imgup.service
```

如果没有使用安装脚本部署，手动修改后请执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart imgup
```

生成强 Token：

```bash
openssl rand -hex 32
```

---

## 反向代理配置

安装脚本会自动配置常见 Web 服务器。需要手动配置时，可以参考下面示例。

### Caddy

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

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

### Nginx

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

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 存储结构

```text
/data/images/
├── 2026-07-16/
│   └── logo.svg
├── 2026-07-17/
│   ├── banner.jpg
│   └── screenshot.png
└── 2026-07-18/
    ├── photo.jpg
    └── photo_a1b2c3d4.jpg
```

同名文件不会覆盖，服务端会自动追加短 hash。

---

## API 参考

### 健康检查

```http
GET /health
```

响应：

```json
{
  "status": "ok",
  "upload_dir": "/data/images"
}
```

### 上传图片

```http
POST /upload
X-Upload-Token: your_token_here
Content-Type: multipart/form-data
```

表单字段：

| 字段 | 说明 |
| --- | --- |
| `file` | 要上传的图片文件 |

支持格式：

```text
.jpg .jpeg .png .gif .webp .svg .bmp .avif .ico
```

---

## 服务管理

```bash
sudo systemctl status imgup
sudo systemctl restart imgup
sudo journalctl -u imgup -f
```

查看配置监听器：

```bash
sudo systemctl status imgup-config-reload.path
```

---

## 常见问题

### 上传返回 401 unauthorized

表示客户端 Token 和服务端 `UPLOAD_TOKEN` 不一致。

检查服务端配置：

```bash
sudo systemctl show imgup -p Environment --no-pager
```

检查客户端配置：

```bash
echo "$IMGUP_TOKEN"
```

Windows 客户端请检查 `imgup_config.json` 或点击“重新配置”。

### 修改 service 文件后还是旧配置

使用安装脚本部署时，`imgup-config-reload.path` 会自动监听配置变更并重启服务。

如果你是旧版本部署，可以手动执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart imgup
```

### 返回链接没有 https

确认服务端 `BASE_URL` 带协议：

```ini
Environment=BASE_URL=https://images.example.com
```

安装脚本允许输入裸域名，但最终会自动写入 `https://...`。

### 域名无法访问

依次检查：

- DNS `A` 记录是否指向服务器公网 IP
- 服务器 80 / 443 端口是否开放
- Caddy / Nginx 是否 reload 成功
- `/upload` 是否正确反向代理到 `127.0.0.1:8765`

---

## 安全建议

- 使用 `openssl rand -hex 32` 生成 Token
- 不要把 Token 写进公开仓库
- 生产环境使用 HTTPS，推荐 Caddy 自动签发证书
- Python 服务端口只监听本机，由 Caddy / Nginx 对外提供访问
- 定期备份 `/data/images`

---

## License

[MIT](LICENSE) © 2026 [FeynmanNddbb](https://github.com/FeynmanNddbb)
