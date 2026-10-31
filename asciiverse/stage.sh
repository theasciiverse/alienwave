#!/bin/sh
# Lays out the av archive in stage/: Alienwave has no data files, so the
# binary sits at the top with its licence, readme and story.
set -eu
rm -rf stage && mkdir -p stage
cp alienwave stage/alienwave
cp COPYING README STORY PATCHES.md stage/
