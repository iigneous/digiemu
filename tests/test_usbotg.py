"""ENDPTPRIME and ENDPTFLUSH read back clear.

The firmware writes a bit and polls until the controller clears it. The hook
does that clear on the read, which is the only moment the poll looks.
"""
import unittest

from emu.usbotg import ENDPTFLUSH, ENDPTPRIME, _done, install


class Mem:
    def __init__(self):
        self.raw = bytearray(b'\xff' * 8)

    def mem_write(self, addr, data):
        off = addr - ENDPTPRIME
        self.raw[off:off + len(data)] = data

    def mem_read(self, addr, size):
        off = addr - ENDPTPRIME
        return bytes(self.raw[off:off + size])


class TestFlushCompletes(unittest.TestCase):
    def test_a_read_clears_both_registers(self):
        uc = Mem()
        uc.mem_write(ENDPTFLUSH, b'\x00\x02\x00\x00')
        _done(uc, None, ENDPTFLUSH, 4, 0, None)
        self.assertEqual(uc.mem_read(ENDPTPRIME, 8), b'\x00' * 8)

    def test_install_hooks_the_register_span(self):
        hooks = []

        class Uc(Mem):
            def hook_add(self, kind, fn, begin, end):
                hooks.append((fn, begin, end))

        class Machine:
            uc = Uc()

            def ensure(self, addr):
                self.ensured = addr

        m = Machine()
        install(m)
        self.assertEqual(m.ensured, ENDPTPRIME)
        self.assertEqual(hooks, [(_done, ENDPTPRIME, ENDPTFLUSH + 3)])
