#!/bin/bash


#!/bin/bash

set -e


fg_black="$(tput setaf 0)"
fg_red="$(tput setaf 1)"
fg_green="$(tput setaf 2)"
fg_yellow="$(tput setaf 3)"
fg_blue="$(tput setaf 4)"
fg_magenta="$(tput setaf 5)"
fg_cyan="$(tput setaf 6)"
fg_white="$(tput setaf 7)"
reset="$(tput sgr0)"

install () {
  echo "${fg_magenta}Installing Friday.. ${fg_reset}"

  echo "${fg_magenta}Copying friday.service to /etc/systemd/system ${fg_reset}"
  cp friday.service /etc/systemd/system

  echo "${fg_green}Install successful! Hopefully..! :) ${fg_reset}"
} 

enable () {
  echo "${fg_magenta}Running systemctl enable friday${fg_reset}"
  systemctl enable friday
}

disable () {
  echo "${fg_magenta}Running systemctl disable friday${fg_reset}"
  systemctl disable friday
}

info () {
  echo "${fg_magenta}Running systemctl status friday${fg_reset}"
  systemctl status friday
}

run () {
  echo "${fg_magenta}Running systemctl start friday${fg_reset}"
  systemctl start friday
}

end () {
  echo "${fg_magenta}Running systemctl stop friday${fg_reset}"
  systemctl stop friday
}

print_help() {
      echo ""
      echo ""
      echo "${fg_green}  ******** Friday Raspberry Pi Install Script ******** ${fg_black}"
      echo " "
      echo "${fg_white} options:"
      echo "-h, --help  show brief help"
      echo "${fg_magenta}--install ${fg_white}, Installs on the pi."
      echo "${fg_magenta}--enable ${fg_white}, Enable auto start assistant."
      echo "${fg_magenta}--disable ${fg_white}, Disable auto start of assistant."
      echo "${fg_magenta}--start ${fg_white},  Start the assistant service."
      echo "${fg_magenta}--stop ${fg_white},  Stop the assistant service."
      echo "${fg_magenta}--status ${fg_white},  Status of the assistant service."
      exit 0
}


#while test $# -gt 0; do
case "$1" in
  -h|--help)
    print_help
    break
    ;;
  --install)
    install
    exit 0
    ;;
  --enable)
    enable
    exit 0
    ;;
  --disable)
    disable
    exit 0
    ;;
  --start)
    run
    exit 0
    ;;
  --stop)
    end
    exit 0
    ;;
  --status)
    info
    exit 0
    ;;
  *)
    print_help
    break
    ;;
esac
#done
print_help
