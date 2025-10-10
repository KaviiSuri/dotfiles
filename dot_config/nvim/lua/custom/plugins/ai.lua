-- vim.api.nvim_set_keymap('i', '<C-x>', cop, { expr = true, noremap = true, silent = true })
-- vim.g.copilot_no_tab_map = true

return {
  {
    'zbirenbaum/copilot.lua',
    cmd = 'Copilot',
    event = 'InsertEnter',
    config = function()
      require('copilot').setup {
        panel = {
          enabled = true,
          auto_refresh = false,
          keymap = {
            jump_prev = '[[',
            jump_next = ']]',
            accept = '<CR>',
            refresh = 'gr',
            open = '<C-a>',
          },
          layout = {
            position = 'bottom', -- | top | left | right
            ratio = 0.4,
          },
        },
        suggestion = {
          enabled = true,
          auto_trigger = true,
          hide_during_completion = true,
          debounce = 75,
          keymap = {
            accept = '<C-x>',
            accept_word = false,
            accept_line = false,
            next = '<M-]>',
            prev = '<M-[>',
            dismiss = '<C-]>',
          },
        },
        filetypes = {
          yaml = true,
          markdown = true,
          help = true,
          gitcommit = true,
          gitrebase = true,
          hgcommit = true,
          svn = true,
          cvs = true,
          ['.'] = true,
        },
        copilot_node_command = 'node', -- Node.js version must be > 18.x
        server_opts_overrides = {},
      }
    end,
  },
  -- {
  --   'robitx/gp.nvim',
  --   config = function()
  --     local conf = {
  --       providers = {
  --         copilot = {
  --           endpoint = 'https://api.githubcopilot.com/chat/completions',
  --           secret = {
  --             'bash',
  --             '-c',
  --             "cat ~/.config/github-copilot/hosts.json | sed -e 's/.*oauth_token...//;s/\".*//'",
  --           },
  --         },
  --         ollama = {
  --           endpoint = 'http://localhost:11434/v1/chat/completions',
  --         },
  --       },
  --       whisper = {
  --         disable = false,
  --       },
  --       default_chat_agent = 'Qwen2.5Coder',
  --       default_command_agent = 'Qwen2.5Coder',
  --
  --       agents = {
  --         {
  --           name = 'Qwen2.5Coder',
  --           chat = true,
  --           command = true,
  --           provider = 'ollama',
  --           model = { model = 'qwen2.5-coder' },
  --           system_prompt = 'I am an AI meticulously crafted to provide programming guidance and code assistance. '
  --             .. 'To best serve you as a computer programmer, please provide detailed inquiries and code snippets when necessary, '
  --             .. 'and expect precise, technical responses tailored to your development needs.\n',
  --         },
  --       },
  --     }
  --     require('gp').setup(conf)
  --
  --     -- Setup shortcuts here (see Usage > Shortcuts in the Documentation/Readme)
  --   end,
  -- },
  -- {
  --   'CopilotC-Nvim/CopilotChat.nvim',
  --   branch = 'canary',
  --   dependencies = {
  --     { 'zbirenbaum/copilot.lua' }, -- or zbirenbaum/copilot.lua
  --     { 'nvim-lua/plenary.nvim' }, -- for curl, log wrapper
  --   },
  --   build = 'make tiktoken', -- Only on MacOS or Linux
  --   opts = {
  --     -- See Configuration section for options
  --   },
  --   -- See Commands section for default commands if you want to lazy load on them
  -- },
  {
    'yetone/avante.nvim',
    event = 'VeryLazy',
    lazy = false,
    version = false, -- set this if you want to always pull the latest change
    opts = {
      ---@alias Provider "claude" | "openai" | "azure" | "gemini" | "cohere" | "copilot" | string
      provider = 'claude', -- Recommend using Claude
      auto_suggestions_provider = 'copilot', -- Since auto-suggestions are a high-frequency operation and therefore expensive, it is recommended to specify an inexpensive provider or even a free provider: copilot
      claude = {
        endpoint = 'https://api.anthropic.com',
        model = 'claude-3-5-sonnet-20241022',
        temperature = 0,
        max_tokens = 4096,
      },
      ---Specify the special dual_boost mode
      ---1. enabled: Whether to enable dual_boost mode. Default to false.
      ---2. first_provider: The first provider to generate response. Default to "openai".
      ---3. second_provider: The second provider to generate response. Default to "claude".
      ---4. prompt: The prompt to generate response based on the two reference outputs.
      ---5. timeout: Timeout in milliseconds. Default to 60000.
      ---How it works:
      --- When dual_boost is enabled, avante will generate two responses from the first_provider and second_provider respectively. Then use the response from the first_provider as provider1_output and the response from the second_provider as provider2_output. Finally, avante will generate a response based on the prompt and the two reference outputs, with the default Provider as normal.
      ---Note: This is an experimental feature and may not work as expected.
      dual_boost = {
        enabled = false,
        first_provider = 'openai',
        second_provider = 'claude',
        prompt = 'Based on the two reference outputs below, generate a response that incorporates elements from both but reflects your own judgment and unique perspective. Do not provide any explanation, just give the response directly. Reference Output 1: [{{provider1_output}}], Reference Output 2: [{{provider2_output}}]',
        timeout = 60000, -- Timeout in milliseconds
      },
      behaviour = {
        auto_suggestions = true, -- Experimental stage
        auto_set_highlight_group = true,
        auto_set_keymaps = true,
        auto_apply_diff_after_generation = false,
        support_paste_from_clipboard = false,
        minimize_diff = true, -- Whether to remove unchanged lines when applying a code block
      },
      mappings = {
        --- @class AvanteConflictMappings
        diff = {
          ours = 'co',
          theirs = 'ct',
          all_theirs = 'ca',
          both = 'cb',
          cursor = 'cc',
          next = ']x',
          prev = '[x',
        },
        suggestion = {
          accept = '<M-l>',
          next = '<M-]>',
          prev = '<M-[>',
          dismiss = '<C-]>',
        },
        jump = {
          next = ']]',
          prev = '[[',
        },
        submit = {
          normal = '<CR>',
          insert = '<C-s>',
        },
        sidebar = {
          apply_all = 'A',
          apply_cursor = 'a',
          switch_windows = '<Tab>',
          reverse_switch_windows = '<S-Tab>',
        },
      },
      hints = { enabled = true },
      windows = {
        ---@type "right" | "left" | "top" | "bottom"
        position = 'right', -- the position of the sidebar
        wrap = true, -- similar to vim.o.wrap
        width = 30, -- default % based on available width
        sidebar_header = {
          enabled = true, -- true, false to enable/disable the header
          align = 'center', -- left, center, right for title
          rounded = true,
        },
        input = {
          prefix = '> ',
          height = 8, -- Height of the input window in vertical layout
        },
        edit = {
          border = 'rounded',
          start_insert = true, -- Start insert mode when opening the edit window
        },
        ask = {
          floating = false, -- Open the 'AvanteAsk' prompt in a floating window
          start_insert = true, -- Start insert mode when opening the ask window
          border = 'rounded',
          ---@type "ours" | "theirs"
          focus_on_apply = 'ours', -- which diff to focus after applying
        },
      },
      highlights = {
        ---@type AvanteConflictHighlights
        diff = {
          current = 'DiffText',
          incoming = 'DiffAdd',
        },
      },
      --- @class AvanteConflictUserConfig
      diff = {
        autojump = true,
        ---@type string | fun(): any
        list_opener = 'copen',
        --- Override the 'timeoutlen' setting while hovering over a diff (see :help timeoutlen).
        --- Helps to avoid entering operator-pending mode with diff mappings starting with `c`.
        --- Disable by setting to -1.
        override_timeoutlen = 500,
      },
    },
    -- if you want to build from source then do `make BUILD_FROM_SOURCE=true`
    build = 'make',
    -- build = "powershell -ExecutionPolicy Bypass -File Build.ps1 -BuildFromSource false" -- for windows
    dependencies = {
      'nvim-treesitter/nvim-treesitter',
      'stevearc/dressing.nvim',
      'nvim-lua/plenary.nvim',
      'MunifTanjim/nui.nvim',
      --- The below dependencies are optional,
      'nvim-tree/nvim-web-devicons', -- or echasnovski/mini.icons
      'zbirenbaum/copilot.lua', -- for providers='copilot'
      {
        -- support for image pasting
        'HakonHarnes/img-clip.nvim',
        event = 'VeryLazy',
        opts = {
          -- recommended settings
          default = {
            embed_image_as_base64 = false,
            prompt_for_file_name = false,
            drag_and_drop = {
              insert_mode = true,
            },
            -- required for Windows users
            use_absolute_path = true,
          },
        },
      },
      {
        -- Make sure to set this up properly if you have lazy=true
        'MeanderingProgrammer/render-markdown.nvim',
        opts = {
          file_types = { 'markdown', 'Avante' },
        },
        ft = { 'markdown', 'Avante' },
      },
    },
  },
  {
    'twilwa/crawler.nvim',
    dependencies = { 'nvim-lua/plenary.nvim' },
  },
  {
    'GeorgesAlkhouri/nvim-aider',
    cmd = {
      'AiderTerminalToggle',
      'AiderHealth',
    },
    keys = {
      { '<leader>ih', '<cmd>AiderHealth<cr>', desc = 'Open Aider' },
      { '<leader>i/', '<cmd>AiderTerminalToggle<cr>', desc = 'Open Aider' },
      { '<leader>is', '<cmd>AiderTerminalSend<cr>', desc = 'Send to Aider', mode = { 'n', 'v' } },
      { '<leader>ic', '<cmd>AiderQuickSendCommand<cr>', desc = 'Send Command To Aider' },
      { '<leader>ib', '<cmd>AiderQuickSendBuffer<cr>', desc = 'Send Buffer To Aider' },
      { '<leader>i+', '<cmd>AiderQuickAddFile<cr>', desc = 'Add File to Aider' },
      { '<leader>i-', '<cmd>AiderQuickDropFile<cr>', desc = 'Drop File from Aider' },
      { '<leader>ir', '<cmd>AiderQuickReadOnlyFile<cr>', desc = 'Add File as Read-Only' },
      -- Example nvim-tree.lua integration if needed
      { '<leader>i+', '<cmd>AiderTreeAddFile<cr>', desc = 'Add File from Tree to Aider', ft = 'NvimTree' },
      { '<leader>i-', '<cmd>AiderTreeDropFile<cr>', desc = 'Drop File from Tree from Aider', ft = 'NvimTree' },
    },
    dependencies = {
      'folke/snacks.nvim',
      'nvim-telescope/telescope.nvim',
      --- The below dependencies are optional
      'catppuccin/nvim',
      'nvim-tree/nvim-tree.lua',
    },
    config = true,
    opts = {
      args = {
        '--no-auto-commits',
        '--pretty',
        '--stream',
      },
      config = {
        os = { editPreset = 'nvim-remote' },
        gui = { nerdFontsVersion = '3' },
      },
      theme = {
        user_input_color = '#a6da95',
        tool_output_color = '#8aadf4',
        tool_error_color = '#ed8796',
        tool_warning_color = '#eed49f',
        assistant_output_color = '#c6a0f6',
        completion_menu_color = '#cad3f5',
        completion_menu_bg_color = '#24273a',
        completion_menu_current_color = '#181926',
        completion_menu_current_bg_color = '#f4dbd6',
      },
      win = {
        style = 'nvim_aider',
        position = 'right',
      },
    },
  },
  -- {
  --   'supermaven-inc/supermaven-nvim',
  --   config = function()
  --     require('supermaven-nvim').setup {
  --       keymaps = {
  --         accept_suggestion = '<C-x>',
  --         clear_suggestion = '<C-]>',
  --         accept_word = '<C-j>',
  --       },
  --     }
  --   end,
  -- },
}
