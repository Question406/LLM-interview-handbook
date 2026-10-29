---
id: cu-failure-taxonomy
section: computer-use
order: 3
level: A
title: >-
  Computer-use Agent 失败后，怎样定量归因到 visual grounding、OCR / 感知、planning、action
  execution 或 environment，而不是笼统说模型差？
quick: >-
  按第一个不可恢复的错误归层：每步留 checkpoint，依次问看见了吗、读对了吗、计划对吗、点对了吗、环境动了吗，后面的连锁失败记成
  propagation。再用各层的 microbench 验证，按任务难度聚合 first-failure 占比，从占比最高的一层开始改。
tags:
  - Failure Analysis
  - GUI Agent
  - Observability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: SeeAct
    url: 'https://arxiv.org/abs/2401.10935'
    type: primary
---

我会按「第一个不可恢复的错误发生在哪一层」来归因：每一步都留 checkpoint，找出 first failure，再用那一层的 microbench 去验证。端到端成功率只能用来验收，它告诉不了你该改哪里。

举个例子，同样是「报销单没提交成功」，可能是 OCR 把金额读错了，可能是看对了却点错了按钮，可能是规划没问题但滚动之后坐标失效了，也可能是点击成功了表单却没提交。这四种修法完全不一样。没有中间产物、只有一个最终 fail 标签的话，统计会把所有层混在一起，看着像「规划不行」，其实可能全是 OCR。

## 五层怎么切

我会按五层查一次运行。observation 看截图、DOM 和无障碍信息全不全；state interpretation 看 OCR、图标和页面语义理解得对不对；plan 看下一步意图对不对；action grounding 看元素或坐标对不对；execution verification 看动作回执和业务状态是否一致。环境层单独记，弹窗、超时、登录过期、站点改版都算这里，别记成 grounding 失败。每层都要有能检查的中间产物，光看最后一屏判断不了。

每个 step 记这些字段：截图 ID、DOM / a11y 摘要 hash、模型观察摘要、候选 action、实际发出的 action、执行回执、oracle checkpoint。这些字段至少要能回答「错发生在发出点击之前还是之后」。然后标出 first irreversible error，后面的连锁失败记为 propagation。标注员只标 first-failure，propagation 由脚本根据后续 checkpoint 自动打。first-failure 最好双人标，并报告层间一致性，别拿 LLM 读自己的视频当唯一标签；有争议的样本拿到 calibration 会上过。

标注手册里把五层写成五个判定问题：看见了吗、读对了吗、计划对吗、点对了吗、环境动了吗。层的定义不稳，分类数字会比模型还抖。

## 这些数怎么用

聚合时按任务难度、应用、需不需要滚动或跨页来切片。另外用独立的小集分别测 OCR、图标识别、元素定位、短程状态转换、长程规划。端到端失败要能回溯到其中一层，回溯不到，就别发「视觉模型升级带来提升」这种因果结论。

周报按 first-failure 占比排改进顺序，改进实验针对占比最高的那层做 microbench，e2e 只当 acceptance checks 复测。某次升级 e2e 涨了，first-failure 分布却没变，多半是环境噪声或者任务太简单。某一层占比突然跳变，先查标注定义和观测是否完整，再下模型变差的结论。

评测里容易刷出好看数字的做法有这几种：人工看视频凭印象归类、不标 first failure、把超时全算到模型头上、用 LLM 读自己的 trace 当唯一标注、把环境改版算进 grounding。能把一次具体失败落到某一层，比说「视觉模型还不够强」有用得多。

## 追问

**点击 API 返回成功，算 execution 成功吗？**
不算。还要看焦点、URL、表单值和业务 oracle 对不对得上。

**observation 缺失怎么判？**
关键控件既不在截图里也不在树里，就归环境 / 观测，别算成模型点不准。

**超时算哪一层？**
先分清是环境没响应还是模型在空转。前者归环境，后者归规划，同时记下预算。

**和坐标漂移那题怎么分？**
`vlm-screenshot-coordinate` 讲坐标为什么会漂；这题讲失败之后怎么定量拆层。
