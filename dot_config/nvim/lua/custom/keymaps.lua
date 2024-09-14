require('which-key').add {
  {
    '<leader>ew',
    desc = 'Toggle [E]xplorer at current [W]indow',
  },
  {
    '<leader>er',
    '<cmd>:NvimTreeToggle<CR>',
    desc = 'Toggle [E]xplorer at [R]oot',
  },
}
