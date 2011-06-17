import re
import os
import datetime
import time
import operator

def loadTopicCSV( topicCSVFileLocation = "/Users/glen/Desktop/data/Enron/enron_allexecs_nn_ldc_topics.csv",
                  sortBy = [3,6,7,8,9] ): #The default sort is by time
    dataFile = open( topicCSVFileLocation, "r")
    maxFields = 10
    emails = []
    header = False
    for line in dataFile:
        if not header:
            header = True
        else:
            emails.append(line.split(",")[0:maxFields])
            for i in range(maxFields):
                emails[-1][i] = int(emails[-1][i])


    for col in reversed(sortBy):
        emails = sorted(emails, key=operator.itemgetter(col))
                
    return emails

def generateNNLDCTopics( outputFilename = "/Users/glen/Desktop/data/Enron/enron_allexecs_nn_ldc_topics.csv"):
    emailInfo = loadNNToLDCTopics()

    FILE = open(outputFilename, "w")

    FILE.write("employeeIndexDict[To],employeeIndexDict[From],Topic,Year,Month,DayOfMonth,DayOfWeek,Hour,Minute,Second,Epoch,messageID\n")

    for line in emailInfo:
        first = True
        for item in line:
            if not first:
                FILE.write(",")
            else:
                first = False
            FILE.write(str(item))
        FILE.write("\n")
        

