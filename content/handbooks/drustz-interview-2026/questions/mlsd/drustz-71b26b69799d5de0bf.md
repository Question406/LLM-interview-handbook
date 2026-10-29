---
id: drustz-71b26b69799d5de0bf
section: mlsd
order: 15
level: A
title: >-
  05 · Case Study：OCR / Signature Recognition ML System Design · 8.
  Security、fraud 与 abuse
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 8.
  Security、fraud 与 abuse
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
## 8. Security、fraud 与 abuse

### 8.1 Threat model

- replay：重复提交一张真实签名；
- copy-paste：从旧文档抠出签名贴到新文档；
- print-scan：用打印/复印抹去编辑痕迹；
- random/simple/skilled/traced forgery；
- diffusion/generative signature；
- enrollment poisoning：攻击者把假 reference 注册成可信样本；
- adversarial/malformed image/PDF，资源耗尽；
- insider/data exfiltration、gallery/embedding 泄漏；
- model probing/extraction，批量试分数找到 threshold。

### 8.2 防御是多信号系统，不是单模型

- enrollment 是根信任：身份校验、capture provenance、reference 更新需 step-up/approval；
- document hash、metadata、image forensic、near-duplicate search、business context 联合；
- high-value transaction 使用设备/账户/行为信号与 second factor；
- rate limit、score 不对外暴露过细、检测 probing pattern；
- gallery access 按 tenant/signer scoped，embedding 加密并可 rotation/version；
- adversarial red-team 持续sampling，新 attack family 独立 slice；
- 低置信/异常不是强行二分类，进入 review 或重新采集；
- 人审也有安全边界：双人复核高金额、审计、role-based access、防 reviewer 被模型分数 anchoring。

> 高分句：离线签名模型只是 risk signal，不是 cryptographic proof。风险越高，越需要独立信号和 step-up authentication。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
