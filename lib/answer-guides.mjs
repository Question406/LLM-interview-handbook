/** Editorial answers are separate from canonical statements and executable code. */
export function validateAnswerGuide(data, body, expectedId) {
  if (data.id !== expectedId) throw new Error(`answer guide ID must match ${expectedId}`);
  if (!['coding', 'design', 'concept', 'project', 'guide'].includes(data.kind)) throw new Error('unknown answer guide kind');
  for (const key of ['situation', 'task', 'approach', 'result']) {
    if (typeof data[key] !== 'string' || !data[key].trim()) throw new Error(`answer guide needs ${key}`);
  }
  if (typeof body !== 'string' || !body.trim()) throw new Error('answer guide needs a spoken answer');
  return { kind: data.kind, situation: data.situation.trim(), task: data.task.trim(), approach: data.approach.trim(), result: data.result.trim(), body: body.trim() };
}