#Takes the NN topic file, youngser's emailaddress->id mapping, and the full email set,
#     returning a file of the format:
#     timestamp, to, from, topic
def loadNNToLDCTopics(nnFileLocation = "/Users/glen/Desktop/data/Enron/7nnToLDCTopics.txt",
                      fullEmailSetRootDir="/Users/glen/Desktop/data/Enron/maildir/",
                      employeeIndexList="/Users/glen/Desktop/data/Enron/employees",
                      duplicateEmailList="/Users/glen/Desktop/data/Enron/dups-ids.txt",
                      originalLDCTopicList="/Users/glen/Desktop/data/Enron/ut_enron_cat_rep.tab",
                      topicsPerMessage=1):

    
    #Nearest Neighbor File Parse
    ############################
    NNFile = open(nnFileLocation, "r")
    messageTopicPairs = []
    #From each line, take the first two cells: messageID and topicNumber
    for line in NNFile:
        messageTopicPairs.append( line.split("\t")[0:2] )
        if messageTopicPairs[-1][1] == "none":
            messageTopicPairs[-1][1] = -1
        else:
            if messageTopicPairs[-1][1] == '0':
                print "Topic read is 0--"
                print line
                print messageTopicPairs[-1]
            messageTopicPairs[-1][1] = int(messageTopicPairs[-1][1] )
    NNFile.close()
    print len(messageTopicPairs)

    #Make a preliminary dicitionary for messageID --> Topic
    messageTopicDict = dict(messageTopicPairs)

    #Original LDC Topic File Parse
    ##############################
    ldcOrigFile = open(originalLDCTopicList, 'r')

    ldcOrigTopics = []
    for line in ldcOrigFile:
        ldcOrigTopics.append(line.strip().split("\t"))
        ldcOrigTopics[-1][1] = int(ldcOrigTopics[-1][1])
        ldcOrigTopics[-1][0] = fullEmailSetRootDir + ldcOrigTopics[-1][0]
    ldcOrigTopicDict = dict(ldcOrigTopics)

    print ldcOrigTopicDict
    print "LDC Orig Dictionary size:", len(ldcOrigTopicDict)
    
    #Duplicate File Parse
    #####################
    dupFile = open(duplicateEmailList,'r')
    topicZeroFromDupsFile = open("topicZeroFromDups.txt", 'w')
    #dupList = []
    for line in dupFile:
        Topic = 0
        splitted = line.strip().split(" ")
        canon = splitted[0]
        needTopics = []
        for i in range(0,len(splitted)):
            if Topic == 0:
                try:
                    Topic = messageTopicDict[ splitted[i] ]
                except:
                    needTopics.append(splitted[i])
            else:
                messageTopicPairs.append( [ splitted[i], Topic ] )
        #We assume that by now we either have a Topic number or are actually stuck with '0'
        for entry in needTopics:
            messageTopicPairs.append( [splitted[i], Topic] )
            if Topic == 0:
                topicZeroFromDupsFile.write(splitted[i]+"\n")
    topicZeroFromDupsFile.close()
            
    #Make a revised dicitionary for messageID --> Topic
    messageTopicDict = dict(messageTopicPairs)
                    

    

    #Gather a list of employees and give them an index according to their placement in the list
    ###########################################################################################
    employeeFile = open(employeeIndexList, "r")
    index = 0
    employeeList = []
    for line in employeeFile:
        employeeList.append( (line.split("\t")[0].strip()+"@enron.com", index) )
        index += 1

    #Make a dictionary for username --> employeeIndex
    employeeIndexDict = dict(employeeList)
    #print employeeIndexDict
    
    #Scan the email directories and pull out the list of emails
    ###########################################################
    emailFileList = recursivelyFindEnronEmails( startingDirectory=fullEmailSetRootDir )

    #MessageID, To, From, Topic, Year, Month, DayOfMonth, Weekday, DayOfYear, Hour, Minute, Second
    emailInfo = []
    #At the moment, we will continue with the convention that each 'email' line can only have one To and one From.
    #     This means that there will be multiple lines per physical email, and each line corresponds to a single edge.
    #     Also, Cc and Bcc will be treated the same as "To".

    emailsMissing = []

    fromRegexer = re.compile(r'^From:')
    messageIDRegexer = re.compile(r'^Message-ID:')
    dateRegexer = re.compile(r'^Date:')
    toRegexer = re.compile(r'^To:')
    ccRegexer = re.compile(r'^Cc:')
    bccRegexer = re.compile(r'^Bcc:')
    continuationRegex = re.compile(r',$')
    includedEmailRegexer = re.compile(r'-----Original Message-----')

    print "Starting scan of email list...."
    
    for emailFilename in emailFileList:
        #print emailFilename
        email = open(emailFilename, "r")
        lineCounter = 0
        messageID = ""
        Topic = 0
        Year = ""
        Month = ""
        DayOfMonth = ""
        Weekday = ""
        DayOfYear = ""
        Hour = ""
        Minute = ""
        Second = ""
        #At the moment we treat CC, BCC, and To exactly the same, so they will all end up in the "To" section
        To = []
        Cc = []
        Bcc = []
        From = ""
        inTo = False
        inCc = False
        inBcc = False
        firstLine = True

        if emailFilename in ldcOrigTopicDict:
            Topic = ldcOrigTopicDict[ emailFilename ]
            print "Topic for", emailFilename, "is", Topic

        for line in email:
            entries = line.strip().split(" ")

            #MessageID is always at the top of the emails
            if firstLine:
                firstLine = False
                #if messageIDRegexer.search(line) and messageID == "":
                messageID = entries[1]
                #print messageID
                #if True:
                #try:
                if messageID in messageTopicDict and Topic == 0:
                    #print messageID, messageID in dupDictionary
                    #if messageID in dupDictionary:
                    #    Topic = messageTopicDict[ dupDictionary[messageID] ]
                    #    print messageID,"found in DupDictionary: replacing with---"
                    #    print dupDictionary[messageID]
                    #else:
                    Topic = messageTopicDict[ messageID ]
                    #print "Topic:", Topic
                    if Topic == 0:
                        print emailFilename
                        emailsMissing.append(messageID)
                else:
                    emailsMissing.append(messageID)
                #except:
                #    print "emailMissing"
                #    emailsMissing.append(messageID)

            #Date 
            if dateRegexer.search(line) and Year =="":
                thisDate = time.strptime(line.split("-")[0], "Date: %a, %d %b %Y %H:%M:%S ")
                try:
                    Epoch = time.mktime(thisDate)
                except:
                    Epoch = -1
                Year, Month, DayOfWeek, Hour, Minute, Second, DayOfMonth, DayOfYear = \
                      time.strftime("%Y,%m,%w,%H,%M,%S,%d,%j", thisDate).split(",")
                #print Epoch
                #print thisDate, Year, Month, DayOfWeek, Hour, Minute, Second, DayOfMonth, DayOfYear
                #For some reason datetime.strptime isn't always implemented, using a time hack instead --GAC
                #thisDate = datetime.strptime(line, "Date: %a, %d %b %Y %H:%M:%S %z (%Z%)")

            #From
            #if entries[0] == "From:" and From == "":
            #print fromRegexer.search(line) 
            if fromRegexer.search(line) and From == "":
                From = entries[1]
                #print From, entries

            #To
            if toRegexer.search(line) or inTo:
                if inTo:
                    entryStart = 0
                else:
                    entryStart = 1
                for item in entries[ entryStart:]:
                    To.append(item.replace(",", "")) #Remove commas from email addresses
                if continuationRegex.search(line.strip()):
                    inTo = True
                else:
                    inTo = False


            #Cc
            if ccRegexer.search(line) or inCc:
                if inCc:
                    entryStart = 0
                else:
                    entryStart = 1
                for item in entries[ entryStart:]:
                    Cc.append(item.replace(",", "")) #Remove commas from email addresses
                if continuationRegex.search(line.strip()):
                    inCc = True
                else:
                    inCc = False


            #Bcc
            if bccRegexer.search(line) or inBcc:
                if inBcc:
                    entryStart = 0
                else:
                    entryStart = 1
                for item in entries[ entryStart:]:
                    Bcc.append(item.replace(",", "")) #Remove commas from email addresses
                if continuationRegex.search(line.strip()):
                    inBcc = True
                else:
                    inBcc = False


            if includedEmailRegexer.search(line):
                pass #How do you break out of a loop?
                
        #Glom CC and BCC into To
        To += Cc
        To += Bcc
        
        #Pull out duplicate entries from multi-line inputs
        To.sort()
        To = set(To) #Dedup, This does make it slightly different from a list, but it can still be ref'd as one would want to

        for to in To:
            #print "about to generate email entry:", From, to
            #print (From in employeeIndexDict) ,(to in employeeIndexDict)
            #print From, to
            if (From in employeeIndexDict) and (to in employeeIndexDict) and not (From == to):
                #emailInfo.append( [employeeIndexDict[to], employeeIndexDict[From], Topic, Year, Month, DayOfMonth, Weekday, DayOfYear, Hour, Minute, Second, messageID] )
                emailInfo.append( [employeeIndexDict[to], employeeIndexDict[From], Topic, Year, Month, DayOfMonth, DayOfWeek, Hour, Minute, Second, Epoch, messageID] )

    print emailInfo
    print len(emailInfo)
    print "Number of emails not found in Tamer's NN:", emailsMissing

    emailsMissingFile = open("emailsMissing.txt", 'w')
    for entry in emailsMissing:
        emailsMissingFile.write(entry+"\n")
    emailsMissingFile.close()
    
    
    return emailInfo

