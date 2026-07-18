#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imgup - Windows GUI 上传工具（独立可执行版本）
双击运行，自动配置管理，支持打包为 exe
"""

import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import mimetypes
from pathlib import Path

# 配置文件名
CONFIG_FILE = "imgup_config.json"

# 默认占位符
DEFAULT_URL = "https://images.example.com/upload"
DEFAULT_TOKEN = "change_me_please"

# 支持的图片格式
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif", ".ico"}


def get_exe_dir():
    """获取 exe 所在目录（或脚本所在目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 exe
        return os.path.dirname(sys.executable)
    else:
        # 开发模式
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    """获取配置文件完整路径"""
    return os.path.join(get_exe_dir(), CONFIG_FILE)


def normalize_url(url):
    """标准化 URL - 防呆设计"""
    url = url.strip()

    # 移除可能的协议前缀
    for prefix in ["https://", "http://", "www."]:
        if url.lower().startswith(prefix):
            url = url[len(prefix):]

    # 移除尾部斜杠
    url = url.rstrip("/")

    # 确保有 /upload 路径
    if not url.endswith("/upload"):
        url = url + "/upload"

    # 添加 https 协议
    url = "https://" + url

    return url


def load_config():
    """加载配置文件"""
    config_path = get_config_path()

    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_path):
        default_config = {
            "url": DEFAULT_URL,
            "token": DEFAULT_TOKEN,
            "version": "1.0"
        }
        save_config(default_config)
        return default_config

    # 读取配置
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config
    except Exception as e:
        messagebox.showerror("配置错误", f"读取配置文件失败：{e}\n\n将使用默认配置。")
        return {"url": DEFAULT_URL, "token": DEFAULT_TOKEN, "version": "1.0"}


