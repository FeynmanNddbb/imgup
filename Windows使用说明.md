# imgup Windows 上传工具 - 配置说明

## 快速开始

1. 双击 `上传图片.bat` 启动程序
2. 在界面中填写你的服务器地址和 Token
3. 点击 "选择图片并上传"

## 配置方法

### 方法一：修改代码默认值（推荐）

编辑 `upload_gui.py` 文件，修改第 17-18 行：

```python
DEFAULT_URL = "https://images.lovecode.xin/upload"  # 改成你的服务器地址
DEFAULT_TOKEN = "change_me_please"                   # 改成你的 Token
```

### 方法二：设置环境变量

在 Windows 系统中设置环境变量：

```cmd
setx IMGUP_URL "https://your-domain.com/upload"
setx IMGUP_TOKEN "your_token_here"
```

设置后重启程序即可生效。

### 方法三：界面中临时修改

启动程序后，直接在配置区域填写（不会保存，下次启动需要重新填写）。

## 常见问题

**Q: 双击 bat 文件没反应？**
- 确保已安装 Python 3
- 尝试右键 → 以管理员身份运行

**Q: 提示 "上传失败 401"？**
- Token 填写错误，检查服务器配置

**Q: 提示 "网络错误"？**
- 检查服务器地址是否正确
- 确保服务器正在运行且可访问

**Q: 上传成功但无法访问图片？**
- 检查服务器的 BASE_URL 配置
- 确认 Caddy 或 Nginx 已正确配置静态文件服务

## 支持的图片格式

jpg, jpeg, png, gif, webp, svg, bmp, avif, ico

## 技术说明

- 使用 Python 标准库 tkinter 构建图形界面
- 纯 Python 3 标准库实现，无需安装任何第三方依赖
- 使用 urllib 发送 HTTP 请求，兼容所有 Python 3.x 版本
