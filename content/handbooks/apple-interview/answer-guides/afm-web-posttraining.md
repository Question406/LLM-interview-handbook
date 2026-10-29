---
{
  "id": "afm-web-posttraining",
  "kind": "design",
  "situation": "新的 base model 有语言能力，但 instruction following、安全和 reasoning 不稳定。",
  "task": "为不同 capability gaps 选择对应的训练信号与验收。",
  "approach": "先建立基线，区分 SFT、preference 与 verifiable reward 的作用，再逐步干预。",
  "result": "目标能力提高，同时保留通用能力并控制 over-refusal。"
}
---

## 可以这样回答

我不会先决定必须做几轮 RL，而会先测 base model：它是不会执行指令，还是能理解任务但经常推理错误？这决定我们缺的是行为示范，还是能区分好坏的反馈。

第一步可以用高质量 SFT 建立对话格式、tool calls 和基础行为。对回答有多种合理方式的任务，再用 preference data 改善有用性与安全取舍。数学和代码如果有可信 checker，可以增加 verifiable reward；但需要先验证 checker，避免模型学会利用测试漏洞。

数据也要分别管理。SFT 需要正确示范，preference 需要同 prompt 的可比候选，online RL 需要可以采集 current policy rollouts 的任务环境。不能因为它们都来自同一批日志，就直接共用一个训练文件。

每增加一个阶段，我会用同一套独立 evaluation 查看目标收益、通用能力、over-refusal 和成本。如果 preference 训练提高了安全分却让正常问题被大量拒绝，就需要检查标签和 data mix，而不是把它当成必然代价。
