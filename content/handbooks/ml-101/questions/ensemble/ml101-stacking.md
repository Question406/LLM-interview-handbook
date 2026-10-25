---
id: ml101-stacking
section: ensemble
order: 11
level: A
title: "Stacking 为什么需要折外预测？"
quick: "Stacking 的二层模型要用基础模型对未见样本的预测训练，折外预测能让这种训练输入接近上线状态。直接用基础模型的训练集预测，会让二层过分相信被记住的答案。先逐折生成完整 OOF 特征，训练二层，再用全训练集重训基础模型；整体效果仍要独立验证。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: StackingClassifier"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html
    type: primary
---

堆叠集成（Stacking）需要折外预测，是因为二层模型上线时拿到的是基础模型对新样本的预测。若训练二层时却用基础模型见过标签的样本预测，输入会过于漂亮，二层容易学错信任程度。

比如一棵深树把训练集几乎记住，训练预测正确率很高，二层就给它很大权重；测试时它失去这个优势，组合也随之变差。生成折外预测（out-of-fold，OOF）时，把训练集分成若干折，每次在其余折拟合基础模型，只预测留出的那折，再拼回所有行。每一行的二层输入都来自没用过该行标签的拟合。

二层在 OOF 特征和原标签上训练。准备上线时，基础模型通常在全训练集重训，再把新样本预测交给已经训练好的二层。[StackingClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html) 区分了这两种拟合过程。标准化、目标编码等有学习过程的预处理，也应放在每折内部。

## 追问

**OOF 上训练二层后，直接在同一 OOF 上打分可以吗？**
可以看拟合情况，但不能当独立泛化评估。二层已经见过这些行的标签，整体还要外层验证或留出测试。

**时间序列能随机分折吗？**
通常不能。应按预测时可获得的信息做时间切分，防止未来记录进入基础模型的训练。
