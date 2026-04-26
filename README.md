# gpt-image

AI 作图 + 图片编辑 Skill，基于 GPT-Image-2（via 302.AI）。

## 快速开始

### 1. 配置环境变量

```bash
export AI_302AI_API_KEY="sk-your-key-here"
```

**获取 API Key**：
- 默认使用 [302.AI](https://302.ai/) 平台
- 注册后获取 API Key
- 将 Key 填入环境变量即可

### 2. 生成图片

```bash
python scripts/generate_image.py \
  --prompt "A minimalist Bauhaus poster with single terracotta accent" \
  --size auto \
  --output-dir output
```

### 3. 编辑图片

```bash
python scripts/edit_image.py \
  --image photo.png \
  --prompt "Change background to deep charcoal #1A1A1A" \
  --output-dir output
```

## 两条线

| 能力 | 脚本 | 场景 |
|------|------|------|
| **生成** | `scripts/generate_image.py` | 从无到有：插画、海报、概念图、产品氛围图 |
| **编辑** | `scripts/edit_image.py` | 从有到好：改背景、换颜色、调风格、局部重绘 |

两条线可以串联——先生成再编辑，或先编辑再生成。

## 设计哲学

```
好图片 = 锚定的事实 × 明确的约束 × 快速验证
```

**三条秩**：

1. **Prompt 锚定** — 画真实的东西之前，先确认它是什么
2. **约束即自由** — 给模型一个钉子（参考艺术家 / HEX / 光线），它就能挂住风格
3. **两段式验证** — Explore 扫方向，Finalize 精调出图

详细设计哲学 → `SKILL.md`

## 自定义与扩展

这个 Skill 的设计是**开放架构**，你可以基于它做任何调整：

- **换 API 供应商**：修改 `scripts/generate_image.py` 和 `scripts/edit_image.py` 中的 `API_ENDPOINT`，可以接入任何 OpenAI-compatible 接口（OpenAI 官方、Azure、Gemini、本地模型等）
- **换模型**：`--model` 参数默认 `gpt-image-2`，可改为任何支持的模型
- **扩展能力**：基于 `scripts/edit_image.py` 的架构，可以增加 inpaint、outpaint、upscale 等能力
- **调整哲学**：`SKILL.md` 中的三条秩是建议而非枷锁，根据你的使用场景自由调整

## 文件结构

```
gpt-image/
├── SKILL.md                    # 核心设计哲学（Agent 读取）
├── README.md                   # 本文件
├── scripts/
│   ├── generate_image.py       # 图片生成脚本
│   └── edit_image.py           # 图片编辑脚本
└── references/
    ├── prompt-crafting.md      # Prompt 写作指南
    ├── scene-sizes.md          # 场景-尺寸映射
    └── adjustment-guide.md     # 调整优先级与素材专线
```

## 系统要求

- Python 3.8+
- 无额外依赖（纯标准库）

## License

MIT
