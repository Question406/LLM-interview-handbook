"use client";

import { useEffect, useRef } from "react";
import { basicSetup, EditorView } from "codemirror";
import { EditorState, Prec } from "@codemirror/state";
import { keymap } from "@codemirror/view";
import { indentWithTab } from "@codemirror/commands";
import { fourSpaceIndentation } from "@/lib/editor-indentation";
import { python } from "@codemirror/lang-python";
import { javascript } from "@codemirror/lang-javascript";

export function PythonEditor({ value, onChange, readOnly = false, label, focusLine, onRun, language = "python" }: {
  value: string; onChange?: (value: string) => void; readOnly?: boolean;
  label: string; focusLine?: number; onRun?: () => void;
  language?: "python" | "javascript";
}) {
  const host = useRef<HTMLDivElement>(null);
  const editor = useRef<EditorView | null>(null);
  const callbacks = useRef({ onChange, onRun });
  useEffect(() => { callbacks.current = { onChange, onRun }; }, [onChange, onRun]);
  useEffect(() => {
    if (!host.current) return;
    const view = new EditorView({
      parent: host.current,
      state: EditorState.create({ extensions: [
        fourSpaceIndentation,
        basicSetup, language === "javascript" ? javascript({ jsx: true }) : python(), Prec.highest(keymap.of([indentWithTab, {
          key: "Mod-Enter", run: () => { callbacks.current.onRun?.(); return true; },
        }])),
        EditorState.readOnly.of(readOnly), EditorView.editable.of(!readOnly),
        EditorView.contentAttributes.of({ "aria-label": label, spellcheck: "false" }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) callbacks.current.onChange?.(update.state.doc.toString());
        }),
        EditorView.theme({
          "&": { height: "100%", backgroundColor: "var(--code-bg)", color: "var(--code-text)" },
          ".cm-scroller": { overflow: "auto", fontFamily: "var(--hb-mono)", fontSize: "13px", lineHeight: "1.7" },
          ".cm-content": { padding: "16px 0", minHeight: "340px", caretColor: "var(--ink)" },
          ".cm-gutters": { backgroundColor: "var(--soft)", color: "var(--muted)", borderRight: "1px solid var(--line)" },
          ".cm-activeLine, .cm-activeLineGutter": { backgroundColor: "var(--mark)" },
          ".cm-cursor": { borderLeftColor: "var(--ink)" },
          "&.cm-focused .cm-selectionBackground, .cm-selectionBackground": { backgroundColor: "var(--mark-edge) !important" },
          "&.cm-focused": { outline: "none" },
        }),
      ] }),
    });
    editor.current = view;
    return () => { view.destroy(); editor.current = null; };
  }, [label, readOnly, language]);
  useEffect(() => {
    const view = editor.current;
    if (view && view.state.doc.toString() !== value) {
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: value } });
    }
  }, [value, label, readOnly, language]);
  useEffect(() => {
    const view = editor.current;
    if (!view || !focusLine) return;
    const line = view.state.doc.line(Math.max(1, Math.min(view.state.doc.lines, focusLine)));
    view.dispatch({ selection: { anchor: line.from }, effects: EditorView.scrollIntoView(line.from, { y: "center" }) });
    view.focus();
  }, [focusLine]);
  return <div ref={host} className="python-editor" />;
}
