---
id: drustz-957c701a4ebbe28fac
section: robotics
order: 44
level: A
title: >-
  05 — Debug Playbook：「The bot is not working」排查手册 · 5. Root Cause 案例卡（12 张，每张
  3–5 行）
quick: >-
  作者文档章节 · 05 — Debug Playbook：「The bot is not working」排查手册 · 5. Root Cause
  案例卡（12 张，每张 3–5 行）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md
    type: primary
---
## 5. Root Cause 案例卡（12 张，每张 3–5 行）

面试时的用法：主叙事讲完框架后，**主动挑 1–2 张卡讲全程**（推荐 #2 地毯 或 #1 标定漂移——同时秀硬件+ML+数据三种肌肉）；其余用于应对 "give me an example of..."。

**#1 相机-lidar 外参标定漂移**
症状：单机渐变，检测框与点云错位，抓取偏移 ~2cm。
路径：可视化叠加投影发现错位 → 标定板复测 → 与出厂外参 diff 超容差。
修复：重标定；长期上在线标定监控（在线失准检测 / 基于运动线索的漂移监控——面试说方法思路即可，别报具体方法名）。

**#2 地毯换了 → 输入分布偏移**
症状：某站点所有机器视觉 policy 成功率骤降，跨软件版本。
路径：cohort 切片锁定单站点 → 回看失败片段图像发现地面纹理全变 → OOD 分数确认输入偏移。
修复：采集新场景数据 fine-tune / domain randomization；流程上加客户环境变更报备 + 输入分布监控告警。

**#3 模型导出/预处理不一致**
症状：新模型离线 eval 更好，上机反而更差。
路径：录同一输入，离线 PyTorch vs 机上 TensorRT 输出 diff → normalization常数/插值方式不一致（或量化掉点）。
修复：部署链路加"训练-部署数值一致性测试"（golden input 回归），进 CI。

**#4 推理延迟尖峰 → 控制变形**
症状：动作偶发顿挫，模型输出本身正确，成功率轻微下降。
路径：p99 延迟直方图双峰 → 与 GPU 温度对齐发现热节流（或同机进程抢 GPU）。
修复：散热/进程隔离/延迟预算监控；policy 侧加延迟鲁棒性测试。

**#5 内存泄漏 → 延迟累积**
症状：运行数小时后变卡、偶发 watchdog 重启；**"重启就好" = 泄漏类经典指纹**。
路径：故障率与 uptime 正相关 → 监控 RSS 增长 → heap profiler 定位泄漏节点。
修复：修泄漏 + 内存/延迟 p99 告警；临时按班次重启缓解。

**#6 多机时间戳不同步**
症状：TF extrapolation error、传感器融合出"重影"、planner 间歇性拒绝。
路径：`tf2_monitor` 看帧延迟 → `chronyc tracking` 发现某计算单元漂 200ms。
修复：修 NTP/PTP + 加时钟偏移监控告警。

**#7 DDS QoS 不匹配**
症状：升级后某订阅者永远收不到消息，**无任何报错**。
路径：`ros2 topic info -v` 对比 pub/sub QoS → reliable vs best-effort 不兼容。
修复：统一 QoS 配置 + CI 加 topic 连通性检查。"Silent failures need active monitoring."

**#8 连接器微振松动**
症状：传感器随机掉线数百 ms，只在高速/颠簸时发生，实验室复现不了。
路径：掉线事件与 IMU 振动幅值做相关性 → wiggle test 复现 → 锁定连接器。
修复：换带锁扣连接器/加固；长期记录总线错误计数以便早发现。

**#9 电池老化 brownout**
症状：老机器在电机大电流瞬间整机重启，冬天更频繁。
路径：重启时刻与电流尖峰对齐 → 电压曲线瞬间跌破阈值 → 换新电池后消失。
修复：换电池 + BMS 内阻/压降健康监控 + 老化预测性更换。

**#10 电机过热降额**
症状：只在下午/连续作业后"没力气"、变慢，**无错误码**（降额是静默的）。
路径：故障与运行时长/环境温度相关 → 电机温度曲线触发 derating 阈值。
修复：改散热/降占空比；把 derating 事件加入 diagnostics。

**#11 镜头进灰/脏污**
症状：单机数周内 success rate 渐降，无任何软件变更。
路径：图像亮度/对比度/清晰度 vs 自身历史基线偏离 → 肉眼看原始图确认。
修复：清洁 + 定检 SOP + 图像质量自动监控。"永远先看原始图，别只看下游输出。"

**#12 半 OTA / 配置错发**
症状：OTA 后少数机器异常，版本号看似正常（或：某 SKU 全体行为怪异）。
路径：细查发现固件更新成功但驱动包失败 → 从未测试过的版本组合；或 diff 生效配置发现拿到别的机型参数。
修复：OTA 事务化（全成或全回滚）+ 启动时全组件版本一致性自检 + config schema 校验与 drift 监控。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/05_debug_playbook.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md)。作者整理资料；许可和第三方来源范围见阅读指南。
