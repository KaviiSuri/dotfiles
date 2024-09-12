-- Function to open NetRW and highlight the current buffer's file
function OpenNetRWAtCurrentFile()
  -- Get the full path of the current file
  local current_file = vim.api.nvim_buf_get_name(0)

  -- Open NetRW at the current file's directory
  vim.cmd('Lexplore ' .. vim.fn.fnamemodify(current_file, ':h'))
end

local netrw_state = {
  mode = nil,
  last_file = nil,
}

require('which-key').add {
  {
    '<leader>ew',
    function()
      if vim.bo.filetype == 'netrw' then
        if netrw_state.mode == 'root' then
          vim.cmd 'close'
          OpenNetRWAtCurrentFile()
          netrw_state.mode = 'current'
        else
          vim.cmd 'close'
        end
      else
        netrw_state.last_file = vim.api.nvim_buf_get_name(0)
        OpenNetRWAtCurrentFile()
        netrw_state.mode = 'current'
      end
    end,
    desc = 'Toggle [E]xplorer at current [W]indow',
  },
  {
    '<leader>er',
    function()
      if vim.bo.filetype == 'netrw' then
        if netrw_state.mode == 'current' then
          vim.cmd 'close'
          vim.cmd 'Lexplore 30'
          netrw_state.mode = 'root'
        else
          vim.cmd 'close'
        end
      else
        netrw_state.last_file = vim.api.nvim_buf_get_name(0)
        vim.cmd 'Lexplore 30'
        netrw_state.mode = 'root'
      end
    end,
    desc = 'Toggle [E]xplorer at [R]oot',
  },
  {
    '<leader>et',
    function()
      if vim.bo.filetype == 'netrw' then
        vim.cmd 'close'
      end
    end,
    desc = 'Close NetRW',
    mode = 'n',
    buffer = true,
  },
}
