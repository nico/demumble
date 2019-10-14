import ctypes
import sys
import os
from distutils import sysconfig

demumble = None

# Demangle a C++ name, windows or itanium style
def demangle(mangled_name):
    if demumble == None:
        return (0, mangled_name)

    func = demumble.demangle
    func.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    func.resptype = ctypes.c_bool

    outbuf = ctypes.create_string_buffer(1024)
    try:
        status = func(mangled_name.encode('utf-8'), outbuf)
    except:
        return (0, mangled_name)
    return (status, outbuf.value.decode('utf-8'))

# is the character in the valid range for itanium
def is_mangle_char_itanium(c):
    func = demumble.is_mangle_char_itanium

    func.argtypes = [ctypes.c_byte]
    func.resptype = ctypes.c_bool
    return func(c)

# is the character in the valid range for windows
def is_mangle_char_win(c):
    func = demumble.is_mangle_char_win

    func.argtypes = [ctypes.c_byte]
    func.resptype = ctypes.c_bool
    return func(c)

def version():
    func = demumble.get_version
    func.argtypes = [ctypes.c_char_p]

    outbuf = ctypes.create_string_buffer(1024)
    func(outbuf)
    return outbuf.value.decode('utf-8')

basedir = os.path.dirname(os.path.realpath(__file__))
if sys.platform.startswith('linux'):
    demumble = ctypes.CDLL(os.path.join(basedir, "libdemumble_shared.so"))
else:
    demumble = ctypes.CDLL(os.path.join(basedir, "demumble_shared.dll"))

def main():
    print("Loaded demumble version:", version())
    status, demangled = demangle(sys.argv[1])
    print(demangled)

if __name__ == '__main__':
    main()
