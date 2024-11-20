return {
  'xiyaowong/transparent.nvim',
  {
    'folke/zen-mode.nvim',
    config = function()
      require('zen-mode').setup {}
      vim.keymap.set('n', '<leader>z', ':ZenMode<CR>', { desc = 'Zen Mode' })
    end,
  },
  {
    'vhyrro/luarocks.nvim',
    priority = 1000, -- Very high priority is required, luarocks.nvim should run as the first plugin in your config.
    config = true,
  },
  {
    'rest-nvim/rest.nvim',
    dependencies = {
      'vhyrro/luarocks.nvim',
      'j-hui/fidget.nvim',
    },
  },
}
