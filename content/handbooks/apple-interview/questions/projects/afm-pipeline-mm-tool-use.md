---
id: afm-pipeline-mm-tool-use
section: projects
order: 10
level: S
title: Pipeline 3：从票据截图到表格操作，合成 multimodal Tool-Use 数据
quick: 我会从票据截图填表这种能检查结果的任务开始。先知道图片里正确的金额，再让 agent 操作，最后读导出的文件判断它到底做没做对。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Data Pipeline 实例
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: AgentTrek — paper
    url: 'https://arxiv.org/abs/2412.09605'
    type: primary
  - title: AgentTrek — official project
    url: 'https://agenttrek.github.io/'
    type: primary
  - title: VisualSkill
    url: 'https://arxiv.org/html/2606.18448v1'
    type: primary
  - title: OSWorld
    url: 'https://arxiv.org/abs/2404.07972'
    type: primary
---

## 面试官可能这样问

举一个 multimodaltool-use 的数据 pipeline。你会怎么收集、怎么判断数据好不好？

## 可以这样回答

我会选一个比较容易检查结果的任务，比如给 agent 一张票据截图，让它把日期、币种和总额填进表格，再导出文件。这样既要读图，也要实际操作软件，最后还有一个可以检查的结果。

最开始我会用合成票据。先确定日期和金额，再把它们渲染成不同样式的图片，所以我知道正确答案是什么。让 agent 在固定的软件环境里操作，记录它每一步看到的截图和接下来的动作。结束以后，我直接检查导出的表格，不能因为 agent 说“已经完成”就算成功。

如果金额填错了，我会先看它是把图读错了，还是知道金额却填错了格子。比如小计是115，总额是128.50，它填了115，这更像是字段理解的问题；如果它正确说出了128.50，却输入到日期那一格，问题就更接近界面操作。这两种错误，我会补不同的数据。

训练时先用实际完成、过程也合理的 trajectories。评价时换一批票据布局，而不只是换金额。如果换个排版就不会了，说明它可能记住了位置，没有真正学会找总额。这条 pipeline 是我会设计的扩展；和我参与的 VisualSkill 工作可以连接起来讲，但不能把这套票据实验说成已经做过。

## 被追问时再展开

**为什么不用 OCR 加脚本？** 我会把它作为 baseline。如果固定票据模板用 OCR 就能很好解决，那没有必要强行做复杂 agent。这个例子更适合需要理解变化的页面、再跨软件完成操作的场景。

**数据怎么扩大？** 我会根据真实失败补变化，比如小计和总额很接近、日期格式不同、表格需要滚动。先确认是哪一种变化带来错误，再生成对应的新样本，而不是只把同一个模板复制很多遍。

## 英文口述参考

I would use a task with an outcome I can check, such as reading a receipt image, entering the date and total into a spreadsheet, and exporting the file.

I would begin with synthetic receipts, so I know the correct fields before rendering the image. During collection, I would record the screenshot the agent saw before each action. Afterwards, I would inspect the exported spreadsheet. The agent saying it succeeded would not be enough.

If it failed, I would separate reading errors from action errors. Entering the subtotal instead of the total suggests a different data problem from reading the amount correctly but typing it into the wrong cell. I would collect examples for the failure I actually observed, and test on new receipt layouts to see whether the model learned more than a fixed screen position.

## 技术备查

