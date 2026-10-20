---
id: cu-failure-taxonomy
section: computer-use
order: 3
level: A
title: Computer-use Agent 失败后，怎样定量归因到 visual grounding、OCR / 感知、planning、action execution 或 environment，而不是笼统说模型差？
quick: 我会用带 checkpoint 的 trace 和能力 microbench 分层。先看观察有没有读错，再看计划、动作执行、环境。记下第一个不可恢复错误和后面怎么传，再按类别和任务难度聚合。
tags:
  - Failure Analysis
  - GUI Agent
  - Observability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SeeAct
    url: https://arxiv.org/abs/2401.10935
    type: primary
---

端到端成功率只能验收，不能指导改哪里。OCR 读错金额、看对了却点错按钮、规划对但滚动后坐标失效、点击成功但表单没提交，修复路径完全不同。分层归因：每一步记 checkpoint，标 first failure，再用 microbench 验证该层。没有中间产物的失败分类，统计上会把所有层混在一起。

## 五层切分

按五层检查一次运行：observation 看截图、DOM 和无障碍信息是否完整；state interpretation 看 OCR、图标和页面语义是否理解正确；plan 看下一步意图是否正确；action grounding 看元素或坐标是否正确；execution verification 看动作回执与业务状态是否一致。环境层单独计：弹窗、超时、登录过期、站点改版。不要把环境故障记成 grounding 失败。关键控件不在截图也不在树里，应归观测 / 环境，而不是模型点不准。点击 API 成功不算 execution 成功，还要看焦点、URL、表单值和业务 oracle。每层都要有可检查的中间产物，不能只看最后一屏。

## 要记的字段

每个 step 记录：截图 ID、DOM / a11y 摘要 hash、模型观察摘要、候选 action、实际发出的 action、执行回执、oracle checkpoint。标注 first irreversible error，后续连锁失败记为 propagation。聚合时按任务难度、应用、是否需要滚动 / 跨页切片。只有最终 fail 标签的数据集，看起来会像「规划不行」，其实可能全是 OCR。双人标注 first-failure，并报告层间一致性；不要只用 LLM 读自己的视频当唯一标签。字段要能回答「错发生在发出点击之前还是之后」。

## Microbench 与能刷的点

用独立小集分别测 OCR、图标识别、元素定位、短程状态转换、长程规划。端到端失败必须能回溯到其中一层，否则不要发「视觉模型升级带来提升」这种因果句。评测上能刷的是：人工看视频凭印象归类；不标 first failure；把超时全算模型；用 LLM 读自己的 trace 当唯一标注；把环境改版算进 grounding。

改进优先级来自分层占比。周报按 first-failure 占比排序改进，而不是按总分焦虑。标注手册写清五层的判定问题：看见了吗、读对了吗、计划对吗、点对了吗、环境动了吗。层定义不稳定，分类数字会比模型还抖。改进实验应针对占比最高的一层做 microbench，e2e 只作门禁复测。若某次升级 e2e 涨了但 first-failure 分布没变，多半是环境噪声或任务过易。

标注员只标 first-failure，propagation 由脚本根据后续 checkpoint 自动打。争议样本进入校准会。若某一层占比突然跳变，先查标注定义和观测是否完整，再下结论说模型变差。能把一次具体失败走到某一层，比说「视觉模型还不够强」更有信息量。

## 追问

- **点击 API 成功算 execution 成功吗？** 不算。还要看焦点、URL、表单值和业务 oracle。
- **observation 缺失怎么判？** 关键控件不在截图也不在树里，应归环境 / 观测，而不是 grounding。
- **和坐标题怎么分？** `vlm-screenshot-coordinate` 讲坐标为何漂；本题讲失败后如何定量拆层。
- **超时算哪一层？** 先看是环境无响应还是模型空转；前者归环境，后者归规划并记预算。
