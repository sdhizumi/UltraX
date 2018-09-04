from .header import Header


class Mdx:
    '''A MDX performance data object.'''

    def __init__(self):
        self.Header = Header()
        self.Tones = []
        self.Data = [bytearray() for _ in range(16)]    # 16 channels
        return

    def Export(self):
        '''Exports the current MDX object to a bytearray.'''
        e = bytearray(self.Header.Export() )

        for tone in self.Tones:
            e.extend(tone.Export() )

        for data in self.Data:
            e.extend(data)

        return e