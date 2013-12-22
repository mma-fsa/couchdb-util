#!/usr/bin/python
import sys, os, re, json
from couchutil import Defaults
from couchutil.DocumentPreprocessor import DocumentPreprocessor
from couchutil.DocumentUpload import DocumentUpload, ConflictResolverType
from couchutil.Utilities import props, make_enum

DocumentType = make_enum(DOCUMENT=1, DESIGN=2)

COMMAND_SYNTAX = "[design|docs]/<your_database>/<your_document>"
DIRECTORY_TYPE_MAP = {'design': DocumentType.DESIGN,
                      'docs': DocumentType.DOCUMENT}
EXTENSION_RE = re.compile(r"^(.*?)(\..*)?$")
class _Parameters():
    document_type = None
    document_name = None

def parse_parameters(targetStr):
    targetParts = targetStr.split('/')
    params = _Parameters()
    #skip until a valid document type is hit, then assume a db name and
    #document name follow immediately after
    for pt in targetParts:
        if not params.document_type:            
            params.document_type = DIRECTORY_TYPE_MAP.get(pt, None)
        elif not params.document_name:
            params.document_name = EXTENSION_RE.match(pt).group(1)
    for propName, val in props(params):
        if not val:
            raise Exception('Failed to parse parameter from argument: %s' % propName)
    return params

def build_doc_url(defaults, parameters):    
    db_url = defaults.databaseURL()
    if parameters.document_type == DocumentType.DESIGN:
        db_url += '/_design/%s'%parameters.document_name
    elif parameters.document_type == DocumentType.DOCUMENT:
        db_url += '/%s'%parameters.document_name
    return db_url

def update_doc_rev(path, revision):
    with open(path, 'r') as f:
        doc = json.loads(f.read())
    doc["_rev"] = revision
    with open(path, 'w') as f:
			f.write(json.dumps(doc, sort_keys=True, indent=2, separators=(',',':')))

def main():
    if len(sys.argv) != 2:
        print 'Argument error, expecting: %s' % COMMAND_SYNTAX
        sys.exit(1)
    target = sys.argv[1]
    path = '/'.join([os.getcwd(), target])
    if not os.path.isfile(path):
        print 'Argument error, "%s" is not a file' % (path)
        sys.exit(1)
    try:                            
        defaults = Defaults.get_defaults()
        parameters = parse_parameters(target)
        doc = DocumentPreprocessor(path).get_document()
        url = build_doc_url(defaults, parameters)    
        up = DocumentUpload(ConflictResolverType.UPDATE_OVERWRITE, verbose=True)            
        updated_doc = up.upload(url, doc, clone_doc=False)
        update_doc_rev(path, updated_doc["_rev"])        
        print 'upload done: %s' % updated_doc["_rev"]
        
    except Exception as ex:
        print 'upload failed: %s'% ex     
        sys.exit(1)
    sys.exit(0)           
    
if __name__ == '__main__':
    main()
    
