#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imgup - Windows GUI 上传工具
双击运行，选择图片文件后自动上传
"""

import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import mimetypes

# 默认配置（可以修改这里的值，或设置环境变量）
DEFAULT_URL = "https://images.example.com/upload"
DEFAULT_TOKEN = "change_me_please"

# 支持的图片格式
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif", ".ico"}


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
    def __init__(self, root):
        self.root = root
        self.root.title("imgup - 图片上传工具")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # 配置变量（优先读取环境变量）
        self.url_var = tk.StringVar(value=os.environ.get("IMGUP_URL", DEFAULT_URL))
        self.token_var = tk.StringVar(value=os.environ.get("IMGUP_TOKEN", DEFAULT_TOKEN))

        self._build_ui()

    def _build_ui(self):
        # ── 配置区 ──────────────────────────────────────────────
        config_frame = tk.LabelFrame(self.root, text="配置", padx=10, pady=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(config_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Entry(config_frame, textvariable=self.url_var, width=55).grid(
            row=0, column=1, columnspan=2, sticky=tk.EW, pady=5
        )

        tk.Label(config_frame, text="上传 Token:").grid(row=1, column=0, sticky=tk.W, pady=5)
        token_entry = tk.Entry(config_frame, textvariable=self.token_var, width=55, show="*")
        token_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

        show_var = tk.BooleanVar()
        tk.Checkbutton(
            config_frame, text="显示",
            variable=show_var,
            command=lambda: token_entry.config(show="" if show_var.get() else "*"),
        ).grid(row=1, column=2, padx=5)

        config_frame.columnconfigure(1, weight=1)

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
            btn_frame, text="清空日志",
            command=lambda: self.log_text.delete(1.0, tk.END),
            padx=20, pady=8,
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

        url = self.url_var.get().strip()
        token = self.token_var.get().strip()
        if not url or not token:
            messagebox.showerror("配置错误", "请填写服务器地址和 Token")
            return

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
    root = tk.Tk()
    try:
        root.iconbitmap(default="")  # 消除 Windows 默认羽毛图标（可选）
    except Exception:
        pass
    UploadApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
