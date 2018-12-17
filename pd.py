import sigrokdecode as srd

'''
OUTPUT_PYTHON format: a dictionary containing a boolean if each button was pressed
'''

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
        ('y-pressed', 'Y Pressed'),
        ('y-unpressed', 'Y Not Pressed'),
        ('select-pressed', 'SELECT Pressed'),
        ('select-unpressed', 'SELECT Not Pressed'),
        ('start-pressed', 'START Pressed'),
        ('start-unpressed', 'START Not Pressed'),
        ('up-pressed', 'UP Pressed'),
        ('up-unpressed', 'UP Not Pressed'),
        ('down-pressed', 'DOWN Pressed'),
        ('down-unpressed', 'DOWN Not Pressed'),
        ('left-pressed', 'LEFT Pressed'),
        ('left-unpressed', 'LEFT Not Pressed'),
        ('right-pressed', 'RIGHT Pressed'),
        ('right-unpressed', 'RIGHT Not Pressed'),
        ('a-pressed', 'A Pressed'),
        ('a-unpressed', 'A Not Pressed'),
        ('x-pressed', 'X Pressed'),
        ('x-unpressed', 'X Not Pressed'),
        ('l-pressed', 'L Pressed'),
        ('l-unpressed', 'L Not Pressed'),
        ('r-pressed', 'R Pressed'),
        ('r-unpressed', 'R Not Pressed'),
    )
    annotation_rows = (
        ('latch', 'Latch', (0,)),
        ('data', 'Data', (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24)),
    )
    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']

    def __init__(self):
        self.reset_buttons()

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_python = self.register(srd.OUTPUT_PYTHON)

    def wait_for_latch(self):
        self.wait({1: 'r'})
        start_latch = self.samplenum
        self.wait({1: 'f'})
        self.put(start_latch, self.samplenum, self.out_ann, [0, ['Latch', 'Lch', 'L']])

    def reset_buttons(self):
        self.button_state = {
            'B': False,
            'Y': False,
            'SELECT': False,
            'START': False,
            'UP': False,
            'DOWN': False,
            'LEFT': False,
            'RIGHT': False,
            'A': False,
            'X': False,
            'L': False,
            'R': False
            }

    @staticmethod
    def button_annotation(button, pressed, pressed_index):
        if pressed:
            return [pressed_index, ['{} Pressed'.format(button), '{} - 1'.format(button), button]]
        return [pressed_index + 1, ['{} Not Pressed'.format(button), '{} - 0'.format(button), button]]

    def next_clock(self):
        data = self.wait({0: 'f'})[2]
        start_press = self.samplenum
        self.wait({0: 'r'})
        return start_press, self.samplenum, data

    def annotate_inputs(self):
        start_inputs = self.samplenum
        for x in range(0, len(self.buttons)):
            start_press, stop_press, data = self.next_clock()
            self.button_state[self.buttons[x]] = not data
            self.put(start_press, stop_press, self.out_ann,
                     Decoder.button_annotation(self.buttons[x], not data, (x*2) + 1))
        stop_inputs = self.samplenum
        self.put(start_inputs, stop_inputs, self.out_python, self.button_state)
        self.reset_buttons()

    def decode(self):
        while True:
            self.wait_for_latch()
            self.annotate_inputs()
