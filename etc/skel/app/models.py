from arbre.timestamping import MillisecondField

from dictshield.document import Document
from dictshield.fields import (IntField,
                               StringField,
                               ObjectIdField)

class SampleModel(Document):
    """Maps the structure generated from Python's email module into a document
    by extending `Email`.
    """
    some_string = StringField()
    some_number = IntField()
    timestamp = MillisecondField()

    def foo(self):
        print 'foo'
