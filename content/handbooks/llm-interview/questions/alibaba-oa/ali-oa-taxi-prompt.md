---
id: ali-oa-taxi-prompt
section: alibaba-oa
order: 7
level: A
title: 阿里 AI 研发 0325 Prompt：出租车计费规则怎么写成可过的提示词？
quick: >-
  写清角色、缺省值、分段计价、夜间只加车费、等候按满 5 分钟、行李不加夜费，并强制只输出约定 JSON，再用不足 1km / 24 分钟等候等反例自测。
tags:
  - Alibaba
  - OA
  - Prompt
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
---

## 真题记录

- 公司 / 场次：阿里 AI 研发 2026.03.25 T4
- 模型：公开复盘为 Qwen3.5-flash
- 题型：根据自然语言行程描述算出租车费，考生提交 Prompt，模型按 Prompt 答题
- 规则（公开复盘）：起步 $3$ km /$10$ 元；$3$–$15$ km 每公里 $3$ 元；超 $15$ km 每公里 $4$ 元（不足 $1$ km 进位）；等候每满 $5$ 分钟 $2$ 元；夜间 $23$:$00$（含）到次日 $05$:$00$（不含）车费 $\times 1.2$ 再进位；大件行李每件 $5$ 元且不参与夜间加收

## 题面

用一段系统提示词，让模型从用户的自然语言里抽出行程要素，严格按计费规则算出费用，并且**只输出约定 JSON**。公开复盘里的关键字段是 `thinking`、`base_fare`、`night_surcharge`、`fare`。

未写明的字段按缺省：等候 $0$、行李 $0$、时间未提则白天。夜间判定看上车时间是否落在 $[23{:}00,\,05{:}00)$。

这题不是算法实现题，评测看的是 Prompt 是否把规则写死、输出是否可解析。

## 思路

观察：失分几乎都在细节，而不是「会不会算分段计费」。要把「谁乘 $1.2$、谁向上取整、谁默认为 $0$」写成检查清单，并禁止模型输出散文。

写法：角色 + 抽取 + 逐步公式 + 强制 JSON。距离先向上取整成整数公里 $D=\lceil X\rceil$，再套三段价；夜间只作用在 `base_fare` 上；等候用 $\lfloor T/5\rfloor\times 2$；行李 $N\times 5$。

## 参考 Prompt

下面这段可以直接贴进评测框。不要改字段名。

```text
你是出租车计费系统。用户用自然语言描述行程。你必须先抽取参数，再按下列步骤计算，最后只输出一个 JSON 对象，不要输出 JSON 以外的任何文字、Markdown 或解释。

# 参数抽取
从用户描述中提取：
- X：行驶距离（公里）。未提及则 X=0。
- T：等候时间（分钟）。未提及则 T=0。
- N：大件行李件数。未提及则 N=0。
- night：是否夜间。若明确写了夜间 / 凌晨，或上车时间落在 23:00（含）到次日 05:00（不含），则 night=true，否则 night=false。未提及时间则视为白天。
05:00 整点不算夜间。23:00 整点算夜间。

# 计算步骤（必须逐步代入数字）

## 1. 整数公里
D = ceil(X)。X 已经是整数则 D=X。0 公里仍按行程处理。

## 2. 基础车费 base_fare（整数元）
起步价 10 元，包含前 3 公里（含 D=3）。
- 若 D <= 3：base_fare = 10
- 若 3 < D <= 15：base_fare = 10 + (D - 3) * 3
- 若 D > 15：base_fare = 10 + 12 * 3 + (D - 15) * 4
不足 1 公里在第 1 步已经进位，这里不要再对分段内部单独四舍五入。

## 3. 夜间车费 vehicle
- night=true：vehicle = ceil(base_fare * 1.2)，即有小数就向远离 0 的方向进到整数。例如 19.2 -> 20。
- night=false：vehicle = base_fare
等候费和行李费绝不参与 *1.2。

## 4. 等候费 wait_fee
wait_fee = floor(T / 5) * 2
只收完整的 5 分钟段。24 分钟只能收 4 段 = 8 元，余下 4 分钟不收。

## 5. 行李费 luggage_fee
luggage_fee = N * 5
行李不加收夜间。

## 6. 总价
fare = vehicle + wait_fee + luggage_fee

# 输出格式
只输出如下 JSON（字段必须齐全，类型必须正确）：
{
  "thinking": "用中文写出每一步代入的数字和中间结果，包括 D、base_fare、vehicle、wait_fee、luggage_fee、fare",
  "base_fare": 基础车费整数,
  "night_surcharge": true或false,
  "fare": 总费用整数
}

night_surcharge 填抽取到的 night，不要填加收金额。
base_fare 填第 2 步的基础车费，不要改成夜间后的 vehicle。
```

## 计费逐步例子

**例 1：白天 $2.3$ km，未提等候和行李。**

- $D=\lceil 2.3\rceil=3$
- $D\le 3$，`base_fare`$=10$
- 白天，`vehicle`$=10$，`night_surcharge`=`false`
- `wait_fee`$=0$，`luggage_fee`$=0$
- `fare`$=10$

不足 $1$ km 的进位发生在整段距离上，不要先按 $2$ km 再另加一截。

**例 2：夜间 $16.2$ km，等候 $24$ 分钟，大件行李 $2$ 件。**

- $D=\lceil 16.2\rceil=17$
- `base_fare`$=10+12\times 3+(17-15)\times 4=10+36+8=54$
- 夜间：`vehicle`$=\lceil 54\times 1.2\rceil=\lceil 64.8\rceil=65$
- `wait_fee`$=\lfloor 24/5\rfloor\times 2=4\times 2=8$（不是 $24/5$ 四舍五入）
- `luggage_fee`$=2\times 5=10$
- `fare`$=65+8+10=83$

若错误地把 $1.2$ 乘到总价上，会变成 $\lceil(54+8+10)\times 1.2\rceil=87$，这是常见扣分点。

**例 3：白天恰好 $15$ km，等候 $4$ 分钟，行李 $0$。**

- $D=15$，`base_fare`$=10+(15-3)\times 3=46$
- 等候不足 $5$ 分钟，`wait_fee`$=0$
- `fare`$=46$

**例 4：上车 $05{:}00$，距离 $3.01$ km。**

- $05{:}00$ 不含在夜间区间，按白天
- $D=\lceil 3.01\rceil=4$，`base_fare`$=10+1\times 3=13$，`fare`$=13$

## 复杂度

无算法代码。Prompt 长度应覆盖规则，不必堆示例到评测框溢出；用上面 4 个反例在本地自测即可。

## 易错 / 面试追问

- 夜间乘数乘到等候费或行李费上；或把 `base_fare` 写成加收后的车费，导致 JSON 对不上隐藏评分。
- 等候 $24$ 分钟按 $5$ 段收费，或距离 $3.2$ km 忘记先 `ceil`。
- 缺字段不给默认值，模型开始追问用户，输出不再是纯 JSON。
- 追问「不足 $1$ km 是每段后进位还是先取整再分段」：先把总距离进成整数公里，再套 $3/15$ 分界，两种写法在常见样例上一致。
