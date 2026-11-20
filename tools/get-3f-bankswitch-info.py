import sys
import os.path
import hashlib

def usage():
  print('USAGE:\n')
  print('USAGE: {} romfile\n'.format(sys.argv[0]))
  sys.exit()
  
if len(sys.argv) != 2:
  usage()

filename = sys.argv[1]
f = open(filename, 'rb')
buf = bytearray(f.read())
f.close()
romsize = len(buf) // 1024
print("; Name: {}".format(os.path.basename(filename)))
print(";  MD5: {}".format(hashlib.md5(buf).hexdigest()))
print("; Size: {}K".format(romsize))

print('\nBankswitch locations:')
for pos in range (0,len(buf)-2):
    #if buf[pos] in opcodes:
    if ((buf[pos] == 0xA9 and buf[pos+2] == 0x85 and buf[pos+3] == 0x3F) or
       (buf[pos] == 0xA0 and buf[pos+2] == 0x84 and buf[pos+3] == 0x3F) or
       (buf[pos] == 0xA2 and buf[pos+2] == 0x86 and buf[pos+3] == 0x3F)):
      if buf[pos] == 0xA9 : s = '{:02X}:{:04X} {:02X} {:02X} {:02X} {:02X} > AD +{:02X} 08 EA ;LDA #${:02X}; STA $1F > LDA +${:04X}; NOP'
      if buf[pos] == 0xA0 : s = '{:02X}:{:04X} {:02X} {:02X} {:02X} {:02X} > 8C +{:02X} 08 EA ;LDY #${:02X}; STY $1F > LDY +${:04X}; NOP'
      if buf[pos] == 0xA2 : s = '{:02X}:{:04X} {:02X} {:02X} {:02X} {:02X} > 8E +{:02X} 08 EA ;LDX #${:02X}; STX $1F > LDX +${:04X}; NOP'
      print(s.format(
      pos >> 12,
      0xF000 + (pos & 0x0FFF),
      buf[pos],
      buf[pos+1],
      buf[pos+2],
      buf[pos+3],
      buf[pos+1],
      buf[pos+1],
      0x800+buf[pos+1]
      ))
      #mdm patch
      #buf[pos]   = 0xAD
      #buf[pos+1] = startbank + buf[pos+1]
      #buf[pos+2] = 0x08
      #buf[pos+3] = 0xEA
      #F6 patch
      #buf[pos]   = 0x2C
      #buf[pos+1] = 0xF6 + buf[pos+1]
      #buf[pos+2] = 0xFF
      #buf[pos+3] = 0xEA

#banksize = 2048
#lastbank = (len(buf)+banksize-1) // banksize - 1
#newrom = bytearray()
#for bank in range (lastbank+1): #+1 for 16K ROM that is easier to detect by emus
#  newrom += buf[bank * banksize : (bank+1) * banksize] + buf[lastbank * banksize : (lastbank+1) * banksize]
#f = open(os.path.splitext(sys.argv[0])[0]+'-test.bin','wb')
#f.write(newrom)
#f.close()
