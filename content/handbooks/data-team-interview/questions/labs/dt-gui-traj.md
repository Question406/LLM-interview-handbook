---
id: dt-gui-traj
section: labs
order: 31
level: A
title: OSWorld / AndroidWorld：屏幕轨迹哪一段能进 SFT？
quick: "只有和执行当时的屏幕元素对得上、能够回放的动作才能进 SFT；依据过期截图做出的操作和犹豫点击要丢掉或 mask。任务是否成功由环境状态验证。OSWorld 的分析中，文本操作历史有帮助，增加历史截图未见同样收益。用户真实屏幕涉及隐私，轨迹用研究集、合成界面或许可演示。"
companies:
  - apple
tags:
  - OSWorld
  - Agent
  - Multimodal
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks"
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: AndroidWorld
    url: https://arxiv.org/abs/2405.14573
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

能进 SFT 的，是那些对应执行当时无障碍树中某个元素、能够回放的原子动作。依据 800ms 前旧截图做出的操作不能进。把标好的点击轨迹整段放进监督微调（SFT），会把错误动作一起教进去：任务终局通过了，中间仍可能点偏，或者对着过期帧点击。

## 公开基准怎么设计

OSWorld 用真实电脑，输入是截图（含鼠标）加无障碍信息树。它的分析发现：分辨率高一点通常更好；多轮文本历史有用，但历史截图越堆越多并没有帮助；VLM 点不准，还会重复点击。

AndroidWorld 有 116 个人写的任务、覆盖 20 个应用，通过参数随机化变出大量变体，奖励按环境状态判定。

## 怎么筛轨迹

1. **对齐元素。** 每个动作都要对应执行当时无障碍树中的元素。只用截图、不用树也能训，但点击会更飘；树是用来对齐的，产品里可以不展示。
2. **按状态判成功。** 每一步记录一个能回放的原子动作，最后由环境状态判断任务是否完成。
3. **处理犹豫点击。** 成功轨迹里的犹豫点击，当作被放弃的尝试或者 mask 掉，不要当正例，见 `dt-swe-success-noise`。
4. **定训练目标。** 截图作为输入上下文，坐标或手势作为训练目标；截图像素本身不计算交叉熵损失。
5. **覆盖分辨率模式。** 模型有多种图像分辨率模式时（AFM 报告里有 tiling / overview / rapid），每种都要覆盖。如果只在高清模式下见过细小按钮，rapid 模式就会乱点，见 `dt-multimodal-data`。

## 轨迹从哪来

用户的真实屏幕涉及隐私，轨迹来源用研究集、合成 UI 和许可演示，见 `dt-privacy-feedback`。

## 追问

- **Android 动态出题会不会污染评测？** 参数随机化本来是为了防背题，但种子模板仍要和门禁评测去重。
