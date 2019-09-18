#!/usr/bin/env python3
# -*- encoding: utf-8- -*-

from requests import get as httpget
from requests.exceptions import *
import yaml
import os
import json
import sys
from urllib.parse import urlparse

# Read subscription URL from user config, detect existing or not
usrconf = os.path.expanduser("~/.config/clash/user-subscribe.json")
if os.path.isfile(usrconf):
    print("User Config File: " + usrconf)
else:
    raise OSError("Config file is not existing, please read README file.")
    sys.exit(1)

usrconf = json.loads(open(usrconf, "r", encoding="utf-8").read())

def checkconfig():
    if usrconf["subscribe-url"] == ["http://host:port/apikey/clash/config.yaml"]:
        raise EnvironmentError("You don't have configured any subscription url till now.")
        sys.exit(2)
    if usrconf["dns-enhanced"] == "fake-ip" or usrconf["dns-enhanced"] == "redir-host":
        pass
    else:
        raise EnvironmentError("DNS Enhanced Mode configuration Error!")
        sys.exit(2)


def main():
    subsconf = []
    # Access each url to get data
    for url in usrconf["subscribe-url"]:
        try:
            subsconf.append(httpget(url).text)
        except ConnectTimeout as timeout:
            print("Cannot connect to " + urlparse(url).netloc + " , This config is ignored!")
    # Remove duplicate guys
    if subsconf:
        subsconf = set(subsconf)
    else:
        print("Cannot Read Content of Subscription Manager Response.")
    # Initiate final data storage area, trying to merge if multiple URL exists.
    finaldata = None
    if isinstance(subsconf, set) and len(subsconf) > 1:
        #TODO
        pass
    else:
        for i in subsconf:
            finaldata = i
    # Dump the data to file
    
    

if __name__ == "__main__":
    main()
