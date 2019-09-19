#!/usr/bin/env bash
# clash_linuxupd installation scripts

CURRENT_USER=$(whoami)

if [ -z "$EDITOR" ]
then
  echo "Your \$EDITOR Variable is not set, please set it."
  exit 1
fi

[ -f "$(which sudo)" ] && echo "sudo Found" || exit 1
[ -f "$(which less)" ] && echo "less Found" || exit 1
[ -f "$(which systemctl)" ] && echo "systemctl Found" || exit 1
[ -f "$(which ${EDITOR})" ] && echo "${EDITOR} Found" || exit 1
[ -f "$(which git)" ] && echo "git Found" || exit 1

mkdir -p ~/.config/clash
mkdir -p ~/.config/systemd/user
sudo mkdir -p /usr/local/clash_linuxupd
sudo chown -R "${CURRENT_USER}":"${CURRENT_USER}" /usr/local/clash_linuxupd

git clone --recursive https://github.com/kmahyyg/clash_linuxupd /usr/local/clash_linuxupd
echo "Please read README."
less /usr/local/clash_linuxupd/README.md
echo "Please modify the config according to readme file."
$EDITOR /usr/local/clash_linuxupd/user-subscribe.json.eg
cp -f /usr/local/clash_linuxupd/user-subscribe.json.eg ~/.config/clash/user-subscribe.json
cp -f /usr/local/clash_linuxupd/clash_linuxup* ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable clash_linuxupd
systemctl --user start clash_linuxupd
systemctl --user enable clash_linuxupd_yacd
systemctl --user start clash_linuxupd_yacd

echo "YACD Web Server is listening on localhost:62038."
echo "Installation Successfully Finished."
echo "Please don\'t forget to modify clash service to let clash_linuxupd start up before clash."
exit 0
