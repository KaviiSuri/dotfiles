# A clip carries two clocks, and the file — not the reader — was wrong

Kavii worked out, against my analysis, that a shot clip is read on two independent clocks: the
renderer counts frame indices (`trim=start_frame`) while the browser reads presentation
timestamps, and an mp4 edit list can make them disagree by a frame. He reached the crucial
judgement himself: compensating in the editor is invalid because shots play for a fixed
duration, so an offset would break start/end alignment against the shot's own length.

**Evidence:** rejected the editor-offset fix unprompted with the duration argument; then
pushed back on my framing that "the renderer is correct and the browser is early", correctly
identifying that the browser follows a standard and that claiming our method is better needed
justification. Both were right and both changed the plan.

**Implications:** he does not need frame-grid fundamentals re-taught. Next zone of proximal
development is (a) the raw/encoder-delay offset that is still only partly characterised, and
(b) the design question he now owns — round vs floor on take ends, and whether shot boundaries
should snap to the frame grid at ingest, which would dissolve this whole class.
