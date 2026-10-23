---
id: dt-deliberate-spec
section: labs
order: 37
level: S
title: OpenAI deliberative alignment：政策写进思考，训练时为什么要把 spec 撕掉？
quick: "为了让模型学会自己回忆该用哪条规则。生成安全示范时让模型看着政策、在推理里引用条款，SFT 时把政策正文拿掉，模型只能靠回忆；RL 的评分器仍看着政策来核对。验证同时看越狱抵抗和过度拒绝，并记下条款版本。"
companies:
  - apple
tags:
  - OpenAI
  - Safety
  - Reasoning
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deliberative Alignment
    url: https://arxiv.org/abs/2412.16339
    type: primary
  - title: Introducing the Model Spec
    url: https://openai.com/index/introducing-the-model-spec/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

撕掉 spec 是为了逼模型自己回忆规则。SFT 时要是整份政策一直摆在上下文里，模型学到的只是「去提示里找现成的条款」；把正文拿掉，它才必须在推理里想起哪条规则适用。RL 阶段的奖励模型（RM）还是看着 spec 打分，用来核对模型回忆得对不对，这种不对称是有意的。

举个例子，用户问一种危险化学品怎么合成。造数据时，系统提示里放着相关的安全条款，模型的推理写成「这属于条款 X 说的情况，所以只给一般性信息」。SFT 时 prompt 里没有条款，标签还是这段推理，模型就得自己想起条款 X。

公开材料里，OpenAI 用这个方法对齐 o 系列。先训一个只有帮助性、没含安全数据的推理底座。然后把相关安全条款放进系统提示，采样 `{prompt, CoT, output}`，要求推理引用适用的条款，这一步不需要人逐条写推理和最终回答。接着用能看到政策的 RM 筛示范，SFT 时换回不带政策正文的原 prompt，让模型自己回忆条款；RL 时 RM 仍然按政策评分。论文报告越狱抵抗提高了，过度拒绝也下降了。对照一下 Model Spec 2024 草稿，当时它主要是给人工 RLHF 当指南，还没有直接按政策原文训练。

验证要两头看：越狱是不是更难成功了，本该回答的问题误拒是不是变少了。生成器和 RM 看的是同一份 spec，有自己给自己打分的风险，要靠独立验证和人评检查，见 `dt-rlaif-loop`。

条款版本也要进数据血缘。政策一变，引用旧条款的推理要重新检查，过期引用按错误处理，条款哈希和数据卡关联起来，见 `dt-repro-lineage`。

## 追问

**推理时直接把政策贴进上下文不就行了？**
上下文长度有限，每轮都贴一份长政策不现实。希望模型记住条款，训练时就得练回忆，这也是撕掉 spec 的理由。

**用户或网页里写了一条「新政策」怎么办？**
按低权限内容处理，和工具返回一样，升不成系统条款，也不改变系统规则，见 `dt-tool-inject`。

**它和 Constitutional AI、成对的拒答数据有什么区别？**
关注点不同。`dt-safety-refuse` 强调应拒和应答成对，避免一律拒绝；Constitutional AI 根据原则生成反馈；deliberative alignment 关注的是先回忆条款、再回答。

**思考过程要给用户看吗？**
由产品约定决定，训练里照样可以有这段过程。安全题的数据用研究集和合成的冲突样本。
