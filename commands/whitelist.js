export default {
  name: 'whitelist',
  description: 'Unblock a user from bot blacklist (owner/admin only)',
  options: [
    {
      name: 'userid',
      description: 'User ID to unblock',
      type: 3, // STRING
      required: true
    }
  ],
  async execute(interaction) {
    const ownerId = process.env.BOT_OWNER_ID || ''; // set in .env
    const isAdmin = interaction.member?.permissions?.has?.('Administrator');
    if (interaction.user.id !== ownerId && !isAdmin) {
      return interaction.reply({ content: 'Bạn không có quyền sử dụng lệnh này.', ephemeral: true, allowedMentions: { parse: [] } });
    }

    const userId = interaction.options.getString('userid', true);
    const dmProtection = (await import('../src/dmProtection.js')).default;
    const ok = dmProtection.unblock(userId);
    if (ok) {
      return interaction.reply({ content: `Đã gỡ block user ${userId}.`, ephemeral: true, allowedMentions: { parse: [] } });
    } else {
      return interaction.reply({ content: `User ${userId} không có trong danh sách block.`, ephemeral: true, allowedMentions: { parse: [] } });
    }
  }
};
