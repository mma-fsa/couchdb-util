#!/usr/bin/python
import sys, os, re, json, argparse

from couchutil import Defaults
from couchutil.DocumentPreprocessor import DocumentPreprocessor
from couchutil.DocumentUploader import DocumentUploader, ConflictResolverType
from couchutil.DocumentDownloader import DocumentDownloader

class _Parameters():
    document_type = None
    document_name = None

def build_url(defaults, doc_path):
    _, filename = os.path.split(doc_path)
    docname = os.path.splitext(filename)[0]
    db_url = defaults.database_url
    return  '%s/_design/%s' % (db_url,docname)    

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Couchdb design document preprocessor.')
    parser.add_argument('design_doc', nargs=1)
    parser.add_argument('--config', nargs='?', dest='config', default=None)
    parser.add_argument('--force', nargs='?', const=True, default=False)    
    parser.add_argument('--merge', nargs='?', const=True, default=False)
    args = parser.parse_args()    
    
    # read defaults from '.couchutil' config files
    defaults = Defaults.get_defaults(args.config)
    arg_design_doc = args.design_doc[0]
    
    # read design document
    if os.path.isfile(arg_design_doc):
        design_doc_abs_path = os.path.abspath(arg_design_doc)
        pp_doc = DocumentPreprocessor(design_doc_abs_path).get_document()        
    else:
        raise IOError('Design document not found')
    
    conflict_strategy = ConflictResolverType.FAIL
    if args.force:
        conflict_strategy = ConflictResolverType.UPDATE_OVERWRITE
    elif args.merge:
        conflict_strategy = ConflictResolverType.UPDATE_MERGE
    
    # do the update    
    uploader = DocumentUploader(conflict_strategy,
                              defaults.auth)
    design_doc_url = build_url(defaults, arg_design_doc)
    uploader.upload(design_doc_url, pp_doc)    
    
    # get the updated doc, write it back to disk
    downloader = DocumentDownloader(defaults.auth)
    updated_design_doc = downloader.download(design_doc_url)    
    with open(design_doc_abs_path, 'w') as f:
        f.write(json.dumps(updated_design_doc, 
                           sort_keys=True, 
                           indent=2, 
                           separators=(',',':')))
    
    sys.exit(0)           
    
if __name__ == '__main__':
    main()
    
