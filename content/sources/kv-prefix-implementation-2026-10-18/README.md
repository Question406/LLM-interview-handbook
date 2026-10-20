# KV Prefix 实现专题

8道可独立运行的原创练习，另有1张导航卡。源码与测试见solutions，卡片映射和源码hash见manifest.json。

验证：`python3 scripts/check-kv-prefix-practice.py --rendered`。原型为CPU NumPy正确性参考，不声称生产GPU吞吐。

端到端engine真正减少prefix前向计算，但恢复连续cache仍复制数组；分页COW与共享prefix分段attention分别独立验证，尚未把所有组件拼成零拷贝多请求服务。
