# Delta Application Center API

## Introduction
This documentation covers the API for the Delta Cluster and IBM Application Center.  On a basic level, it is a modification of the Application Center API that uses REST to run queries on running jobs, and obtain information for a user.  It has three main components, which can be used to suit researchers' needs.  

The Template API is the default Application Center API.  It is fully functional, but also serves as a template to create new scripts.  The Query API is a customized API built from heavily modifying the Application Center API.  If you are interested in building your own customized script or workflow, it is strongly recommended to start there.  It is also fully functional, but is commented and documented to supplement IBM's meager documentation on the topic.  

The Bash API is a workflow that, unlike the other two, does not directly use Application Center, but rather uses Bash Shells that fire off commands, then periodically "listens" for a response from Application Center.  It is important to note that this works on *both* port 22 and port 8080, and if both of these ports are not available, it will not function.  It is also worth mentioning that a potential security risk presents itself in the form of users who could maliciously send off countless commands, thereby clogging the node and potentially the entire cluster.  As such, Bash should be jailed appropriately, and strict limits should be placed on the HPC queues.

## Requirements
* Template API: httplib, httplib2, urllib, urllib2, python 2.7.x, access to port 8080; note that the module requests is not supported
    * pac_api.py must be in the same directory
* Query API: httplib, httplib2, urllib, urllib2, python 2.7.x, access to port 8080; note that the module requests is not supported
    * pac_api.py must be in the same directory
* Bash API: httplib, httplib2, urllib, urllib2, python 2.7.x, Bash 3.0+, access to port 22, access to port 8080

## Overview of API and formulating GET/POST requests
The Application Center API and Query API both run on commandline, and first must obtain a token from Application Center.  The initial request **must** use:
* POST request
* the url "http://delta-lsf.cct.lsu.edu:8080/platform/webservice/pacclient/logon/"
* the headers 'Content-Type': 'application/xml', 'Accept': 'text/plain,application/xml,text/xml'

Subsequent requests must use the token that is created during login, which is about 2 hours.  It must be formatted before sending in subsequent requests in the following way:
* the string *platform_token=* must be added to the beginning
* any double quotes must be replaced with *#quote#*

The Template API stores this token in the file '.pacpass', and then retrieves it before each GET or POST request.  This is not strictly necessary (Query API does not do this), but it is not a bad idea.

The basic formatting for subsequent requests is:
* POST or GET (specified below)
* url: each url will **always** start with http://delta-lsf.cct.lsu.edu:8080/platform/ with additional strings or subdomains appended ; note this will be referred to as **base_url**
* header that contains 'Cookie' : cookieString, 'Content-Type': 'application/xml', 'Accept': 'text/plain,application/xml,text/xml,multipart/mixed'
* body (if required)

According to IBM's [documentation](https://www.ibm.com/support/knowledgecenter/SSZRJV_10.1.0/api_ref/chap_web_services.html), with the exception of the initial logon request, responses can be formatted as either JSON or XML, however, XML seems to be the only workable format for responses.  It is unclear if this is due to the formatting from Application Center, or another reason.  Accordingly, the Template API has a built-in parser/formatter that automagically formats the responses into a nicely readable format.  The parser functions by downloading all values, then parsing them client-side.  The Query API is more specific, in that it parses and selectively downloads the provided request, but it is more limited in scope and expandability.  

### Specific Application Center Queries

##### Login and get token
Requirements
* Must use GET
* Headers should be formatted as:
* url must be:

###### Usage specific to Template API

python pacclient.py logon -l http://delta-lsf.cct.lsu.edu:8080/ -u USERNAME -p PASSWORD

* where USERNAME is a username, PASSWORD is the password.  Note that the token will be stored in ~/.pacpass

###### Usage specific to Query API
* Add username and password to main()
* token will be stored in TOKEN variable

##### Get job info from jobs submitted by user
Requirements:
* Must have already logged in and have token
* Must use GET
* Headers should be formatted as:

    headers = {'Content-Type': 'application/xml', 'Cookie': token, 'Accept': 'text/plain,application/xml,text/xml,multipart/mixed'}
* url must be:
    'base_url/webservice/pacclient/jobs?+user=USERNAME&details=&past='
    where base_url is the url described above, USERNAME is the username, details are specific information, and past is a timeframe to use.  Note that the order is important; *details* and *past* can be left blank, but they must be included.    

###### Usage specific to Template API
python pacclient.py -u USERNAME
* where USERNAME is the username of a logged-in user

###### Usage specific to Query API
* run method from main()

#### Get specific job information
Requirements:
* Must have already logged in and have token
* Will use POST or GET, depending on query

###### Usage specific to Template API
python pacclient.py job JOBID
* where JOBID is the job id
* This will be a GET Query

python pacclient.py job -n JOBNAME
* where JOBNAME is a string that matches a currently running job
* This will be a POST query

###### Usage specific to Query API
* add parameter in the form of (username, (parametername, parameterValue)) to the method checkJobsForParameter()

#### Submit job
Requirements:
* Must have already logged in and have token
* Must use POST
* Only implemented in Template API at this time

###### Usage specific to Template API
python pacclient.py submit -a "FORMNAME:TEMPLATENAME" -c PATH_on_local_matchine -p JOB_PARAMETERS
* -a is required, and must match a published form in Application Center.  If desired, a submission template is optional but can be included
* -c is the path for the local machine, but must correspond to key-value pairs of field_ID, or value.  If a single key has multiple values, use a hash to indicate multiple values map back to it:
    * SOMEFORMITEM=SOMEVALUE,upload
    * SOMEOTHERFORMITEM=ITEM1,upload#ITEM2,upload
* -p is for the job submission parameters, set up as key-value pairs described under *-c*
