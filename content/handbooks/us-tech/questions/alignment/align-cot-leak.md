---
id: align-cot-leak
section: alignment
order: 25
level: A
title: 对齐：隐藏思维链与思考预算如何泄漏
quick: "隐藏思维链除了直接展示，还可能通过工具参数、日志、计费 token 数、TTFT 与二次训练泄露。应把可见回答和内部思考分开，限制日志与回传权限，用工具证据和最终行为评测，避免把隐藏链当成可靠解释或训练标签。"
tags:
  - OpenAI
  - Anthropic
  - Reasoning
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Learning to reason with LLMs (OpenAI)
    url: https://openai.com/index/learning-to-reason-with-llms/
    type: primary
  - title: Extended thinking (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
    type: primary
  - title: Language Models Don't Always Say What They Think
    url: https://arxiv.org/abs/2305.04388
    type: primary
---

隐藏思维链的泄漏要按数据流检查：除了用户直接索取，工具参数、日志、usage、延迟和后续训练都可能把内部信息带出去。关闭前端展示，只堵住其中一个出口。

OpenAI 推理模型公开说明内部链不直接展示，Anthropic extended thinking 区分思考块与可见回复，并要求签名、完整回传。具体 API 预算与可见性见 `anthropic-extended-thinking`。这道题据公开资料整理，并非现场逐字题。

隐藏的理由包括用户不需要整屏草稿、知识产权，以及内部安全判断本身可能成为攻击面。监督上也不能默认 CoT 忠实：Turpin 等人的 Language Models Don't Always Say What They Think 说明，写出的步骤未必反映实际推理。把漂亮 CoT 当标签还可能奖励形式，与 `align-process-reward` 的格式刷分有关。

## 沿出口逐项检查

用户或开发者接口直接要求内部块时，终端产品默认只给摘要或拒绝提供内部块。若开发者 API 返回完整思考，就是把边界扩到每个集成方，需要明确合同、默认关闭和日志分级，不能再直接透传终端用户。

工具也是出口。模型可能在搜索 query、代码注释或浏览器表单中写出推理，使第三方和宿主日志留下副本，工具参数要接受政策检查，见 `design-tool-prod`。账单与 usage 也可能暴露思考 token 长度，TTFT 暴露等待时间，足以让人推测难度、安全检查或长预算是否触发。固定 token 上限或 effort 越大，可能越慢、越贵、有时更准，预算既影响能力，也构成侧信道。

回传和二次训练同样要管。带 thinking 的 trace 被当作 SFT 或偏好数据，会把内部输出分布写进下一版权重。Anthropic 的签名与不接受残缺回传要求，用于防篡改和残缺泄漏，不能让用户任意改 thinking 再回传。默认用户日志不记录 thinking，内部调试、标注员与生产用户会话 ACL 分开，避免客服导出将其带出。

下面示意只取明确标记为可见的助手消息：

```python
def user_visible(trace):
    # trace 含 thinking / content / tool；对终端用户只放 content
    return [m for m in trace if m["role"] == "assistant" and m.get("visible")]
```

## 怎样评测和使用

探针集检查内部敏感结论、该拒的细节或隐藏假设是否复述进可见答案；红队把直接索取与诱导写入工具分成专门切片，见 `align-red-team`。Grader / RM 评最终答案，避免 RFT 变成优化写给 grader 的内部草稿，见 `align-rft`；过程信号尽量取环境事件。

摘要也不能承诺等同因果解释。有证据需求时给工具结果和文档跨度，见 `apple-siri-grounded`。安全监控主要看动作、最终输出，必要时抽样子轨迹，不能只信自述链。

Serving 要给用户独立的“正在推理”状态，长思考会拖 TTFT，也会与 `design-chat-serving` 的输出 token 桶争额度。若讨论开 thinking 提高 Arena，要一起评估延迟、计费、泄漏与过优化，见 `align-overopt-rm`。

## 追问

**关掉展示就安全了吗？**
还不够。工具、计费、延迟和二次训练仍可能暴露内部信息。

**CoT 展示能当安全监控吗？**
不可靠，链可能不忠实，应结合动作与最终输出。

**给开发者返回 thinking 可以吗？**
这是另一个信任边界，需要合同、默认关闭和日志分级，终端产品不默认透传。

**过程奖励会冲突吗？**
若直接奖励隐藏链，可能让模型更擅长输出这段内部过程；优先使用可检查的环境事件。
