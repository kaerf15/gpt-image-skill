#!/usr/bin/env python3
"""
GPT Image Generation Script
Calls GPT-Image-2 (and related models) through the 302.AI OpenAI-compatible images API.
Handles prompt input, API calling, and image download.
Supports streaming mode for partial image previews.
Reference: https://302ai.apifox.cn/288853804e0
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime

# Create SSL context
try:
    import certifi
    _ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_context = ssl._create_unverified_context()


API_ENDPOINT = "https://api.302.ai/v1/images/generations"


def download_image(url: str, output_path: str) -> bool:
    """Download image from URL to local file."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60, context=_ssl_context) as resp:
            with open(output_path, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        return False


def parse_sse_stream(resp) -> list[dict]:
    """Parse Server-Sent Events stream and return list of JSON events."""
    events = []
    for line in resp:
        line = line.decode('utf-8').strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            event = json.loads(data)
            events.append(event)
        except json.JSONDecodeError:
            continue
    return events


def call_gpt_image_api(
    api_key: str,
    model: str,
    prompt: str,
    size: str = "auto",
    n: int = 1,
    quality: str = "auto",
    background: str = "auto",
    output_format: str = "png",
    stream: bool = False,
    partial_images: int = 0
) -> dict | list[dict] | None:
    """Call the GPT Image API through 302.AI.
    
    Returns:
        - dict: Normal (non-streaming) response
        - list[dict]: Streaming response events
        - None: Error
    """

    body = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
        "background": background,
        "output_format": output_format,
        "stream": stream,
        "partial_images": partial_images
    }

    # Remove default values that might confuse API
    if not stream:
        body.pop("stream", None)
    if partial_images == 0:
        body.pop("partial_images", None)

    data = json.dumps(body).encode('utf-8')

    req = urllib.request.Request(
        API_ENDPOINT,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=300, context=_ssl_context) as resp:
            if stream:
                events = parse_sse_stream(resp)
                return events if events else None
            else:
                result = json.loads(resp.read().decode('utf-8'))
                return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request Error: {e}", file=sys.stderr)
        return None


