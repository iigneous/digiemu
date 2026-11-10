"""USB OTG endpoint prime and flush complete at once.

The ChipIdea controller at 0xFC0B0000 has two command registers the firmware
polls. ENDPTPRIME (offset 0x1B0) and ENDPTFLUSH (offset 0x1B4): writing a bit
asks the controller to prime or flush that endpoint, and the bit stays set
until the controller finishes. Software waits for it to read back as clear.

Nothing here is a USB device, so a prime or a flush has nothing to do and is
already finished. A read of either register is 0.

Without that, confirming the Syntakt's warm-up dialog flushes an endpoint
from the main task with interrupts masked and spins on bit 17 of ENDPTFLUSH.
The dialog stays on screen and no key is taken.
"""
from unicorn import UC_HOOK_MEM_READ

ENDPTPRIME = 0xFC0B01B0
ENDPTFLUSH = 0xFC0B01B4


def _done(uc, typ, addr, size, val, data):
    uc.mem_write(ENDPTPRIME, b'\x00' * 8)


def install(m):
    m.ensure(ENDPTPRIME)
    m.uc.hook_add(UC_HOOK_MEM_READ, _done, begin=ENDPTPRIME,
                  end=ENDPTFLUSH + 3)
