require('luasnip.session.snippet_collection').clear_snippets 'go'
local ls = require 'luasnip'

local s = ls.snippet
local i = ls.insert_node
local fmt = require('luasnip.extras.fmt').fmt
local rep = require('luasnip.extras').rep

ls.add_snippets('go', {
  s(
    'rie',
    fmt(
      [[
if {} != nil {{
   return nil, {}
}}
  ]],
      {
        i(1, 'err'),
        rep(1),
      }
    )
  ),
})