'''
The Super Nintendo Controller utilizes a protocol that communicates with
a parallel in serial out shift register found in the controller using 3
primary lines, clock, latch, and data.
'''

from .pd import Decoder
