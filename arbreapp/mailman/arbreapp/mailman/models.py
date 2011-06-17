from arbre.timestamping import MillisecondField

from dictshield.document import Document
from dictshield.fields import (IntField,
                               StringField,
                               EmailField,
                               ObjectIdField)


###
### Document designs
###
        
class Email(Document):
    """Working model for the structure of data found in the Email transcript.
    Fields are used to contain headers and message body. 
    """
    ### internal tracking
    SOURCE_NAME = 'NOT SET CORRECTLY' # RAWR

    # the source should be either 'lucene' or 'maildir'
    source = StringField(required=True, default=SOURCE_NAME)
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
    def gen_from_message(cls, msg):
        """Generates an Email instance from the msg generated by
        `email.message_from_file`.
        """
        contents = cls.headermap_from_list(msg._headers)
        contents['body'] = msg._payload
        return cls(**contents)

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
            return CommunicationEdge(**params)

        fun = lambda to: gen_edge(to)
        if mongo_ready:
            fun = lambda to: gen_edge(to).to_python()

        to_list = [fun(to) for to in self.to.split(',')]
        return to_list

    
class MaildirEmail(Email):
    """Maps the structure generated from Python's email module into a document
    by extending `Email`.
    """
    SOURCE_NAME = 'maildir'
    
    source = StringField(required=True, default=SOURCE_NAME)

    ### Maildir variations
    content_type = StringField()
    mime_version = StringField()
    content_transfer_encoding = StringField()
    attendees = StringField()
    time = StringField()

    
class LuceneEmail(Email):
    """Maps the structure generated from Python's email module into a document
    by extending `Email`.
    """
    SOURCE_NAME = 'lucene'

    source = StringField(required=True, default=SOURCE_NAME)

    # Trust 'fromName' in lucene more than 'x-from'    
    dirty_x_from = StringField() 
    dirty_x_to = StringField()

    ### Meta fields
    quoted_lines = StringField()
    quoted_type = StringField()
    unstemmed_contents = StringField()
    num_quoted = StringField()
    length = StringField()
    contents = StringField()
    contents_lines = StringField()
    
    
class CommunicationEdge(Document):
    """Working model for the relevant data describing a communication
    instance between two people: a sender and a recipient. Multiple instances
    of this class should be used to contain an email with multiple recipients.
    """
    # Header fields
    source = StringField(required=True, default='NOT SET CORRECTLY') # RAWR
    date = MillisecondField(required=True, default=0)
    email = ObjectIdField()
    message_id = StringField()
    subject = StringField()
    to = StringField()
    ffrom = EmailField() # from is a keyword

    def __unicode__(self):
        return u'%s => %s :: %s' % (self.ffrom, self.to, self.subject)

