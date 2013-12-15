from Utilities import make_enum

DocumentUploadType = make_enum(DESIGN=1, DOCUMENT=2)

class DocumentUpload(object):
    def __init__(self, documentUploadType, documentJSONString):
        pass
    
    def upload(self, databaseURL):
        pass
    