# imgup Windows 图形上传工具 - 使用指南

## 📦 已添加的文件

1. **upload_gui.py** - 图形界面上传程序（Python 脚本）
2. **上传图片.bat** - Windows 启动脚本（双击运行）
3. **Windows使用说明.md** - 详细使用说明

## 🚀 快速使用

### 第一步：配置服务器信息

在 `upload_gui.py` 文件的第 17-18 行修改默认配置：

```python
DEFAULT_URL = "https://your-server.com/upload"  # 你的服务器地址
DEFAULT_TOKEN = "your_secret_token"              # 你的上传 Token
```

### 第二步：启动程序

**方式1（推荐）：** 双击 `上传图片.bat` 文件

**方式2：** 在命令行运行：
```cmd
python upload_gui.py
```

或使用无窗口模式：
```cmd
pythonw upload_gui.py
```

### 第三步：上传图片

1. 在打开的窗口中确认服务器地址和 Token
2. 点击 "📂 选择图片并上传" 按钮
3. 选择一个或多个图片文件（支持多选）
4. 等待上传完成
5. 上传成功后，所有图片链接会自动复制到剪贴板

## ✨ 功能特性

- ✅ **纯图形界面** - 无需命令行操作，双击即用
- ✅ **批量上传** - 支持同时选择多个图片文件
- ✅ **实时日志** - 显示详细的上传进度和结果
- ✅ **自动复制** - 上传成功后链接自动复制到剪贴板
- ✅ **配置灵活** - 支持代码配置、环境变量、界面临时配置
- ✅ **格式检查** - 自动验证文件格式和大小
- ✅ **错误提示** - 清晰的错误信息和解决建议
- ✅ **零依赖** - 仅使用 Python 标准库，无需安装任何包

## 🖼️ 界面说明

```
┌─────────────────────────────────────────────┐
│  imgup - 图片上传工具                        │
├─────────────────────────────────────────────┤
│  配置                                        │
│  ┌───────────────────────────────────────┐  │
│  │ 服务器地址: [                        ]│  │
│  │ 上传 Token: [********************] ☐显示│  │
│  └───────────────────────────────────────┘  │
│                                              │
│  [📂 选择图片并上传]  [清空日志]            │
│                                              │
│  上传日志                                    │
│  ┌───────────────────────────────────────┐  │
│  │ ============================================│
│  │ imgup Windows 上传工具                  │
│  │ ============================================│
│  │ 支持格式: .jpg, .png, .gif, ...        │
│  │ 点击 [选择图片并上传] 开始              │
│  │                                         │
│  │ 正在上传: photo.jpg (204,800 字节)     │
│  │ ✓ 成功: https://...                    │
│  │   文件名: photo.jpg | 大小: 204,800 B  │
│  └───────────────────────────────────────┘  │
│  就绪 — 点击按钮选择图片                    │
└─────────────────────────────────────────────┘
```

## 🔧 配置选项

### 默认配置修改

编辑 `upload_gui.py`，修改：

```python
DEFAULT_URL = "https://images.lovecode.xin/upload"
DEFAULT_TOKEN = "change_me_please"
```

### 环境变量配置

设置系统环境变量（优先级高于默认配置）：

```cmd
# 临时设置（当前命令行窗口有效）
set IMGUP_URL=https://your-server.com/upload
set IMGUP_TOKEN=your_token
python upload_gui.py

# 永久设置（所有新窗口生效）
setx IMGUP_URL "https://your-server.com/upload"
setx IMGUP_TOKEN "your_token"
```

### 界面临时配置

启动程序后直接在配置区域修改（不保存）。

## 📝 支持的图片格式

- **常用格式**: .jpg, .jpeg, .png, .gif
- **现代格式**: .webp, .avif
- **矢量图**: .svg
- **其他**: .bmp, .ico

## ❓ 常见问题

### 双击 bat 文件没反应？

1. 确保已安装 Python 3
   - Windows 10/11 可从 Microsoft Store 安装
   - 或访问 https://www.python.org/downloads/

2. 验证 Python 安装：
   ```cmd
   python --version
   ```

3. 尝试右键 → 以管理员身份运行

### 提示 "上传失败 (401)"？

- Token 错误，检查服务器的 `UPLOAD_TOKEN` 配置
- 确保配置中的 Token 与服务器一致

### 提示 "网络错误"？

- 检查服务器地址是否正确（需要包含 `/upload` 路径）
- 确认服务器正在运行：`systemctl status imgup`
- 测试服务器连通性：`curl https://your-server.com/health`

### 提示 "不支持的文件格式"？

- 只支持图片格式，不支持视频、文档等
- 检查文件扩展名是否在支持列表中

### 上传成功但无法访问图片？

- 检查服务器的 `BASE_URL` 环境变量配置
- 确认 Caddy/Nginx 已配置静态文件服务
- 检查文件权限：`ls -l /data/images/`

## 🔍 技术细节

- **语言**: Python 3 (标准库)
- **GUI 框架**: tkinter (内置)
- **HTTP 客户端**: urllib (内置)
- **编码**: UTF-8
- **协议**: multipart/form-data
- **认证**: X-Upload-Token 请求头

## 📚 相关文档

- 服务器部署: 参见主 `README.md`
- Shell 客户端: 使用 `upload.sh` (Linux/Mac)
- API 文档: 参见主 `README.md` 的 API 参考部分
