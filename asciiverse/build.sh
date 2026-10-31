#!/bin/sh
# Builds alienwave. Linux: run inside alpine:3.22 for a fully static binary
# (ncurses linked in); macOS: run on the runner with CC_ARCH set to x86_64
# or arm64, linking the system's ncurses.
#   docker run --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh
# Leaves ./alienwave. Upstream's Makefile is used as is; CC and LIB are
# overridden on the command line rather than patched. It strips the
# binary itself.
set -eu
if [ -f /etc/alpine-release ]; then
  apk add --no-cache build-base ncurses-dev ncurses-static >/dev/null
  libs="-static -lncursesw"
else
  libs="-lncurses"
fi
cc="cc${CC_ARCH:+ -arch $CC_ARCH}"
make distclean >/dev/null
make CC="$cc" LIB="$libs"
make clean >/dev/null
