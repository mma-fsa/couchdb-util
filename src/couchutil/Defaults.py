import re, sys
from os.path import expanduser
from os import getcwd

GLOBAL_DEFAULTS_FILE = '%s/.couchutil'%expanduser("~")
LOCAL_DEFAULTS_FILE = '%s/'%getcwd()

class InvalidDefaultsException(Exception):
    def __init__(self, message):
        super(InvalidDefaultsException, self).__init__(message)
        self.message = message

class Defaults:
    
    def __init__(self, defaultsFile=None):
        self._init_parsers()
        if defaultsFile != None:
            self.process(defaultsFile)        
    
    def databaseURL(self, overrides={}):
        return "%(protocol)s://%(userpart)s%(url)s/%(database)s"%\
            self._merge_args(self.__defaultProperties, overrides)
    
    def dbmsURL(self, overrides={}):
        return "%(protocol)s://%(userpart)s%(url)s"%\
            self._merge_args(self.__defaultProperties, overrides)
    
    def process(self, defaultsFile):        
        with open(defaultsFile, 'r') as f:
            for line in f:                
                if self.__whitespace.match(line) or\
                     self.__comment.match(line):
                    continue
                processed = False
                for attr, parser in self.__propertyParsers.iteritems():
                    m = parser.match(line) 
                    if m:
                        self.__defaultProperties[attr] = m.group(1)
                        processed = True
                        break
                if not processed:
                    raise InvalidDefaultsException("invalid config line in %s: %s"%\
                                                       (defaultsFile, line))
                    
    def _init_parsers(self):
        for k in self.__defaultProperties:
            self.__propertyParsers[k] = self._make_parser(k)
    
    def _make_parser(self, propertyName):
        return re.compile(r"\s*" + propertyName + "\s*=\s*(.*?)\s*$")
    
    def _merge_args(self, base, override):
        args = dict(base.items() + override.items())
        userpart = args['user'] if args['user'].strip() != '' else ''
        userpart+= ":%s"%args['pass'] if args['pass'].strip() != '' and\
            userpart != '' else ''
        args['userpart'] = "%s@"%userpart if userpart != '' else userpart
        return args
                        
    __defaultDatabaseURL = ''
    __defaultProperties = {'user':'', 'pass':'', 'protocol':'http', 'url':'localhost:5984', 'database':''}
    __propertyParsers = {}
    __comment = re.compile(r"^\s*\#.*$")
    __whitespace = re.compile(r"^\s*$")

def get_defaults():
    defaults = None
    nextDefaultsFile = GLOBAL_DEFAULTS_FILE
    try:
        #read global defaults, then the local
        defaults = Defaults(nextDefaultsFile)
        nextDefaultsFile = LOCAL_DEFAULTS_FILE
        defaults.process(nextDefaultsFile)
    except IOError as ex:
        raise InvalidDefaultsException("Unable to read defaults '%s' : "
                                       %(nextDefaultsFile, ex.message))
    except Defaults.InvalidDefaultsException as ex:
        raise InvalidDefaultsException("Error in defaults '%s': %s"
                                       %(nextDefaultsFile, ex.message))
    except:
        raise InvalidDefaultsException('Error: %s' % sys.exc_info()[0])

    return defaults

###############
## TEST CASE ##
###############
def doTests():
    print 'tests started...'
    try:
        defaults = Defaults()
        url = defaults.databaseURL()
        
        print 'tests passed'
    finally:
        print 'done' 

if __name__ == "__main__":
    doTests()