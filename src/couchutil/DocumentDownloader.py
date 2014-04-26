import requests, json

COUCH_HEADER = {'Content-type':'application/json'}
class DocumentDownloader(object):
    def __init__(self, auth=None,
                 verbose=False):
        self._auth = auth
        self._verbose = verbose
    
    def download(self, url):
        resp = self._download(url)
        if resp.status_code != 200:
            msg = "HTTP Request error: %s %s" % (resp.status_code, resp.text)
            self._log(msg)
            raise requests.exceptions.HTTPError(msg)
        return json.loads(resp.text)
    
    def _download(self, url):
        self._log('Downloading from %s' % url)
        try:
            resp = requests.get(url,
                                headers=COUCH_HEADER,
                                auth=self._auth)
        except requests.exceptions.ConnectionError as ex:
            self._log("Server error: %s" % (ex))
            raise ex        
        return resp
         
    def _log(self, str):
        if self._verbose:
            print(str)