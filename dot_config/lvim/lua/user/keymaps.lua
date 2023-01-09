M = {}

lvim.keys.normal_mode["H"] = ":bprev<cr>"
lvim.keys.normal_mode["L"] = ":bnext<cr>"
-- lvim.builtin.which_key.mappings["Z"] = "ZenMode<cr>"
-- Visual --
-- Stay in indent mode
lvim.keys.visual_mode["<"] = "<gv"
lvim.keys.visual_mode[">"] = ">gv"

lvim.keys.visual_mode["p"] = '"_dP'
-- lvim.keys.visual_mode["P"] = '"_dP'


lvim.keys.normal_mode["gx"] = [[:silent execute '!$BROWSER ' . shellescape(expand('<cfile>')] = 1)<CR>]]

lvim.keys.normal_mode["Q"] = "<cmd>Bdelete!<CR>"

lvim.keys.normal_mode["<S-tab>"] = "<cmd>lua require('telescope.builtin').buffers(require('telescope.themes').get_dropdown{previewer = false, initial_mode='normal'})<cr>"

vim.keymap.set("i", "jk", "<Esc>", { noremap = true })

Mshow_documentation = function()
  local filetype = vim.bo.filetype
  if vim.tbl_contains({ "vim", "help" }, filetype) then
    vim.cmd("h " .. vim.fn.expand "<cword>")
  elseif vim.tbl_contains({ "man" }, filetype) then
    vim.cmd("Man " .. vim.fn.expand "<cword>")
  elseif vim.fn.expand "%:t" == "Cargo.toml" then
    require("crates").show_popup()
  else
    vim.lsp.buf.hover()
  end
end

lvim.keys.normal_mode["K"] = ":lua require('user.keymaps').show_documentation()<CR>"

return M

