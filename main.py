#!/usr/bin/env python3
# -*- encoding: utf-8- -*-

from requests import get as httpget
from requests.exceptions import *
import yaml
import os
import json
import sys
from urllib.parse import urlparse
from copy import deepcopy
from secrets import token_hex as randtkn

# Read subscription URL from user config, detect existing or not
usrconf = os.path.expanduser("~/.config/clash/user-subscribe.json")
cusserv = os.path.expanduser("~/.config/clash/self_servers.json")
if os.path.isfile(usrconf) and os.path.isfile(cusserv):
    print("Detecting if config file exists...")
    print("User Config File: " + usrconf)
    print("Custom server config: "+ cusserv)
else:
    raise OSError("Config file is not existing, please read README file.")


usrconf = json.loads(open(usrconf, "r", encoding="utf-8").read())
cusserv = json.loads(open(cusserv, "r", encoding="utf-8").read())["servers"]


def checkconfig():
    print("Checking if subscription url is configured...")
    if usrconf["subscribe-url"] == ["http://host:port/apikey/clash/config.yaml"]:
        raise EnvironmentError("You don't have configured any subscription url till now.")
    print("Checking if Enhanced DNS is configured...")
    if usrconf["dns-enhanced"] == "fake-ip" or usrconf["dns-enhanced"] == "redir-host":
        pass
    else:
        raise EnvironmentError("DNS Enhanced Mode configuration Error!")


def preparing():
    print("Build initial template of clash config file...")
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
    print("Connect to URL to get your managed subscription data...")
    for url in usrconf["subscribe-url"]:
        try:
            if usrconf["is_gfwed"]:
                fuckgfw = {
                    'http': usrconf["gfwed_proxy"],
                    'https': usrconf["gfwed_proxy"],
                }
                subsconf.append(httpget(url, timeout=15, proxies=fuckgfw).text)
            else:
                subsconf.append(httpget(url, timeout=15).text)
        except ConnectTimeout:
            print("Cannot connect to " + urlparse(url).netloc + " , This config is ignored!")
        except ProxyError:
            print("Your Proxy Server Config is not correct, please check again.")
            sys.exit(2)
    # Remove duplicate guys
    print("Collecting all datas just have been gotten...")
    if subsconf:
        subsconf = list(dict.fromkeys(subsconf))
    else:
        raise Exception("Cannot Read Content of Subscription Manager Response.")
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
        for p in i["Proxy"]:
            proxy_servers.append(p)
    for i in cusserv:
        proxy_servers.append(i)
    finaldata["Proxy"] = proxy_servers
    # Processing PROXY GROUP PARSE
    proxy_groups = []
    for i in range(0, len(tempstorage)):
        if i == usrconf["rules-preference"]:
            for dt in tempstorage[i]["Proxy Group"]:
                proxy_groups.append(dt)
        else:
            for groupdt in tempstorage[i]["Proxy Group"]:
                if groupdt["name"] == service_provider_list[i]:
                    new_groupdt = deepcopy(groupdt)
                    for server in new_groupdt["proxies"]:
                        if server not in proxy_servers:
                            new_groupdt["proxies"].remove(server)
                        else:
                            pass
                    proxy_groups.append(new_groupdt)
                else:
                    pass
    finaldata["Proxy Group"] = proxy_groups
    # ADD AUTO_LOAD_BALANCE_STRATEGY
    # Reference: https://github.com/Dreamacro/clash
    print("Building customized load balance config...")
    load_balancer_policy = {"name": "LB-ALLPROXY", "type": "load-balance",
                            "url": usrconf["latency-test-url"],
                            "interval": 300, "proxies": ["DIRECT"]
                            }
    for proxies in service_provider_list:
        load_balancer_policy["proxies"].append(proxies)
    proxy_groups.append(load_balancer_policy)
    # Processing Rules
    print("Add the preferred rules managed by your ISP...")
    # Process rules to replace ISP name to LB-ALLPROXY
    finaldata["Rule"] = []
    print("Replace ISP Rules to Load Balancer...")
    for perr in tempstorage[usrconf["rules-preference"]]["Rule"]:
        dt = perr.replace(service_provider_list[usrconf["rules-preference"]], "LB-ALLPROXY")
        finaldata["Rule"].append(dt)
    # Final Process to Remove Useless groups
    prxygp = []
    for i in finaldata["Proxy Group"]:
        if i["name"] != "LB-ALLPROXY":
            pass
        else:
            i["proxies"] = ["DIRECT"]
            for p in finaldata["Proxy"]:
                i["proxies"].append(p["name"])
            prxygp = i
    finaldata["Proxy Group"] = prxygp
    # Dump the data to file
    print("Write processed config to file...")
    with open(os.path.expanduser('~/.config/clash/config.yaml'), 'w', encoding='utf-8') as configfd:
        configfd.write(yaml.dump(finaldata, allow_unicode=True, encoding='utf-8').decode())
    print("Please restart clash service... The web panel is on port 62038...")
    return 0


if __name__ == "__main__":
    main()
