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
        self._isDisposed = False
    
    def upload(self, url, document):
        if self._isDisposed:            
            raise Exception("Document already complete")                
        while not self._isDisposed:                
            resp = self._upload(url, document)                           
            if (resp.status_code == 409 and
                self._uploadType != ConflictResolverType.FAIL and
                self._resolveCount < MAX_RESOLVE_TRIES):            
                self._log("Resolving document conflict...")
                self._resolveCount += 1
                self._resolve_conflict(url, document)                        
            elif resp.status_code != 201:
                msg = "HTTP Request error: %s %s" % (resp.status_code, resp.text)
                self._log(msg)
                self._isDisposed = True
                raise requests.exceptions.HTTPError(msg)
            else:
                self._isDisposed = True
    
    def _resolve_conflict(self, url, local_document):        
        try:
            server_document = json.loads(requests.get(url))
        except Exception as ex:
            pass                    
        if self._resolveType == ConflictResolverType.UPDATE_MERGE:
            #add properties into local_document.  If a property exists in the
            #server_document, but not in the local_document, then it is added,
            #otherwise the property in the local_document is used.                               
            self._deep_merge(local_document, server_document)                    
        local_document["id"] = server_document["id"]
    
    def _deep_merge(self, merge_into, merge_from):
        for k,v in merge_from.iteritems():
            if isinstance(v, dict):
                merge_into[k] = merge_into.get(k, dict())
                if isinstance(merge_into[k], dict):
                    self._recursive_merge(merge_into[k], v)
            else:
                merge_into[k] = merge_into.get(k, v)
    
    def _upload(self, url, document):
        self._log('Uploading to %s...' % url)
        try:
            resp = requests.post(url, data=document, headers=COUCH_HEADER)
        except requests.exceptions.ConnectionError as ex:
            self._log("Server error: %s" % (ex))
            raise ex
        return resp       
    
    def _log(self, str):
        if self._verbose:
            print(str)
    
    _verbose = False
    _databaseURL = None
    _resolveType = None
    _resolveCount = 0