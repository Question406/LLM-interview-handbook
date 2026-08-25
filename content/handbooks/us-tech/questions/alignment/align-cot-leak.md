---
id: align-cot-leak
section: alignment
order: 25
level: A
title: 对齐：隐藏思维链与思考预算如何泄漏
quick: >-
  产品给用户看的是摘要，模型内部还有一段思考。泄漏不只是「请复述你的 hidden thoughts」：计费与 token
  数、TTFT、工具参数、日志和二次训练都会把链交出去。默认不展示、不当标签、不让用户改 thinking 再回传。
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

OpenAI 的推理模型公开说内部链不直接给用户；Anthropic extended thinking 把思考块和可见回复拆开，还强调签名和回传完整性。对齐 / 产品岗问的是「为什么藏、藏不住会怎样」，不是让你设计套话去把链掏出来。不是某次现场逐字题。API 预算与可见性见 `anthropic-extended-thinking`。Turpin 等人说明：即使把 CoT 写出来，也不等于模型真按那段话推理。

## 为什么要藏，藏的是什么

隐藏链的产品理由通常有三条：用户体验（一屏草稿）、知识产权、安全（模型在内部权衡如何拒答、如何绕过自己的政策，那段话本身是攻击面）。监督理由是：可见 CoT 当标签会训练模型**写漂亮步骤**，和 `align-process-reward` 的格式刷分同类；而 Turpin 的结果是 CoT 可以不忠实。所以「把思考展示给用户当可解释」在面试里要先打折。

泄漏通道比「用户问一句」多：

1. **直接索取。** 用户或开发者接口要求打印内部块。产品默认应拒绝或只给摘要；开发者 API 若返回思考，等于把链交给每一个集成方。
2. **工具侧写。** 模型把推理写进搜索 query、代码注释、浏览器表单。宿主日志和第三方就有了副本。工具参数要过政策，见 `design-tool-prod`。
3. **遥测与计费。** 思考按输出 token 计费时，账单和 usage 字段会暴露长度。长度本身是信号：难题、安全检查、是否触发了长预算。
4. **时间侧写。** TTFT 随思考变长。即使用户看不到字，也能区分「秒回」和「想了很久」。
5. **回传与二次训练。** 把带思考的 trace 当 SFT / 偏好数据，等于把本不该公开的分布写进下一版权重。Anthropic 文档要求思考块带签名、半截不回传——工程上就是防篡改和防残缺泄漏。

思考预算（固定 token 上限或 effort）会从产品行为泄漏：同一题开高预算就慢、贵、有时更准。攻击者不必读到字，只要能操纵预算开关或观察延迟。面试讲「预算是能力旋钮也是侧信道」。

```python
def user_visible(trace):
    # trace 含 thinking / content / tool；对终端用户只放 content
    return [m for m in trace if m["role"] == "assistant" and m.get("visible")]
```

不要在用户日志里默认打开 thinking。内部调试与用户会话 ACL 分开。

## 评测和训练纪律

评测泄漏：用探针集看模型是否把内部结论复述进可见答案（该拒的细节、隐藏的中间假设）。这是行为测试，不是越狱教程。训练：grader / RM 打最终答案，不要打隐藏链；否则 RFT 会优化「写给 grader 看的草稿」，见 `align-rft`。红队把「索取内部块、诱导写入工具」单列一类，见 `align-red-team`。

忠实性：即使用户看到摘要，也不要承诺摘要等于因果解释。需要接地时，引用的是工具结果和文档跨度，见 `apple-siri-grounded`，不是内部独白。

Serving 上思考块会拖 TTFT：用户侧要独立的「正在推理」状态，不要假装已经在写答案。预算开大时和 `design-chat-serving` 的输出 token 桶抢额度。产品若把 thinking 流给内部标注员，ACL 必须和生产用户会话分开，否则一次客服导出就泄漏。

面试收：藏链是信任边界，不是装饰。问你「能不能开 thinking 提高 Arena」时，把延迟、计费、泄漏和过优化一起讲，见 `align-overopt-rm`。

## 追问

- **给开发者 API 返回 thinking 可以吗？** 等于换了一个信任边界。要合同、默认关、日志分级；终端用户产品不要透传。
- **CoT 展示能当安全监控吗？** 不可靠。链可以不忠实，监控应看动作和最终输出，必要时看抽样子轨迹。
- **关掉展示就安全了吗？** 没有。工具、计费、延迟、二次训练仍会漏。
- **和过程奖励冲突吗？** 过程奖若吃隐藏链，等于把泄漏通道训练得更顺。过程信号用环境事件。
