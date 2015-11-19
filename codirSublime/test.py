# import sys, os
# path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, path + '/socketIO')
# from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace

# def on_aaa_response(*args):
#     print('on_aaa_response', args)

# socketIO = SocketIO('128.164.26.120', 8603, LoggingNamespace)
# socketIO.on('test', on_aaa_response)
# socketIO.emit('live-file-connection')
# socketIO.wait(seconds=1)
import os

print (os.path.dirname(os.path.realpath(__file__)))