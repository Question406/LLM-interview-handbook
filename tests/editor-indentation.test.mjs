import assert from "node:assert/strict";
import test from "node:test";
import { EditorState } from "@codemirror/state";
import { indentWithTab, insertNewlineAndIndent } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { fourSpaceIndentation } from "../lib/editor-indentation.ts";

function target(doc, anchor = doc.length) {
  const view = {
    state: EditorState.create({ doc, selection: { anchor }, extensions: [python(), fourSpaceIndentation] }),
    dispatch(transaction) { view.state = transaction.state; },
  };
  return view;
}

test("Tab and Shift-Tab add/remove four spaces without inserting tab characters", () => {
  const view = target("pass");
  indentWithTab.run(view);
  assert.equal(view.state.doc.toString(), "    pass");
  assert.equal(view.state.tabSize, 4);
  indentWithTab.shift(view);
  assert.equal(view.state.doc.toString(), "pass");
});

test("Enter after a Python block uses the same four-space indentation", () => {
  const view = target("if True:");
  insertNewlineAndIndent(view);
  assert.equal(view.state.doc.toString(), "if True:\n    ");
});
