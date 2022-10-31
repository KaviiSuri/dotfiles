vim.g.gitblame_enabled = 0
vim.g.gitblame_message_template = "<summary> • <date> • <author>"
vim.g.gitblame_highlight_group = "LineNr"

vim.g.gist_open_browser_after_post = 1

local status_ok, gitlinker = pcall(require, "gitlinker")
if not status_ok then
  return
end

gitlinker.setup()
