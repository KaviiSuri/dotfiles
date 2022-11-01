lvim.builtin.which_key.mappings["g"]["G"] = {
  name = "Gist",
  a = { "<cmd>Gist -b -a<cr>", "Create Anon" },
  d = { "<cmd>Gist -d<cr>", "Delete" },
  f = { "<cmd>Gist -f<cr>", "Fork" },
  g = { "<cmd>Gist -b<cr>", "Create" },
  l = { "<cmd>Gist -l<cr>", "List" },
  p = { "<cmd>Gist -b -p<cr>", "Create Private" },
}

lvim.builtin.which_key.mappings["g"]["g"] = { "<cmd>LazyGit<cr>", "LazyGit" }

lvim.builtin.which_key.mappings["z"] = { "<cmd>ZenMode<cr>", "ZenMode" }
lvim.builtin.which_key.mappings["l"]["h"] = { "<cmd>lua require('lsp-inlayhints').toggle()<cr>", "Toggle Hints" }

lvim.builtin.which_key.mappings["X"] = { ":lua require('user.utils.hexmode').Toggle()<cr>", "Toggle HexMode" }
lvim.builtin.which_key.mappings["gy"] = { "Link" }

lvim.builtin.which_key.mappings["l"]["f"] = {
  function()
    require("lvim.lsp.utils").format { timeout_ms = 10000 }
  end, "Format"
}
