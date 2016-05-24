from __future__ import print_function

tests = [
    ('demumble hello', 'hello\n'),
    ('demumble _Z4funcPci _Z1fv', 'func(char*, int)\nf()\n'),
    ('demumble < _Z4funcPci _Z1fv', 'func(char*, int)\nf()\n'),
    ('demumble ?Fx_i@@YAHP6AHH@Z@Z', 'int __cdecl Fx_i(int (__cdecl*)(int))\n'),
    ('demumble __Znwi', 'operator new(int)\n'),  # Strip extra _ (for OS X)
    ('demumble < __Znwi', 'operator new(int)\n'),  # Also from stdin
]

import os, subprocess
for t in tests:
    cmd = t[0].split()
    # Assume that demumble is next to this script.
    cmd[0] = os.path.join(os.path.dirname(__file__) or '.', cmd[0])
    if cmd[1] == '<':
      p = subprocess.Popen(cmd[0], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      out = p.communicate(input='\n'.join(cmd[2:]) + '\n')[0]
    else:
      out = subprocess.check_output(cmd)
    if out != t[1]:
      print("`%s`: Expected '%s', got '%s'" % (t[0], t[1], out))
