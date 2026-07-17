# imgup 🖼️

<div align="center">

**轻量级自托管图片上传服务**

零依赖 · 日期归档 · 跨平台客户端

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()

</div>

---

## 📖 简介

imgup 是一个纯 Python 标准库实现的图片上传服务，无需任何第三方依赖。上传的图片自动按日期归档到 `YYYY-MM-DD/` 文件夹，配合 Caddy 或 Nginx 即可对外提供访问。

```
上传 photo.jpg  →  https://images.example.com/2026-07-17/photo.jpg
```

## ✨ 特性

<table>
<tr>
<td>

**服务端**
- 🚀 零依赖，纯 Python 3 标准库
- 📅 自动日期归档 `YYYY-MM-DD/`
- 🔒 Token 认证保护
- 🔄 防重名（MD5 hash）
- 🌐 CORS 跨域支持
- 📦 多格式支持（jpg/png/gif/webp/svg/...）

</td>
<td>

**客户端**
- 🖥️ Windows 图形界面（双击即用）
- 🐧 Linux/Mac Shell 脚本
- 📋 自动复制链接到剪贴板
- 📊 实时上传进度显示
- 🔢 批量上传支持
- 🌍 Web API 调用

</td>
</tr>
</table>

## 🎯 快速开始

### 服务端部署

#### 一键安装（推荐）

```bash
git clone https://github.com/yourusername/imgup.git
cd imgup
bash install.sh
```

安装脚本会自动：
- ✅ 询问配置（上传目录、域名、端口）
- ✅ 生成随机 Token
- ✅ 注册并启动 systemd 服务
- ✅ 创建 `imgup` 命令到 `/usr/local/bin`

#### 手动安装

```bash
# 1. 复制文件
sudo cp server.py /opt/imgup/server.py
sudo cp imgup.service /etc/systemd/system/imgup.service

# 2. 编辑配置
sudo nano /etc/systemd/system/imgup.service

# 3. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable --now imgup
sudo systemctl status imgup
```

### 客户端配置

<details>
<summary><b>🖥️ Windows 图形界面（推荐新手）</b></summary>

#### 步骤 1：配置服务器信息

编辑 `upload_gui.py` 文件第 17-18 行：

```python
DEFAULT_URL = "https://your-server.com/upload"
DEFAULT_TOKEN = "your_secret_token"
```

#### 步骤 2：启动程序

双击 `上传图片.bat` 文件

#### 步骤 3：选择并上传

点击 **"📂 选择图片并上传"** 按钮，选择图片文件（支持多选）

![Windows GUI](https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Windows+GUI+Upload+Tool)

**功能亮点：**
- ✨ 零学习成本，双击即用
- 📦 批量上传多个文件
- 📋 自动复制链接到剪贴板
- 📊 实时日志显示
- 🔧 支持配置保存

📚 [详细使用说明 →](WINDOWS_GUI.md)

</details>

<details>
<summary><b>🐧 Linux/Mac Shell 脚本（推荐开发者）</b></summary>

```bash
# 1. 设置环境变量（加入 ~/.bashrc 或 ~/.zshrc）
export IMGUP_URL="https://images.example.com/upload"
export IMGUP_TOKEN="your_token_here"

# 2. 上传单张图片
./upload.sh photo.jpg

# 3. 批量上传
./upload.sh *.png

# 4. 快速截图并上传（macOS）
screencapture -i /tmp/screenshot.png && ./upload.sh /tmp/screenshot.png
```

上传成功后自动复制链接到剪贴板。

</details>

<details>
<summary><b>🌐 curl 命令行</b></summary>

```bash
curl -X POST https://images.example.com/upload \
  -H "X-Upload-Token: your_token_here" \
  -F "file=@/path/to/image.jpg"
```

**返回示例：**

```json
{
  "url": "https://images.example.com/2026-07-17/photo.jpg",
  "filename": "photo.jpg",
  "date": "2026-07-17",
  "size": 204800
}
```

</details>

<details>
<summary><b>💻 JavaScript/TypeScript</b></summary>

```javascript
async function uploadImage(file, token) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("https://images.example.com/upload", {
    method: "POST",
    headers: { "X-Upload-Token": token },
    body: formData,
  });

  const data = await response.json();
  return data.url; // https://images.example.com/2026-07-17/photo.jpg
}

// 使用示例
const input = document.querySelector('input[type="file"]');
input.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  const url = await uploadImage(file, "your_token");
  console.log("上传成功:", url);
});
```

</details>

## ⚙️ 配置

所有配置通过环境变量传入（在 `imgup.service` 中修改）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `UPLOAD_DIR` | `/data/images` | 文件存储根目录 |
| `UPLOAD_TOKEN` | `change_me_please` | 上传鉴权 Token（**务必修改**） |
| `BASE_URL` | `https://images.example.com` | 公网访问域名 |
| `PORT` | `8765` | 监听端口（仅本地 127.0.0.1） |
| `MAX_SIZE_MB` | `20` | 单文件最大体积（MB） |

