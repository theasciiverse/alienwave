#!/usr/bin/env python3
"""Records asciiverse/alienwave.cast, Alienwave's catalog preview, at 100x30
(hub/RECORDING.md): the title screen, then up to 40 s of play by a simple
pilot that reads the screen (pyte), slides under the nearest alien, fires,
dodges what comes too close and raises the shield when it can't, then the
score Alienwave prints on the way out. Needs pyte. Waves are random per run
(srand(time)), so take the best of a few. Usage, from the repo root after
building ./alienwave:
    python3 asciiverse/record-preview.py"""
import os, pty, struct, fcntl, select, termios, time
import pyte

COLS, ROWS = 100, 30
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", LANG="C.UTF-8")


# ncurses draws runs of one character with REP (CSI n b), which pyte lacks
class Screen(pyte.Screen):
    last = " "
    def draw(self, data):
        if data: self.last = data[-1]
        super().draw(data)
    def rep(self, n=1, *args, **kwargs):
        self.draw(self.last * max(n, 1))

class Stream(pyte.ByteStream):
    csi = dict(pyte.ByteStream.csi, b="rep")

screen = Screen(COLS, ROWS)
stream = Stream(screen)

pid, fd = pty.fork()
if pid == 0:
    os.chdir(root)      # so the recording shows no local paths
    os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "-i", "2",
        "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,COLORTERM,LANG",
        "-c", "./alienwave", "asciiverse/alienwave.cast"], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))

done = False
def alive():
    global done
    if not done and os.waitpid(pid, os.WNOHANG)[0]: done = True
    return not done

def pump(t):
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.01)
        if r:
            try: stream.feed(os.read(fd, 65536))
            except OSError: return

def key(k, wait=0.0):
    os.write(fd, k); pump(wait)

# The 80x25 field is centred (main.c right_size): at 100x30 it starts at
# column 10, row 2. The ship's top is on field row 21 and its cockpit
# "| _ |" on row 22, a cell right of its x (0..73); it is 7 wide and
# fires from x+3.
XO, YO = (COLS - 80) // 2, (ROWS - 25) // 2
# arrows as xterm sends them in keypad mode (ncurses turns that on)
LEFT, RIGHT, STOP = b"\x1bOD", b"\x1bOC", b"\x1bOB"

def cell(fx, fy):
    return screen.display[fy + YO][fx + XO]

def ship_x():
    # by its cockpit: some aliens have the same "/^\\" nose
    line = screen.display[22 + YO]
    i = line.find("| _ |", XO, XO + 80)
    return i - XO - 1 if i >= 0 else None

def aliens():
    """Field cells (x, y) holding something that isn't ours."""
    out = []
    for fy in range(1, 20):
        row = screen.display[fy + YO]
        for fx in range(80):
            if row[fx + XO] not in " !":
                out.append((fx, fy))
    return out

def shield_ready():  # the charge bar, top left
    return sum(cell(i, 0) == "-" for i in range(20)) >= 8

pump(2.5)
key(b" ", 0.3)                  # "Press any key to start"
speed = 0                       # what we think the ship's speed is
fire = [b" ", b"\r"]            # alternate: a repeated key counts once
shots = 0
seen = []                       # recent ship positions
end = time.time() + float(os.environ.get("PLAY_SECONDS", 40))
while time.time() < end and alive():
    pump(0.06)
    x = ship_x()
    if x is None:
        continue
    seen = (seen + [x])[-3:]
    # resync: stopped by a wall, or a key that the game dropped
    if len(seen) == 3 and seen[0] == seen[-1]: speed = 0
    elif len(seen) == 3 and (seen[-1] - seen[0]) * speed < 0: speed = -speed
    cells = aliens()
    def threat(sx):
        """How crowded the air over a ship at sx is: lower and nearer counts more."""
        t = 0
        for ax, ay in cells:
            if ay < 8: continue
            slack = (21 - ay) // 3      # they drift sideways as they come
            if sx - 1 - slack <= ax <= sx + 7 + slack:
                t += (ay - 6) ** 2
        return t
    shield = screen.display[20 + YO].find("/~~~^~~~\\", XO, XO + 80) - XO
    if max((ay for ax, ay in cells if x - 1 <= ax <= x + 7), default=0) >= 17 \
            and shield_ready() and shield < -1:
        key(b"s"); continue
    if shield >= -1 and shield <= x <= shield + 2:
        want = 0                # it stays where it was raised: stay under it
    else:
        # under the lowest alien still high enough to shoot, away from
        # crowded air
        high = [c for c in cells if c[1] <= 12]
        aim = max(high, key=lambda c: c[1])[0] - 3 if high else x
        best = min(range(0, 74), key=lambda sx: threat(sx) * 4 + abs(sx - aim))
        d = best - x
        want = 0 if abs(d) <= 1 else (1 if d > 0 else -1) * (2 if abs(d) > 20 else 1)
    if want != speed:
        if want == 0 or want * speed < 0: key(STOP); speed = 0
        elif want > speed: key(RIGHT); speed += 1
        else: key(LEFT); speed -= 1
    if any(abs(ax - (x + 3)) <= 3 for ax, _ in cells):
        key(fire[shots % 2]); shots += 1
pump(0.5)
if alive():
    key(b"\x1b", 2.5)           # quit: Alienwave prints the score
for _ in range(30):
    if not alive(): break
    pump(0.2)
