---
id: drustz-56de7ddbcbb63aad16
section: mlsd
order: 8
level: A
title: 05 · Case Study：OCR / Signature Recognition ML System Design · 1. 需求、输出合同与系统边界
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 1.
  需求、输出合同与系统边界
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md
    type: primary
---
## 1. 需求、输出合同与系统边界

### 1.1 成功定义

系统不应只返回一个无解释的 `0.87`，而应返回一个可审计的 decision artifact：

```json
{
  "document_id": "doc_123",
  "model_version": "sig-v17",
  "policy_version": "claims-high-value-v4",
  "signatures": [
    {
      "bbox": [0.14, 0.72, 0.46, 0.83],
      "detection_confidence": 0.995,
      "type": "wet_ink",
      "quality": { "usable": true, "issues": [] },
      "linked_fields": {
        "signer_name": { "value": "Jane Doe", "source_bbox": [0.1, 0.63, 0.43, 0.69] },
        "signed_date": {
          "value": "2026-07-21",
          "source_bbox": [0.53, 0.72, 0.72, 0.78]
        }
      },
      "verification": {
        "reference_set_id": "ref_jane_v3",
        "score": 0.78,
        "calibrated_p_genuine": 0.94,
        "decision": "REVIEW",
        "reason_codes": ["single_reference", "cross_device_shift"]
      }
    }
  ]
}
```



关键原则：

- **score 不是 probability**；只有经过 held-out calibration 后才能叫概率。
- `model_version` 与 `policy_version` 分开。模型产生证据/分数，业务 policy 根据风险、金额、客户决定阈值。
- detection、quality、verification 各自保留分数，避免只看到最终 decision 而无法归因。
- OCR 字段必须带 `source_bbox`；签名验证结果不应被表述为法律上的“真实性证明”。

### 1.2 Non-goals（主动讲很加分）

v1 不做：

- 仅凭静态图像宣称绝对检测所有 sophisticated forgery；
- 用签名字形猜测性格、健康、性别等没有业务依据的属性；
- 在 reference 不可信或只有严重裁剪的一张样本时给高置信自动通过；
- 把 cryptographic digital signature validation 和手写图像相似度混为一谈；
- 让一个通用 VLM 直接输出“真/假”并作为高风险最终裁决。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
