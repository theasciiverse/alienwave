# Alienwave (Asciiverse packaging)

Alienwave 0.4.0 by Alessandro Pira, an ncurses vertical shoot-'em-up
(waves of zorxians, a stationary shield, the queen Xzarna), with fixes,
packaged for the Asciiverse catalog and as system packages. Not our code:
keep changes small and list every one in PATCHES.md.

- No upstream repository (only the 0.4.0 tarball on
  alessandropira.org); history starts from it (tag `0.4.0`), then ours.
  `origin` is to be github.com/theasciiverse/alienwave.
- Release: tag `v0.4.0-av.<n>` and push it.
- Local build: `make` (needs libncurses-dev). Static build: `docker run
  --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh` leaves
  `./alienwave`.
- Needs a terminal of at least 80x25; the field is centred in bigger ones.
- Preview: `python3 asciiverse/record-preview.py` (needs pyte). Under
  pyte, send arrows as `ESC O x` (keypad mode): `ESC [ x` reads as Esc,
  which quits.
