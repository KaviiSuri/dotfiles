-- autopairs
-- https://github.com/windwp/nvim-autopairs

return {
  'windwp/nvim-autopairs',
  event = 'InsertEnter',
  -- Optional dependency
  dependencies = { 'hrsh7th/nvim-cmp' },
  config = function()
    local npairs = require('nvim-autopairs')
    local Rule = require('nvim-autopairs.rule')

    npairs.setup({
      check_ts = true, -- treesitter integration
      disable_filetype = { "TelescopePrompt" },
      enable_check_bracket_line = false,  -- Changed to false to allow nested pairs
      map_bs = true, -- map the <BS> key
      map_cr = true, -- map <CR> key
      map_c_h = true, -- Map the <C-h> key to delete a pair
      map_c_w = true, -- map <c-w> to delete a pair if possible
      ignored_next_char = "[%w%.]", -- will ignore alphanumeric and `.` symbol
      fast_wrap = {
        map = '<M-e>',
        chars = { '{', '[', '(', '"', "'" },
        pattern = string.gsub([[ [%'%"%)%>%]%}%,] ]], '%s+', ''),
        offset = 0, -- Offset from pattern match
        end_key = '$',
        keys = 'qwertyuiopzxcvbnmasdfghjkl',
        check_comma = true,
        highlight = 'Search',
        highlight_grey = 'Comment'
      },
    })

    -- Add spaces between parentheses
    local brackets = { { '(', ')' }, { '[', ']' }, { '{', '}' } }
    npairs.add_rules {
      Rule(' ', ' ')
        :with_pair(function (opts)
          local pair = opts.line:sub(opts.col - 1, opts.col)
          return vim.tbl_contains({
            brackets[1][1]..brackets[1][2],
            brackets[2][1]..brackets[2][2],
            brackets[3][1]..brackets[3][2],
          }, pair)
        end)
    }
    for _, bracket in pairs(brackets) do
      npairs.add_rules {
        Rule(bracket[1]..' ', ' '..bracket[2])
          :with_pair(function() return false end)
          :with_move(function(opts)
            return opts.prev_char:match('.%'..bracket[2]) ~= nil
          end)
          :use_key(bracket[2])
      }
    end

    -- If you want to automatically add `(` after selecting a function or method
    local cmp_autopairs = require('nvim-autopairs.completion.cmp')
    local cmp = require('cmp')
    cmp.event:on('confirm_done', cmp_autopairs.on_confirm_done())
  end,
}
