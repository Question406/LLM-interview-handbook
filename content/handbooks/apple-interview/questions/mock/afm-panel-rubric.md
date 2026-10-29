---
id: afm-panel-rubric
section: mock
order: 70
level: A
title: Panel 五场模拟：四轮技术＋一轮 Culture 的题目、追问与评分
quick: 四场技术分别练飞轮、合成、诊断和偏好，第五场使用真实提前预判故事。每场45分钟，有统一 scoring rubric、追问时点与复盘记录。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - 全流程模拟
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: RewardBench 2
    url: 'https://arxiv.org/abs/2506.01937'
    type: primary
  - title: 'HelpSteer2-Preference: Complementing Ratings with Preferences'
    url: 'https://arxiv.org/abs/2410.01257'
    type: primary
---

## 使用方式
原创模拟结构，对齐用户提供的四技术＋一文化安排；场次顺序为手册练习安排。每场0–5分钟澄清，5–20分钟独立方案，20–35分钟追问，35–42分钟验证与取舍，42–45分钟总结。面试官事先读参考，候选人只看题面。

| 场次 | 起始任务 | 第20分钟追加 | 第30分钟追加 |
| --- | --- | --- | --- |
| 技术1 飞轮 | 用 `afm-case-endtoend` 设计 feedback loop | 私人截图不能进入训练 | 下一轮预算减半、一个来源要撤回 |
| 技术2 合成 | 为时区与工具恢复造数据 | verifier 通过率98%但真实任务降 | teacher 开始重复自己文风，如何停迭代 |
| 技术3 诊断 | `afm-mock-debug-tools` 的附件 | 只给两个训练实验名额 | 环境版本和策略同时改过 |
| 技术4 偏好 | `afm-mock-debug-reward` 的附件 | 同家族 judge、回答长度翻倍 | 不同 locale 偏好冲突，如何选 RM/DPO/RL |
| Culture | 你的 See Around Corners 真实经历 | 同事当时为什么不同意 | 预警有一半错了，怎么承认并修正 |

## 统一 scoring rubric
每轮五项各0–4：问题及目标定义、技术/证据正确性、实验与数据设计、规模/成本/治理、沟通和取舍。0无回答，1关键错误，2提示后完成，3独立自洽，4能提供区分性实验并认识 evidence limitations。自练14分且无关键错误为通过；这是练习标准，不是 Apple 评分。

技术轮关键错误包括训练评测混用、用同一 RM 自证、默认私有交互可训练、只报总分掩盖违规。Culture 不强求编造 quantization 收益，但必须分清亲自行动与团队成果、事前预判与事后解释。没有真实经历就选另一件真实工作，不用题本故事替换。

## 参考要点与复盘
飞轮轮须讲完整来源到发布、每轮可 attribution 实验和停止；合成轮须有独立 verifier、难度覆盖、contamination 与课程；诊断轮须先证实测量与环境，再做数据干预；偏好轮须区分 RM 准确率、probability calibration 和下游质量；文化轮须有真实时间线、不同意见、行动与纠错。

每场记录：总分__/20；两次关键追问的原话__；哪条证据缺失__；哪一步靠面试官提示__；下次要复现的反例__。连续两次闭卷完成再标掌握，不因读懂参考答案就打勾。
