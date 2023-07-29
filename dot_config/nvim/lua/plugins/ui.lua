-- UI Related Plugins and Overrides

return {
  {
    "folke/tokyonight.nvim",
    opts = {
      transparent = true,
      styles = {
        sidebars = "transparent",
        floats = "transparent",
      },
    },
  },
  "ellisonleao/glow.nvim",
  { "akinsho/toggleterm.nvim", version = "*", config = true },
  "f-person/git-blame.nvim",
  {
    "chentoast/marks.nvim",
    opts = {},
  },
}