修改后重启服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart imgup
```

## 🌐 Web 服务器配置

### Caddy（推荐）

在 `/etc/caddy/Caddyfile` 中添加：

```caddy
images.example.com {
    encode gzip zstd

    # 上传接口代理
    handle /upload {
        reverse_proxy 127.0.0.1:8765
    }

    # 健康检查
    handle /health {
        reverse_proxy 127.0.0.1:8765
    }

    # 静态文件浏览
    handle {
        root * /data/images
        file_server browse
    }
}
```

重载配置：

```bash
caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name images.example.com;

    # SSL 配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 上传接口
    location /upload {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 20M;
    }

    # 静态文件
    location / {
        root /data/images;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
}
```

## 📁 文件结构

```
/data/images/
├── 2026-07-15/
│   ├── screenshot.png
│   └── banner.jpg
├── 2026-07-16/
│   └── logo.svg
└── 2026-07-17/
    ├── photo.jpg
    └── photo_a1b2c3d4.jpg   ← 重名时自动加 hash
```

## 📋 API 参考

### `GET /health`

健康检查

**响应示例：**

```json
{
  "status": "ok",
  "upload_dir": "/data/images"
}
```

### `POST /upload`

上传图片

**请求头：**

```
Content-Type: multipart/form-data
X-Upload-Token: your_token
```

**表单字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | File | 图片文件 |

**支持格式：**

`.jpg` `.jpeg` `.png` `.gif` `.webp` `.svg` `.bmp` `.avif` `.ico`

**响应示例：**

```json
{
  "url": "https://images.example.com/2026-07-17/photo.jpg",
  "filename": "photo.jpg",
  "date": "2026-07-17",
  "size": 204800
}
```

**错误响应：**

```json
{
  "error": "unauthorized: invalid token"
}
```

## 🔧 服务管理

```bash
# 查看状态
sudo systemctl status imgup

# 重启服务
sudo systemctl restart imgup

# 停止服务
sudo systemctl stop imgup

# 查看实时日志
sudo journalctl -u imgup -f

# 查看最近日志
sudo journalctl -u imgup -n 100
```

## 🛠️ 开发与扩展

### 本地开发

```bash
# 设置环境变量
export UPLOAD_DIR="./uploads"
export UPLOAD_TOKEN="test_token"
export BASE_URL="http://localhost:8765"
export PORT="8765"

# 启动开发服务器
python3 server.py
```

### 自定义客户端

imgup 使用标准的 HTTP multipart/form-data 协议，可以轻松集成到任何语言：

<details>
<summary>Python 示例</summary>

```python
import requests

def upload_image(file_path, url, token):
    with open(file_path, "rb") as f:
        files = {"file": f}
        headers = {"X-Upload-Token": token}
        response = requests.post(url, files=files, headers=headers)
        return response.json()

result = upload_image("photo.jpg", "https://images.example.com/upload", "your_token")
print(result["url"])
```

</details>

<details>
<summary>Go 示例</summary>

```go
package main

import (
    "bytes"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func uploadImage(filePath, url, token string) error {
    file, _ := os.Open(filePath)
    defer file.Close()

    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)
    part, _ := writer.CreateFormFile("file", filePath)
    io.Copy(part, file)
    writer.Close()

    req, _ := http.NewRequest("POST", url, body)
    req.Header.Set("Content-Type", writer.FormDataContentType())
    req.Header.Set("X-Upload-Token", token)

    client := &http.Client{}
    resp, err := client.Do(req)
    return err
}
```

</details>

## 🔒 安全建议

1. **强 Token**：使用随机生成的长 Token
   ```bash
   openssl rand -hex 32
   ```

2. **HTTPS**：生产环境务必启用 SSL
   ```bash
   # 使用 Caddy 自动获取证书
   caddy run --config /etc/caddy/Caddyfile
   ```

3. **防火墙**：仅允许 Web 服务器访问上传端口
   ```bash
   sudo ufw allow from 127.0.0.1 to any port 8765
   ```

4. **文件权限**：限制上传目录权限
   ```bash
   sudo chown -R www-data:www-data /data/images
   sudo chmod -R 755 /data/images
   ```

5. **备份**：定期备份图片目录
   ```bash
   rsync -avz /data/images/ backup@server:/backup/images/
   ```

## 📊 监控

### Prometheus Exporter

可以添加 `/metrics` 端点导出指标：

```python
# 在 server.py 中添加
def do_GET(self):
    if self.path == "/metrics":
        metrics = f"""
# HELP imgup_uploads_total Total number of uploads
# TYPE imgup_uploads_total counter
imgup_uploads_total {upload_count}

# HELP imgup_upload_bytes_total Total bytes uploaded
# TYPE imgup_upload_bytes_total counter
imgup_upload_bytes_total {total_bytes}
"""
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(metrics.encode())
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

**[⬆ 回到顶部](#imgup-️)**

Made with ❤️ by [Your Name](https://github.com/yourusername)

</div>