###############################
# Tamer's Index to LDC Topics #
###############################

def generateTamer2TopicMap(nnFileLocation = "/Users/glen/Desktop/data/Enron/7nnToLDCTopics.txt",
                           fullEmailSetRootDir="/Users/glen/Desktop/data/Enron/maildir/",
                           employeeIndexList="/Users/glen/Desktop/data/Enron/employees",
                           duplicateEmailList="/Users/glen/Desktop/data/Enron/dups-ids.txt",
                           originalLDCTopicList="/Users/glen/Desktop/data/Enron/ut_enron_cat_rep.tab",
                           tamerIndex2MessageID="/Users/glen/Desktop/data/Enron/email-id-int-to-string.txt"):
    

    emailFileList = []
    
    #Original LDC Topic File Parse
    ##############################
    ldcOrigFile = open(originalLDCTopicList, 'r')

    ldcOrigTopics = []
    for line in ldcOrigFile:
        ldcOrigTopics.append(line.strip().split("\t"))
        ldcOrigTopics[-1][1] = int(ldcOrigTopics[-1][1])
        #ldcOrigTopics[-1][0] = fullEmailSetRootDir + ldcOrigTopics[-1][0]
        emailFileList.append(ldcOrigTopics[-1][0])
    ldcOrigTopicDict = dict(ldcOrigTopics)

    #print ldcOrigTopicDict
    #print "LDC Orig Dictionary size:", len(ldcOrigTopicDict)


    #Load Tamer's Index to MessageID mapping
    ########################################
    tamerMapFile = open(tamerIndex2MessageID,'r')
    
    tamer2messageID = []
    for line in tamerMapFile:
        temp = line.strip().split("\t")
        tamer2messageID.append([temp[1],temp[0]])
        tamer2messageID[-1][1] = int(tamer2messageID[-1][1])
    tamer2messageID = dict(tamer2messageID)
    
    #print tamer2messageID

    
    #Scan the email directories and pull out the list of emails
    ###########################################################
    #emailFileList = recursivelyFindEnronEmails( startingDirectory=fullEmailSetRootDir )

    #MessageID, To, From, Topic, Year, Month, DayOfMonth, Weekday, DayOfYear, Hour, Minute, Second
    emailInfo = []
    #At the moment, we will continue with the convention that each 'email' line can only have one To and one From.
    #     This means that there will be multiple lines per physical email, and each line corresponds to a single edge.
    #     Also, Cc and Bcc will be treated the same as "To".

    messageIDRegexer = re.compile(r'^Message-ID:')

    print "Starting scan of email list...."

    emailsProcd = 0
    
    for emailFilename in emailFileList:
        #print emailFilename
        email = open(fullEmailSetRootDir+emailFilename, "r")
        messageID = ""
        Topic = 0

        firstLine = True
        
        if emailFilename in ldcOrigTopicDict:
            Topic = ldcOrigTopicDict[ emailFilename ]
            print "Topic for", emailFilename, "is", Topic
        else:
            print "Erroneous Email not in our collection!!!!!--------------------------------------"
            
        for line in email:
            entries = line.strip().split(" ")

            #MessageID is always at the top of the emails
            if firstLine:
                firstLine = False
                messageID = entries[1]
        email.close()
                
        
        if messageID:
            #print tamer2messageID
            print messageID
            print "Procd",emailsProcd

            print "==<1496412.1075844912868.JavaMail.evans@thyme>"
            print tamer2messageID["<1496412.1075844912868.JavaMail.evans@thyme>"]
            
            emailInfo.append( [tamer2messageID[messageID], Topic, messageID, emailFilename])
        emailsProcd += 1  

    print emailInfo
    
