# Agent explanations get weighted by evidence, not confidence

Across this investigation I produced three explanations for the same 0.04s lead-in; the first
two (`avoid_negative_ts`, then "floor lands on the previous frame") were confidently stated
and both were disproved by one-line experiments. Kavii asked for the mechanism specifically so
he could "call out any inconsistencies" — treating a fluent explanation as unverified until
measured.

**Implications:** every lesson in this workspace must separate measured claims from asserted
ones explicitly (the `.measured` / `.unverified` callouts exist for this). Do not smooth over
gaps; he reads for them. Teaching should bias toward "here is the command that would falsify
this" over narrative explanation.
