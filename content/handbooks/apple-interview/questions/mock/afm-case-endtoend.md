---
id: afm-case-endtoend
section: mock
order: 50
level: A
title: 贯穿案例：截图创建日历事件，从合成到评测再到偏好 feedback loop
quick: 用同一个任务贯穿视觉证据、字段抽取、工具执行、恢复 trajectories、偏好选择和隐私反馈。每轮只针对确认的缺口改数据，并用独立任务和副作用指标验收。
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
  - title: Multimodal RewardBench 2
    url: 'https://arxiv.org/abs/2512.16899'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---

## 任务与 constraints
原创设计案例，不是你的项目或 Apple 内部配方。输入许可来源的活动海报截图和用户指令，输出可核验的日历提议；执行写入需遵循产品确认契约。必备字段为标题、日期、开始时间、时区；图中缺失的信息应澄清，不能猜。线上不默认把私人截图加入 training data 基础模型训练。

## 一条完整 pipeline
来源登记许可和用途→按海报模板家族切分→渲染海报与隐藏结构化真值→生成不同表达指令→模型生成字段、工具参数和回复→schema/字段/时区/执行状态验证→按成功、可恢复失败、违规 trajectories 归类→构造 SFT 与 preference data→固定预算训练→独立模板、日期、语言和真实许可样本评测。记录 source_id、template_family、generator_version、verifier_version、dataset_hash 和 split，防止同模板改字 leakage。

一个记录包含 task_id、image_ref、instruction、evidence_fields、tool_schema_version、trajectory、final_state、verifier_result、label_provenance；证据字段是合成环境或 annotator 真值，不能暴露给被评模型。SFT 对监督助手 token 计 loss，失败过程不整段当正例。偏好比较同一指令的两条 trajectories：先满足权限与状态约束，再比较正确、完整和必要澄清，不能让礼貌补偿错日期。

## 三轮迭代与 attribution
第0轮冻结任务和 capability slices，建立 OCR/字段/调用/状态各层 baseline。第1轮若证据显示时区错，训练干预补跨日、夏令时 edge cases 与缺失时区澄清，保持总 token、算力和其余 mix；环境时间语义需用固定版本时区库校验。第2轮若 tool timeout 后重复创建，补可 replay 的幂等请求、查状态和安全重试 trajectories；不要把普通写入错误解释成视觉不足。每轮记录对照、样本收益、negative transfer 和成本，不预写“第二轮必涨”。

评价包括字段 exact match、完整任务成功、重复写入、不当确认、必要澄清、延迟及成本。按模板家族做配对评测和不确定性分析。成功率提高但重复写入超过预设上限时不发布。反馈只在合法授权通道处理，聚合失败类型可指导合成复现；数据撤回按 lineage 定位来源，并按政策处理派生数据。

## 可运行的缩小实验
[self-iteration 脚本](/apple-prep/self_iteration.py) 用 CPU PyTorch 做“student 提议候选→精确 verifier 筛选→student 重训→独立验证→停止”。为保证可运行，它使用算术回归而不是截图或 LLM，不把玩具收益当作 multimodal 结果。每轮输出候选数、通过数、训练新增和冻结开发/最终测试误差；最终测试仅在停止后读取。运行 `python3 self_iteration.py`，无需网络或真实日志。

## 面试追问
**什么时候选 pre/mid/post？** 普遍视觉文字覆盖不足考虑基础/continued pre-training，已有读图能力但领域分布不足比较 mid-training，工具协议、澄清与确认行为优先比较 post-training；用对照与遗忘风险决定，不只背阶段名。
**verifier 被钻空子呢？** 单独保留对抗 validator 测试与真实许可评价，检查只改表面格式是否骗过规则；状态正确也不等于没有越权。
**Director 要你砍一半预算？** 保留独立评测和关键风险审计，缩小生成量与训练规模，先用无训练诊断确认瓶颈。
