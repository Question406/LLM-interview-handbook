export const STATEMENT_END_MARKER = "<!-- problem-statement:end -->";

/** The authored statement is always first; later answers never supply its text. */
export function splitQuestionStatement(body) {
  const source = body.trimStart();
  const heading = /^## 题目描述[^\n]*\n/.exec(source);
  if (!heading) return null;
  const tail = source.slice(heading[0].length);
  const marker = tail.indexOf(STATEMENT_END_MARKER);
  const following = /^## /m.exec(tail);
  const end = marker >= 0 ? marker : following?.index ?? tail.length;
  return {
    markdown: tail.slice(0, end).trim(),
    rest: tail.slice(end + (marker >= 0 ? STATEMENT_END_MARKER.length : 0)).trimStart(),
  };
}

export function validateCodingStatement(body) {
  const statement = splitQuestionStatement(body);
  if (!statement) return "编程题正文必须先写独立的 ## 题目描述，再写题解";
  if (statement.markdown.length < 180) return "编程题面过短，请补足任务、接口、输入输出和具体示例";
  if (!/输入|参数|接口/.test(statement.markdown) || !/输出|返回|副作用/.test(statement.markdown)) return "题面缺少输入、输出或接口约定";
  if (!/示例|例子/.test(statement.markdown)) return "题面必须包含至少一组具体输入输出示例";
  const example = /^### [^\n]*(?:示例|例子)[^\n]*\n/m.exec(statement.markdown);
  if (!example) return "题面必须将具体输入输出示例单列为 ### 示例，不能只写见测试或题解";
  const contract = statement.markdown.slice(0, example.index);
  if (!/^### (?![^\n]*(?:示例|例子))[^\n]*(?:输入|接口|参数|规则|约束|任务|模块|状态)/m.test(contract)) {
    return "题面必须在示例前说明接口、输入含义与输出规则";
  }
  const exampleText = statement.markdown.slice(example.index + example[0].length);
  if (!/(?:\d|True|False|None|\[\]|\{\}|["“][^"”\n]+["”])/.test(exampleText)
      || !/(?:->|→|=|返回|输出|结果|得到|return|assert)/.test(exampleText)) {
    return "题面示例必须给出具体输入和预期结果，不能仅指向参考实现";
  }
  return null;
}
