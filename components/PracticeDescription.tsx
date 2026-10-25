"use client";

import { Fragment, useMemo, type ReactNode } from "react";
import { marked, type Token, type Tokens } from "marked";
import katex from "katex";

function mathText(text: string): ReactNode {
  return text.split(/(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)/g).map((part, index) => {
    if (!part.startsWith("$") || part.length < 3) return part;
    const display = part.startsWith("$$");
    const source = part.slice(display ? 2 : 1, display ? -2 : -1);
    // Only KaTeX-generated markup is inserted; arbitrary source HTML is never
    // interpreted. External links are separately restricted below.
    return <span key={index} dangerouslySetInnerHTML={{ __html: katex.renderToString(source, { displayMode: display, throwOnError: false, trust: false }) }} />;
  });
}

function inline(tokens: Token[]): ReactNode {
  return tokens.map((token, index) => {
    const children = "tokens" in token && Array.isArray(token.tokens) ? inline(token.tokens) : null;
    switch (token.type) {
      case "strong": return <strong key={index}>{children}</strong>;
      case "em": return <em key={index}>{children}</em>;
      case "codespan": return <code key={index}>{token.text}</code>;
      case "br": return <br key={index} />;
      case "link": return /^https?:\/\//.test(token.href) ? <a key={index} href={token.href} target="_blank" rel="noopener noreferrer">{children}</a> : <Fragment key={index}>{children}</Fragment>;
      default: return <Fragment key={index}>{children ?? mathText("text" in token ? String(token.text) : token.raw)}</Fragment>;
    }
  });
}

function blocks(tokens: Token[]): ReactNode {
  return tokens.map((token, index) => {
    switch (token.type) {
      case "space": return null;
      case "paragraph": case "text": return <p key={index}>{inline((token as Tokens.Paragraph).tokens ?? marked.Lexer.lexInline(token.text))}</p>;
      case "heading": return <h3 key={index}>{inline(token.tokens ?? [])}</h3>;
      case "code": return <pre key={index}><code>{token.text}</code></pre>;
      case "list": {
        const items = token.items.map((item: Tokens.ListItem, itemIndex: number) => <li key={itemIndex}>{blocks(item.tokens)}</li>);
        return token.ordered ? <ol key={index}>{items}</ol> : <ul key={index}>{items}</ul>;
      }
      case "blockquote": return <blockquote key={index}>{blocks(token.tokens ?? [])}</blockquote>;
      case "hr": return <hr key={index} />;
      default: return <p key={index}>{"text" in token ? String(token.text) : token.raw}</p>;
    }
  });
}

export function PracticeDescription({ source }: { source: string }) {
  const tokens = useMemo(() => marked.lexer(source), [source]);
  return <div className="lab-description">{blocks(tokens)}</div>;
}
