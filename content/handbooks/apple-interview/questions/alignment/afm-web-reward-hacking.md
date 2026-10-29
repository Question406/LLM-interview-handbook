---
{
  "id": "afm-web-reward-hacking",
  "section": "alignment",
  "order": 703,
  "level": "S",
  "title": "Reward Model：怎样训练，并识别高分却退化的 reward hacking？",
  "quick": "用同 prompt 的 preference 数据训练，再用独立评价检查 score 与行为是否一致。 真实质量提高，而非只提高被优化的 proxy。",
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
      "title": "TechAIInterview — Post-training & Alignment Q4",
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

参考 [TechAIInterview — Post-training & Alignment Q4](https://www.techaiinterview.com/topics/post-training-alignment/) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
说明 reward model 的训练数据与 objective。当 RL reward 提高而 human preference 降低时，如何诊断、修复与决定是否回滚？来源题讨论 reward model 和 reward hacking；冗长退化是练习场景。

## 技术备查
对于 prompt $x$ 与 preferred / rejected responses $y_w,y_l$，常见 pairwise loss 为：
$$\mathcal{L}_{RM}=-\log\sigma(r_\phi(x,y_w)-r_\phi(x,y_l)).$$
该 objective 学到相对排序，不自动保证跨任务的绝对 score 可比。应按 prompt family 划分数据，避免近重复对泄露。

独立评价不要依赖同一个被优化的 reward model。检查 length-controlled preference、verifiable correctness、over-refusal 和不同 policy 来源；测试 evaluator 是否被回答内的指令干扰。

## 面试追问
**更大的 reward model 能解决吗？** 容量可能改善拟合与泛化，也可能更好地学习 spurious correlations；需要独立实验，不能只看训练 accuracy。

**Outcome reward 与 process reward 怎么选？** 可验证终局适合 outcome signal；过程监督能定位中间错误，但成本与标注歧义更高，过程高分也不保证最终正确。
