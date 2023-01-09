-- " ## added by OPAM user-setup for vim / base ## 93ee63e278bdfc07d1139a748ed3fff2 ## you can edit, but keep this line
-- let s:opam_share_dir = system("opam config var share")
-- let s:opam_share_dir = substitute(s:opam_share_dir, '[\r\n]*$', '', '')
local opam_share_dir = vim.fn.system()
opam_share_dir = vim.fnsubstitute(opam_share_dir, '[\r\n]*$', '', '')

-- let s:opam_configuration = {}
local opam_configuration = {}

-- function! OpamConfOcpIndent()
--   execute "set rtp^=" . s:opam_share_dir . "/ocp-indent/vim"
-- endfunction
-- let s:opam_configuration['ocp-indent'] = function('OpamConfOcpIndent')
function OpamConfOcpIndent()
  vim.fn.execute("set rtp^=" .. opam_share_dir .. "/ocp-indent/vim")
end
opam_configuration['ocp-indent'] = OpamConfOcpIndent

-- function! OpamConfOcpIndex()
--   execute "set rtp+=" . s:opam_share_dir . "/ocp-index/vim"
-- endfunction
-- let s:opam_configuration['ocp-index'] = function('OpamConfOcpIndex')
function OpamConfOcpIndex()
  vim.fn.execute("set rtp+=" .. opam_share_dir .. "/ocp-index/vim")
end
opam_configuration['ocp-index'] = OpamConfOcpIndex



-- function! OpamConfMerlin()
--   let l:dir = s:opam_share_dir . "/merlin/vim"
--   execute "set rtp+=" . l:dir
-- endfunction
-- let s:opam_configuration['merlin'] = function('OpamConfMerlin')

function OpamConfMerlin()
  local dir = opam_share_dir .. "/merlin/vim"
  vim.fn.execute("set rtp+=" .. dir)
end
opam_configuration['merlin'] = OpamConfMerlin

-- let s:opam_packages = ["ocp-indent", "ocp-index", "merlin"]
local opam_packages = {"ocp-indent", "ocp-index", "merlin"}

-- let s:opam_check_cmdline = ["opam list --installed --short --safe --color=never"] + s:opam_packages
-- local opam_check_cmdline = "opam list --installed --short --safe --color=never" + s:opam_packages
-- let s:opam_available_tools = split(system(join(s:opam_check_cmdline)))
-- for tool in s:opam_packages
--   " Respect package order (merlin should be after ocp-index)
--   if count(s:opam_available_tools, tool) > 0
--     call s:opam_configuration[tool]()
--   endif
-- endfor
-- " ## end of OPAM user-setup addition for vim / base ## keep this line
-- " ## added by OPAM user-setup for vim / ocp-indent ## af00aed8059a762ea569298f47546400 ## you can edit, but keep this line
-- if count(s:opam_available_tools,"ocp-indent") == 0
--   source "/Users/kavii/.opam/cs3110-2022fa/share/ocp-indent/vim/indent/ocaml.vim"
-- endif
-- " ## end of OPAM user-setup addition for vim / ocp-indent ## keep this line
