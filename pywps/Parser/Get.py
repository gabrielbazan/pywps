# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Lince: 
# 
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import types
from string import split
from pywps.Parser.Parser import Parser

class Get(Parser):
    """ Main Class for parsing HTTP GET request types """
    wps = None
    unparsedInputs =  {}    # temporary store for later validation
    GET_CAPABILITIES = "getcapabilities"
    DESCRIBE_PROCESS = "describeprocess"
    EXECUTE = "execute"
    SERVICE = "service"
    WPS = "wps"
    requestParser = None

    def __init__(self,wps):
        """Contructor"""
        Parser.__init__(self,wps)

    def parse(self,queryString):
        """Parse given string with parameters given in KVP encoding
        
        Keyword arguments:
        queryString -- string of parameters taken from URL in KVP encoding
        
        """
        
        key = None
        value = None
        keys = []
        maxInputLength = self.wps.config.getint("server","maxinputparamlength")

        # parse query string
        # arguments are separated by "&" character
        # everything is stored into unparsedInputs structure, for latter
        # validation
        for feature in queryString.split("&"):
            feature = feature.strip()
            key,value = split(feature,"=",maxsplit=1)
            if value.find("[") == 0:  # if value in brackets:
                value = value[1:-1]   #    delete brackets
            keys.append(key)
            self.unparsedInputs[key.lower()] = value[:maxInputLength]

        try:
            self.checkInputLength()
            self.findRequestType()
        except KeyError,e:  # if service or request keys not found
            raise self.wps.exceptions.MissingParameterValue(str(e).strip("'"))
            

    def checkInputLength(self):
        """ Check for max input length, raise exception, if the input
        is too long.  """
            
        key = None
        value = None

        for key in self.unparsedInputs.keys():
            value = self.unparsedInputs[key]

            # check size
            if self.wps.maxInputLength > 0 and\
                    len(value) > self.wps.maxInputLength:
               
                raise FileSizeExceeded(key)

        # check service name: service name is mandatory; service must be "WPS"
        if self.unparsedInputs[self.SERVICE].lower() != self.WPS:
            raise self.wps.exceptions.InvalidParameterValue(
                    self.unparsedInputs[self.SERVICE])
    
    def findRequestType(self):
        """Find requested request type and import given request parser."""

        # test, if one of the mandatory WPS operation is called (via request)
        if self.unparsedInputs["request"].lower() ==\
           self.GET_CAPABILITIES:
            import GetCapabilities 
            self.requestParser = GetCapabilities.Get(self.wps)
        elif self.unparsedInputs["request"].lower() ==\
           self.DESCRIBE_PROCESS:
            import DescribeProcess 
            self.requestParser = DescribeProcess.Get(self.wps)
        elif self.unparsedInputs["request"].lower() ==\
           self.EXECUTE:
            import Execute 
            self.requestParser = Execute.Get(self.wps)
        else:
            raise self.wps.exceptions.InvalidParameterValue(
                    self.unparsedInputs["request"])

        # parse the request
        self.requestParser.parse(self.unparsedInputs)
        return
