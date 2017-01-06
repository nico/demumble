#!/usr/bin/env python

from __future__ import print_function
import os
import re
import subprocess
import unittest


class TestDemumble(unittest.TestCase):

  TESTS = [
      # Format:
      # Args, Stdin (if any), expected output.
      ('hello', None, 'hello\n'),
      ('_Z4funcPci _Z1fv', None, 'func(char*, int)\nf()\n'),
      ('?Fx_i@@YAHP6AHH@Z@Z', None, 'int __cdecl Fx_i(int (__cdecl*)(int))\n'),
      ('__Znwi', None, 'operator new(int)\n'),  # Strip extra _ (for OS X)
      ('-m hi _Z1fv ho _Z1gv', None, 'hi\nf()\nho\ng()\n'),
      ('Pi', None, 'int*\n'),
      ('-- -m', None, '-m\n'),
      ('-- -h', None, '-h\n'),
      ('-h', None, re.compile(r'.*usage: demumble.*')),
      ('--help', None, re.compile(r'.*usage: demumble.*')),
      ('--version', None, re.compile(r'.*\..*')),

      ('', '_Z4funcPci _Z1fv', 'func(char*, int)\nf()\n'),
      ('', '__Znwi', 'operator new(int)\n'),  # Also from stdin
      ('-m', 'hi_ho _Z1fv ho _Z1gv ?hm', 'f()\ng()\n?hm\n'),
      ('-m', '_Z1fv!_Z1gv', 'f()\ng()\n'),
      ('-m', '_Z1fv!foo_bar', 'f()\n'),
      ('', 'Pi', 'Pi\n'),
      ('', '___Z10blocksNRVOv_block_invoke',
       'invocation function for block in blocksNRVO()\n'),
      ('', '.____Z10blocksNRVOv_block_invoke',
       '.invocation function for block in blocksNRVO()\n'),
      ('-m', '.____Z10blocksNRVOv_block_invoke',
       'invocation function for block in blocksNRVO()\n'),
  ]

  def runWithArgs(self, args, stdin_text=None):
    demumble_bin = os.path.join(os.path.dirname(__file__) or '.', 'demumble')
    if stdin_text:
      p = subprocess.Popen([demumble_bin] + args.split(),
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
      out = p.communicate(input='\n'.join(stdin_text.split()) + '\n')[0]
    else:
      out = subprocess.check_output([demumble_bin] + args.split(),
                                    universal_newlines=True)
    return out

  def testAll(self):
    for t in self.TESTS:
      args, stdin_text, expected = t
      out = self.runWithArgs(args, stdin_text)

      if isinstance(expected, str):
        self.assertSequenceEqual(expected, out)
      else:
        # Regex.
        self.assertRegexpMatches(out, expected)


if __name__ == '__main__':
  unittest.main()
