import os, os.path, json, re
from DocumentTraversal import DocumentTraversal, DocumentTraversalType

class _DesignDocumentPreprocessorState:
    cur_path = []

class DesignDocumentPreprocessor:
    def __init__(self, absolutePathToFile):
        if not os.path.isfile(absolutePathToFile):
            raise Exception('Invalid path to file: %s' % absolutePathToFile)
        self._pathToFile = absolutePathToFile
        self._fileDir = os.path.dirname(self._pathToFile)
            
    def get_document(self):
        doc = None
        with open(self._pathToFile, 'r') as f:
            doc = json.loads(f.read())
        #find includes by doing a DFS
        traversal = DocumentTraversal(DocumentTraversalType.DEPTH_FIRST, doc)
        traversal.accept(self._do_visit, self._do_pop_visit)
        #load includes from filesystem, insert into doc
        self._perform_includes(doc)
        return doc        
    
    def _do_visit(self, key, value):
        state = self._parserState
        state.cur_path.append(key)
        try:
            if self._includeParser.match(value):
                self._prepare_include(state.cur_path)
        except TypeError:
            pass                                    
                        
    def _do_pop_visit(self, key, value):
        self._parserState.cur_path.pop()
    
    def _prepare_include(self, path):
        self._includes.append(path[:])
        
    def _perform_includes(self, doc):
        for inc in self._includes:
            included_file = self._get_included_file(inc)            
            doc_ptr = doc
            for pt in inc:
                if isinstance(doc_ptr[pt], basestring):
                    doc_ptr[pt] = included_file
                else:
                    doc_ptr = doc_ptr[pt]
    
    def _get_included_file(self, inc):        
        pathToInclude = '/'.join(inc[:-1])
        fullPath = self._fileDir + '/' + pathToInclude + '/' + inc[-1] + '.json'
        if not os.path.isfile(fullPath):
            raise Exception('Cannot include file: %s' % fullPath)
        with open(fullPath, 'r') as f:
            return f.read()      

    _parserState = _DesignDocumentPreprocessorState()
    _pathToFile = None
    _fileDir = None
    _includeParser = re.compile(r"\s*#.*$")
    _includes = []
    
if __name__ == "__main__":
    filePath = '/home/mike/workspace/couchdb-carplots/design/carplots/plots.json'
    preprocessor = DesignDocumentPreprocessor(filePath)
    doc = preprocessor.get_document()