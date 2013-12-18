from Utilities import make_enum
import sys, requests, json

DocumentUploadType = make_enum(STANDARD=1, FORCE_UPDATE=2)

COUCH_HEADER = {'Content-type':'application/json'}
class DocumentUpload(object):
    def __init__(self, databaseURL, documentUploadType=DocumentUploadType.STANDARD,
                 verbose=False):
        self._uploadType = documentUploadType
        self._databaseURL = databaseURL
        self._verbose = verbose
    
    def upload(self, documentPath, document, isRetry=False):
        url = '/'.join[self._databaseURL, documentPath]
        self._log('Uploading to %s...' % url)        
        try:
            resp = requests.post(url, data=document, headers=COUCH_HEADER)
        except requests.exceptions.ConnectionError as ex:
            self._log("Server error: %s" % (ex))
            raise ex                         
        if (not isRetry and resp.status_code == 409 and 
            self._uploadType == DocumentUploadType.FORCE_UPDATE):
            self._log("Document conflict retrying...")
            self._upload(documentPath, self._updateDoc(documentPath, document),
                         False)
        elif resp.status_code != 201:
            msg = "HTTP Request error: %s %s" % (resp.status_code, resp.text)
            self._log(msg)
            raise requests.exceptions.HTTPError(msg)
    
    def _uploadDoc(self, documentPath, document):
        pass
    
    def _log(self, str):
        if self._verbose:
            print(str)
    
    _verbose = False
    _databaseURL = None
    _uploadType = None