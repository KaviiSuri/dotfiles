-- Neo-tree is a Neovim plugin to browse the file system
-- https://github.com/nvim-neo-tree/neo-tree.nvim

return {
  -- 'nvim-neo-tree/neo-tree.nvim',
  -- version = '*',
  -- dependencies = {
  --   'nvim-lua/plenary.nvim',
  --   'nvim-tree/nvim-web-devicons', -- not strictly required, but recommended
  --   'MunifTanjim/nui.nvim',
  -- },
  -- cmd = 'Neotree',
  -- keys = {
  --   { '<leader>e', ':Neotree reveal<CR>', desc = 'NeoTree reveal', silent = true },
  -- },
  -- opts = {
  --   filesystem = {
  --     window = {
  --       mappings = {
  --         ['<leader>e'] = 'close_window',
  --       },
  --     },
  --   },
  -- },
  {
    'nvim-tree/nvim-tree.lua',
    dependencies = { 'nvim-tree/nvim-web-devicons' }, -- Optional for file icons
    config = function()
      require('nvim-tree').setup {
        view = {
          width = 30,
          side = 'left',
          number = false,
          relativenumber = false,
        },
        renderer = {
          icons = {
            show = {
              git = true,
              folder = true,
              file = true,
              folder_arrow = true,
            },
          },
        },
        actions = {
          open_file = {
            quit_on_open = false,
          },
        },
      }

      local api = require 'nvim-tree.api'
      -- Keybinding to toggle NvimTree
      vim.keymap.set('n', '<leader>e', function()
        if vim.bo.filetype == 'NvimTree' then
          api.tree.toggle()
        else
          api.tree.find_file({
            focus = true,
            open = true,
          })
        end
      end, { noremap = true, silent = true })
    end,
  },
  -- {
  --   'stevearc/oil.nvim',
  --   ---@module 'oil'
  --   ---@type oil.SetupOpts
  --   opts = {},
  --   -- Optional dependencies
  --   -- dependencies = { { "echasnovski/mini.icons", opts = {} } },
  --   dependencies = { 'nvim-tree/nvim-web-devicons' }, -- use if prefer nvim-web-devicons
  -- },
}
