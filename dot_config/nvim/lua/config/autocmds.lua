-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
-- Add any additional autocmds here

-- Setup autocmd for revealing all folds when a file is opened
-- using zR in neovim
vim.cmd([[
  augroup Folds
    autocmd!
    autocmd BufWinEnter * normal zR
  augroup END
]])
