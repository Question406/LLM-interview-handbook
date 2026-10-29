---
{
  "id": "afm-web-posttraining",
  "section": "alignment",
  "order": 705,
  "level": "S",
  "title": "Post-Training Design：从 base model 到可靠 assistant，数据怎样分工？",
  "quick": "先建立基线，区分 SFT、preference 与 verifiable reward 的作用，再逐步干预。 目标能力提高，同时保留通用能力并控制 over-refusal。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "alignment"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "TechAIInterview — Post-training & Alignment Q7",
      "url": "https://www.techaiinterview.com/topics/post-training-alignment/",
      "type": "reference"
    },
    {
      "title": "InstructGPT: training with human feedback",
      "url": "https://arxiv.org/abs/2203.02155",
      "type": "primary"
    }
  ]
}
---

## 来源与范围

参考 [TechAIInterview — Post-training & Alignment Q7](https://www.techaiinterview.com/topics/post-training-alignment/) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
为新 base model 设计 post-training pipeline，覆盖 helpfulness、safety、reasoning 和 tool use。说明数据、训练阶段、反馈迭代与 release criteria。来源为 Staff 级 post-training 设计题；tool-use 及具体验收要求是 AFM 扩展。

## 技术备查
Pre-training 建立广泛知识与表示；mid-training 的具体命名因团队而异，面试时需先确认是否指领域、长上下文或能力定向的 continued training；post-training 关注 instruction following、偏好与交互行为。阶段名不替代 objective、data mix 和 evaluation 的定义。

每阶段保存数据 lineage、训练配置与 checkpoint。先隔离 evaluation，再生成新样本；不能将最终 blind set 的失败逐题扩写后仍报告为未见测试。

## 面试追问
**Self-improvement 怎么接入？** Current policy 产生多候选，经独立 verifier 或审计后得到示范与 pairs；按任务家族检查 coverage 和错误，下一轮评估使用未参与选择的数据。

**什么时候不继续训练？** 若问题来自工具权限、检索缺失或环境故障，先修系统；模型数据干预需要对应证据。
