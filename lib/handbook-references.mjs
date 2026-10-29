/** Validate a collection's references to canonical question sources. */
export function validateQuestionReferences(value, sectionIds, ownSlug) {
  if (!Array.isArray(value)) throw new Error("question references must be an array");
  const ids = new Set();
  return value.map((entry, index) => {
    if (!entry || typeof entry !== "object") throw new Error(`question reference ${index} must be an object`);
    for (const field of ["book", "question", "section"]) {
      if (typeof entry[field] !== "string" || !/^[a-z0-9][a-z0-9-]*$/.test(entry[field])) {
        throw new Error(`question reference ${index} has invalid ${field}`);
      }
    }
    if (entry.book === ownSlug) throw new Error("question references cannot import their own handbook");
    if (!sectionIds.has(entry.section)) throw new Error(`unknown reference section ${entry.section}`);
    if (ids.has(entry.question)) throw new Error(`duplicate referenced question id ${entry.question}`);
    ids.add(entry.question);
    if (entry.order !== undefined && (!Number.isInteger(entry.order) || entry.order < 0)) {
      throw new Error(`invalid reference order for ${entry.question}`);
    }
    return { ...entry, order: entry.order ?? index + 1 };
  });
}

/** Selected questions link inside the collection; other references keep their source book. */
export function collectionQuestionCatalog(selected, source, sourceBook) {
  return [...new Map([
    ...source.map((question) => [question.id, { ...question, book: sourceBook }]),
    ...selected.map((question) => [question.id, question]),
  ]).values()];
}
