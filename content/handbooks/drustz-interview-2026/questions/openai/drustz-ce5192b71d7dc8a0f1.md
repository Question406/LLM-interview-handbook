---
id: drustz-ce5192b71d7dc8a0f1
section: openai
order: 109
level: A
title: Monster Battle (Coding)
quick: original-structured-preparation-guide · Monster Battle (Coding)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/04bc716b-4b8c-41b6-9b84-d6653af68394
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Monster Battle（Coding）：攻击—反击的确定性模拟

## 证据边界

面经确认 Monster Battle 是实际 coding 题并重视自写测试；公开同题家族版本明确要求严格按“主攻、检查死亡、若存活则反击、再次检查死亡、推进队伍游标”处理。当前 UUID 的会员正文未取得，所以下面是该公开变体的完整可练版本，不声称所有名称和返回格式一致。

## 可读题面与接口

输入两支有序怪物队，每只怪物有名字、生命值和攻击力。当前为 `A[i]` 对 `B[j]`：A 先令 B 扣除自身攻击力；若 B 已死，B 不得反击并令 `j+=1`；否则 B 反击 A，A 死亡则 `i+=1`。只要一队游标越过末尾，战斗结束。函数不得删除原列表，返回胜队与完整日志。

```python
def battle(a: list[Monster], b: list[Monster]) -> BattleResult: ...


# A=[("Wolf",10,6)], B=[("Slime",8,4)]
# Wolf 打后 Slime hp=2；Slime 反击后 Wolf hp=6；下一轮 Wolf 击杀
# 输出：winner="A", rounds=2
```



## 解法与关键数据结构

复制两队的可变 HP，用两个整数游标指向当前存活怪物。循环体必须严格保持事件顺序，尤其不能让已经被主攻击杀的怪物反击。日志最好记录结构化 `Event(actor,target,damage,hp_after,kind)`，最后再格式化，避免字符串逻辑干扰状态更新。每轮至少应造成正伤害或推进游标，否则要防止死循环。

## 复杂度与边界测试

若共发生 `R` 次有效攻击，时间 `O(R+n+m)`，额外状态 `O(n+m)`，日志 `O(R)`；仅用原地 HP 时状态可降到 `O(1)`，但会修改调用方。测试空队、首只怪物初始已死、恰好清零、被击杀者不反击、反击恰好杀死主攻者、多个怪物连续晋级、攻击力为零、两边都空，以及是否允许负 HP。若题面规定双方轮流取得先手，需替换回合规则，不能沿用本版。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/04bc716b-4b8c-41b6-9b84-d6653af68394)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
