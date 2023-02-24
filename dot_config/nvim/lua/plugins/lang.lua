return {
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
}