def save_images_from_data(data_list: list[dict], output_dir: str, prefix: str, output_format: str, label: str = "") -> list[str]:
    """Download and save images from data array. Supports both URL and base64."""
    saved_paths = []
    for i, img_data in enumerate(data_list):
        img_url = img_data.get("url")
        b64_data = img_data.get("b64_json")

        suffix = f"_{label}{i+1}" if label else (f"_{i+1}" if len(data_list) > 1 else "")
        filename = f"{prefix}{suffix}.{output_format}"
        output_path = os.path.join(output_dir, filename)

        if b64_data:
            # Save from base64
            print(f"Saving image {i+1}/{len(data_list)} from base64...", file=sys.stderr)
            try:
                import base64
                img_bytes = base64.b64decode(b64_data)
                with open(output_path, 'wb') as f:
                    f.write(img_bytes)
                rel_path = os.path.relpath(output_path, os.getcwd())
                saved_paths.append(rel_path)
                print(f"SUCCESS:{rel_path}")
                continue
            except Exception as e:
                print(f"Error decoding base64 for image {i+1}: {e}", file=sys.stderr)

        if img_url:
            # Download from URL
            print(f"Downloading image {i+1}/{len(data_list)}...", file=sys.stderr)
            if download_image(img_url, output_path):
                rel_path = os.path.relpath(output_path, os.getcwd())
                saved_paths.append(rel_path)
                print(f"SUCCESS:{rel_path}")
            else:
                print(f"Error: Failed to download image {i+1}", file=sys.stderr)
        else:
            print(f"Warning: No URL or base64 data for image {i+1}", file=sys.stderr)

    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="Generate images with GPT-Image models via 302.AI"
    )
    parser.add_argument("--api-key", help="302.AI API key")
    parser.add_argument("--model", default="gpt-image-2", help="Model name")
    parser.add_argument("--prompt", "-p", help="Image generation prompt text")
    parser.add_argument("--prompt-file", help="Path to prompt file")
    parser.add_argument(
        "--size", default="auto",
        help="Image size: auto, 1024x1024, 1536x1024, 1024x1536, or custom"
    )
    parser.add_argument("--n", type=int, default=1, help="Number of images (1-10)")
    parser.add_argument(
        "--quality", default="auto",
        choices=["auto", "high", "medium", "low"],
        help="Image quality"
    )
    parser.add_argument(
        "--background", default="auto",
        choices=["auto", "transparent", "opaque"],
        help="Background type"
    )
    parser.add_argument(
        "--output-format", default="png",
        choices=["png", "jpeg", "webp"],
        help="Output image format"
    )
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--output-name", help="Output filename prefix")
    parser.add_argument(
        "--stream", action="store_true",
        help="Enable streaming mode for partial image previews"
    )
    parser.add_argument(
        "--partial-images", type=int, default=0, choices=[0, 1, 2, 3],
        help="Number of partial image previews in streaming mode (0-3)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print prompt and parameters, then exit without calling API"
    )

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("AI_302AI_API_KEY")
    if not args.dry_run and not api_key:
        print(
            "Error: Missing API key. Provide --api-key or set AI_302AI_API_KEY",
            file=sys.stderr
        )
        sys.exit(1)

    # Get prompt
    if args.prompt_file:
        prompt_path = (
            args.prompt_file if os.path.isabs(args.prompt_file)
            else os.path.join(os.getcwd(), args.prompt_file)
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
    elif args.prompt:
        prompt = args.prompt.strip()
    else:
        # Try reading from stdin
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            print(
                "Error: Provide --prompt, --prompt-file, or pipe prompt via stdin",
                file=sys.stderr
            )
            sys.exit(1)

    if not prompt:
        print("Error: Prompt is empty", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("DRY_RUN_PROMPT_BEGIN")
        print(prompt)
        print("DRY_RUN_PROMPT_END")
        print(
            f"DRY_RUN_PARAMS: model={args.model}, size={args.size}, n={args.n}, "
            f"quality={args.quality}, background={args.background}, "
            f"format={args.output_format}, stream={args.stream}, "
            f"partial_images={args.partial_images}"
        )
        return

    # Call API
    stream_label = " (streaming)" if args.stream else ""
    print(f"Calling GPT-Image API ({args.model}){stream_label} via 302.AI...", file=sys.stderr)
    print(f"  Prompt length: {len(prompt)} chars", file=sys.stderr)

    result = call_gpt_image_api(
        api_key=api_key or "",
        model=args.model,
        prompt=prompt,
        size=args.size,
        n=args.n,
        quality=args.quality,
        background=args.background,
        output_format=args.output_format,
        stream=args.stream,
        partial_images=args.partial_images
    )

    if result is None:
        print("Error: Failed to get response from GPT-Image API", file=sys.stderr)
        sys.exit(1)

    # Prepare output directory
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = args.output_name or f"gpt_image_{timestamp}"

    saved_paths = []

    if args.stream and isinstance(result, list):
        # Handle streaming response: multiple events
        print(f"Received {len(result)} streaming event(s)", file=sys.stderr)

        # Save partial images (all events except last)
        if len(result) > 1 and args.partial_images > 0:
            for idx, event in enumerate(result[:-1]):
                data_list = event.get("data", [])
                if data_list:
                    print(f"Saving partial preview {idx+1}/{len(result)-1}...", file=sys.stderr)
                    partial_paths = save_images_from_data(
                        data_list, output_dir, prefix, args.output_format,
                        label=f"partial{idx+1}_"
                    )
                    saved_paths.extend(partial_paths)

        # Save final image (last event)
        final_event = result[-1]
        data_list = final_event.get("data", [])
        if not data_list:
            print(
                f"Error: No data in final stream event. Event: {json.dumps(final_event, indent=2)}",
                file=sys.stderr
            )
            sys.exit(1)

        print("Saving final image(s)...", file=sys.stderr)
        final_paths = save_images_from_data(
            data_list, output_dir, prefix, args.output_format
        )
        saved_paths.extend(final_paths)

    else:
        # Handle normal (non-streaming) response
        if isinstance(result, dict):
            data_list = result.get("data", [])
        else:
            data_list = []

        if not data_list:
            print(
                f"Error: No data in response. Response: {json.dumps(result, indent=2)}",
                file=sys.stderr
            )
            sys.exit(1)

        saved_paths = save_images_from_data(
            data_list, output_dir, prefix, args.output_format
        )

    if not saved_paths:
        sys.exit(1)


if __name__ == "__main__":
    main()
