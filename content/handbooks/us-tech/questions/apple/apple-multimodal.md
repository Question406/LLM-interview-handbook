---
id: apple-multimodal
section: apple
order: 9
level: S
title: Apple：图文 / 屏幕理解 grounding，引用的是像素区域还是 OCR 文本？
quick: >-
  两者都要，契约不同。要点击、高亮、指「这块」用像素框或 mask；要朗读、复制、填槽用 OCR / 文本 span。图标几乎没有字；纯
  OCR 会把相邻按钮粘错。Ferret-UI 一类工作把 referring / grounding 做成区域标注，不要只把整屏 OCR 塞进
  prompt。
tags:
  - Apple
  - Multimodal
  - Grounding
  - UI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Ferret-UI — Grounded Mobile UI Understanding with Multimodal LLMs
    url: https://machinelearning.apple.com/research/ferretui-mobile
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Intelligence Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Siri / Visual Intelligence / 屏幕感知类设计题，容易答成「上个多模态大模型」。Apple 的约束是接地、端侧、可指可点。文本工具的接地见 `apple-siri-grounded`；屏幕上证据经常不是一段 API JSON，而是用户正在看的像素。Apple 公开的 Ferret-UI 把 referring、grounding、基础 UI 任务（找字、列控件、认图标）做成带区域标注的指令数据。Foundation model 公开叙述也把端侧 / 服务端模型写成多模态。本题按这些公开工作收，不当成真题逐字记录。

## 两种引用，产品行为不一样

记屏幕为图像 $I$，用户问题 $q$。生成要能指向证据 $e$。$e$ 有两种常见形态：

- **像素区域：** 框 $[x_1,y_1,x_2,y_2]$ 或低分辨率 mask。坐标系相对屏幕，可转成点击。适合「按右上角那个开关」「图里的红色按钮」。图标、相册缩略图、无障碍需要的高亮，都没有稳定字符串。
- **OCR 文本：** 某条字符串加可选的文本框。适合「邮件标题是什么」「把验证码读出来」「填进日历的是哪一行字」。TTS 最终也只能读文本，见 `apple-siri-latency`。

错法是只选一边。只 OCR：图标、图形按钮、重叠半透明层会瞎；阅读顺序一乱，验证码和按钮标题粘在一起；多语言 / 竖排更差。只框：模型可以说「这块」，但 Siri 没法把「这块」读成「下午三点」，除非框里再跑 OCR 或视觉问答。

正确分层：

1. **感知：** 控件检测加 OCR 加图标分类，输出一组带几何的候选 $E=\{e_i\}$。Ferret-UI 把屏幕按长宽比切成子图（竖屏上下切），避免小字被整图缩放抹掉。
2. **指称理解：** $q$ 里的「那个蓝色的」解析到某个 $e_i$（referring）。输入可以是语言加区域。
3. **生成接地：** 回答里的槽位必须能指回 $e_i$。动作输出用框（可点）；口头输出用 OCR 字符串（可说）。两者 id 要能对上，不能口播 A 却点了 B。
4. **拒答：** $E$ 里没有就问「你指的是左上还是右下」，不要靠预训练知识补屏幕上没有的字。这和工具接地同一契约。

Accessibility 是硬约束：VoiceOver 已经以控件树加文本为主。视觉模型是补树缺失（自定义绘制、游戏、截图）。面试说「先信系统 UI 树，像素模型补洞」，比「截图送云端 VLM」更像 Apple。

## 评测把几何和字符串拆开

- **框：** IoU 或中心是否落在真值控件内。动作成功等于点击命中可激活区域，不是画得好看。
- **OCR：** 字段级准确率，数字 / 验证码单独计。BLEU 无意义。
- **对齐：** 口播 span 与点击 id 一致率。这是幻觉的一种：话说对了点错。
- **分辨率：** 小字、长屏。切子图 / any-resolution 是为这个，不是为刷通用 VQA。

隐私：完整屏幕往往含消息和密码。默认端上感知，不要把原始截图设计成训练数据或长期日志。Foundation model 公开原则是不用私有用户数据训练。需要更大模型时走 PCC，仍然不是把截图拿去 SFT 下一版，见 `apple-diff-privacy`、`apple-personalize`。

延迟：截图编码比文本 prefill 贵。动作类交互要在百毫秒到一秒内给可点框，能用检测器就不要先跑一轮 3B 生成。生成只在需要语言推理时上场。屏幕理解若走 ANE，静态分辨率档位和 `apple-ane` 同一套痛。

## 和纯图文 caption 的差别

相册「描述这张照片」可以引用物体框（狗在左下）或纯文本。屏幕理解多了可执行：框是 API。Ferret-UI 的基础任务里同时有 find text 和 widget listing，就是在逼模型两种输出都练。面试若只谈 CLIP 相似度，缺了 grounding 格式。

坐标规范化：模型喜欢输出相对 0–1000 的整数，推理时乘回像素。训练与推理分辨率不一致是高发 bug，切子图后坐标要映射回全屏。

## 追问

- **为什么不把 OCR 当唯一证据？** 没字的控件、艺术字、低对比。而且 OCR 错一个数字，口头层会非常自信地读错。
- **为什么不只出框？** 语音通道必须是文本；复制 / 填表也是文本。框是动作，字是内容。
- **和工具接地怎么统一评测？** 都是命题能否在 $E$ 里定位。$E$ 从 JSON 换成带几何的控件列表而已。
- **多窗 / 通知遮挡？** $E$ 要带叠放顺序和可见性。点到被挡住的框算失败，即使 IoU 对下层真值很高。
