#!/usr/bin/python

import sys
import os
import time
import httplib
import httplib2
from xml.etree import ElementTree as ET
from xml.dom import minidom
from xml.parsers.expat import ExpatError

ROOT_URL='http://delta-lsf.cct.lsu.edu:8080/platform/'
ACCEPT_TYPE='text/plain,application/xml,text/xml'
ERROR_STR='errMsg'
NOTE_STR='note'
ERROR_TAG='<' + ERROR_STR + '>'
APP_NAME='AWESOMEAPP'
EXPIRED_MSG='LOGON EXPIRED.   To Logon to PAC, rerun pacclient login.'
TOKEN=''

def token2TOKEN(t):
    t_string = t.replace('"', '#quote#')
    return t_string

def logon(username, password):
    http = httplib2.Http()
    url_logon = ROOT_URL + 'webservice/pacclient/logon/'
    headers = {'Content-Type': 'application/xml', 'Accept': ACCEPT_TYPE}
    body='<User><name>%s</name> <pass>%s</pass> </User>' % (username, password)
    try:
        response, content = http.request(url_logon, 'GET', body=body, headers=headers)
        if response['status'] == '200':
            xdoc=minidom.parseString(content)
            tk=xdoc.getElementsByTagName("token")
            if len(tk) > 0:
                print("You have logged on to IBM Platform Application Center as: " + username)
                tkString = tk[0].childNodes[0].nodeValue
                print("unparsed token is " + tkString)
                TOKEN = token2TOKEN(tkString)
                return tkString
    			    # saveToken(url, tk[0].childNodes[0].nodeValue)
            else:
                err=xdoc.getElementsByTagName("errMsg")
                print err[0].childNodes[0].nodeValue
                sys.exit(1)
        else:
            print "Error. Failed to connect to web service URL: %s" % url_logon
            print response['status']
            sys.exit(1)
    except (AttributeError, httplib2.ServerNotFoundError, httplib.InvalidURL, ExpatError):
        print "Cannot connect to the web service: %s" % url_logon
        sys.exit(1)

def checkJobsForUser(username):
    if not TOKEN:
        print("Error, no Login Token Found!!  It looks like you are not logged in to Application Center, or may have been logged out.  Please log in to continue!")
        return 'None', 0
    url_getjobsForUser = ROOT_URL + 'webservice/pacclient/jobs?' + 'user=' + username + '&details=&past='
    headers = {'Content-Type': 'application/xml', 'Cookie': TOKEN, 'Accept': ACCEPT_TYPE}
    try:
        response, content = http.request(url_getjobsForUser, 'GET', headers=headers)
        if response['status'] == '200':
            xdoc=ET.fromstring(content)
            if ERROR_TAG in content:
				tree=xdoc.getiterator("Jobs")
				err=tree[0].find(ERROR_STR)
            elif NOTE_STR in content:
				tree=xdoc.getiterator("Jobs")
				err=tree[0].find(NOTE_STR)
                return 'error', err.text
            else:
                return 'ok', content
        else:
			return 'error', _getmsg("failed_connect_wsurl") % url_getjobsForUser
    except:
        return 'error', _getmsg("connect_ws_err") % url_getjobsForUser

def checkJobsForParameter(username, parameter):
    parameter_url = ''
    parameterValue = ''
    if not TOKEN:
        print("Error, no Login Token Found!!  It looks like you are not logged in to Application Center, or may have been logged out.  Please log in to continue!")
        return 'None', 0
    parameterCheck = ''
    try:
        parameterCheck = parameter[0]
        parameterValue = parameter[1]
    except IndexError:
        print("Parameter that was entered not recognized.  Please re-enter it!  The parameter was:")
        print(parameter)
        return 0
    if parameterCheck == 'jobname':
        parameter_url = ROOT_URL + 'webservice/pacclient/jobs?'+'name='+parameterValue+'&user='+username+'&details='+'&past='
    elif parameterCheck == 'jobID':
        parameter_url = ROOT_URL + 'webservice/pacclient/jobs?'+'id='+jobID+'&user='+username'&details='+'&past='
    elif parameterCheck == 'jobStatus'
        parameter_url = ROOT_URL + 'webservice/pacclient/jobs?'+'status='+jobStatus+'&user='+username+'&details='+'&past='
    else:
        print("Parameter that was entered not recognized.  Please re-enter it!  The parameter was:")
        print(parameter)
        return 0

    headers = {'Content-Type': 'application/xml', 'Cookie': TOKEN, 'Accept': ACCEPT_TYPE}
    try:
        response, content = http.request(parameter_url, 'GET', headers=headers)
        if response['status'] == '200':
            xdoc=ET.fromstring(content)
            if ERROR_TAG in content:
				tree=xdoc.getiterator("Jobs")
				err=tree[0].find(ERROR_STR)
            elif NOTE_STR in content:
				tree=xdoc.getiterator("Jobs")
				err=tree[0].find(NOTE_STR)
                return 'error', err.text
            else:
                return 'ok', content
        else:
			return 'error', _getmsg("failed_connect_wsurl") % url_getjobsForUser
    except:
        return 'error', _getmsg("connect_ws_err") % url_getjobsForUser

ef main(argv):
    # add username and password here, or add argparser
    token=logon('username', '*******')

    # must run logon() first
    resultCode, result = checkJobsForUser(username)

    # must run logon() first
    # checkJobsForParameter requires a username and ('jobname', JOBNAME) where
    # JOBNAME is the actual job name, ('jobID', JOBID) where JOBID is the actual Job ID, or
    # ('jobStatus', JOBSTATUS) where JOBSTATUS is the
    # actual job status (running, pending, cancelled, finished)
    resultCode, result = checkJobsForParameter(username, (jobname|jobID|jobStatus, STRING))


if __name__ == "__main__":
    main(sys.argv[1:])
