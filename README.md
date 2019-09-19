# Clash Automated Subscription Config File Updater

Suitable for Linux Distributions based on Systemd.

## Dependency

First, modify your current `/usr/lib/systemd/system/clash@.service`, append ` clash_linuxupd.service` to `After=` line.

For Arch Linux User, just install `clash` from `archlinuxcn` repo. And enable then start `clash@<YOUR_USERNAME>.service` after you run this service.

## Usage

- Create Folder and Chown `mkdir -p /usr/local/clash_linuxupd && chown $(whoami):$(whoami) /usr/local/clash_linuxupd`
- Clone the repo with `--recursive` into `/usr/local/clash_linuxupd`
- Change config (ports, dns, allow-lan) in `user-subscribe.json.eg`
- Rename `user-subscribe.json.eg` to `user-subscribe.json` and copy to `~/.config/clash`
- Insert your managed subscription config file URL into json
- Copy the `clash_linuxupd.service` into `~/.config/systemd/user/`
- Run `systemctl --user daemon-reload` and `systemctl --user enable clash_linuxupd` to enable autorestart.
- Finally `systemctl --user start clash_linuxupd` to start service.

## YACD

Thanks to [YACD - Yet Another Clash Dashboard](https://github.com/haishanh/yacd), the `yacd` comes from its `gh-pages` branch, version 190829.

If you need web service, simply copy `clash_linuxupd_yacd.service` into `~/.config/systemd/user/`.

Then `systemctl --user daemon-reload` and `systemctl --user enable clash_linuxupd_yacd` to enable autostart, run `systemctl --user start clash_linuxupd_yacd` to boot up web server.

The Web Server will listen on `127.0.0.1:62038`.

## Disclaimer

I'm not take any responsibility for any of your loss or malfunction.

## Config File Explained

```json
{
    "local-httpport": 1085,         // local http proxy port
    "local-socks5port": 1086,       // local socks5 proxy port
    "local-redirport": 1087,        // local transparent proxy port
    "control-addr": "127.0.0.1:9090",       // remote restapi listen port
    "allow-lan": true,              // allow devices in lan connection
    "dns-enable": true,             // enable built-in dns resolver support
    "dns-socket": "0.0.0.0:53",     // built-in dns listen on
    "dns-enhanced": "fake-ip",      // built-in dns working mode, available: fake-ip / redir-host
    "dns-ipv6": true,               // built-in dns resolving ipv6
    "upstream-dns": ["119.29.29.29", "223.5.5.5"],      // upstream dns address, support protocol: pure ip (Traditional UDP) , tls:// (DoT), https:// (DoH EndPoint),  tcp:// (Fallback DNS, concurrent processing),
    "fallback-dns": ["1.1.1.1", "8.8.8.8"],         // Fallback DNS if GEOIP is not CN
    "subscribe-url": ["http://host:port/apikey/clash/config.yaml"],      // Your Subscription URL
    "rules-preference": 0,         // Clash Rule Preferrence, default is the rules comes with your first subscription URL, start from 0
    "latency-test-url": "http://captive.rixcloud.io/generate_204",     // Clash for Windows Specific Latency Test URL
    "gfwed_proxy": "http://127.0.0.1:1086",         // If subscription URL get banned, use this proxy first, support: (http/socks5)://user:pass@host:port
    "is_gfwed": true        // Option to confirm subscription URL get banned, manually set
}
```

# Licence

 clash-linux-upd
 Copyright (C) 2019  kmahyyg
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.
 
 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

