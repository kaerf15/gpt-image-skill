# 调整指南

## 常见问题 → 调整顺序

| 症状 | 第一调 | 第二调 | 第三调 |
|------|--------|--------|--------|
| 太 generic | 加风格层约束（参考艺术家） | 加色彩层（锁 2-3 个 HEX） | 加光线层（单一硬光源） |
| 构图失衡 | 调构图层（视角、留白） | 调环境层（简化背景） | — |
| 色调漂移 | 调色彩层（重复 HEX + 分布比例） | 调光线层（色温） | — |
| 有 slop 混入 | 在对应层加负向约束 | 加风格层参考 | — |
| 主体不清晰 | 加光线层（方向光分离） | 调环境层（简化） | 加材质层（反光强调） |

## 设计素材专线

icon / 贴纸 / UI 元素 / 需要叠加的图：

> 输出目录**默认**基于当前工作目录，可通过 `--output-dir` 指定其他位置。Agent 执行时保持 cwd 为用户的项目目录。

```bash
python3 scripts/generate_image.py \
  --prompt "[七层导演脚本，固定风格锚点]" \
  --n 5 --quality medium \
  --background transparent --output-format png \
  --output-dir "assets/icons"
```

透明底只在叠加/复用场景使用。封面、氛围图用 auto。

Agent 读图筛选：边缘干净、风格统一、无多余细节。保留最优 2-3 张。

## 快速预览

```bash
--n 5 --quality low --size auto --stream true --partial-images 2
```

生成到 30% 和 60% 时返回中间版，方向不对立即停。
