#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imgup - 图片上传工具（交互式单文件版）"""

import os
import sys
import json
import mimetypes
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    except Exception:
        pass

CONFIG_FILE = "imgup_config.json"
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif", ".ico"}


def get_exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    return os.path.join(get_exe_dir(), CONFIG_FILE)


def has_tty():
    return sys.stdin is not None and sys.stdin.isatty()


def prompt_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        return None


def pick_files():
    try:
        from tkinter import Tk
        from tkinter.filedialog import askopenfilenames
    except Exception as e:
        print(f"  无法打开系统文件选择器: {e}")
        return None

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        files = askopenfilenames(
            title="选择要上传的图片",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.gif *.webp *.svg *.bmp *.avif *.ico"),
                ("All files", "*.*"),
            ],
        )
    finally:
        root.destroy()

    return list(files)


def pause_exit(message="按回车键退出..."):
    if has_tty():
        try:
            input(message)
            return
        except EOFError:
            return
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, "imgup", 0x00000040)
            return
        except Exception:
            try:
                import msvcrt
                print(message, end="", flush=True)
                msvcrt.getch()
                return
            except Exception:
                pass
    time.sleep(2)


def normalize_url(url):
    url = url.strip()
    for prefix in ["https://", "http://", "www."]:
        if url.lower().startswith(prefix):
            url = url[len(prefix):]
    url = url.rstrip("/")
    if not url.endswith("/upload"):
        url += "/upload"
    return "https://" + url


def load_config():
    try:
        with open(get_config_path(), "r", encoding="utf-8") as f:
            c = json.load(f)
        url = c.get("url", "")
        token = c.get("token", "")
        if url and "example.com" not in url.lower() and token and token != "change_me_please":
            return url, token
    except Exception:
        pass
    return None


def save_config(url, token):
    try:
        with open(get_config_path(), "w", encoding="utf-8") as f:
            json.dump({"url": url, "token": token, "version": "1.0"}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  保存失败: {e}")
        return False


def do_config():
    print()
    print("── 配置图床信息 ──────────────────────────────")
    existing = load_config()
    if existing:
        print(f"  当前 URL:   {existing[0]}")
        print(f"  当前 Token: {'*' * 20}")
        print()

    while True:
        prompt = "图床域名（例如 images.example.com）: "
        url_raw = prompt_input(prompt)
        if url_raw is None:
            print("  输入已结束，取消配置。")
            return
        url_input = url_raw.strip()
        if not url_input:
            if existing:
                url = existing[0]
                print("  → 保持原值")
                break
            print("  不能为空")
            continue
        try:
            url = normalize_url(url_input)
            print(f"  → {url}")
            break
        except Exception as e:
            print(f"  错误: {e}")

    while True:
        token_raw = prompt_input("上传 Token: ")
        if token_raw is None:
            print("  输入已结束，取消配置。")
            return
        token_input = token_raw.strip()
        if not token_input:
            if existing:
                token = existing[1]
                print("  → 保持原值")
                break
            print("  不能为空")
            continue
        token = token_input
        print("  → Token 已设置")
        break

    if save_config(url, token):
        print()
        print("✓ 配置已保存")


def create_multipart(file_path, boundary):
    filename = os.path.basename(file_path)
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        data = f.read()
    parts = [
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(),
        f"Content-Type: {mime}".encode(),
        b"",
        data,
        f"--{boundary}--".encode(),
    ]
    return b"\r\n".join(parts)


def upload_one(file_path, url, token):
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTS:
        return False, f"不支持的格式 {ext}"
    if not os.path.exists(file_path):
        return False, "文件不存在"
    try:
        boundary = "----Boundary" + os.urandom(8).hex()
        body = create_multipart(file_path, boundary)
        req = Request(url, data=body, method="POST")
        req.add_header("X-Upload-Token", token)
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("Content-Length", str(len(body)))
        with urlopen(req, timeout=30) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        try:
            msg = json.loads(msg).get("error", msg)
        except Exception:
            pass
        return False, f"服务器错误 ({e.code}): {msg}"
    except URLError as e:
        return False, f"网络错误: {e.reason}"
    except Exception as e:
        return False, str(e)


def do_upload():
    print()
    print("── 上传图片 ──────────────────────────────────")

    config = load_config()
    if not config:
        print("  未配置！请先选择 1 进行配置。")
        return

    url, token = config
    print(f"  服务器: {url}")
    print()
    print(f"  支持格式: {', '.join(sorted(ALLOWED_EXTS))}")
    print("  正在打开系统文件选择器...")

    files = pick_files()
    if files is None:
        return
    if not files:
        print("  已取消")
        return

    print()
    success_urls = []
    for i, fp in enumerate(files, 1):
        fp = fp.strip()
        name = os.path.basename(fp)
        size = os.path.getsize(fp) if os.path.exists(fp) else 0
        print(f"  [{i}/{len(files)}] {name} ({size:,} 字节) ...", end=" ", flush=True)
        ok, result = upload_one(fp, url, token)
        if ok:
            link = result.get("url", "")
            success_urls.append(link)
            print("✓")
            print(f"          {link}")
        else:
            print("✗")
            print(f"          {result}")

    print()
    print(f"  完成：成功 {len(success_urls)}/{len(files)}")

    if success_urls:
        try:
            import subprocess
            subprocess.run(["clip"], input="\n".join(success_urls).encode("utf-8"), shell=True, capture_output=True)
            print("  ✓ 链接已复制到剪贴板")
        except Exception:
            pass


def main():
    print("=" * 52)
    print("  imgup 图片上传工具")
    print("=" * 52)

    while True:
        config = load_config()
        status = config[0] if config else "未配置"
        print()
        print(f"  服务器: {status}")
        print()
        print("  1. 上传图片")
        print("  2. 修改配置")
        print("  0. 退出")
        print()

        choice_raw = prompt_input("  请选择 [1/2/0]: ")
        if choice_raw is None:
            print("\n  未检测到可用输入，程序结束。")
            break
        choice = choice_raw.strip()

        if choice == "1":
            do_upload()
        elif choice == "2":
            do_config()
        elif choice == "0":
            break
        else:
            print("  请输入 1、2 或 0")

    print()
    print("  再见！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已退出")
    except Exception as e:
        print(f"\n  程序错误: {e}")
        import traceback
        traceback.print_exc()
        pause_exit("\n  按回车键退出...")
