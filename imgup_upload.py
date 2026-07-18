#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imgup 上传工具 - 命令行版本
用法:
  python imgup_upload.py image.png
  python imgup_upload.py img1.jpg img2.png img3.gif
  python imgup_upload.py *.jpg
"""

import os
import sys
import json
import mimetypes
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


CONFIG_FILE = "imgup_config.json"

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif", ".ico"}


def get_config_path():
    """获取配置文件路径（脚本所在目录）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, CONFIG_FILE)


def load_config():
    """加载配置文件"""
    config_path = get_config_path()

    if not os.path.exists(config_path):
        print("错误：找不到配置文件，请先运行 imgup_config.py 进行配置")
        print(f"  期望路径: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"错误：读取配置文件失败：{e}")
        sys.exit(1)

    url = config.get("url", "")
    token = config.get("token", "")

    if not url or "example.com" in url.lower():
        print("错误：配置的 URL 无效，请先运行 imgup_config.py 进行配置")
        sys.exit(1)

    if not token or token == "change_me_please":
        print("错误：配置的 Token 无效，请先运行 imgup_config.py 进行配置")
        sys.exit(1)

    return url, token


def create_multipart_data(file_path, boundary):
    """创建 multipart/form-data 请求体"""
    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = []
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    body.append(f"Content-Type: {mime_type}".encode())
    body.append(b"")
    body.append(file_data)
    body.append(f"--{boundary}--".encode())

    return b"\r\n".join(body)


def upload_file(file_path, url, token):
    """上传单个文件，返回 (success, result_or_error)"""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTS:
        return False, f"不支持的格式 {ext}，支持: {', '.join(sorted(ALLOWED_EXTS))}"

    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"

    file_size = os.path.getsize(file_path)

    try:
        boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
        body = create_multipart_data(file_path, boundary)

        req = Request(url, data=body, method="POST")
        req.add_header("X-Upload-Token", token)
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("Content-Length", str(len(body)))

        with urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return True, result

    except HTTPError as e:
        error_msg = e.read().decode("utf-8", errors="ignore")
        try:
            error_data = json.loads(error_msg)
            return False, f"服务器错误 ({e.code}): {error_data.get('error', error_msg)}"
        except Exception:
            return False, f"服务器错误 ({e.code}): {error_msg}"

    except URLError as e:
        return False, f"网络错误: {e.reason}"

    except Exception as e:
        return False, f"上传出错: {e}"


def main():
    if len(sys.argv) < 2:
        print("用法: python imgup_upload.py <图片文件> [图片文件2 ...]")
        print()
        print("示例:")
        print("  python imgup_upload.py photo.jpg")
        print("  python imgup_upload.py img1.png img2.jpg img3.webp")
        print()
        print(f"支持格式: {', '.join(sorted(ALLOWED_EXTS))}")
        return 1

    url, token = load_config()

    files = sys.argv[1:]
    print(f"服务器: {url}")
    print(f"共 {len(files)} 个文件待上传")
    print("-" * 60)

    success_count = 0
    fail_count = 0
    success_urls = []

    for i, file_path in enumerate(files, 1):
        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        print(f"[{i}/{len(files)}] {filename} ({size:,} 字节) ... ", end="", flush=True)

        ok, result = upload_file(file_path, url, token)

        if ok:
            link = result.get("url", "")
            success_urls.append(link)
            success_count += 1
            print(f"✓")
            print(f"        {link}")
        else:
            fail_count += 1
            print(f"✗")
            print(f"        {result}")

    print("-" * 60)
    print(f"完成：成功 {success_count} 个，失败 {fail_count} 个")

    if success_urls:
        print()
        print("全部链接：")
        for link in success_urls:
            print(f"  {link}")

        # 尝试复制到剪贴板（Windows）
        try:
            import subprocess
            text = "\n".join(success_urls)
            subprocess.run(
                ["clip"],
                input=text.encode("utf-8"),
                shell=True,
                check=True,
                capture_output=True,
            )
            print()
            print("✓ 链接已复制到剪贴板")
        except Exception:
            pass  # 剪贴板不可用时静默忽略

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
