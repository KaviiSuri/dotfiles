require('which-key').add {
  {
    '<leader>e',
    function()
      if vim.bo.filetype == 'netrw' then
        vim.cmd 'close'
      else
        vim.cmd 'Lexplore 30'
      end
    end,
    desc = 'Toggle [E]xplorer',
  },
}