def save_config(config):
    """保存配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("保存失败", f"无法保存配置文件：{e}")
        return False


def is_placeholder_config(config):
    """判断配置是否为占位符"""
    return (config.get("url", "").lower().find("example.com") != -1 or
            config.get("token", "") == DEFAULT_TOKEN)


def show_first_time_setup():
    """首次启动配置向导"""
    dialog = tk.Toplevel()
    dialog.title("imgup - 首次配置向导")
    dialog.geometry("500x350")
    dialog.resizable(False, False)

    # 居中显示
    dialog.transient()
    dialog.grab_set()

    result = {"url": None, "token": None, "cancelled": False}

    # 说明文字
    tk.Label(
        dialog,
        text="欢迎使用 imgup 图片上传工具！",
        font=("Arial", 14, "bold"),
        fg="#2196F3"
    ).pack(pady=(20, 10))

    tk.Label(
        dialog,
        text="首次使用需要配置您的图床服务器信息",
        font=("Arial", 10)
    ).pack(pady=(0, 20))

    # 配置区域
    config_frame = tk.Frame(dialog)
    config_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)

    # 服务器域名
    tk.Label(config_frame, text="图床域名:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, sticky=tk.W, pady=(0, 5)
    )
    tk.Label(
        config_frame,
        text="（只需输入域名，例如：images.example.com）",
        font=("Arial", 8),
        fg="gray"
    ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

    url_var = tk.StringVar()
    url_entry = tk.Entry(config_frame, textvariable=url_var, width=40, font=("Arial", 10))
    url_entry.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
    url_entry.focus()

    # Token
    tk.Label(config_frame, text="上传 Token:", font=("Arial", 10, "bold")).grid(
        row=3, column=0, sticky=tk.W, pady=(0, 5)
    )
    tk.Label(
        config_frame,
        text="（从服务器配置中获取的密钥）",
        font=("Arial", 8),
        fg="gray"
    ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

    token_var = tk.StringVar()
    token_entry = tk.Entry(config_frame, textvariable=token_var, width=40, font=("Arial", 10), show="*")
    token_entry.grid(row=5, column=0, columnspan=2, sticky=tk.EW)

    config_frame.columnconfigure(0, weight=1)

    def on_confirm():
        url = url_var.get().strip()
        token = token_var.get().strip()

        if not url:
            messagebox.showwarning("输入错误", "请输入图床域名", parent=dialog)
            return

        if not token:
            messagebox.showwarning("输入错误", "请输入上传 Token", parent=dialog)
            return

        # 标准化 URL
        try:
            normalized_url = normalize_url(url)
            result["url"] = normalized_url
            result["token"] = token
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("URL 错误", f"域名格式有误：{e}", parent=dialog)

    def on_cancel():
        result["cancelled"] = True
        dialog.destroy()

    # 按钮区域
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=20)

    tk.Button(
        btn_frame,
        text="确认",
        command=on_confirm,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        width=12,
        height=1
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        btn_frame,
        text="取消",
        command=on_cancel,
        width=12,
        height=1,
        font=("Arial", 10)
    ).pack(side=tk.LEFT, padx=10)

    # 绑定回车键
    dialog.bind('<Return>', lambda e: on_confirm())
    dialog.bind('<Escape>', lambda e: on_cancel())

    dialog.wait_window()
    return result


def create_multipart_data(file_path, boundary):
    """创建 multipart/form-data 格式的请求体"""
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


def upload_file(file_path, url, token, log_callback):
    """上传单个文件，返回 (success: bool, result: str|dict)"""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTS:
        return False, f"不支持的文件格式: {ext}"
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"

    file_size = os.path.getsize(file_path)
    log_callback(f"正在上传: {filename} ({file_size:,} 字节)")

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
            return False, f"上传失败 ({e.code}): {error_data.get('error', error_msg)}"
        except Exception:
            return False, f"上传失败 ({e.code}): {error_msg}"

    except URLError as e:
        return False, f"网络错误: {e.reason}"

    except Exception as e:
        return False, f"上传出错: {e}"


class UploadApp:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.root.title("imgup - 图片上传工具")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self._build_ui()

        # 显示配置提示
        if not is_placeholder_config(config):
            self._show_config_info()

    def _show_config_info(self):
        """显示配置信息提示"""
        config_path = get_config_path()
        msg = (
            f"当前配置：\n"
            f"  服务器: {self.config['url']}\n"
            f"  Token: {'*' * 20}\n\n"
            f"如需修改配置，请编辑文件：\n"
            f"  {config_path}\n\n"
            f"修改后重启本程序即可生效。"
        )
        self._log("=" * 58)
        self._log("配置已加载")
        self._log("=" * 58)
        for line in msg.split("\n"):
            if line.strip():
                self._log(line)
        self._log("")

    def _build_ui(self):
        # ── 顶部信息栏 ──────────────────────────────────────────
        info_frame = tk.Frame(self.root, bg="#f5f5f5", relief=tk.RIDGE, bd=1)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            info_frame,
            text=f"📡 服务器: {self.config['url']}",
            bg="#f5f5f5",
            font=("Arial", 9)
        ).pack(anchor=tk.W, padx=10, pady=(5, 2))

        tk.Label(
            info_frame,
            text=f"🔑 Token: {'*' * 20}",
            bg="#f5f5f5",
            font=("Arial", 9)
        ).pack(anchor=tk.W, padx=10, pady=(2, 5))

        # ── 按钮区 ──────────────────────────────────────────────
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(
            btn_frame, text="📂  选择图片并上传",
            command=self.select_and_upload,
            bg="#4CAF50", fg="white",
            font=("Arial", 12, "bold"),
            padx=20, pady=8,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="⚙️ 重新配置",
            command=self.reconfigure,
            padx=15, pady=8,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="清空日志",
            command=lambda: self.log_text.delete(1.0, tk.END),
            padx=15, pady=8,
        ).pack(side=tk.LEFT, padx=5)

        # ── 日志区 ──────────────────────────────────────────────
        log_frame = tk.LabelFrame(self.root, text="上传日志", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ── 状态栏 ──────────────────────────────────────────────
        self.status_var = tk.StringVar(value="就绪 — 点击按钮选择图片")
        tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            fill=tk.X, side=tk.BOTTOM
        )

        # 欢迎信息
        self._log("=" * 58)
        self._log("imgup  Windows 上传工具")
        self._log("=" * 58)
        self._log(f"支持格式: {', '.join(sorted(ALLOWED_EXTS))}")
        self._log("点击 [选择图片并上传] 开始\n")

    def _log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def reconfigure(self):
        """重新配置"""
        setup_result = show_first_time_setup()
        if not setup_result["cancelled"] and setup_result["url"] and setup_result["token"]:
            new_config = {
                "url": setup_result["url"],
                "token": setup_result["token"],
                "version": "1.0"
            }
            if save_config(new_config):
                messagebox.showinfo(
                    "配置已保存",
                    "配置已更新！\n程序将重新启动以应用新配置。"
                )
                self.root.destroy()
                # 重启程序
                os.execl(sys.executable, sys.executable, *sys.argv)

    def select_and_upload(self):
        file_paths = filedialog.askopenfilenames(
            title="选择要上传的图片（可多选）",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.webp *.svg *.bmp *.avif *.ico"),
                ("所有文件", "*.*"),
            ],
        )
        if not file_paths:
            return

        url = self.config["url"]
        token = self.config["token"]

        self._log(f"\n{'='*58}")
        self._log(f"开始上传 — 共 {len(file_paths)} 个文件")
        self._log(f"{'='*58}\n")

        success_urls = []
        success_count = fail_count = 0

        for i, path in enumerate(file_paths, 1):
            self.status_var.set(f"上传中 {i}/{len(file_paths)}: {os.path.basename(path)}")
            ok, result = upload_file(path, url, token, self._log)
            if ok:
                success_count += 1
                link = result.get("url", "")
                success_urls.append(link)
                self._log(f"✓ 成功: {link}")
                self._log(f"  文件名: {result.get('filename')}  |  "
                           f"大小: {result.get('size', 0):,} B  |  "
                           f"日期: {result.get('date')}\n")
            else:
                fail_count += 1
                self._log(f"✗ 失败: {result}\n")

        self._log(f"{'='*58}")
        self._log(f"完成 — 成功: {success_count}  失败: {fail_count}")
        self._log(f"{'='*58}\n")

        if success_urls:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(success_urls))
            self._log("✓ 全部链接已复制到剪贴板\n")

        self.status_var.set(f"完成 — 成功: {success_count}  失败: {fail_count}")

        if success_count:
            messagebox.showinfo(
                "上传完成",
                f"成功上传 {success_count} 个文件\n{'链接已复制到剪贴板' if success_urls else ''}",
            )


def main():
    # 加载配置
    config = load_config()

    # 检查是否为首次启动或配置为占位符
    if is_placeholder_config(config):
        setup_result = show_first_time_setup()
        if setup_result["cancelled"]:
            sys.exit(0)

        if setup_result["url"] and setup_result["token"]:
            config = {
                "url": setup_result["url"],
                "token": setup_result["token"],
                "version": "1.0"
            }
            save_config(config)

    # 启动主界面
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    UploadApp(root, config)
    root.mainloop()


if __name__ == "__main__":
    main()
