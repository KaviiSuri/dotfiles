local status_ok, which_key = pcall(require, "which-key")
if not status_ok then
  return
end

local opts = {
  mode = "n", -- NORMAL mode
  prefix = "<leader>",
  buffer = nil, -- Global mappings. Specify a buffer number for buffer local mappings
  silent = true, -- use `silent` when creating keymaps
  noremap = true, -- use `noremap` when creating keymaps
  nowait = true, -- use `nowait` when creating keymaps
}

function _G.rails_generate_model()
  local model = vim.fn.input("Name of the Model: ", "")
  vim.cmd(":Generate model" .. model)
end

function _G.rails_generate_controller()
  local controller = vim.fn.input("Name of the Controller: ", "")
  vim.cmd(":Generate Controller" .. controller)
end

local mappings = {
  C = {
    name = "Ruby",
    i = { "<cmd>Bundle install --path ./vendor/bundle<Cr>", "Install Go Dependencies" },
    G = {
      name = "Generate",
      m = { "<cmd>:lua rails_generate_model()<cr>", "Generate Model" },
      c = { "<cmd>:lua rails_generate_controller()<cr>", "Generate Controller" }
    },
    t = { "<cmd>lua require('dap-go').debug_test()<cr>", "Debug Test" },
  },
}

which_key.register(mappings, opts)
