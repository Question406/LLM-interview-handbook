---
id: drustz-eee45b8e3ca850703a
section: robotics
order: 41
level: A
title: 05 — Debug Playbook：「The bot is not working」排查手册 · 2. 分层排查树（六层栈，白板默写版）
quick: >-
  作者文档章节 · 05 — Debug Playbook：「The bot is not working」排查手册 · 2.
  分层排查树（六层栈，白板默写版）
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
## 2. 分层排查树（六层栈，白板默写版）

白板上从下往上画。每层记住 2–3 个典型故障 + 一句"怎么确认"。**判据**列 = 看到什么就能把嫌疑锁定在这一层。

### L0 电源与硬件（单机故障的第一嫌疑层）

| 部件 | 典型故障 | 检查手段 | 判据（确认信号） |
|---|---|---|---|
| 电池/BMS | 老化内阻上升 → 大电流瞬间 brownout 重启；单体不均衡触发保护断电 | 重启事件与电流尖峰做时序对齐；换已知好电池 | 重启时刻电压曲线瞬间跌破阈值；换电池后消失 |
| 电机/驱动器 | 过热降额（thermal derating）→ 扭矩不足、变慢，**无错误码** | 拉温度曲线；空载 vs 带载对比；读驱动器 fault register | 故障只在长时间运行/高温后出现，温度过 derating 阈值 |
| 编码器 | 磁环滑移/码盘脏 → odometry 漂移、控制抖振 | 手转关节对比读数；轮式 odom vs lidar/视觉定位残差 | 单侧残差系统性增大；手转验证读数不符 |
| 相机 | 进灰/脏污/水汽 → 图像变暗变糊；USB 带宽不够丢帧 | **直接看原始图像流（不是下游输出！）**；对比历史同场景 | 图像亮度/清晰度指标偏离该机自身历史基线 |
| IMU | 温漂、bias 跳变、震动饱和 | 静止读 bias；对比标称噪声谱 | bias 超标称范围；clipping 计数非零 |
| 连接器/线缆 | **微振松动——间歇性故障最常见来源** | wiggle test（边动线边看数据）；换线 | 掉线事件与振动幅值/特定姿态强相关 |
| 散热 | 风扇积灰停转 → SoC/GPU 热节流 → 全系统变慢 | `tegrastats`/`sensors` 看温度与当前频率 | throttling 事件计数 > 0，频率被压 |

**这一层的面试论点**：间歇性硬件故障靠 comprehensive logging + 与振动/温度/时间做相关性分析，以及 **swap test**——故障跟着部件走就是硬件，留在机器上就往上层查。

### L1 固件与驱动

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| 固件与驱动版本不匹配（部分 OTA 后） | 读版本号 vs manifest 比对 | 版本组合不在已测试矩阵中 |
| 设备枚举顺序变化 → `/dev/ttyUSB*` 错位、左右相机互换 | `dmesg`、`lsusb` 对比期望设备清单 | 设备路径与 serial number 映射错乱 |
| 驱动崩溃后 silent 不重启；CAN bus off | journalctl、`candump` 看错误帧 | 总线错误计数飙升 / 设备掉线事件 |

### L2 中间件（ROS 2 / pub-sub / 时间同步）

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| **QoS 不匹配（reliable vs best-effort）→ 消息静默不投递，无报错** | `ros2 topic info -v` 对比 pub/sub QoS | 拓扑连着但订阅端 hz = 0 |
| 多计算单元时间不同步 → TF extrapolation error、融合出"鬼影" | `tf2_monitor`、`chronyc tracking` | 某计算单元时钟偏移量级达数十~数百 ms |
| executor 饿死 / callback 排队 → 延迟累积 | `ros2 topic hz`、tracing 看 callback 时序 | 端到端延迟随 uptime 增长 |

### L3 经典自主栈（感知/定位/规划/控制）

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| **外参标定漂移**（振动/热胀/磕碰）→ 相机-lidar 投影错位、抓取偏移 | 可视化叠加投影；标定板复测 vs 出厂外参 diff | 投影错位肉眼可见；复测值超容差 |
| 定位跳变（特征贫乏区/地图过期） | 定位协方差时序；地图版本核对 | 协方差在固定区域规律性膨胀 |
| 规划器振荡/控制发散（新负载） | planner 失败原因码；控制跟踪误差 | commanded vs actual 误差在特定负载下发散 |

**这一层的核心动作**：把同一个 bag 逐级回放，在 RViz/Foxglove 里叠加看——**哪一级开始错，问题就在那一级与下一级之间**。

### L4 ML Policy 推理（ML 岗必被追问的层）

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| 模型 artifact 错：checkpoint hash 不符；TensorRT/ONNX 量化导出数值不一致 | 核对模型 hash + config；golden input 离线 vs 机上输出 diff | 同输入两端输出差异超数值容差 |
| **预处理不匹配**（normalization常数/resize 插值/通道顺序）——经典 silent failure | 录现场输入，离线复现整条预处理链 | 离线 eval 好、上机差，且 diff 定位到预处理输出 |
| 输入分布漂移（光照/场景/物体偏离训练分布） | 输入 embedding 的 OOD score / 与训练集距离 | OOD 分数上升**先于** success rate 下降 |
| 推理延迟尖峰 → 控制频率掉 → 行为变形 | p50/p99 延迟直方图；GPU 温度/利用率对齐 | p99 双峰，且与热节流/抢占事件对齐 |

**这一层的加分句**："Latency is part of the input distribution too — a policy trained at 30 Hz behaves differently when inference stutters, even if every individual output is correct."

### L5 云端 / 网络 / OTA / 配置

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| 配置下发错（错的 SKU 拿到错的参数） | diff 机上生效配置 vs 期望（config drift 检测） | cohort 切片只有某 SKU 中招 + diff 出差异项 |
| **半 OTA**：固件成、驱动包败 → 从未测试过的版本组合 | OTA 事件日志 + 全组件版本一致性自检 | 版本组合不在测试矩阵 |
| 证书过期 → 云连接静默失败；网络盲区打断 teleop | 云端 API 错误率；网络 RTT/丢包与位置热力图 | 故障与固定区域/固定时段强相关 |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/05_debug_playbook.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md)。作者整理资料；许可和第三方来源范围见阅读指南。
