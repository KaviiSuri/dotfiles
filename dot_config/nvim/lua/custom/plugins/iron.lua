return {
  'Vigemus/iron.nvim',
  keys = {
    { '<leader>rs', '<cmd>IronRepl<cr>', desc = 'Start REPL' },
    { '<leader>rr', '<cmd>IronRestart<cr>', desc = 'Restart REPL' },
    { '<leader>rf', '<cmd>IronFocus<cr>', desc = 'Focus REPL' },
    { '<leader>rh', '<cmd>IronHide<cr>', desc = 'Hide REPL' },
  },
  config = function()
    require('iron.core').setup {
      config = {
        repl_definition = {
          python = {
            command = { 'ipython', '--no-autoindent' },
          },
        },
        repl_open_cmd = require('iron.view').split.vertical.rightbelow(0.4),
      },
      keymaps = {
        send_motion = '<leader>sc',
        visual_send = '<leader>sc',
        send_file = '<leader>sf',
        send_line = '<leader>sl',
        send_paragraph = '<leader>sp',
        send_until_cursor = '<leader>su',
        cr = '<leader>s<cr>',
        interrupt = '<leader>s<space>',
        exit = '<leader>sq',
        clear = '<leader>cl',
      },
    }
  end,
}
