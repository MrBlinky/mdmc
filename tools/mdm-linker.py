################################################################################
#  MDM-Linker v1.02                  Edwin Blink aka  Blinky Oct 2015-Aug 2023 #
################################################################################

import sys
import os.path
import hashlib
try:
  from serial.tools.list_ports  import comports
  from serial import Serial
except:
  print("The PySerial module is required but not installed!")
  print("Use 'pip install pyserial' from the commandline to install.")
  time.sleep(3)
  sys.exit()

PATCH_DIR = 'mdm-patches'

def usage():
    print('USAGE:\n')
    print('To dump a ROM:\nmdm-linker.py -r serialPort startBank numberOfBanks romFilename\n')
    print('To flash a ROM:\nmdm-linker.py -w serialPort startBank romFilename\n')
    print('To create a MDM patched ROM:\nmdm-linker.py -c startBank romFilename\n')
    print('Example:\nmdm-linker.py -w COM1 0 space-invaders.bin\n')
    print('Note:\nWhen flashing ROMs make sure the rom size is 4K or a multiple of 4K\n')
    exit()
    
def patchFile(file):
    global buf
    f = open(PATCH_DIR + '/' + file)
    lines=f.read().splitlines()
    f.close()
    
    romtype = ''
    banksize = 4096
    for line in lines:
        line = line.upper().split('MD5:')
        if len(line) == 2:
            found = rom_md5 == line[1].lower().strip()
            if found:
                break
    if found:
        print('Found patch in ' + file)
        sys.stdout.write('Applying patch...')
        for line in lines:
            line = line.split(';')[0].strip() #remove remarks from line
            if line[2:3] == ':':
                addr=int(line[0:2],16) * banksize + (int(line[3:7],16) % banksize)
                addrOverflow = False
                for val in line.split('>')[1].split():
                    if val[0] == '+' :
                      if addrOverflow:
                        buf[addr] = int(val,16) + 1 # in case base addres < 0x0800 is used
                        addrOverflow = False
                      else:
                        bank = startbank + int(val,16)
                        buf[addr] = bank & 0xFF
                        addrOverflow = bank > 0xFF
                    else:
                        buf[addr] = int(val,16)
                        addrOverflow = False
                    addr += 1
            elif "ROMTYPE=3F" in line.upper():
              romtype = "3F"
              banksize = 2048
        if romtype == "3F": #expand tigervision rom
          lastbank = (len(buf)+2047) // 2048 - 1
          newrom = bytearray()
          for bank in range (lastbank):
            newrom += buf[bank * banksize : (bank+1) * banksize] + buf[lastbank * banksize : (lastbank+1) * banksize]
          buf = newrom
        print('Done!')
        return True
    return False

pagesize = 128

def getPageSize():
  global pagesize
  com.write([ord('x')])
  info = com.read(4)
  pagesize = 128
  if info[0] == 0x1f and (info[1] == 0xa4 or info[1] == 0xda): pagesize = 256
  elif info[0] == 0xDA and info[1] == 0x46: pagesize = 256
  
print('MDM-Linker v1.02                  Edwin Blink aka Blinky Oct 2015-Aug 2023\n')

if  (len(sys.argv) < 3):
    usage()

if (sys.argv[1] == '-c') and (len(sys.argv) == 4):  # -c startBank filename
    startbank = int(sys.argv[2])
    filename  = sys.argv[3]
    f = open(filename, 'rb')
    buf = bytearray(f.read())
    f.close()
    rom_md5 = hashlib.md5(buf).hexdigest()
    print('ROM MD5 signature: '+ rom_md5)
    print()
    print('Searching for patch file(s)...')
    patched = False
    if os.path.exists(PATCH_DIR):
        for file in os.listdir(PATCH_DIR):
            if file.endswith('.mdm'):
                if patchFile(file):
                    patched = True
                    break
    if not patched:
        print('No patch found. No ROM created.')
    else:    
      f = open(os.path.splitext(filename)[0]+'-mdm.bin','wb')
      f.write(buf)
      f.close()
      print('Patched ROM created.')
    exit()

try:
    com = serial.Serial()
    com.port = sys.argv[2]
    com.baudrate = 115200
    com.timeout = 1
    com.setDTR(False) #Prevents Arduino from resetting on opening port
    com.open()
except serial.SerialException:
    print('Error! Can\'t open serial port ' + sys.argv[2])
    exit()

if (sys.argv[1] == '-r') and (len(sys.argv) == 6) : # -r serialPort startBank numberOfBanks filename
    startbank = int(sys.argv[3])
    endbank   = startbank + int(sys.argv[4])
    filename  = sys.argv[5]
    f = open(filename, 'wb')
    sys.stdout.write("Dumping")
    getPageSize()
    for bank in range (startbank, endbank):
        for addr in range (0x0000,0x1000,pagesize):
            com.write([ord('r'), bank, addr >> 8, addr & 0xFF])
            f.write(com.read(pagesize))
        sys.stdout.write(".")
        sys.stdout.flush()
    f.close()
    print('Done!')
    exit()

if (sys.argv[1] == '-w') and (len(sys.argv) == 5):  # -w serialPort startBank filename
    startbank = int(sys.argv[3])
    filename  = sys.argv[4]
    f = open(filename, 'rb')
    buf = bytearray(f.read())
    f.close()
    rom_md5 = hashlib.md5(buf).hexdigest().lower()
    print('ROM MD5 signature: '+ rom_md5)
    print()
    print('Searching for patch file(s)...')
    patched = False
    if os.path.exists(PATCH_DIR):
        for file in os.listdir(PATCH_DIR):
            if file.endswith('.mdm'):
                if patchFile(file):
                    patched = True
                    break
    if not patched:
      print('No patch found. Using original ROM.')

    sys.stdout.write("\nFlashing")
    getPageSize()
    endbank = startbank + (len(buf) >> 12);
    for bank in range (startbank, endbank):
        for addr in range (0x0000,0x1000,pagesize):
            pos = (bank - startbank) * 0x1000 + addr
            com.write([ord('w'), bank, addr >> 8, addr & 0xFF])
            com.write(buf[pos:pos+pagesize])
            if ((com.read(1)) != b'.'):
                print(' Failed! Make sure the cart switch is in PROGram mode.')
                exit()
        sys.stdout.write(".")
        sys.stdout.flush()
    print('Done!')
    exit()

usage()
