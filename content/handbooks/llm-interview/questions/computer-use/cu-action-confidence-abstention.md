---
id: cu-action-confidence-abstention
section: computer-use
order: 7
level: A
title: GUI Agent 何时应降低动作置信并 abstain / 求助，而不是瞎点？
quick: 候选元素分歧大、OCR 和树对不上、或者动作不可逆且我不确定时，我会 abstain。门控用校准过的置信和风险等级，不会拿口头「我很确定」当数。
tags:
  - Abstention
  - Calibration
  - GUI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Selective Classification for Deep Neural Networks
    url: https://arxiv.org/abs/1705.08500
    type: primary
---

强迫每一步都点出去，是 GUI Agent 最贵的错误。同屏两个相似图标、a11y 名和截图对不上、加载动画还没结束，模型仍会给一个坐标。错法：把 softmax 最高分当校准置信，或把 abstain 藏起来不报。选择性预测的结论是覆盖率和风险必须一起谈，不能只刷全覆盖准确率。生产上低风险可以试探，高风险必须 abstain 或问人。评测要画 coverage–accuracy 曲线。

## 置信从哪来

可用信号至少四类：多假设一致性（独立采样或树候选与视觉点是否落到同一控件）；detector / grounding 分数；历史同类动作成功率；观测冲突（OCR 与 a11y 名不一致、bbox 与可点区域错位）。一致性可写成 $c = 1 - H(p)$ 或 top-2 间距 $\Delta = p_{(1)}-p_{(2)}$；仅当 $c \ge \gamma$ 且 $\Delta \gt \delta$ 才进入执行。单一 logit 未校准，不能当门控。冲突本身是强信号：树说「提交」、视觉点在「取消」上，应直接降档，而不是平均两个框。记录候选 ID、分数、是否冲突、最终是执行 / 缩小再问 / abstain。没有冲突字段，失败只能叫 grounding。

## 按风险门控，按曲线评测

把动作分成可逆试探（滚动、聚焦、打开菜单）与不可逆（提交、删除、支付、外发）。门控：$r(a)\cdot(1-c) \lt \tau$ 才自动执行，否则 abstain、clarify，或改用键盘 / a11y 接口。低风险允许一次受控试探，但必须用下一帧断言状态；试探失败要停，不要连点。高风险即使 $c$ 看起来高，只要观测冲突或参数未解析完整，仍须人审。选择性分类文献把目标写成：在覆盖率 $\phi$ 下控制风险 $R \le r^*$；GUI 里 $R$ 应是不可逆误操作率，不是 token 级准确率。

评测禁止只报端到端成功率。至少报：覆盖率（自动执行步占比）、自动步准确率、abstain 后任务仍可完成率、高风险误触率。画 coverage–accuracy 曲线：提高 $\gamma$ 时准确率应升、覆盖率应降；若覆盖率降了准确率不动，说明阈值没校准到错误。评测上能刷的是：用口头 CoT「我不确定」当 abstain，但点击已经发出；把所有难例都 abstain 刷准确率；不测冲突样本。

高风险不确定就停；低风险才允许带断言的试探。SeeClick 一类 grounding 评测告诉你点得准不准；本题问的是不准的时候你停不停。生产把 abstain 率当健康指标：长期为 $0$ 说明在逼模型瞎点；突然升很高说明观测或阈值坏了。校准要用持出集：不可逆误操作率在自动执行子集上须 $\lt r^*$，达不到就提高 $\gamma$，而不是事后在 prompt 里写「请谨慎」。

## 追问

- **为什么不能用原始 softmax？** 未校准，且 GUI 候选彼此相关；冲突和历史成功率往往比 logit 更有信息。
- **低风险为什么还要断言？** 试探的价值是用下一帧验证，不是多点一次碰运气。
- **coverage–accuracy 怎么读？** 同一任务集上扫阈值，报 $(\phi, \mathrm{acc})$；只报全覆盖准确率会惩罚诚实的 abstain。
- **和 grounding 题怎么分？** 定位题回答点哪里；本题回答何时故意不点。
