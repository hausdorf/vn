from arbre.timestamping import MillisecondField

from dictshield.document import Document
from dictshield.fields import (StringField,
                               ObjectIdField,
                               IntField)


###
### Calculation Models
###

class BaseAnalytic(Document):
    """Basic model for storing calculation values. Each `BaseAnalytic` has a 1:1
    mapping with a `BaseSubject`.
    """
    SOURCE_NAME = 'baseanalytic'
    source = StringField(required=True, default=SOURCE_NAME)

    ### Subject Info (can by anything with an ObjectId)
    subject_id = ObjectIdField()
    subject_name = StringField(required=True)

    ### Analytic Values
    analytic_name = StringField(required=True)
    created_at = MillisecondField(required=True, default=0)
    content_score = IntField()
    context_score = IntField()

    def __unicode__(self):
        return u'%s - %s - %s' % (self.name, self.employee, self.value)

