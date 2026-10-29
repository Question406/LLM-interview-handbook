---
{
  "id": "afm-web-photos-search",
  "kind": "design",
  "situation": "用户用自然语言搜索自己的照片，query 同时包含视觉内容和个人上下文。",
  "task": "设计 retrieval、训练数据、隐私友好的 evaluation 和 embedding migration。",
  "approach": "分开视觉语义与时间人物信息，使用获授权的数据验证，版本化 embedding。",
  "result": "搜索成功改善，同时不跨用户访问且升级期间结果可用。"
}
---

## 可以这样回答

我会先把 query 拆开。“海边的狗”主要是图像与文本语义；“Emma 在 2019 年的生日”还需要人物分组和时间信息。单纯提高 image-text similarity 不一定能解决后者。

我会用 dual encoder 做视觉语义 retrieval，再结合时间、OCR 和经过授权的个人上下文处理约束。训练阶段可以先用许可清楚的 image-text pairs，不能默认把用户私有照片拿给标注人员。针对个人查询的 evaluation，需要明确授权的数据或可控的 synthetic libraries。

我会分别评估视觉概念、时间人物、多条件和容易混淆的任务。线上也可以看经过隐私审核的 aggregate signals，但点击一张图并不总表示它是正确答案，所以不能直接把每次点击当正标签。

升级模型时，我会给 embedding 和 encoder 记录版本，分批 backfill，并保证同一次搜索的 query 与 image vectors 处于兼容空间。新模型离线更强，如果全量照片还没有重新编码，也不能直接切换。
