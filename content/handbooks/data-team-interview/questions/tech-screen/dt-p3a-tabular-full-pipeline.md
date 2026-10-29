---
id: dt-p3a-tabular-full-pipeline
section: tech-screen
order: 81
level: A
title: Apple MLE 原帖：拿到数据后现场完成预处理、训练、评测与可视化
quick: >-
  先冻结 train/test split，只在 training set 拟合缺失值填补、standardization、模型和降维投影；test set
  只做 transform 与最终指标计算。先跑通简单 baseline，再解释降维图和误差，不用复杂网络掩盖 data leakage。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - 一亩三分地原帖核对
  - AFM 专项 2026-10
  - 一亩三分地追加第二批
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: Apple MLE 新鲜面经，候选人原帖，Chrome核对2026-10-26
    url: 'https://www.1point3acres.com/bbs/thread-1084615-1-1.html'
    type: interview
  - title: scikit-learn Pipeline
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html
    type: primary
  - title: 'scikit-learn Common pitfalls: data leakage'
    url: 'https://scikit-learn.org/stable/common_pitfalls.html'
    type: primary
---

## 题目描述

### 原帖核对与练习约定

- 来源：[Apple MLE 新鲜面经](https://www.1point3acres.com/bbs/thread-1084615-1-1.html)，Chrome 页面显示 2024-09-05 14:00:32，采集日期为 2026-10-26。
- 主楼与作者第一页回复可见；积分段显示当前会话已经可以浏览，未绕过访问限制。原帖未明确团队为 AFM data team。
- 原帖披露第三轮给数据集，现场写模型并训练、输出指标，做特征降维和可视化；作者回复确认预处理、训练、测试、评价全流程都要写，模型可以简单。
- **练习约定**：原帖未说明数据类型、指定算法和接口。本题选数值表格二分类、逻辑回归及 PCA 二维投影作为完整可运行 baseline；算法选择由手册设定。投影仅用于可视化，不改变分类模型的输入。建议限时 40 分钟。

### 输入与接口

实现 `fit_tabular_baseline(x_train,y_train,x_test,y_test)`。特征为 NumPy 浮点 matrix，形状分别 `[N,D]`、`[M,D]`，N>=4、M>=1、D>=2。数值有限或 NaN，每个训练特征至少有一个非缺失值；`y_train`、`y_test` 为对应长度的一维 0/1 数组，training set 有两类，test set 可以只有一类。数据已划分，不能重新随机切分。

### 输出与约束

返回字典包含：

- `model`：拟合好的 sklearn Pipeline，依次为名称 `impute` 的中位数填补器、`scale` 的 StandardScaler、`classify` 的 LogisticRegression；分类器采用 `max_iter=1000,random_state=0`。
- `pred`：测试预测 `[M]`；`proba`：正类概率 `[M]`。
- `metrics`：Python float 类型的 `accuracy`、二类等权的 `macro_f1`、`log_loss`。macro F1 固定 labels=[0,1] 且 zero_division=0，log loss 固定 labels=[0,1]。
- `projector`：只在填补、standardization 后的训练特征上拟合的二维 PCA，采用 `svd_solver='full'`；`plot_train`、`plot_test` 为 `[N,2]`、`[M,2]` 投影坐标，可直接画散点图。

只能在训练特征上拟合任何变换或模型，测试标签只用于 metrics。不修改输入；允许使用 sklearn，不要求手写 optimizer。无需在函数内部显示或保存图像。

### Features、labels 与模型选择范围

x 的每一行是一条已编码的数值记录，y 的同一行是其 binary class label；NaN 表示缺失 feature，不表示 label 缺失。最终分类概率来自 LogisticRegression 的 class 1；PCA 只产生用于画图的坐标，不替代分类器输入。所有返回对象和 metrics 均需要生成，不只是打印 accuracy。

对题面示例，`proba`、`log_loss` 是所规定 sklearn defaults 训练得到的数值；PCA 向量存在符号约定，不用硬编码投影坐标。可检查 `pred=[0,1]`、两个投影 shapes 以及返回模型重算的概率是否一致；不能仅为满足示例跳过训练。

### 示例

```text
x_train=[[-3,0],[-2,NaN],[-1,0],[1,0],[2,NaN],[3,0]]
y_train=[0,0,0,1,1,1]
x_test=[[-2,0],[2,NaN]], y_test=[0,1]
pred=[0,1]，accuracy=1.0，macro_f1=1.0
plot_train形状为[6,2]，plot_test为[2,2]。
```

## 解题思路与参考答案

先用 Pipeline 封装训练和预测，防止遗漏测试变换。可视化单独对已由训练统计量变换的特征拟合 PCA，并保留 projector 供之后样本复用。测试标签完全不进入模型与投影计算。

```python
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score, log_loss


def fit_tabular_baseline(x_train, y_train, x_test, y_test):
    model = Pipeline(
        [
            ('impute', SimpleImputer(strategy='median')),
            ('scale', StandardScaler()),
            ('classify', LogisticRegression(max_iter=1000, random_state=0)),
        ]
    )
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    proba = model.predict_proba(x_test)[:, 1]
    train_scaled = model.named_steps['scale'].transform(
        model.named_steps['impute'].transform(x_train)
    )
    test_scaled = model.named_steps['scale'].transform(
        model.named_steps['impute'].transform(x_test)
    )
    projector = PCA(n_components=2, svd_solver='full').fit(train_scaled)
    return {
        'model': model,
        'pred': pred,
        'proba': proba,
        'metrics': {
            'accuracy': float(accuracy_score(y_test, pred)),
            'macro_f1': float(
                f1_score(y_test, pred, labels=[0, 1], average='macro', zero_division=0)
            ),
            'log_loss': float(
                log_loss(y_test, np.column_stack([1 - proba, proba]), labels=[0, 1])
            ),
        },
        'projector': projector,
        'plot_train': projector.transform(train_scaled),
        'plot_test': projector.transform(test_scaled),
    }
```

输入大小为 $O((N+M)D)$。逻辑回归迭代成本随求解器与迭代次数变化；full SVD 的 PCA 成本约为 $O(ND\min(N,D))$。很大的 D 或 N 需要 sampling 展示或换降维方法，不能把完整 SVD 当成免费可视化。

## 简单测试怎么写

将实现与测试保存为 `solution.py`，运行 `python3 solution.py`，依赖 NumPy 与 scikit-learn。第一组验证手算可分的小例子；第二组改变测试分布与标签，确认训练统计和参数不随之变化。

```python
x = np.array(
    [[-3.0, 0.0], [-2.0, np.nan], [-1.0, 0.0], [1.0, 0.0], [2.0, np.nan], [3.0, 0.0]]
)
y = np.array([0, 0, 0, 1, 1, 1])
xt = np.array([[-2.0, 0.0], [2.0, np.nan]])
yt = np.array([0, 1])
copy_x = x.copy()
result = fit_tabular_baseline(x, y, xt, yt)
assert result['pred'].tolist() == [0, 1]
assert result['metrics']['accuracy'] == result['metrics']['macro_f1'] == 1.0
assert all(isinstance(v, float) and np.isfinite(v) for v in result['metrics'].values())
assert result['plot_train'].shape == (6, 2)
assert result['plot_test'].shape == (2, 2)
assert np.all((result['proba'] > 0) & (result['proba'] < 1))
assert np.array_equal(x, copy_x, equal_nan=True)
shifted = fit_tabular_baseline(x, y, np.array([[1000.0, 50.0], [2000.0, 60.0]]), 1 - yt)
for name, attr in [
    ('impute', 'statistics_'),
    ('scale', 'mean_'),
    ('classify', 'coef_'),
]:
    assert np.allclose(
        getattr(result['model'].named_steps[name], attr),
        getattr(shifted['model'].named_steps[name], attr),
    )
assert np.allclose(result['projector'].components_, shifted['projector'].components_)
```

## 面试追问

**图中分得开就证明泛化好吗？** 不证明。监督标签、投影参数和展示 sampling 都可能制造视觉印象；独立指标与错误 evaluation slices 更重要。PCA 方差大不意味着包含标签信息。

**若改成 PyTorch 呢？** 保留同样的 train/test isolation，增加 Dataset、batch、训练模式与 no_grad 推断。standardization 仍只拟合 training set；不能因模型换成神经网络就把预处理 leakage 忽略掉。

**什么时候做降维后再训练？** 作为另一个候选配方，在训练/validation set 上选择维度，冻结方案后测试。当前 PCA 只用于展示，不应把投影图称为分类模型的 decision boundaries。
