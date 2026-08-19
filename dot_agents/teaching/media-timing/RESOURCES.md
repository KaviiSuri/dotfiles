# Media Timing Resources

## Knowledge

- [FFmpeg Documentation — main options (`-ss`, `-t`, `-frames`)](https://ffmpeg.org/ffmpeg.html)
  The primary source for what a flag *claims* to do. Verified wording: `-ss` as an **input**
  option "seeks in this input file to position"; as an **output** option it "decodes but
  discards input until the timestamps reach position". Use for: settling arguments about
  which frames survive a seek.
  ⚠️ Note what it does *not* say: nothing about what timestamp the surviving frames receive.
  That silence is why the 0.04s lead-in had to be measured.

- [FFmpeg Formats Documentation — `avoid_negative_ts`, mov/mp4 options](https://ffmpeg.org/ffmpeg-formats.html)
  Verified wording: `make_zero` = "Shift timestamps so that the first timestamp is 0";
  `auto` (default) = "Enables shifting when required by the target format". Documents the mov
  **demuxer's** `ignore_editlist` / `advanced_editlist`. Use for: muxer/demuxer timestamp flags.
  ⚠️ The mov **muxer's** edit-list behaviour is undocumented here — how it represents an
  initial delay is not specified. Measured behaviour beats guessing.

- [ISO/IEC 14496-12 (ISO Base Media File Format)](https://www.iso.org/standard/83102.html)
  The actual spec for the `elst` (edit list) box that browsers honour. Paywalled; use the
  MDN/W3C summaries below for day-to-day work and this when precision matters.

- [MDN — HTMLMediaElement.currentTime](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/currentTime)
  Defines the player's clock — the *other* clock in the two-clock problem. Use for:
  reasoning about what a browser will display at a given time.

- [MDN — requestVideoFrameCallback](https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback)
  Exposes `mediaTime` of the frame actually presented. Use for: proving what a browser is
  really showing, rather than inferring it from `currentTime`.

## Wisdom (Communities)

- [FFmpeg user mailing list](https://ffmpeg.org/mailman/listinfo/ffmpeg-user)
  Where the maintainers actually answer. Use for: "is this muxer behaviour intended?" — the
  exact class of question that had to be answered by experiment this week.
- [Video Production Stack Exchange](https://video.stackexchange.com/)
  Moderated, practitioner-heavy. Use for: container/timestamp questions with reproducible cases.
- [r/ffmpeg](https://reddit.com/r/ffmpeg)
  Lower signal than the above, but fast. Use for: sanity-checking a command line.

## Gaps

- **No trusted source found for how the mov muxer chooses its edit-list entry.** The rule
  (`declared_lead_in = round(residual / frameDur) × frameDur`) is *ours*, derived from 9
  measurements on ffmpeg 8.1 across 25/30/23.976fps. It is not documented and not verified
  against ffmpeg source. Treat as empirical until confirmed — ideally by reading
  `libavformat/movenc.c` or asking the mailing list.
- No resource yet on frame-accurate NLE conform practice (how editors model sub-frame
  boundaries). Relevant to the "should shots snap to the frame grid?" decision.