## 新找到的公开材料
[AgentTrek](https://arxiv.org/abs/2412.09605) 提供教程收集、任务化、replay 及 trajectories 评价的公开路径；[官方项目页](https://agenttrek.github.io/)可继续找代码与数据。它使用 VLM 评价，不等于 trajectories 被形式化证明正确。

下面的票据→表格流程是建议扩展，不是 AgentTrek、OSWorld 的指定任务，也不是你的既有实验。[VisualSkill](https://arxiv.org/html/2606.18448v1) 用于衔接你参与的图文技能研究，[OSWorld](https://arxiv.org/abs/2404.07972) 用于理解真实软件的状态验收。

## 1. 具体任务与 tool interface 与 permissions
给 agent 一张合成票据截图，要求在本地表格模板填写商户、日期、币种、含税总额，并导出报销 CSV。例子字段为商户 Atlas、日期2026-10-02、币种 USD、总额128.50。不能把小计115.00当总额，也不能按 locale 把1,280.50误读成1.28050。

动作接口为读取截图、点击、输入、滚动、快捷键及等待；工具返回只包含运行时可见信息。verifier 侧可以检查合成真值和最终文件，agent 不能读取隐藏 CSV 答案/底层数据库。若另开文件读取或 OCR 工具，单独作为 action space 条件做对照，不能混报为纯视觉能力。

## 2. Pipeline 与产物
`许可教程/人工演示 → 结构化任务spec → 合成票据与真值 → 按布局/任务家族切分 → 在冻结软件环境回放 → 对齐截图和动作 → 字段/状态/权限核验 → 过程清洗 → SFT/偏好/RL视图 → 未见布局验收 → 定向生成难例`

| 阶段 | 中间产物 | data quality checks |
| --- | --- | --- |
| 任务 seed | 许可教程或人工标注的操作目标、前置条件、工具范围 | UI 版本、数据用途与可执行性明确；教程不是最终真值 |
| 票据生成 | structured seed、render 参数、截图、字段真值 | 真值对照渲染结果，检查截断/模糊/遮挡；无法辨认时需澄清，不硬标可解 |
| 家族切分 | vendor/layout family、locale、字段组合、软件模板 | 同底图/布局 near-duplicates 及派生 trajectories 同 split；新 seed 不自动代表新布局 |
| 多 trajectories 采集 | policy checkpoint、初态、动作前截图、tool 输入输出、结束状态 | reset 一致；前一轮输入的文件不能遗留到下一 attempt |
| 对齐 | obs_id、frame 时间、viewport/DPI、action 时间、state 版本 | 必须动作前可见的帧；过期截图、错位坐标或不稳定工具记录隔离 |
| 独立验收 | 导出 CSV 解析、字段对比、目标路径、无额外写入 | 不由 agent 自报成功；可接受多条合法操作路径，不硬贴唯一 click 序列 |
| 训练清洗 | 成功、失败、恢复、越权、不可判定 | 终局成功但改错其他单元格/读取隐藏状态的 trajectories 不能自动入选 |

## 3. 一步样本与权限分离
```json
{
  "task_id": "receipt-021",
  "task_family": "receipt-to-sheet",
  "split": "train",
  "obs_id": "frame-004",
  "screenshot_ref": "example://receipt-021/before-004.png",
  "viewport": { "width": 1280, "height": 800, "scale": 1 },
  "pre_state_version": 3,
  "action": { "tool": "gui.type_text", "arguments": { "text": "128.50" } },
  "post_state_version": 4,
  "supervision": { "assistant_action": true, "observation_loss": false },
  "artifact_status": "schema_example_not_collected_trace"
}
```

核验侧另存 `expected_fields`、渲染 seed、隐藏输出检查及关键错误，不与模型 prefix 拼接。`gui.type_text`是本例自定义工具名，不宣称某公开框架提供此接口。[示意 JSONL](/apple-prep/pipelines/mm_tool_use.jsonl)给出完成、错读金额、截图错位三种记录。

## 4. 如何验证“真的看图并正确用工具”
先核对图像是否有可辨识真值，再分别做：正确截图、只改总额的成对截图、去掉必要视觉证据、给 oracle 字段、给 oracle 点击目标。它们用于区分读图/语义、grounding 和执行规划；不能只看一次遮图掉分就下 causal 结论。

主要验收是导出文件的字段正确、任务完成、无额外修改；截图 VLM 评分只能作为补充。只有已知币种/locale 才能正确 normalization 金额和日期，缺少证据时澄清是合格行为。按金额、小数、日期、币种、滚动和错误恢复 evaluation slices，警惕视觉 judge 偏爱格式漂亮但数字错误的产物。

## 5. 三类训练样本
**SFT**：保留合法成功与经过审计的恢复操作；输入包括当时截图、指令、允许的历史工具结果，loss 只监督 assistant 动作/回答。不把环境截图、工具回包或私有真值当作要模型生成的目标。随机一条 trajectories 的坐标不能直接贴到不同 viewport 上。

**Preference / RM / DPO**：从同一票据、模板与初态分别 rollout，正确导出胜过错金额但流畅总结；两条都正确时再比较重复操作和成本。若比较同一 prefix 后的分支，必须重置到相同状态再执行。跨任务随意配 success/fail 会 leakage 难度和长度，不能当作纯质量偏好。

**RL**：将渲染器、软件快照与独立 checker 打包成可重置环境，current policy 在线操作。终局成功是主要奖励，越权和破坏文件是约束；中间“填满一格”只能是经验证的辅助项，避免鼓励填错也得分。若过程缺少足够可验证状态，先用 SFT 冷启动与可学任务，不拼凑伪奖励。

## 6. data flywheel 与规模
如果读图 oracle 恢复，补字段易混淆布局；如果 oracle 字段仍失败而 oracle 点击恢复，补 UI grounding；如果点击也正确却导出错位置，补多步状态检查与文件流程。每轮按确认的失败家族造新任务，保留正常短流程与澄清任务；不只放大错误最多的重复模板。

截图以对象 hash 保存，manifest 只放引用，按可见 viewport 和应用版本 deduplication/分桶；大规模采集 worker 独立环境、超时恢复和幂等 attempt 记录。报告每千条独立合格 trajectories 的成本及 hard examples 收益，而不是只报生成量。图像含私人内容的部署不能默认把反馈加入 training data，研究环境使用许可或合成材料。

最终在未见布局、应用模板和不同分辨率上，与同模型同预算的 no-training/随机合成/定向合成对照。记录端到端任务、字段正确、非法副作用、时间与视觉 token 成本；训练环境涨分而新布局不涨时，先排查模板记忆和 checker 漏洞。

## 90秒英文参考
> For multimodal tool use, I would build a receipt-to-spreadsheet pipeline. A structured seed would generate the receipt image and private ground truth. The agent would see screenshots and interact with a fixed GUI tool interface, while a separate verifier would inspect the exported file. Every action would be aligned with the screenshot visible before it. I would use matched image edits and oracle substitutions to distinguish visual extraction from grounding and planning failures. Verified trajectories could support SFT, resettable branches could form preference pairs, and the same task generator could support online RL with held-out layout families.

## 追问
**为什么不直接用 OCR 加脚本？** 这是有价值的强 baseline；若结构化输入已够，不必强行 VLM。只有需要视觉判别和 GUI 操作的任务才测本 pipeline 额外价值。
**教程 replay 与模型自主执行有何不同？** 教程可用于采 seed，训练/验收不能永久提供测试题逐步答案；保留无指导的新任务评价。
**可以说是你的 multimodal 项目吗？** 这条是方案，VisualSkill 里实际做过的内容按真实职责连接。

