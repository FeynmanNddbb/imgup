<div align="center">

# imgup

### 轻量、安全、完全自托管的图片上传服务

把本地图片一键上传到自己的服务器，并生成稳定可分享的 HTTPS 图片链接。

<br>

[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)
[![Client](https://img.shields.io/badge/Client-Windows%20%7C%20Linux%20%7C%20macOS-6366f1?style=flat)]()
[![GitHub Stars](https://img.shields.io/github/stars/FeynmanNddbb/imgup?style=flat&logo=github)](https://github.com/FeynmanNddbb/imgup/stargazers)

<br>

```text
photo.jpg  ->  imgup  ->  https://images.example.com/2026-07-18/photo.jpg
```

<br>

[部署流程](#部署流程) ·
[客户端使用](#客户端使用) ·
[配置参考](#配置参考) ·
[API](#api-参考) ·
[排查](#常见问题)

</div>

---

## 项目定位

imgup 是一个私有图床服务。图片存储在你的服务器上，上传接口通过 Token 保护，图片链接公开可访问，适合博客、Markdown 文档、团队资料、截图分享和轻量内容站点。

**核心特性**

| 能力 | 说明 |
| --- | --- |
| 自托管存储 | 图片保存到自己的服务器目录，例如 `/data/images` |
| Token 上传鉴权 | 只有携带正确 `X-Upload-Token` 的请求可以上传 |
| 自动日期归档 | 图片按 `YYYY-MM-DD/` 分目录保存 |
| 防重名覆盖 | 同名文件自动追加短 hash |
| 零服务端依赖 | 服务端只依赖 Python 3 标准库 |
| 自动反向代理配置 | 安装脚本优先适配 Caddy，其次 Nginx、Apache |
| 多平台客户端 | Windows GUI、Linux/macOS 命令行、curl/API |

---

## 部署流程

推荐按这个顺序操作：

```text
准备域名 -> 添加 DNS 解析 -> 安装服务端 -> 配置客户端 -> 上传验证
```

### 1. 准备域名

建议使用一个独立子域名作为图床域名，例如：

```text
images.example.com
img.example.com
pic.example.com
```

用户输入域名时不需要带 `https://`。安装脚本和客户端都会自动补全：

```text
images.example.com
```

会被规范化为：

```text
https://images.example.com/upload
```

### 2. 添加 DNS 解析

在你的域名服务商后台添加一条 `A` 记录：

| 类型 | 主机记录 | 记录值 |
| --- | --- | --- |
| `A` | `images` | 你的服务器公网 IP |

如果你使用 Cloudflare、阿里云、腾讯云等 DNS 服务，主机记录通常只填子域名前缀。例如图床域名是 `images.example.com`，主机记录填 `images`。

等待解析生效后，可以在本地检查：

```bash
ping images.example.com
```

解析到服务器公网 IP 即可继续部署。

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
- 监听 `/etc/systemd/system/imgup.service` 变更，配置修改后自动重启服务

安装完成后会输出：

```text
图床地址 : https://images.example.com
Token    : <your_token>
配置文件 : /etc/systemd/system/imgup.service
```

请把 Token 保存下来，客户端上传时必须使用同一个 Token。

---

## 客户端使用

### Windows 图形客户端

1. 在 [Releases](https://github.com/FeynmanNddbb/imgup/releases) 下载 `imgup.exe`，或参考 [打包说明](打包说明.md) 自行打包。
2. 首次启动会弹出配置向导。
3. 图床域名填写裸域名即可，例如：

```text
images.example.com
```

4. Token 填写安装脚本输出的 Token。
5. 点击“选择图片并上传”，上传成功后链接会自动复制到剪贴板。

配置文件位于 `imgup_config.json`，格式如下：

```json
{
  "url": "https://images.example.com/upload",
  "token": "your_token_here",
  "version": "1.0"
}
```

也可以在程序内点击“重新配置”更新域名和 Token。

### Linux / macOS 命令行

安装脚本会把客户端命令安装为：

```bash
imgup photo.jpg
```

如果你在其他机器上使用仓库里的 `upload.sh`，先配置环境变量：

```bash
export IMGUP_URL="images.example.com"
export IMGUP_TOKEN="your_token_here"
```

`IMGUP_URL` 可以只填裸域名，脚本会自动补全为 `https://images.example.com/upload`。

上传单张图片：

```bash
imgup photo.jpg
```

批量上传：

```bash
imgup *.png *.jpg
```

macOS 截图后上传：

```bash
screencapture -i /tmp/shot.png && imgup /tmp/shot.png
```

Linux 截图后上传：

```bash
scrot -s /tmp/shot.png && imgup /tmp/shot.png
```

### curl / 脚本集成

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
