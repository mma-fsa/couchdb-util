import Utilities, sys

DocumentTraversalType = Utilities.make_enum(DEPTH_FIRST=1, BREADTH_FIRST=2) 

class DocumentTraversalVistorException(Exception):
     def __init__(self, message):
        Exception.__init__(self, message)

class DocumentTraversal():
    def __init__(self, documentTraversalType, document):
        self._traversal = documentTraversalType
        self._document = document
        
    def accept(self, visit, pop_visit=lambda k,v: True):
        """ Performs the dictionary traversal specified in the constructor,
            performing callbacks in visit(key, value) and pop_visit(key, value)
            :param visit: called when the node is first encountered, BEFORE
                it's children have been visited.
            :param pop_visit: (optional) called AFTER all the node's children 
                have been visited, when the node's stackframe is being popped.
        """
        if self._traversal == DocumentTraversalType.DEPTH_FIRST:
            self._depth_first_search(None, self._document, visit, pop_visit)
        elif self._traversal == DocumentTraversalType.BREADTH_FIRST:
            self._breadth_first_search(None, self._document, visit, pop_visit, [])
            
    def _depth_first_search(self, currentKey, currentValue, visit, pop_visit):
        try:
            for k, v in currentValue.iteritems():
                try:     
                    visit(k, v)
                except Exception as e:
                    raise DocumentTraversalVistorException("visit threw exception."),\
                        None, sys.exc_info()[2]
                self._depth_first_search(k, v, visit, pop_visit)                
        except (AttributeError, TypeError) as e: 
            pass
        #don't call pop_visit for root node (currKey == None)
        if currentKey != None:
            try:
                pop_visit(currentKey, currentValue)
            except Exception as e:
                raise DocumentTraversalVistorException("pop_visit threw exception."), None, sys.exc_info()[2]
    
    def _breadth_first_search(self, currentKey, currentValue, visit, pop_visit, q):
        try:
            for k,v in currentValue.iteritems():                
                try:     
                    visit(k, v)
                except Exception as e:
                    raise DocumentTraversalVistorException("visit threw exception."), None, sys.exc_info()[2]
                q.append((k,v))
        except (AttributeError, TypeError): 
            pass
        if len(q) > 0:
            next = q.pop(0)
            self._breadth_first_search(next[0], next[1], visit, q)        
        #don't call pop_visit for root node (currKey == None)
        if currentKey != None:
            try:
                pop_visit(currentKey, currentValue)
            except Exception as e:
                raise DocumentTraversalVistorException("pop_visit threw exception."), None, sys.exc_info()[2]
        
    _document = None
    _traversal = None
