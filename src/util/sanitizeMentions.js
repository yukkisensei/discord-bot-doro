export function sanitizeForOutput(text) {
  if (!text || typeof text !== 'string') return text;
  // Neutralize @everyone/@here (including zero-width space bypasses)
  let out = text.replace(/@\u200b?(everyone|here)/gi, (_, mention) => `(${mention.toLowerCase()})`);

  // Neutralize role mentions like <@&ROLEID>
  out = out.replace(/<@&\d+>/g, '(role-mention)');

  // Neutralize user mentions like <@!123> or <@123>
  out = out.replace(/<@!?\d+>/g, '(user-mention)');

  // Neutralize channel mentions like <#123>
  out = out.replace(/<#\d+>/g, '(channel-mention)');

  return out;
}
