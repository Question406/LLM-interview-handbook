---
id: drustz-9af98d029a981ceb73
section: robotics
order: 35
level: A
title: 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 6. Privacy 专节（家用机器人必考）
quick: >-
  作者文档章节 · 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 6. Privacy
  专节（家用机器人必考）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Robotics · Data、Learning 与 System Design
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md
    type: primary
---
## 6. Privacy 专节（家用机器人必考）

### 6.1 必背反面案例：iRobot × Scale AI

Roomba 开发测试机图像（含如厕照、儿童面孔）经 Scale AI 的委内瑞拉众包标注员外泄到 Facebook/Discord；测试者签的同意书被认为有误导性；iRobot 终止与 Scale 合作。同类先例：Ring 员工滥看用户视频，FTC 罚 580 万美元（2023）。
**教训**：隐私风险在**整条数据供应链**（含标注外包），不只在设备端。

### 6.2 正面模板：1X NEO 的四件套

1. **逐次同意**：teleop 必须车主 App 内逐次批准/预约时间窗并指定任务，操作员无法擅自接管；
2. **边缘脱敏**：操作员视野内实时人像模糊、音频遮蔽；可设房间/时段 **no-go zones**；
3. **人员控制**：自有（非零工）操作员 + 背景调查 + NDA；
4. **坦率的 social contract**：CEO Børnich 公开言明 "If we don't have your data, we can't make the product better… it is a social contract." —— 用数据换更便宜/进步更快的产品，明码标价而非藏在条款里。

### 6.3 工程措施清单（按数据生命周期）

| 环节 | 措施 |
|---|---|
| 机端 | on-device 推理让原始视频不出户（1X Redwood 跑板载 GPU 的动机之一）；事件触发式最小化上传（Tesla 模式） |
| 上传前 | 边缘侧人脸/敏感区域 redaction（AV 惯例：人脸+车牌模糊） |
| 标注 | PII 清洗 + 受控环境（禁下载、屏幕审计）；供应商纳入威胁模型 |
| 存储 | 保留期限 + 删除权（GDPR/CCPA）；每次远程访问留审计日志 |

**未解难题（主动提出显深度）**：访客/家庭其他成员并未签署同意（第三方同意问题）；LiDAR/深度图同样能重建户型隐私；Figure Go-Big 在 Brookfield 物业拍摄也面临拍摄对象同意与场景真实性的追问。

### 6.4 英文观点句（挑 2-3 句用）

> "Privacy isn't a compliance checkbox on a home robot — it's an architectural constraint that decides what the data engine even looks like: on-device triage, event-based minimal upload, and edge redaction before anything leaves the house."

> "The iRobot leak taught the industry that your threat model has to cover the entire data supply chain — the breach happened at an outsourced labeling vendor, not on the device."

> "I like 1X's framing of an explicit social contract: per-session consent, no-go zones, employed and vetted operators, and an honest statement that data is the price of a product that improves. Users accept data collection they can see and control; they revolt against collection they discover."

> "The unsolved part is third-party consent — guests and family members never signed anything. That's why I'd default to edge blurring of all faces, not just the owner's opt-outs."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/04_data_engine.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md)。作者整理资料；许可和第三方来源范围见阅读指南。
