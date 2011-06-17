from dictshield.document import Document
from dictshield.fields import StringField


###
### Subject Models
###

class Employee(Document):
    """A model representing employee descriptions.
    """
    SOURCE_NAME = 'employees'
    source = StringField(required=True, default=SOURCE_NAME)

    ### Employee features
    full_name = StringField()
    email_name = StringField()
    position = StringField()
    comments = StringField()

    def __unicode__(self):
        return u'%s - %s' % (self.email_name, self.full_name)
