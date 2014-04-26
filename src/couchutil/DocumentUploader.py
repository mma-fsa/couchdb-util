from Utilities import make_enum
import sys, requests, json

ConflictResolverType = make_enum(FAIL=1, UPDATE_MERGE=2, UPDATE_OVERWRITE=3)

COUCH_HEADER = {'Content-type':'application/json'}
MAX_RESOLVE_TRIES = 10
class DocumentUploader(object):
    def __init__(self, conflictResolver=ConflictResolverType.FAIL,
                 auth=None,
                 verbose=False):
        self._resolveType = conflictResolver
        self._resolveCount = 0
        self._verbose = verbose
        self._isDisposed = False
        self._auth = auth
    
    def upload(self, url, original_document, clone_doc=True):
        if self._isDisposed:            
            raise Exception("Document already complete")
        document = original_document if not clone_doc\
            else json.loads(json.dumps(original_document))         
        while not self._isDisposed:                
            resp = self._upload(url, document)                           
            if (resp.status_code == 409 and
                self._resolveType != ConflictResolverType.FAIL and
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
        json_resp = json.loads(resp.text)
        document["_rev"] = json_resp["rev"]
        return document
    
    def _resolve_conflict(self, url, local_document):        
        try:
            server_document = json.loads(requests.get(url).text)
        except Exception as ex:
            pass                    
        if self._resolveType == ConflictResolverType.UPDATE_MERGE:
            #add properties into local_document.  If a property exists in the
            #server_document, but not in the local_document, then it is added,
            #otherwise the property in the local_document is used.                               
            self._deep_merge(local_document, server_document)                    
        local_document["_rev"] = server_document["_rev"]
    
    def _deep_merge(self, merge_into, merge_from):
        for k,v in merge_from.iteritems():
            if isinstance(v, dict):
                merge_into[k] = merge_into.get(k, dict())
                if isinstance(merge_into[k], dict):
                    self._deep_merge(merge_into[k], v)
            else:
                merge_into[k] = merge_into.get(k, v)
    
    def _upload(self, url, document):
        self._log('Uploading to %s...' % url)
        try:
            resp = requests.put(url, 
                                data=json.dumps(document), 
                                headers=COUCH_HEADER, 
                                auth=self._auth)
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