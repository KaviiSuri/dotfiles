lvim.plugins = {
  'christoomey/vim-tmux-navigator',
  "j-hui/fidget.nvim",
  "windwp/nvim-ts-autotag",
  "NvChad/nvim-colorizer.lua",
  "moll/vim-bbye",
  "folke/todo-comments.nvim",
  "f-person/git-blame.nvim",
  "lvimuser/lsp-inlayhints.nvim",
  {
    'ruifm/gitlinker.nvim',
    requires = { 'nvim-lua/plenary.nvim' },
  },
  "mattn/vim-gist",
  -- visualization plugins
  "folke/zen-mode.nvim",
  "kevinhwang91/nvim-bqf",
  "hrsh7th/cmp-emoji",
  "nacro90/numb.nvim",

  { "christianchiarulli/telescope-tabs", branch = "chris" },

  "simrat39/rust-tools.nvim",
  {
    "saecki/crates.nvim",
    tag = "v0.3.0",
    requires = { "nvim-lua/plenary.nvim" },
    config = function()
      require("crates").setup({
        null_ls = {
          enabled = true,
          name = "crates.nvim",
        },
      })
    end,
  },
  "olexsmir/gopher.nvim",
  "leoluz/nvim-dap-go",
  "mfussenegger/nvim-dap-python",
  "jose-elias-alvarez/typescript.nvim",
  "mxsdev/nvim-dap-vscode-js",
  "monaqa/dial.nvim",
  "dracula/vim",
  "ellisonleao/glow.nvim",
  "kdheepak/lazygit.nvim",
  "tpope/vim-bundler",
  "tpope/vim-rails",
  "tpope/vim-dispatch",
  {
    "Equilibris/nx.nvim",
    requires = {
      "nvim-telescope/telescope.nvim",
    },
    config = function()
      require("nx").setup {}
    end
  }
}
