---
id: dt-gui-traj
section: labs
order: 31
level: A
title: OSWorld / AndroidWorld：屏幕 trajectories 哪一段能进 SFT？
quick: >-
  只有能对上执行当时屏幕元素、能 replay 的动作才能进 SFT；依据过期截图的操作和犹豫点击要丢掉或 mask，任务成功与否由环境状态判。OSWorld
  发现文本操作历史有帮助，堆历史截图没有同样的收益。trajectories 用研究集、合成界面或许可演示，用户真实屏幕涉及隐私。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks'
    url: 'https://arxiv.org/abs/2404.07972'
    type: primary
  - title: AndroidWorld
    url: 'https://arxiv.org/abs/2405.14573'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

能进 SFT 的，是能对上执行当时无障碍树里某个元素、能 replay 的原子动作；依据 800ms 前旧截图做出的操作不能进。把标好的点击 trajectories 整段放进 SFT，会把错误动作一起教进去：任务终局通过了，中间仍可能点偏，或者对着过期帧点击。

比如一条「把文件移到回收站」的 trajectories，第三步模型点的是旧截图里「删除」按钮的位置，可这时弹窗已经把按钮挤开了，它点空了，又点了一次才成功。任务结果是对的，那次点空的动作不该当正例。

公开基准的设计可以参考。OSWorld 用真实电脑，输入是截图（含鼠标）加无障碍信息树；它的分析发现分辨率高一点通常更好，VLM 点不准，还会重复点击。AndroidWorld 有 116 个人写的任务，覆盖 20 个应用，通过参数随机化变出大量变体，奖励按环境状态判定。

筛 trajectories 时，每个动作先对到执行当时无障碍树里的元素。只用截图、不用树也能训，但点击会更飘；树是拿来对齐的，产品里可以不展示。每一步记一个能 replay 的原子动作，最后由环境状态判断任务有没有完成。成功 trajectories 里的犹豫点击当作被放弃的尝试，或者 mask 掉，不当正例，见 `dt-swe-success-noise`。

训练目标是坐标或手势，截图只当输入上下文，截图像素本身不算 cross-entropy 损失。

## 追问

**历史截图要不要都放进上下文？**
不用越堆越多。OSWorld 发现多轮文本历史有用，历史截图越堆越多并没有帮助。

**模型有好几种图像分辨率模式，要注意什么？**
每种都要覆盖。AFM 报告里有 tiling / overview / rapid 几种模式，如果只在高清模式下见过细小按钮，rapid 模式就会乱点，见 `dt-multimodal-data`。

**trajectories 从哪来？**
研究集、合成 UI 和许可演示。用户的真实屏幕涉及隐私，见 `dt-privacy-feedback`。

**Android 动态出题会不会 contamination 评测？**
有可能。参数随机化本来是为了防背题，但 seed 模板仍要和 evaluation gate 评测 deduplication。
