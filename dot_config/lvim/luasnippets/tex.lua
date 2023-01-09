return {
  s("tt", {
    t"\\texttt{", i(1), t"}"
  }),
  s("ff", {
    t"\\frac{", i(1), t"}{", i(2), t"}"
  }),
  s("hr", {
    t"\\href{", i(1, "url"), t"}{", i(2, "display name"), t"}"
  })
}, {}
