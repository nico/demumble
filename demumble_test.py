from __future__ import print_function

tests = [
    ('demumble hello', 'hello\n'),
    ('demumble _Z4funcPci', 'func(char*, int)\n'),
    ('demumble ?Fx_i@@YAHP6AHH@Z@Z', 'int __cdecl Fx_i(int (__cdecl*)(int))\n'),
]

import os, subprocess
for t in tests:
    cmd = t[0].split()
    # Assume that demumble is next to this script.
    cmd[0] = os.path.join(os.path.dirname(__file__) or '.', cmd[0])
    out = subprocess.check_output(cmd)
    if out != t[1]:
      print("`%s`: Expected '%s', got '%s'" % (t[0], t[1], out))
