return {
  -- RUST
  "simrat39/rust-tools.nvim",
  {
    "saecki/crates.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    init = function()
      require("crates").setup({
        null_ls = {
          enabled = true,
          name = "crates.nvim",
        },
      })
    end,
  },
  -- Tailwind
  {
    "neovim/nvim-lspconfig",
    opts = function(_, opts)
      opts.servers.tailwindcss = {}
    end,
  },
  {
    "laytan/tailwind-sorter.nvim",
    dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-lua/plenary.nvim" },
    build = "cd formatter && npm i && npm run build",
    config = {},
  },
  {
    "NvChad/nvim-colorizer.lua",
    opts = {
      user_default_options = {
        tailwind = true,
      },
    },
  },
  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      { "roobert/tailwindcss-colorizer-cmp.nvim", config = true },
    },
    opts = function(_, opts)
      local format_kinds = opts.formatting.format
      opts.formatting.format = function(entry, item)
        format_kinds(entry, item)
        return require("tailwindcss-colorizer-cmp").formatter(entry, item)
      end
    end,
  },
  {
    "klen/nvim-test",
    config = function()
      require("nvim-test").setup({
        run = true, -- run tests (using for debug)
        commands_create = true, -- create commands (TestFile, TestLast, ...)
        filename_modifier = ":.", -- modify filenames before tests run(:h filename-modifiers)
        silent = false, -- less notifications
        term = "toggleterm", -- a terminal to run ("terminal"|"toggleterm")
        termOpts = {
          direction = "vertical", -- terminal's direction ("horizontal"|"vertical"|"float")
          width = 96, -- terminal's width (for vertical|float)
          height = 24, -- terminal's height (for horizontal|float)
          go_back = false, -- return focus to original window after executing
          stopinsert = "auto", -- exit from insert mode (true|false|"auto")
          keep_one = true, -- keep only one terminal for testing
        },
        runners = { -- setup tests runners
          cs = "nvim-test.runners.dotnet",
          go = "nvim-test.runners.go-test",
          haskell = "nvim-test.runners.hspec",
          javascriptreact = "nvim-test.runners.jest",
          javascript = "nvim-test.runners.jest",
          lua = "nvim-test.runners.busted",
          python = "nvim-test.runners.pytest",
          ruby = "nvim-test.runners.rspec",
          rust = "nvim-test.runners.cargo-test",
          typescript = "nvim-test.runners.jest",
          typescriptreact = "nvim-test.runners.jest",
        },
      })
      require("nvim-test.runners.jest"):setup({
        command = "./node_modules/.bin/jest", -- a command to run the test runner
        args = { "--collectCoverage=false" }, -- default arguments

        file_pattern = "\\v(__tests__/.*|(spec|test))\\.(js|jsx|coffee|ts|tsx)$", -- determine whether a file is a testfile
        find_files = { "{name}.test.{ext}", "{name}.spec.{ext}" }, -- find testfile for a file
      })
    end,
    dependencies = { "akinsho/toggleterm.nvim" },
  },

  -- SvelteKit
  {
    "evanleck/vim-svelte",
    config = function()
      vim.g.svelte_preprocessors = { "typescript" }
    end,
    dependencies = { "othree/html5.vim", "pangloss/vim-javascript" },
    ft = { "svelte" },
  },
}
