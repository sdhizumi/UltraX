from ... import pymdx
from .reader import Channel_Reader, Pattern_Reader

from .. import locale

#rowtick = 0x18
TICKS_PER_ROW = 0x06

VALUES_STEREO = {
        0x10: 0b01,  0xF0: 0b01,
        0x11: 0b11,  0xFF: 0b11,
        0x01: 0b10,  0x0F: 0b10,
        0x00: 0b00
    }

EMPTY_FX_CMDS = [ [], [] ]


class Dmfc_Parser:

    Dmfc_Cntr = None


    def Compiler(self, Dmfc_Cntr):

        self.Dmfc_Cntr = Dmfc_Cntr

        cr = [
            Channel_Reader(channel) for channel in 
                Dmfc_Cntr.DmfObj.Module.Channels[:Dmfc_Cntr.AMOUNT_CHANNELS]
        ]

        


        # Calculate the initial tempo
        tempo = CalcTempo(Dmfc_Cntr.DmfObj.Module.Tick1, Dmfc_Cntr.REFRESH_RATE, Dmfc_Cntr.TIME_BASE)
        if (Dmfc_Cntr.DmfObj.Module.Tick1 == Dmfc_Cntr.DmfObj.Module.Tick2 - 1  or  Dmfc_Cntr.DmfObj.Module.Tick1 == Dmfc_Cntr.DmfObj.Module.Tick2 + 1):
            tempo = round((tempo + CalcTempo(Dmfc_Cntr.DmfObj.Module.Tick2, Dmfc_Cntr.REFRESH_RATE, Dmfc_Cntr.TIME_BASE)) / 2)
        Dmfc_Cntr.MdxObj.DataTracks[0].Add.Tempo_Bpm(tempo)

        # Init channel settings
        for c, channel in enumerate(cr):
            chn_data = Dmfc_Cntr.Channels[c]
            if (c < 8):
                chn_data.Add(pymdx.command.Volume(0x80) )
                chn_data.Add(pymdx.command.Tone(0) )
                channel.Volume = 0x7F
            else:
                if (Dmfc_Cntr.USES_EXPCM):
                    chn_data.Add(pymdx.command.Tone(0) )
                #chn_data.Add(pymdx.command.Volume(0x9D) )
                chn_data.Add(pymdx.command.Volume(0xA2) )
                channel.Volume = 0x7F
            
            channel.Bpm = tempo



        done = [False for _ in range(len(cr))]
        # done = [True for _ in range(len(cr))]
        # done[8] = False
        # done[9] = False
        # done[10] = False
        # done[11] = False
        # done[12] = False
        while not all(done):

            # Effects/commands
            special_cmds = [ [], [] ]

            # Special commands
            # for c, channel in enumerate(cr):

            #     if (done[c]):
            #         continue

            #     row = channel.Pattern.Row

            #     for fx in row.Fx:
            #         if 


            # if tempo change
            #   if Porta not None / if channel.Porta
            #       readadjust porta shit

            # Row data parsing
            for c, channel in enumerate(cr):

                #print("channel {} : position {}, pattern {} : row {}".format(c+1, channel.Pattern.Position, channel.Pattern.PatternId, channel.Pattern.Position) )

                if (done[c]):
                    continue

                fx_cmds = self.Read_Fx(c, channel)
                self.Read_Note(c, channel, fx_cmds)


            # Read next row into reader objects
            for c, channel in enumerate(cr):

                # Check whether channel is done
                if (done[c]):
                    continue

                pattern = channel.Pattern # Current pattern
                pattern.AdvanceRow()

                if (pattern.Row is None):
                    channel.AdvancePattern()
                    pattern = channel.Pattern # Current pattern
                    # If all patterns done/read
                    if (pattern is None):
                        done[c] = True
                        continue
                    else:
                        Dmfc_Cntr.Channels[c].Advance()
                    
        
        # Cut off any notes, if active
        for c, channel in enumerate(cr):
            if (channel.NoteActive):
                Dmfc_Cntr.Channels[c].Add(pymdx.command.Rest(TICKS_PER_ROW) )

        return


    def Read_Fx(self, c, channel):
        
        #region Effects/commands
        fx_cmds = [ [], [] ]

        row = channel.Pattern.Row

        if not (row.Instr == -1):
            if (c < 8):
                if not (row.Instr is channel.Instrument):
                    fx_cmds[0].append(pymdx.command.Tone(row.Instr))
                    channel.Instrument = row.Instr

        if not (row.Volume == -1):
            if not (row.Volume is channel.Volume):
                volume = (-(row.Volume - 0x7F)) + 0x80
                fx_cmds[0].append(pymdx.command.Volume(volume))
                channel.Volume = row.Volume

        for fx in row.Fx:
            # FX commands only for YM2151
            if (c < 8):

                # Vibrato
                if (fx.Code == 0x04):
                    if (fx.Value == 0x00 or fx.Value == -1):
                        if (channel.Vibrato):
                            fx_cmds[0].append(pymdx.command.Lfo_Pitch_Disable() )
                        channel.Vibrato = None
                    else:
                        pass

                        # if not (channel.Vibrato):
                        #     fx_cmds[0].append(pymdx.command.Lfo_Pitch_Enable() )
                        # fx_cmds[0].append(pymdx.command.Lfo_Pitch_Control(
                        #     # TODO: _cmd.py LFO commands should check if enum or int and convert to int if enum
                        #     #pymdx.command.LFO_WAVEFORM.TRIANGLE.value,
                        #     2,
                        #     GetHexDigit(1, fx.Value) * 1 * 3, # * mod_hz,
                        #     GetHexDigit(0, fx.Value) * 180
                        # ))
                        # channel.Vibrato = fx_cmds[0][-1]

                        # Speed: Set the number of steps. Step number of LFO 1/4 period (the smaller, the faster)
                        # Depth: Units are 1/64 of semitone (= D1)
                    

                # Stereo/pan
                if (fx.Code == 0x08):
                    if (fx.Value in VALUES_STEREO):
                        fx_cmds[0].append(pymdx.command.Pan(VALUES_STEREO[fx.Value]))
                    else:
                        raise Exception

                # Porta commands
                elif (fx.Code == 0x01  or  fx.Code == 0x02  or  fx.Code == 0x03):

                    if (fx.Value == 0  or  fx.Value == -1):
                        channel.Porta = None
                        channel.PortaCount = 0

                    else:
                        # TODO: The calculation is probably incorrect
                        mdx_hz = channel.Bpm / 60
                        multiplier = self.Dmfc_Cntr.REFRESH_RATE / mdx_hz
                        value = round(fx.Value * (TICKS_PER_ROW * channel.Tickspeed) * multiplier)
                        value = pymdx._misc._util.Clamp(value, -32768, 32767)

                        # TODO: Note actions are a bit bugged with portas

                        # Porta up
                        if (fx.Code == 0x01):
                            fx_cmds[0].append(pymdx.command.Portamento(value))

                        # Porta down
                        elif (fx.Code == 0x02):
                            fx_cmds[0].append(pymdx.command.Portamento(-value))

                        #channel.Porta = fx_cmds[0][-1]
                        # Porta up
                        #elif (fx.Code == 0x03):
                        #    fx_cmds[0].append(pymdx.command.Portamento(fx.Value * multiplier))
                        #    fx_cmds[1].append(pymdx.command.Note(0x80, 0))
                            # channel.new.portacounter()
        return fx_cmds


    def Read_Note(self, c, channel, fx_cmds):
        # Row Note actions


        row = channel.Pattern.Row
        chn_data = self.Dmfc_Cntr.Channels[c]
        
        # Empty
        if (row.Note == 0 and row.Octave == 0):
            # If first row in module
            if (channel.Note is None):
                chn_data.Extend(fx_cmds[0])
                chn_data.Add(pymdx.command.Rest(TICKS_PER_ROW) )
                channel.Note = chn_data.Get(-1)
            else:
                if (fx_cmds != EMPTY_FX_CMDS):
                    if (channel.NoteActive):
                        chn_data.Insert(-1, pymdx.command.Legato() ) # TODO: make this better, not use insert?
                        #mdx.DataTracks[c].Add.Legato()
                        chn_data.Extend(fx_cmds[0])
                        if (fx_cmds[1] != []):
                            chn_data.Extend(fx_cmds[1])
                        else:
                            chn_data.Add(pymdx.command.Note(channel.Note.Data, 0) )
                    else:
                        chn_data.Extend(fx_cmds[0])
                        chn_data.Add(pymdx.command.Rest(0) )
                    # Set reference to current Note/Rest
                    channel.Note = chn_data.Get(-1)

                if (c > 7):
                    if (channel.Note.Clocks + TICKS_PER_ROW > 0xFF):
                        chn_data.Add(pymdx.command.Rest(0) )
                        channel.Note = chn_data.Get(-1) ####
                        channel.NoteActive = False

                channel.Note.Clocks += TICKS_PER_ROW
                #print(channel.Note.Clocks)
        # Note data
        else:
            # Note OFF
            if (row.Note == 100):
                if (channel.NoteActive):
                    if (fx_cmds != []):
                        chn_data.Extend(fx_cmds[0])
                    chn_data.Add(pymdx.command.Rest(TICKS_PER_ROW) )
                    channel.NoteActive = False
                    channel.Note = chn_data.Get(-1)
                # Note OFF when note already OFF
                else:
                    if not (channel.Note is None):
                        channel.Note.Clocks += TICKS_PER_ROW
            # Note ON
            else:
                if (fx_cmds != []):
                    chn_data.Extend(fx_cmds[0])
                #note = row.Note + (12 * row.Octave) + 0x7D
                if (c < 8):
                    note = row.Note + (12 * row.Octave) + 0x7D
                    if (note < 0x80):

                        self.Dmfc_Cntr.Channels[c].Errors.append(locale.JSON_DATA['error']['note_below'].format(
                            channel.Position, channel.Pattern.PatternId, channel.Pattern.Position
                        ))
                    else:
                        chn_data.Add(pymdx.command.Note(note, TICKS_PER_ROW) )

                else:
                    note = row.Note + (12 * channel.SampleBank) + 0x80
                    chn_data.Add(pymdx.command.Note(note, TICKS_PER_ROW) )
                channel.NoteActive = True
                channel.Note = chn_data.Get(-1)

        return




# pattern_tick = speed / hertz
# beat_duration = pattern_tick * amount_rows_for_beat (8)
# bpm = 60 / beat_duration

def CalcTempo(tickspeed, refresh=60, basetime=1):
    row_duration  = tickspeed / refresh
    beat_duration = row_duration * 8
    bpm = (60 / beat_duration) / basetime
    return round(bpm)



def GetHexDigit(position, hex_var):
    var = hex(hex_var)[-position - 1]
    # TODO: code to control if position not too far
    return int("0x"+var, 0)


# PSEUDO CODE FOR DETUNE CALCULATION
# command == E5xx
# if xx > 80:
#   command_value = xx - 80
#   if command_value > 63:
#       command_value = 63
#
# if xx < 80:
#   command_value = 64 - (80 - xx)
#   if command_value > 0:
#       command_value = 0
#   note -= 1
