return {
  {
    -- Conjure!
    'Olical/conjure',
    ft = { 'clojure', 'fennel' },
    init = function()
      vim.g['conjure#mapping#doc_word'] = false
    end,
  },

  -- Structural editing, optional
  'guns/vim-sexp',
  'tpope/vim-sexp-mappings-for-regular-people',
  'tpope/vim-repeat',
  'tpope/vim-surround',
}
