#!/usr/bin/env python3
import argparse
import os
import sys

# 设置模型镜像
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')


def main():
    parser = argparse.ArgumentParser(description='实时中文语音转英文字幕服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=5000, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    args = parser.parse_args()

    from app import create_app

    app, socketio = create_app()

    print(f"\n{'='*60}")
    print(f"  实时中文语音转英文字幕服务")
    print(f"  模型: facebook/seamless-m4t-v2-large")
    print(f"  访问地址: http://{args.host}:{args.port}")
    print(f"{'='*60}\n")

    socketio.run(
        app,
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_reloader=False
    )


if __name__ == '__main__':
    main()
