# Changes from upstream

This is the Asciiverse packaging of Alienwave 0.4.0 (GPL-2.0-or-later) by
Alessandro Pira, an ncurses shoot-'em-up, and its last release
(alessandropira.org/alienwave/aw.html). History here starts from the
release tarball (alienwave-0.4.0.tar.gz, sha256
9f317cfa0fabf98e5c47dc793f6eb4dbca0b6e65e136e0661abc267ce720fc44),
tagged `0.4.0`. Gentoo, FreeBSD and SlackBuilds package it with build-flag
changes only; we pass ours on make's command line instead.

## Ours

- **Runs where `char` is unsigned.** The wave tables were plain `char`
  arrays holding negative values (-1 for "no alien needs to go first",
  for full-speed movement and for the end of a wave). On ARM Linux `char`
  is unsigned, so -1 read as 255 and the game crashed (SIGSEGV) as soon as
  the first wave started. The tables are now `signed char`.
- **No write past the shots array.** With all 25 shots in the air, one
  more went into the slot after the end of the array.
- **Pause shows in the field.** "*** PAUSED ***" was drawn at a fixed
  spot, off to the top left in any terminal bigger than 80x25; it now
  sits in the centred field like everything else. The function is
  renamed `pause_game`, since `pause` is also the C library's.
- **Esc answers at once.** Esc quits, and ncurses held each Esc for a
  second to see whether it began an arrow key, freezing the game; it now
  waits 25 ms (a set `ESCDELAY` still wins).
- **A clearer size message.** "must be run in an 80x25 terminal" now says
  at least 80x25, and gives the terminal's own size.
- **Header guard typo** in aliens.h (`_ALEINS_H`), which current GCC
  warns about.

## Packaging (new files)

- `asciiverse/build.sh`: static Linux build in Alpine, macOS builds per
  architecture, through upstream's Makefile.
- `asciiverse/stage.sh`: the av archive (binary at the top, no data).
- `asciiverse/nfpm.yaml`: .deb, .rpm, .apk and Arch packages.
- `asciiverse/record-preview.py`: records the catalog preview with a
  pilot that reads the screen through pyte; the kept take is
  `asciiverse/alienwave.cast`, best of several (a run ends at the first
  hit).
- `.github/workflows/release.yml`: builds all of it on a tag.

## Not changed

- The field is 80x25, one row more than the classic 80x24 terminal; the
  game refuses to start in anything smaller.
- One life, no high-score table: the score is printed on the way out.
- Xzarna comes after 5000 points (upstream's medium setting; the
  Makefile's `LEV_EASY`/`LEV_HARD` switches are left off), and the waves
  come in their fixed order (`RANDOM_LEVELS` off).
- A held key mostly counts once (the game ignores a key equal to the one
  it read the frame before), so moving faster means pressing the arrow
  again, and firing means pressing Space (or Enter) for each shot.
- No Windows build.
