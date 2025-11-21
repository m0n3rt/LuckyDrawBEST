import argparse
import qrcode


def gen_register_qr(base_url: str) -> str:
    base = base_url.rstrip('/')
    target = f"{base}/register_form"
    img = qrcode.make(target)
    out_path = 'register_qr.png'
    img.save(out_path)
    return f"生成二维码 -> {out_path} 指向: {target}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成注册页二维码 (/register_form)')
    parser.add_argument('--base', default='http://127.0.0.1:8000', help='后端基础 URL，例如 http://192.168.1.88:8000')
    args = parser.parse_args()
    print(gen_register_qr(args.base))
