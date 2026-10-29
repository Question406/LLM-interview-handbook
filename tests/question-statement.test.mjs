import assert from "node:assert/strict";
import test from "node:test";
import { splitQuestionStatement, validateCodingStatement, STATEMENT_END_MARKER } from "../lib/question-statement.mjs";

test("practice statements stop before answers, including legacy HTML answers", () => {
  const prompt = "给定数组，返回合法结果。";
  assert.deepEqual(splitQuestionStatement(`## 题目描述\n\n${prompt}\n\n## 解题思路\n先看参考答案。`), {
    markdown: prompt, rest: "## 解题思路\n先看参考答案。",
  });
  assert.deepEqual(splitQuestionStatement(`## 题目描述\n\n${prompt}\n\n${STATEMENT_END_MARKER}\n<div>solution</div>`), {
    markdown: prompt, rest: "<div>solution</div>",
  });
});

test("a title or answer excerpt cannot stand in for an independently readable coding task", () => {
  assert.equal(splitQuestionStatement("我会用哈希表。\n\n## 题目描述\n后补的题面"), null);
  assert.match(validateCodingStatement("## 思路\n使用哈希表。"), /正文必须先写/);
  assert.match(validateCodingStatement("## 题目描述\n实现标题中的算法，见测试。"), /题面过短/);
  const statement = `## 题目描述\n\n给定一个整数数组和目标值，返回两个不同位置的下标，使两数之和等于目标。保证唯一解，同一个位置不能重复使用。\n\n### 输入与输出\n输入参数为 nums 和 target。输出是包含两个下标的列表，顺序不限。数组长度至少为二，元素可以为负数，输入满足约束，不要求额外检查非法输入。结果是位置而非对应数值，重复数值的不同位置可以同时参与结果。\n\n### 示例\n输入 nums=[2,7,11,15], target=9，输出 [0,1]。\n\n## 解题思路\n答案。`;
  assert.equal(validateCodingStatement(statement), null);
  assert.match(validateCodingStatement(statement.replace("输入 nums=[2,7,11,15], target=9，输出 [0,1]。", "运行参考实现即可，具体输入输出见测试。")), /具体输入和预期结果/);
  assert.match(validateCodingStatement(statement.replace("### 输入与输出", "### 相关背景")), /接口、输入含义与输出规则/);
});
