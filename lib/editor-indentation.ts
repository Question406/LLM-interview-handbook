import { EditorState } from "@codemirror/state";
import { indentUnit } from "@codemirror/language";

export const fourSpaceIndentation = [indentUnit.of("    "), EditorState.tabSize.of(4)];
