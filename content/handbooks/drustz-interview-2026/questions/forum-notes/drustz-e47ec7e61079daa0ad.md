---
id: drustz-e47ec7e61079daa0ad
section: forum-notes
order: 130
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · How to Change the Images
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · How to Change the Images
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## How to Change the Images

Every JSON file in the `transformations/` folder lists changes to make in order. There are **six types** of changes:

### Simple Changes (No Settings)

| Type | Description |
| :--- | :--- |
| `grayscale` | Turn the image black and white |
| `flip_horizontal` | Mirror the image left-to-right |
| `flip_vertical` | Mirror the image top-to-bottom |

### Advanced Changes (With Settings)

| Type | Setting | Description |
| :--- | :--- | :--- |
| `scale` | `factor` (float) | Resize the image (e.g., 0.5 is half size) |
| `blur` | `radius` (int) | Blur the image by this amount |
| `rotate` | `angle` (float) | Rotate the image by degrees |

### Example JSON File

```json
{
  "transformations": [
    { "type": "grayscale" },
    { "type": "scale", "factor": 0.5 },
    { "type": "rotate", "angle": 90 }
  ]
}
```



This list tells the program to:

- Turn the image grayscale.
- Shrink it to 50% size.
- Rotate it 90 degrees.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
