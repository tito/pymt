#!/usr/bin/env python
import ogg
import ogg.vorbis

import struct
import array

class WaveReader:
    def __init__(self, filename):
        self.filename = filename
        self._f = open(filename, 'rb')
        self._read_header()

    def _read_header(self):
        f = self._f
        f.seek(12) #skip RIFF chunk, go to fmt chunk
        if f.read(3) != 'fmt':
            raise RuntimeError, "Bad chunk"
        f.seek(20)
        data = f.read(16)

        # format, channels, sample rate, Bpsec, Bpsample, bpsample
        res = struct.unpack('<HHIIHH', data)
        (self.format, self.channels,
         self.rate, self.bytespersec,
         self.bytespersample, self.bitspersample) = res

        # read data header
        data = f.read(8)
        if data[:4] != 'data':
            raise RuntimError, "Error in wave; expected 'data', got %s" % data
        (self.datalen, ) = struct.unpack('<I', data[4:])
        self.samples = self.datalen / (self.channels * 2)

        # now we're ready to read data

    def read_stereo(self, samples):
        assert(self.channels == 2)
        inbuff = self._f.read(samples * 4)

        if not inbuff: return
        samples = len(inbuff) / 4

        tempbuff = array.array('i')

        # Andrew reminds himself what a WAV looks like...
        # |     sample k        |    sample k+1            |
        # | short0_k | short1_k | short 0_k+1 | short1_k+1 |

        struct_string = '<' + 'hh' * samples
        tempbuff = struct.unpack(struct_string, inbuff)
        return self._splitvalues(tempbuff)

    def _splitvalues(self, buff):
        fact = 1/32768.0
        outbuf0 = array.array('f')
        outbuf1 = array.array('f')
        
        for x in range(len(buff) / 2):
            val0, val1 = buff[2 * x : 2 * x + 2]
            outbuf0.append(val0 * fact)
            outbuf1.append(val1 * fact)

        return outbuf0.tostring(), outbuf1.tostring()

class NumericWaveReader(WaveReader):
    """This doesn't appear to be any faster, but I wrote it anyway"""
    
    def _splitvalues(self, buff):
        import Numeric
        buff = Numeric.array(buff)
        
        fact = 1/32768.0
        samples = len(buff) / 2
        outbuf0 = buff[::2]
        outbuf1 = buff[1::2]

        outbuf0 = outbuf0 * fact
        outbuf1 = outbuf1 * fact

        return outbuf0.tostring(), outbuf1.tostring()


def main():
    vi = ogg.vorbis.VorbisInfo(quality=0.1)
    vc = ogg.vorbis.VorbisComment()

    vd = vi.analysis_init()
    vb = vd.create_block()
    (header, header_com, header_code) = vd.headerout(vc)
    
    os = ogg.OggStreamState(5)
    
    os.packetin(header)
    os.packetin(header_com)
    os.packetin(header_code)
    
    fout = open('out.ogg', 'wb')
    inwav = WaveReader('in.wav')

    og = os.flush()
    while og:
        og.writeout(fout)
        og = os.flush()

    packets = 0
    samples = 0
    
    eos = 0
    while not eos:
        #returns a tuple of strings representing arrays of floats
        channel_data = inwav.read_stereo(2048)
        if not channel_data:
            print "No data"
            vd.write(None) # didn't read any data
        else:
            apply(vd.write, channel_data) 

            samples = samples + len(channel_data[0]) / 4

        vb = vd.blockout()
        while vb:
            packets = packets + 1

            # print percent of samples read;
            # note that this is currently wrong (off by factor of 2)
            # not sure why, but it shouldn't be too big a deal
            if packets % 10 == 0: 
                print "%0.2f" % (100.0 * samples / inwav.samples)
            
            vb.analysis()
            vb.addblock()
            
            op = vd.bitrate_flushpacket()
            while op:
                os.packetin(op)
                while not eos:
                    og = os.pageout()
                    if not og:
                        break
                    og.writeout(fout)
                    eos = og.eos()
                op = vd.bitrate_flushpacket()
            
            vb = vd.blockout()
    
    vd.close()
    fout.close()

if __name__ == '__main__':
    main()





