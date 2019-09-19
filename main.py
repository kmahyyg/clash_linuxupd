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


def preparing():
    clash_conf = {
        "port": usrconf["local-httpport"],
        "socks-port": usrconf["local-socks5port"],
        "redir-port": usrconf["local-redirport"],
        "allow-lan": usrconf["allow-lan"],
        "mode": "Rule",
        "log-level": "info",
        "external-controller": usrconf["control-addr"],
        "dns": {
            "enable": usrconf["dns-enable"],
            "listen": usrconf["dns-socket"],
            "enhanced-mode": usrconf["dns-enhanced"],
            "ipv6": usrconf["dns-ipv6"],
            "nameserver": usrconf["upstream-dns"],
            "fallback": usrconf["fallback-dns"]
        },
        "cfw-latency-url": usrconf["latency-test-url"],
        "cfw-bypass": ["qq.com", "music.163.com", "*.music.126.net", "localhost", "127.*", "10.*", "172.16.*",
                       "172.17.*", "172.18.*", "172.19.*", "172.20.*", "172.21.*", "172.22.*", "172.23.*", "172.24.*",
                       "172.25.*", "172.26.*", "172.27.*", "172.28.*", "172.29.*", "172.30.*", "172.31.*",
                       "192.168.*", "<local>"],
        "cfw-latency-timeout": 5000,
        "Proxy": [],
        "Proxy Group": [],
        "Rule": []
    }
    return clash_conf


def findispname(data):
    for pxygp in data["Proxy Group"]:
        if pxygp["type"] == "select":
            return pxygp["name"]
        else:
            pass


def main():
    checkconfig()
    subsconf = []
    # Access each url to get data
    for url in usrconf["subscribe-url"]:
        try:
            subsconf.append(httpget(url).text)
        except ConnectTimeout:
            print("Cannot connect to " + urlparse(url).netloc + " , This config is ignored!")
    # Remove duplicate guys
    if subsconf:
        subsconf = list(dict.fromkeys(subsconf))
    else:
        print("Cannot Read Content of Subscription Manager Response.")
    finaldata = preparing()  # Initiate final data storage area.
    tempstorage = []  # Save the loaded yaml dict
    service_provider_list = []
    for cfgfd in subsconf:
        current_isp = yaml.safe_load(cfgfd)
        tempstorage.append(current_isp)
        service_provider_list.append(findispname(current_isp))
    try:
        print(str("Service Provider Preference: " + service_provider_list[usrconf["rules-preference"]]))
    except IndexError:
        print("Error: Rule preference is not corresponding to subscribe URL number.")
        print("Note: Preference Number Start From 0, Not 1!")
        sys.exit(2)
    # Processing PROXY SERVER PARSE
    proxy_servers = []
    for i in tempstorage:
        proxy_servers.append(i["Proxy"])
    finaldata["Proxy"] = proxy_servers
    # Processing PROXY GROUP PARSE
    proxy_groups = []
    for i in range(0, len(tempstorage)):
        if i == usrconf["rules-preference"]:
            proxy_groups.append(tempstorage[i]["Proxy Group"])
        else:
            for existing_conf in tempstorage[i]:
                for groupdt in existing_conf["Proxy Group"]:
                    if groupdt["name"] == service_provider_list[i]:
                        proxy_groups.append(groupdt)
                    else:
                        pass
    # ADD AUTO_LOAD_BALANCE_STRATEGY
    # Reference: https://github.com/Dreamacro/clash
    load_balancer_policy = {"name": "lb-allproxy", "type": "load-balance",
                            "url": usrconf["latency-test-url"],
                            "interval": 300, "proxies": ["DIRECT", "REJECT"]
                            }
    for proxies in service_provider_list:
        load_balancer_policy["proxies"].append(proxies)
    proxy_groups.append(load_balancer_policy)
    # Processing Rules
    finaldata["Rule"] = tempstorage[usrconf["rules-preference"]]["Rule"]
    # Dump the data to file
    with open(os.path.expanduser('~/.config/clash/config.yaml'), 'w') as configfd:
        configfd.write(yaml.dump(finaldata))
    return 0


if __name__ == "__main__":
    main()
