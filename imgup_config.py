#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imgup 配置工具 - 命令行版本
用于设置图床域名和上传 Token
"""

import os
import sys
import json


CONFIG_FILE = "imgup_config.json"


def get_config_path():
    """获取配置文件路径（脚本所在目录）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, CONFIG_FILE)


def normalize_url(url):
    """标准化 URL"""
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
    """加载现有配置"""
    config_path = get_config_path()

    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"警告：读取配置文件失败：{e}")
        return None


def save_config(url, token):
    """保存配置到文件"""
    config_path = get_config_path()

    config = {
        "url": url,
        "token": token,
        "version": "1.0"
    }

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"错误：无法保存配置文件：{e}")
        return False


def main():
    print("=" * 60)
    print("imgup 配置工具")
    print("=" * 60)
    print()

    # 显示现有配置
    existing = load_config()
    if existing:
        print("当前配置：")
        print(f"  URL:   {existing.get('url', '未设置')}")
        print(f"  Token: {'*' * 20}")
        print()

    print("请输入新的配置信息（直接回车保持原值）：")
    print()

    # 输入域名
    while True:
        url_input = input("图床域名（例如 images.example.com）: ").strip()

        if not url_input and existing:
            # 保持原值
            url = existing.get('url', '')
            print(f"  → 保持原值: {url}")
            break
        elif not url_input:
            print("  错误：首次配置必须输入域名")
            continue
        else:
            try:
                url = normalize_url(url_input)
                print(f"  → 标准化为: {url}")
                break
            except Exception as e:
                print(f"  错误：域名格式有误：{e}")
                continue

    # 输入 Token
    while True:
        token_input = input("上传 Token: ").strip()

        if not token_input and existing:
            # 保持原值
            token = existing.get('token', '')
            print(f"  → 保持原值: {'*' * 20}")
            break
        elif not token_input:
            print("  错误：首次配置必须输入 Token")
            continue
        else:
            token = token_input
            print(f"  → Token 已设置")
            break

    print()

    # 保存配置
    if save_config(url, token):
        print("✓ 配置已保存到：", get_config_path())
        print()
        print("现在可以使用 imgup_upload.py 上传图片了")
        return 0
    else:
        print("✗ 配置保存失败")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
