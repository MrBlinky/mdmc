import sys
import os.path
import hashlib

opcodes = [0x0C,0x0D,0x0E,0x1C,0x20,0x2C,0x2D,0x2E,0x3C,0x4C,0x4D,0x4E,0x5C,0x6D,0x6E,0x7C,0x8C,0x8D,0x8E,0xAC,0xAD,0xAE,0xCC,0xCD,0xCE,0xDC,0xEC,0xED,0xEE,0xFC]
mnemonics = ['NOP','ORA','ASL','NOP','JSR','BIT','AND','ROL','NOP','JMP','EOR','LSR','NOP','ADC','ROR','NOP','STY','STA','STX','LDY','LDA','LDX','CPY','CMP','DEC','NOP','CPX','SBC','INC','NOP']

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
if romsize == 8:
  minbank = 0xf8
  maxbank = 0xf9
elif romsize == 16:
  minbank = 0xf6
  maxbank = 0xf9
elif romsize == 32:
  minbank = 0xf4
  maxbank = 0xfb
elif romsize == 64:
  minbank = 0xf0
  maxbank = 0xf0

print('\nBankswitch locations:')
for pos in range (0,len(buf)-2):
    if buf[pos] in opcodes:
        if (buf[pos+2] & 0x1F) == 0x1F:
          if (buf[pos+1] >= minbank) and (buf[pos+1] <= maxbank):
            print('{:02X}:{:04X} {:02X} {:02X} {:02X} > {:02X} +{:02X} {:02X} ;{} {:02X}{:02X} > {} {:04X}'.format(
            pos >> 12,
            0xF000 + (pos & 0x0FFF), 
            buf[pos], 
            buf[pos+1], 
            buf[pos+2], 
            buf[pos], 
            buf[pos+1] - minbank, 
            0x08,
            mnemonics[opcodes.index(buf[pos])],
            buf[pos+2],
            buf[pos+1],
            mnemonics[opcodes.index(buf[pos])],
            0x800 + buf[pos+1] - minbank
            ))
    elif (buf[pos] == 0xbd) and ((buf[pos+2] & 0x1F) == 0x1F) and (buf[pos+1] >= minbank-1) and (buf[pos+1] <= maxbank):
            print('{:02X}:{:04X} {:02X} {:02X} {:02X} > ;LDA {:02X}{:02X},X'.format(pos >> 12, 0xF000 + (pos & 0x0FFF), buf[pos], buf[pos+1], buf[pos+2], buf[pos+2], buf[pos+1]))