#######################
# Directory Searching #
#######################
    
def recursivelyFindEnronEmails( startingDirectory="."):
    regexer = re.compile(r'[0-9]+\.')
    return recursivelyFindFiles( startingDirectory, regexer)
    
#regexer is a pre-compiled regex expression see "recursivelyFindHtmls" for an example --GAC 050109
def recursivelyFindFiles( startingDirectory, regexer):

    if not os.path.isdir(startingDirectory):
        raise "Directory path provided is not valid."
    #print os.path.isfile(startingDirectory)

    dirsToRecur = []
    relativePathList = []

    dirsToRecur.append( os.path.realpath( startingDirectory ) )
    

    while dirsToRecur:
        currentDir = dirsToRecur.pop()
        #print currentDir
        dirListing = os.listdir(currentDir)
        #print dirListing
        for entry in dirListing:
            #print os.path.isdir (os.path.realpath( os.path.join(currentDir,entry) ))
            if os.path.isdir( os.path.join(currentDir,entry) ):
                dirsToRecur.append(os.path.realpath( os.path.join(currentDir,entry) ))
            else:
                if regexer.search( entry ):
                    relativePathList.append( os.path.realpath( os.path.join(currentDir,entry)) )

            #Short circuit for testing purposes
             #if len(relativePathList) > 50:
            #    return relativePathList
            
    #print os.path.realpath(startingDirectory)
    
    #os.path.walk(path, visit, arg)
    
    return relativePathList #Relative to the starting Directory provided
    
    
