---
{
  "id": "afm-web-synthetic-privacy-bias",
  "section": "synthetic",
  "order": 709,
  "level": "S",
  "title": "Synthetic Data Audit：合成数据为什么仍会泄露隐私或放大 bias？",
  "quick": "追踪源数据权限，测试 memorization 与任务分布，必要时采用明确的 privacy mechanism。 有证据支持限定用途的共享，并且 minority tasks 的质量没有被掩盖。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "synthetic"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "Sahi Padhai — Training Data and Synthetic Data: follow-ups",
      "url": "https://sahipadhai.cc/course/ai-engineer-interview/training-data-and-synthetic-data",
      "type": "reference"
    }
  ]
}
---

## 来源与范围

参考 [Sahi Padhai — Training Data and Synthetic Data: follow-ups](https://sahipadhai.cc/course/ai-engineer-interview/training-data-and-synthetic-data) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
如何判断一份 synthetic dataset 是否适合共享或训练？讨论 privacy leakage、bias amplification 与 utility。来源章节明确列出相关追问；本卡不提供特定司法辖区的法律结论。

## 技术备查
Nearest-neighbour distance 与 membership inference 是经验性审计，依赖攻击能力和参照数据；它们不是 differential privacy guarantee。若采用 DP，需明确保护单位、邻接定义、隐私预算及组合；不能只在输出文本上“加一点噪声”。

Utility test 应在未参与生成与选择的真实数据上运行，并检查 subgroup sample sizes 和 uncertainty。边缘分布接近不等于联合分布或任务关系得到保留。

## 面试追问
**只删姓名够吗？** 不够，稀有属性组合或逐字复制的事件仍可能识别个人；需要结合用途和 threat model。

**少数群体多生成一些就解决 bias 吗？** 数量不是标签质量或真实性。先定义具体任务差异，再核查生成内容是否变成刻板模板，最后看真实 subgroup utility。
