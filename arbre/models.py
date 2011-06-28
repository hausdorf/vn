from arbre.timestamping import MillisecondField

from dictshield.document import Document
from dictshield.fields import (StringField,
                               ObjectIdField,
                               IntField,
                               EmailField)


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


###
### Relationship Models
###

class Edge(Document):
    """Abstract representation of an edge. 
    """
    SOURCE_NAME = 'edge'
    source = StringField(required=True, default=SOURCE_NAME)

    timestamp = MillisecondField(default=0)

    reference_id = StringField()
    name = StringField()

    to = StringField()
    ffrom = StringField() # from is a keyword

    def __unicode__(self):
        return u'%s => %s :: %s' % (self.ffrom, self.to, self.subject)


###
### Email Models
###

class EmailEdge(Document):
    """Working model for the relevant data describing a communication
    instance between two people: a sender and a recipient. Multiple instances
    of this class should be used to contain an email with multiple recipients.
    """
    SOURCE_NAME = 'emailedge' # Subclasses should override this
    source = StringField(required=True, default=SOURCE_NAME)

    date = MillisecondField(required=True, default=0)
    email = ObjectIdField()
    message_id = StringField()
    subject = StringField()
    to = StringField()
    ffrom = EmailField() # from is a keyword

    def __unicode__(self):
        return u'%s => %s :: %s' % (self.ffrom, self.to, self.subject)
    

class Email(Document):
    """Working model for the structure of data found in the Email transcript.
    Fields are used to contain headers and message body. 
    """
    ### internal tracking
    SOURCE_NAME = 'email'
    source = StringField(required=True, default=SOURCE_NAME)

    ### Source folder, if available
    folder = StringField() 

    ### typical fields
    date = MillisecondField(required=True, default=0)
    message_id = StringField()
    subject = StringField()
    to = StringField()
    ffrom = EmailField() # from is a keyword
    cc = StringField()
    bcc = StringField()

    ### content fields
    body = StringField()

    ### ldc and ldccknn
    ldc_topic = IntField()
    ldc_knn_topic = IntField()

    ### extra headers - not necessarily with an 'X-' prefix
    x_to = StringField()
    x_from = StringField()
    x_cc = StringField()
    x_bcc = StringField()
    x_filename = StringField()
    x_origin = StringField()
    x_folder = StringField()
    # 're' maps to 'inReplyTo' in lucene - JD
    re = StringField() 
    
    def __unicode__(self):
        return u'From: %s Subject: %s' % (self.ffrom, self.subject)

    def __init__(self, *args, **kwargs):
        """Constructs an Email instance by mapping the **keyword arguments
        s to fields.

        Standard use is to set the keyword arguments to all of the headers and
        the body.

        `from` is mapped to `ffrom` because `from` is a Python keyword.
        """
        new_kwargs = dict()
        for key,value in kwargs.items():
            new_key = key.lower()
            if new_key == "from": new_key = "ffrom"
            new_key = new_key.replace('-', '_')
            if isinstance(value, list):
                value = value[0] # TODO ignoring list for now
            new_kwargs[new_key] = value
        super(Email, self).__init__(*args, **new_kwargs)

    @classmethod
    def headermap_from_list(cls, header_tuples):
        """Expects a list of key-value tuples as input and returns a map
        of header name to either a value or a list of values.
    
            {
                'header_one': value,
                'header_two': [value, value, ...],
                'header_three': value,
            }
    
        By returning either a value or list of values, we can map the header
        into the Mongo document and preserve the searchable lists. Lists
        are not completely free with Mongo, so we avoid them and go with a value
        alone when possible.
    
        ZOI makes this easy: http://en.wikipedia.org/wiki/Zero_One_Infinity
        """
        accumulated = dict()
        for (k,v) in header_tuples: # ex. [(k,v), (k,v)]
            if k in accumulated:
                existing = accumulated[k]
                # infinity
                if isinstance(existing, list):
                    accumulated[k].append(v)
                # one
                else: 
                    is_a_list = [existing]
                    is_a_list.append(v)
                    accumulated[k] = is_a_list
            # zero
            else:
                accumulated[k] = v
        return accumulated

    def gen_edge_list(self, mongo_ready=False):
        """Generates the list of edges contained in this email. Fails
        silently if email has no 'to' attribute.

        Returns a list of Mongo-ready documents as the only obvious use
        for this function is to generate a list from new email data.

        Can't explain why there are emails without a 'to' element yet, but
        it seems to be true at least once.
        """
        if not hasattr(self, 'to') or self.to is None:
            return list()

        # Object won't have id if it hasn't been saved # TODO
        #if not hasattr(self, id):
        #    raise ValueError('Email must be saved before generating edges')

        def gen_edge(recipient):
            recipient = recipient.strip()
            params = dict(source=self.source,
                          date=self.date,
                          email=self.id, # TODO
                          message_id=self.message_id,
                          subject=self.subject,
                          to=recipient,
                          ffrom=self.ffrom)
            return EmailEdge(**params)

        fun = lambda to: gen_edge(to)
        if mongo_ready:
            fun = lambda to: gen_edge(to).to_python()

        to_list = [fun(to) for to in self.to.split(',')]
        return to_list
