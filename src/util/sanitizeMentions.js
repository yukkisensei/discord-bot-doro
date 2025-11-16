export function sanitizeForOutput(text) {
  if (!text || typeof text !== 'string') return text;
  // Neutralize @everyone and @here
  let out = text.replace(/@everyone/gi, '(everyone)').replace(/@here/gi, '(here)');

  // Neutralize role mentions like <@&ROLEID>
  out = out.replace(/<@&\d+>/g, '(role-mention)');

  // Neutralize user mentions like <@!123> or <@123>
  out = out.replace(/<@!?\d+>/g, '(user-mention)');

  return out;
}
