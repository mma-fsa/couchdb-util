from Utilities import make_enum
import sys, requests, json

ConflictResolverType = make_enum(FAIL=1, UPDATE_MERGE=2, UPDATE_OVERWRITE=3)

COUCH_HEADER = {'Content-type':'application/json'}
MAX_RESOLVE_TRIES = 10
class DocumentUpload(object):
    def __init__(self, conflictResolver=ConflictResolverType.FAIL,
                 verbose=False):
        self._resolveType = conflictResolver
        self._resolveCount = 0
        self._verbose = verbose
        self._is_disposed = False
    
    def upload(self, url, document):
        if self._is_disposed:            
            raise Exception("Document already complete")                
        while not self._is_disposed:                
            try:
                self._log('Uploading to %s...' % url)
                resp = requests.post(url, data=document, headers=COUCH_HEADER)
            except requests.exceptions.ConnectionError as ex:
                self._log("Server error: %s" % (ex))
                raise ex                                         
            if (resp.status_code == 409 and
                self._uploadType != ConflictResolverType.FAIL and
                self._resolveCount < MAX_RESOLVE_TRIES):            
                self._log("Resolving document conflict...")
                self._resolveCount += 1
                self._resolveConflict(url, document)                        
            elif resp.status_code != 201:
                msg = "HTTP Request error: %s %s" % (resp.status_code, resp.text)
                self._log(msg)
                self._is_disposed = True
                raise requests.exceptions.HTTPError(msg)
            else:
                self._is_disposed = True
    
    def _resolveConflict(self, url, document):        
        try:
            current_document = json.loads(requests.get(url))
        except Exception as ex:
            pass         
        if self._resolveType == ConflictResolverType.UPDATE_MERGE:
            #merge properties not present in document
            for k,v in current_document.iteritems():
                document = document.get(k, v)
            
        elif self._resolveType == ConflictResolverType.UPDATE_OVERWRITE:
            document["id"] = current_document["id"]
    
    
    def _recursive_merge(self, merge_from, merge_into):
        for k,v in merge_from.iteritems():
            if isinstance(v, dict):
                merge_into[k] = merge_into.get(k, dict())
                if isinstance(merge_into[k], dict):
                    self._recursive_merge(v, merge_into[k])
            else:
                merge_into[k] = merge_into.get(k, v)
    
    def _upload(self, documentPath, document):
        pass
    
    def _log(self, str):
        if self._verbose:
            print(str)
    
    _verbose = False
    _databaseURL = None
    _resolveType = None
    _resolveCount = 0