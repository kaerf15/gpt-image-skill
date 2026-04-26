#!/usr/bin/env python3
"""
GPT Image Editing Script
Calls GPT-Image-2 edits API through 302.AI.
Takes an image + prompt, returns edited image.
Supports optional mask for region-specific edits.
"""

import argparse
import json
import os
import sys
import urllib.request
import ssl
from pathlib import Path
from datetime import datetime

try:
    import certifi
    _ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_context = ssl._create_unverified_context()

API_ENDPOINT = "https://api.302.ai/v1/images/edits"


def call_edit_api(
    api_key: str,
    model: str,
    image_path: str,
    prompt: str,
    mask_path: str = None,
    size: str = "auto",
    n: int = 1,
    quality: str = "auto",
    background: str = "auto",
    output_format: str = "png"
) -> dict | None:
    """Call the GPT Image Edits API through 302.AI."""

    boundary = "----PythonFormBoundary"
    body_parts = []

    # Add image file
    with open(image_path, "rb") as f:
        image_data = f.read()
    body_parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{os.path.basename(image_path)}"\r\n'
        f'Content-Type: image/png\r\n\r\n'.encode()
    )
    body_parts.append(image_data)
    body_parts.append(f'\r\n'.encode())

    # Add mask if provided
    if mask_path and os.path.exists(mask_path):
        with open(mask_path, "rb") as f:
            mask_data = f.read()
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="mask"; filename="{os.path.basename(mask_path)}"\r\n'
            f'Content-Type: image/png\r\n\r\n'.encode()
        )
        body_parts.append(mask_data)
        body_parts.append(f'\r\n'.encode())

    # Add text fields
    fields = {
        "model": model,
        "prompt": prompt,
        "n": str(n),
        "size": size,
        "quality": quality,
        "background": background,
        "output_format": output_format,
    }
    for key, value in fields.items():
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f'{value}\r\n'.encode()
        )

    body_parts.append(f'--{boundary}--\r\n'.encode())
    data = b''.join(body_parts)

    req = urllib.request.Request(
        API_ENDPOINT,
        data=data,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Authorization': f'Bearer {api_key}'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=300, context=_ssl_context) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request Error: {e}", file=sys.stderr)
        return None


def save_images_from_data(data_list: list[dict], output_dir: str, prefix: str, output_format: str) -> list[str]:
    """Save images from data array. Supports base64."""
    import base64
    saved_paths = []
    for i, img_data in enumerate(data_list):
        b64_data = img_data.get("b64_json")
        if not b64_data:
            print(f"Warning: No b64_json for image {i+1}", file=sys.stderr)
            continue

        suffix = f"_{i+1}" if len(data_list) > 1 else ""
        filename = f"{prefix}{suffix}.{output_format}"
        output_path = os.path.join(output_dir, filename)

        try:
            img_bytes = base64.b64decode(b64_data)
            with open(output_path, 'wb') as f:
                f.write(img_bytes)
            rel_path = os.path.relpath(output_path, os.getcwd())
            saved_paths.append(rel_path)
            print(f"SUCCESS:{rel_path}")
        except Exception as e:
            print(f"Error saving image {i+1}: {e}", file=sys.stderr)

    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="Edit images with GPT-Image models via 302.AI"
    )
    parser.add_argument("--api-key", help="302.AI API key")
    parser.add_argument("--model", default="gpt-image-2", help="Model name")
    parser.add_argument("--image", required=True, help="Path to source image")
    parser.add_argument("--mask", help="Optional mask image for region-specific edit")
    parser.add_argument("--prompt", "-p", required=True, help="Edit instruction")
    parser.add_argument("--size", default="auto", help="Output size")
    parser.add_argument("--n", type=int, default=1, help="Number of variants")
    parser.add_argument("--quality", default="auto", choices=["auto", "high", "medium", "low"])
    parser.add_argument("--background", default="auto", choices=["auto", "transparent", "opaque"])
    parser.add_argument("--output-format", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--output-name", help="Output filename prefix")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("AI_302AI_API_KEY")
    if not api_key:
        print("Error: Missing API key", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"DRY_RUN: Edit '{args.image}' with prompt: {args.prompt}")
        sys.exit(0)

    print(f"Calling GPT-Image Edit API ({args.model}) via 302.AI...", file=sys.stderr)
    print(f"  Image: {args.image}", file=sys.stderr)
    print(f"  Prompt: {args.prompt}", file=sys.stderr)
    if args.mask:
        print(f"  Mask: {args.mask}", file=sys.stderr)

    result = call_edit_api(
        api_key=api_key,
        model=args.model,
        image_path=args.image,
        prompt=args.prompt,
        mask_path=args.mask,
        size=args.size,
        n=args.n,
        quality=args.quality,
        background=args.background,
        output_format=args.output_format
    )

    if result is None:
        print("Error: Failed to get response", file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = args.output_name or f"gpt_image_edit_{timestamp}"

    data_list = result.get("data", [])
    if not data_list:
        print(f"Error: No data in response", file=sys.stderr)
        sys.exit(1)

    saved_paths = save_images_from_data(data_list, output_dir, prefix, args.output_format)

    if not saved_paths:
        sys.exit(1)


if __name__ == "__main__":
    main()
