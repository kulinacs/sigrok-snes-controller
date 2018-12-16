import sigrokdecode as srd

class Decoder(srd.Decoder):
    api_version = 3
    id = 'snes_controller'
    name = 'SNES Controller'
    longname = 'Super Nintendo Controller'
    desc = 'Protocol for controlling the Super Nintendo'
    license = 'gplv3+'
    inputs = ['logic']
    outputs = ['snes_controller']
    channels = (
        {'id': 'clk', 'name': 'Clock', 'desc': 'Clock pulses to receive data'},
        {'id': 'lch', 'name': 'Latch', 'desc': 'Latch to lock current input state'},
        {'id': 'data', 'name': 'Data', 'desc': 'Data representing controller state'},
    )
    optional_channels = ()
    options = ()
    annotations = (
        ('latch', 'Latch'),
        ('b-pressed', 'B Pressed'),
        ('b-unpressed', 'B Not Pressed'),
    )
    annotation_rows = (
        ('latch', 'Latch', (0,)),
        ('data', 'Data', (1, 2,)),
    )

    def __init__(self):
        self.state = 'WAIT_LATCH'

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def wait_for_latch(self):
        self.wait({1: 'r'})
        start_latch = self.samplenum
        self.wait({1: 'f'})
        self.put(start_latch, self.samplenum, self.out_ann, [0, ['Latch', 'Lch', 'L']])

    def decode(self):
        while True:
            self.wait_for_latch()
            (clock, latch, data) = self.wait({0: 'f'})
            start_press = self.samplenum
            self.wait({0: 'r'})
            if not data:
                self.put(start_press, self.samplenum, self.out_ann, [1, ['B Pressed', 'B - 0', 'B']])
            else:
                self.put(start_press, self.samplenum, self.out_ann, [2, ['B Not Pressed', 'B - 1', 'B']])
