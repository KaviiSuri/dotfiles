M = {}
function M.Toggle()
  if vim.b.hexmode then
    vim.cmd("%!xxd -r")
    vim.b.hexmode = false
  else
    vim.cmd("%!xxd")
    vim.b.hexmode = true
  end
end

return M
