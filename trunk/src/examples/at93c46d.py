#!/usr/bin/env python
# Example code for reading from the AT93C46D microwire EEPROM chip.

import sys
import binascii
from mpsse import *

try:
	command = sys.argv[1]
	address = int(sys.argv[2], 0)
	nbytes = data = sys.argv[3]
except:
	print "Usage: %s read  <address> <number of bytes>" % sys.argv[0]
	print "       %s write <address> <data>" % sys.argv[0]
	sys.exit(1)

def read(address, nbytes):
	global at93c
	data = ''

	for i in range(address, address+nbytes):
		# Assert CS
		at93c.Start()

		# This assumes ORG pin is low (x8 mode)
		# If ORG pin is high (x16 mode), there are only 6 address bits, not 7
		#
		# START BIT   READ COMMAND   ADDRESS BITS
		# 1           1 0            0 0 0 0 0 0 0
		at93c.WriteBits(6, 3)
		at93c.WriteBits(i, 7)

		# One dummy bit preceeds the actual data for each read operation
		dummy = at93c.ReadBits(1)
	
		# Read the byte at address i
		data += at93c.Read(1)

		# Desassert CS
		at93c.Stop()

	return data

def write(address, data):
	global at93c

	# START BIT   EWEN COMMAND   DATA BITS
	# 1           0 0            1 1 0 0 0 0 0
	at93c.Start()
	at93c.WriteBits(0x13, 5)
	at93c.WriteBits(0, 5)
	at93c.Stop()

	for i in range(0, len(data)):
		# This assumes ORG pin is low (x8 mode)
		# If ORG pin is high (x16 mode), there are only 6 address bits, not 7
		#
		# START BIT   WRITE COMMAND   ADDRESS BITS     DATA BITS
		# 1           0 1             0 0 0 0 0 0 0    0 0 0 0 0 0 0 0
		at93c.Start()
		at93c.WriteBits(5, 3)
		at93c.WriteBits(address+i, 7)
		at93c.Write(data[i])
		at93c.Stop()

		# Wait for the write to complete
		at93c.Start()
		while at93c.ReadBits(1) == 0:
			time.sleep(1)
		at93c.Stop()

# Initialize the FTDI chip
at93c = MPSSE(SPI0, ONE_MHZ, MSB)

# Chip select idles low
at93c.SetCSIdle(0)

if command == 'read':
	data = read(address, int(nbytes, 0))
	print "Read %d bytes: %s" % (len(data), binascii.hexlify(data))
elif command == 'write':
	write(address, binascii.unhexlify(data))
	print "Write complete."

# Close connection to the FTDI chip
at93c.Close()

