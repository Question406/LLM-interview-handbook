---
id: ali-multimodal-arch
section: alibaba
order: 30
level: B
title: 为 Agent 增加“以图找同款”，后端要做哪些改造？
quick: 增加视觉理解/特征服务、图搜索引、多模态检索链路、权限与审核、以及 Agent 工具 schema；编排上新增“图→候选→确认”状态，并评估延迟与成本。
tags:
  - Alibaba
  - 多模态
  - Agent
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 开发技术面
    url: 'https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>增加视觉理解/特征服务、图搜索引、多模态检索链路、权限与审核、以及 Agent 工具 schema；编排上新增“图→候选→确认”状态，并评估延迟与成本。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>改造清单：</p>
<ul>
<li>接入多模态模型或特征提取服务；</li>
<li>商品图索引与相似度检索；</li>
<li>新 tool：image_search_same_item；</li>
<li>链路：上传→检索→重排→商品卡→用户确认；</li>
<li>内容安全与版权审核；</li>
<li>监控：检索空结果率、同款准确率、RT。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 开发技术面</a></div>
