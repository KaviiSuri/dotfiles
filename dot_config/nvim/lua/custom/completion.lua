local cmp = require 'cmp'
local luasnip = require 'luasnip'
luasnip.config.setup {
  history = false,
  updateevents = 'TextChanged,TextChangedI',
}

cmp.setup {
  snippet = {
    expand = function(args)
      luasnip.lsp_expand(args.body)
    end,
  },
  completion = { completeopt = 'menu,menuone,noinsert' },

  -- For an understanding of why these mappings were
  -- chosen, you will need to read `:help ins-completion`
  --
  -- No, but seriously. Please read `:help ins-completion`, it is really good!
  mapping = cmp.mapping.preset.insert {
    -- Select the [n]ext item
    ['<C-n>'] = cmp.mapping.select_next_item(),
    -- Select the [p]revious item
    ['<C-p>'] = cmp.mapping.select_prev_item(),

    -- Scroll the documentation window [b]ack / [f]orward
    ['<C-b>'] = cmp.mapping.scroll_docs(-4),
    ['<C-f>'] = cmp.mapping.scroll_docs(4),

    -- Accept ([y]es) the completion.
    --  This will auto-import if your LSP supports it.
    --  This will expand snippets if the LSP sent a snippet.
    ['<C-y>'] = cmp.mapping.confirm { select = true },

    -- If you prefer more traditional completion keymaps,
    -- you can uncomment the following lines
    --['<CR>'] = cmp.mapping.confirm { select = true },
    --['<Tab>'] = cmp.mapping.select_next_item(),
    --['<S-Tab>'] = cmp.mapping.select_prev_item(),

    -- Manually trigger a completion from nvim-cmp.
    --  Generally you don't need this, because nvim-cmp will display
    --  completions whenever it has completion options available.
    ['<C-Space>'] = cmp.mapping.complete {},

    -- For more advanced Luasnip keymaps (e.g. selecting choice nodes, expansion) see:
    --    https://github.com/L3MON4D3/LuaSnip?tab=readme-ov-file#keymaps
  },
  sources = {
    { name = 'buffer' },
    {
      name = 'lazydev',
      -- set group index to 0 to skip loading LuaLS completions as lazydev recommends it
      group_index = 0,
    },
    { name = 'nvim_lsp' },
    { name = 'luasnip' },
    { name = 'path' },
  },
}

function ReloadSnips()
  for _, ft_path in ipairs(vim.api.nvim_get_runtime_file('lua/custom/snippets/*.lua', true)) do
    loadfile(ft_path)()
  end
end

ReloadSnips()

vim.keymap.set('n', '<leader>rs', ReloadSnips, { silent = true, desc = 'reload snippets' })

-- Think of <c-k> as moving to the right of your snippet expansion.
--  So if you have a snippet that's like:
--  function $name($args)
--    $body
--  end
--
-- <c-k> will move you to the right of each of the expansion locations.
-- <c-j> is similar, except moving you backwards.
vim.keymap.set({ 'i', 's' }, '<C-k>', function()
  if luasnip.expand_or_jumpable() then
    luasnip.expand_or_jump()
  end
end, { silent = true, desc = 'expand or jump' })
vim.keymap.set({ 'i', 's' }, '<C-j>', function()
  if luasnip.locally_jumpable(-1) then
    luasnip.jump(-1)
  end
end, { silent = true, desc = 'jump backwards' })

-- next choice
vim.keymap.set({ 'i', 's' }, '<C-h>', function()
  if luasnip.choice_active() then
    luasnip.change_choice(1)
  end
end, { silent = true, desc = 'next choice' })
