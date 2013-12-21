#!/usr/bin/python
import sys, os
from couchutil import Defaults, DocumentPreprocessor
from couchutil.DocumentUpload import DocumentUpload, ConflictResolverType
from couchutil.Utilities import props, make_enum

DocumentType = make_enum(DOCUMENT=1, DESIGN=2)

COMMAND_SYNTAX = "[design|docs]/<your_database>/<your_document>.json"
DIRECTORY_TYPE_MAP = {'design': DocumentType.DESIGN,
                      'docs': DocumentType.DOCUMENT}
class _Parameters():
    document_type = None
    database_name = None
    document_name = None

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

def build_doc_url(defaults, parameters):    
    db_url = '/'.join[defaults.dbmsURL(), parameters.database_name]
    if parameters.document_type == DocumentType.DESIGN:
        db_url += '/_design/%s'%parameters.document_name
    elif parameters.document_type == DocumentType.DOCUMENT:
        db_url += '/%s'%parameters.document_name
    return db_url    

def main():
    if len(sys.argv) != 2:
        print 'Argument error, expecting: %s' % COMMAND_SYNTAX
        sys.exit(1)
    target = sys.argv[1]
    path = os.getcwd() + target
    if not os.path.isfile(path):
        print 'Argument error, "%s" is not a file' % (path)
        sys.exit(1)
    try:                            
        defaults = Defaults.get_defaults()
        parameters = parse_parameters(target)
        doc = DocumentPreprocessor(path).get_document()
        url = build_doc_url(defaults, parameters)    
        up = DocumentUpload(ConflictResolverType.UPDATE_MERGE)    
        up.upload(url, doc)
        print 'upload done'
    except:
        print 'upload failed: %s\n\n%s', sys.exc_info()[0], sys.exc_info()[2]
        sys.exit(1)
    sys.exit(0)           
    
if __name__ == '__main__':
    main()
    