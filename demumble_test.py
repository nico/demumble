#!/usr/bin/env python3
import os, re, subprocess, sys

tests = [
    ('demumble hello', 'hello\n'),
    ('demumble _Z4funcPci _Z1fv', 'func(char*, int)\nf()\n'),
    ('demumble < _Z4funcPci _Z1fv', 'func(char*, int)\nf()\n'),
    ('demumble _RINvNtC3std3mem8align_ofdE _RNvNvC5mylib3foo3bar',
     'std::mem::align_of::<f64>\nmylib::foo::bar\n'),
    ('demumble < _RINvNtC3std3mem8align_ofdE _RNvNvC5mylib3foo3bar',
     'std::mem::align_of::<f64>\nmylib::foo::bar\n'),
    ('demumble ?Fxi@@YAHP6AHH@Z@Z', 'int __cdecl Fxi(int (__cdecl *)(int))\n'),
    ('demumble ??0S@@QEAA@$$QEAU0@@Z', 'public: __cdecl S::S(struct S &&)\n'),
    ('demumble ??_C@_02PCEFGMJL@hi?$AA@', '"hi"\n'),
    ('demumble __Znwi', 'operator new(int)\n'),  # Strip extra _ (for macOS)
    ('demumble < __Znwi', 'operator new(int)\n'),  # Also from stdin
    ('demumble -m hi _Z1fv ho _Z1gv', 'hi\nf()\nho\ng()\n'),
    ('demumble -m < hi_ho _Z1fv ho _Z1gv ?hm', 'f()\ng()\n?hm\n'),
    ('demumble -m < _Z1fv!_Z1gv', 'f()\ng()\n'),
    ('demumble -m < _Z1fv!foo_bar', 'f()\n'),
    ('demumble Pi', 'int*\n'),
    ('demumble < Pi', 'Pi\n'),
    ('demumble < ___Z10blocksNRVOv_block_invoke',
     'invocation function for block in blocksNRVO()\n'),
    ('demumble < .____Z10blocksNRVOv_block_invoke',
     '.invocation function for block in blocksNRVO()\n'),
    ('demumble -m < .____Z10blocksNRVOv_block_invoke',
     'invocation function for block in blocksNRVO()\n'),
    ('demumble _ZN2zx7channelD4Ev', 'zx::channel::~channel()\n'),
    ('demumble -- -b', '-b\n'),
    ('demumble -- -m', '-m\n'),
    ('demumble -- -h', '-h\n'),
    ('demumble -h', re.compile('.*usage: demumble.*')),
    ('demumble --help', re.compile('.*usage: demumble.*')),
    ('demumble --version', re.compile('.*\..*')),
    ('demumble -b hello', 'hello\n'),
    ('demumble -b _Z1fv', '"f()" (_Z1fv)\n'),
    ('demumble -b < _Z1fv', '"f()" (_Z1fv)\n'),
    ('demumble -bm < _Z1fv!foo_bar', '"f()" (_Z1fv)\n'),
    ('demumble -mb < _Z1fv!foo_bar', '"f()" (_Z1fv)\n'),
    ('demumble --foo < bar', re.compile(".*unrecognized option `--foo'.*")),
    ('demumble -bx < bar', re.compile(".*unrecognized option `x' in `-bx'.*")),
    ('demumble < _ZZ3fooiENK3$_0clEi',
     'foo(int)::$_0::operator()(int) const\n'),
    ('demumble .?AVNet@@', "class Net `RTTI Type Descriptor Name'\n"),
    ('demumble < asdf?x@@3HAjkl', 'asdfint xjkl\n'),
    ('demumble < asdf?x@@3Hjkl', 'asdf?x@@3Hjkl\n'),
    ('demumble ?x@@3HAjkl', 'int x\n  unused suffix: jkl\n'),
]

status = 0
for t in tests:
    cmd = t[0].split()
    # Assume that demumble is next to this script.
    cmd[0] = os.path.join(os.path.dirname(__file__) or '.', cmd[0])
    if '<' in cmd:
        p = subprocess.Popen(cmd[:cmd.index('<')], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True)
        out = p.communicate(input='\n'.join(cmd[cmd.index('<') + 1:]) + '\n')[0]
    else:
        out = subprocess.check_output(cmd, universal_newlines=True)
    if (out != t[1] if isinstance(t[1], str) else not t[1].match(out)):
        print(f"`{t[0]}`: Expected '{t[1]}', got '{out}'")
        status = 1
print('passed' if status == 0 else 'failed')
sys.exit(status)
