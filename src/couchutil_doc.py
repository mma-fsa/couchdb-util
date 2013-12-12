#!/usr/bin/python
import sys, os, re
from couchutil import Defaults
from os.path import expanduser

COMMAND_SYNTAX = "[design|docs]/<your_database>/<your_document>.json"
GLOBAL_DEFAULTS_FILE = '%s/.couchutil'%expanduser("~")
LOCAL_DEFAULTS_FILE = '%s/'%os.getcwd()

def get_defaults():
    defaults = None
    nextDefaultsFile = GLOBAL_DEFAULTS_FILE
    try:
        #read global defaults, then the local
        defaults = Defaults(nextDefaultsFile)
        nextDefaultsFile = LOCAL_DEFAULTS_FILE
        defaults.process(nextDefaultsFile)
    except IOError as ex:
        print "Unable to read defaults '%s' : "%(nextDefaultsFile, ex.message)
        sys.exit(1)
    except Defaults.InvalidDefaultsException as ex:
        print "Error in defaults '%s': %s"%(nextDefaultsFile, ex.message)
        sys.exit(1)
    except:
        print 'Error: %s' % sys.exc_info()[0]
        sys.exit(1)
    return defaults

def main():
    if len(sys.argv) != 2:
        print 'Argument error, expecting: %s' % COMMAND_SYNTAX
        sys.exit(1)    
    
    defaults = get_defaults()
    target = sys.argv[1]

    #TODO: os.path.walk
    
if __name__ == '__main__':
    main()