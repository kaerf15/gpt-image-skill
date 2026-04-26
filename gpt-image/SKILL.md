---
name: gpt-image
description: "AI 作图 + 图片编辑。触发词：画图、编辑图片、generate image、edit image。"
---

# GPT Image

## 一句话

好图片 = 锚定的事实 × 明确的约束 × 快速验证

## 两条线

- **生成**：从无到有，`scripts/generate_image.py`
- **编辑**：从有到好，`scripts/edit_image.py`

两条线可以串联——先生成再编辑，或先编辑再生成。

## 三条秩

### 秩一 · Prompt 锚定
输入质量 = 输出质量。

画真实的东西之前，先确认它是什么。错的事实 + 精致的像素 = 精致的错误。

涉及品牌、产品、事件、人物 → `WebSearch` 验证，把事实写进 prompt。纯虚构 → 尽情发挥。

**编辑同样**：编辑指令不能违背图片本身的事实。

### 秩二 · 约束即自由
AI 默认产出 = 训练语料的统计平均 = 谁都不是。

给模型一个钉子（参考艺术家 / HEX / 光线 / 材质），它就能挂住风格。

反 slop：默认不用紫渐变 / emoji / 圆角+左border / 纯色剪影 / uniform soft light。

一个视觉焦点做到 120%，其他自然——这是品味的来源。

**编辑同样**："背景换成深蓝 #0A1628" 比 "改好看" 有效 10 倍。

### 秩三 · 两段式验证
方向错了早改比晚改便宜 100 倍。

Explore：`n=10, low, auto`——不求完美，只求方向对。

Finalize：`n=1, high, 精确尺寸`——基于选定方向精调。

不是 workflow 教条：效果 OK 就直接给用户看。

## 工作流

**生成**：理解需求 → 锚定事实（如需）→ 写 prompt → Explore → 用户确认 → Finalize

**编辑**：拿到图片 → 明确编辑指令 → Edit → 效果 OK 直接交 / 不对再调指令

写 prompt / 编辑指令像导演一场戏。七层不是 checklist，是七个镜头。

```
环境 → 主体 → 材质 → 光线 → 构图 → 色彩 → 风格
```

简单场景砍到三层：主体 + 色彩 + 风格。详细写法 → `references/prompt-crafting.md`

## 调用

脚本在 skill 目录的 `scripts/` 下。Agent 根据自己安装位置调用即可。输出目录**默认**基于当前工作目录，可通过 `--output-dir` 指定其他位置。执行时保持 cwd 为用户的项目目录。

```bash
# 生成
python scripts/generate_image.py --prompt "..." --size auto

# 编辑
python scripts/edit_image.py --image photo.png --prompt "Change background to blue"
```

参数默认值：size=auto, n=1, quality=auto, background=auto, output-dir=`./output/`。Bash timeout：`300000`。

尺寸映射、调整优先级、素材专线 → `references/`

## 自检

1. 事实锚定了吗？（秩一）
2. 有足够的约束锚点吗？（秩二）
3. 方向对吗？（秩三）

三张图里两张过关就交。全不对，回到 Explore。

## API

Key：`AI_302AI_API_KEY` | Model：`gpt-image-2`
