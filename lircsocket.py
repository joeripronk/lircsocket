#!/usr/bin/python
import sys
import os
import argparse
import socket
import select
import signal

server_address = '/run/lirc/lircd'
eventlircd_address = '/run/lirc/eventlircd'
lircd_address = '/run/lirc/lircd0'
size=4096
timeout=1000
debug=False
verbose=False

parser = argparse.ArgumentParser(description='interconnect eventlircd and lircd to get lircd (ir blasting) and eventlircd to work over a single socket.')
parser.add_argument('-e','--eventlircd',help='socket for eventlircd')
parser.add_argument('-l','--lircd',help='socket for lircd')
parser.add_argument('-s','--socket',help='listening socket for me')
parser.add_argument('-v','--verbose',help='be a bit verbose',action='store_true',default=False)
parser.add_argument('-d','--debug',help='debug communication',action='store_true',default=False)
args = parser.parse_args()
if args.eventlircd:
  eventlircd_address=args.eventlircd
if args.lircd:
  lircd_address=args.lircd
if args.socket:
  server_address=args.socket
if args.socket:
  server_address=args.socket
if args.debug:
  debug=True
if args.verbose:
  verbose=True
del args
del parser
eventlircd=None
lircd = None
def cleanup():
  if verbose:
    print "server shutdown"
  server.close() 
  if not lircd is None:
    lircd.close()
  if not lircd is None:
    eventlircd.close()
def signal_shutdown(signal, frame):
  cleanup()
  sys.exit(0)

try:
  os.unlink(server_address)
except OSError:
  if os.path.exists(server_address):
    raise
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
signal.signal(signal.SIGINT, signal_shutdown)
signal.signal(signal.SIGTERM, signal_shutdown)
signal.signal(signal.SIGQUIT, signal_shutdown)
server.bind(server_address)
if verbose:
  print 'Listening on %s' % server_address
server.listen(1)
server.setblocking(0)
input = [server]
output = []
running = 1
while running:
  if eventlircd is None:  
    eventlircd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
      eventlircd.connect(eventlircd_address)
      input.append(eventlircd)
      if verbose:
        print 'connected to %s' % eventlircd_address
    except socket.error, msg:
      if verbose:
        print >>sys.stderr, '%s: %s' % (eventlircd_address,msg)
      eventlircd=None

  if lircd is None:  
    lircd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
      lircd.connect(lircd_address)
      input.append(lircd)
      if verbose:
        print 'connected to lircd %s' % lircd_address
    except socket.error, msg:
      if verbose:
        print >>sys.stderr, '%s: %s' % (lircd_address,msg)
      lircd=None

  # process sockets
  inputready,outputready,exceptready = select.select(input,[],[],timeout)
  for s in inputready:
    if s == server:
    # handle the server socket
      if verbose:
        print "new connection on %s" % server_address
      client, address = server.accept()
      input.append(client)
      output.append(client)
    elif s == lircd:
      if debug:
        print "reading from lircd"
      try:
        data = s.recv(size)
      except:
        print "failed to receive from lircd:"
        data=None
      if data:
        if debug:
          print "lircd: '%s'" % data
        for o in output:
          try:
            o.send(data)
          except:
            if verbose:
              print >>sys.stderr, 'failed to send data to client'
            try:
              input.remove(o)
            except:
              print >>sys.stderr, 'could not cleanup input'
            try:
              o.close()
            except:
              print >>sys.stderr, 'could not close socket'
            try:
              output.remove(o)
            except:
              print >>sys.stderr, 'could not cleanup output'
      else:
        if verbose:
          print "connection to %s lost" % lircd_address
        s.close()
        input.remove(s)
        lircd=None
    elif s == eventlircd:
      if debug:
        print "reading from eventlircd"
      try:
        data = s.recv(size)
      except:
        data=None
      if data:
        if debug:
          print "eventlircd: '%s'" % data
        for o in output:
          try:
            o.send(data)
          except:
            if verbose:
              print >>sys.stderr, 'failed to send data to client'
            output.remove(o)
            input.remove(o)
            s.close()
      else:
        if verbose:
          print "connection to %s lost" % eventlircd_address
        s.close()
        input.remove(s)
        eventlircd=None
    else:
      # handle all other sockets
      try:
        if debug:
          print "reading from client"
        data = s.recv(size)
      except:
        data = None
      if data:
        if debug:
          print "client: '%s'" % data
        if lircd:
          try:
            lircd.send(data)
            if debug:
              print "sent to lircd"
            data=lircd.recv(size)
            if debug:
              print "read from lircd '%s'" % data
          except:
            print >>sys.stderr, 'failed to send data to lircd'
            try:
              lircd.close()
            except:
              if debug:
                print "cannot close lircd"
            lircd=None
            data=None
          try:
            s.send(data)
            if debug:
              print "sent to client '%s'" % data
          except:
            print "cannot sent answer to client '%s'" % data
      else:
        if verbose:
          print "client disconnected"
	try:
          s.close()
        except:
          if debug:
            print "cannot close socket"
        try:
          input.remove(s)
        except:
          if debug:
            print "cannot remove input"
        try:
          output.remove(s)
        except:
          if debug:
            print "cannot remove output"
