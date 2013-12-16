#!/usr/bin/python
import sys, os, re
from os.path import expanduser
from couchutil import Defaults, DesignDocumentPreprocessor, DocumentUpload
from couchutil.Utilities import props

COMMAND_SYNTAX = "[design|docs]/<your_database>/<your_document>.json"
GLOBAL_DEFAULTS_FILE = '%s/.couchutil'%expanduser("~")
LOCAL_DEFAULTS_FILE = '%s/'%os.getcwd()
DIRECTORY_TYPE_MAP = {'design': DocumentUpload.DocumentUploadType.DESIGN,
                      'docs': DocumentUpload.DocumentUploadType.DOCUMENT,}

class _Parameters():
    document_type = None
    database_name = None
    document_name = None

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

def parse_parameters(targetStr):
    targetParts = targetStr.split('/')
    params = _Parameters()
    #skip until a valid document type is hit, then assume a db name and
    #document name follow immediately after
    for pt in targetParts:
        if not params.document_type:            
            params.document_type = DIRECTORY_TYPE_MAP.get(pt, None)
        elif not params.database_name:
            params.database_name = pt
        elif not params.document_name:
            params.document_name = pt
    for propName, val in props(params):
        if not val:
            raise Exception('Failed to parse parameter from argument: %s' % propName)

def build_design_doc_url():
    pass

def main():
    if len(sys.argv) != 2:
        print 'Argument error, expecting: %s' % COMMAND_SYNTAX
        sys.exit(1)            
    defaults = get_defaults()
    target = sys.argv[1]
    path = os.getcwd() + target
    if not os.path.isfile(path):
        print 'Argument error, "%s" is not a file' % (path)
        sys.exit(1)
    parameters = parse_parameters(target)
    doc_url = '/'.join[defaults.dbmsURL + '/' + parameters.database_name,
    if parameters.document_type == DocumentUpload.DocumentUploaparameters.document_type, document)
        
        documentUploader.upload()
    else:
        print 'Operation not implemented'
        sys.exit(1)
    
    print 'upload done'
    sys.exit(0)           
    
if __name__ == '__main__':
    main()
    