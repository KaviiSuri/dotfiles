-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here
vim.keymap.set("i", "jk", "<Esc>", { noremap = true })

vim.g.copilot_no_tab_map = true
vim.api.nvim_set_keymap("i", "<C-X>", 'copilot#Accept("<CR>")', { silent = true, expr = true })

-- Harpoon
local mark = require("harpoon.mark")
local ui = require("harpoon.ui")
vim.keymap.set("n", "<leader>a", mark.add_file)
vim.keymap.set("n", "<leader>h", ui.toggle_quick_menu)
vim.keymap.set("n", "<C-u>", function()
  ui.nav_file(1)
end)
vim.keymap.set("n", "<C-i>", function()
  ui.nav_file(2)
end)
vim.keymap.set("n", "<C-o>", function()
  ui.nav_file(3)
end)
vim.keymap.set("n", "<C-p>", function()
  ui.nav_file(4)
end)

-- Editor
-- Move lines
vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv")
vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv")

-- Stay in the middle
vim.keymap.set("n", "n", "nzzzv")
vim.keymap.set("n", "N", "Nzzzv")
