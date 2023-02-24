# PROXY CONFIG
# -----------------------------------------------------------------------------

# Usage
# conf-proxy PROXY_PROFILE
#
# Proxy Profiles are stored in ~/conf-proxy/profiles/ folder
# Each profile is a file, with the following optional variables
# ALL_PROXY, HTTP_PROXY, HTTPS_PROXY

if [ -n "$1" ]; then
  if [ -f "$HOME/conf-proxy/profiles/$1" ]; then
    source "$HOME/conf-proxy/profiles/$1"
  else 
    echo "Disabling Proxy"
  fi

  if [ -z $HTTPS_PROXY ]; then
    export HTTPS_PROXY=$ALL_PROXY
  fi
  if [ -z $HTTP_PROXY ]; then
    export HTTP_PROXY=$ALL_PROXY
  fi
else 
  unset ALL_PROXY
  unset HTTP_PROXY
  unset HTTPS_PROXY
fi


set_npm_proxy() {
  if [ "$2" == "secure" ]; then
    npm config set https-proxy "http://$1"
  else
    npm config set proxy "http://$1"
  fi
}

unset_npm_proxy() {
  if [ "$2" == "secure" ]; then
    npm config delete https-proxy
  else
    npm config delete proxy
  fi
}


set_git_proxy() {
  if [ "$2" == "secure" ]; then
    git config --global https.proxy "$1"
  else
    git config --global http.proxy "$1"
  fi
}

unset_git_proxy() {
  if [ "$1" == "secure" ]; then
    git config --global --unset-all https.proxy
  else
    git config --global --unset-all http.proxy
  fi
}

set_env_proxy() {
  PROXY_FILE="$HOME/conf-proxy/proxy-conf.sh"
  echo "# PROXY CONFIG" > "$PROXY_FILE"
  echo "# ------------" >> "$PROXY_FILE"
  echo "unset ALL_PROXY && unset HTTPS_PROXY && unset HTTP_PROXY" >> "$PROXY_FILE"

  if [ -n "$ALL_PROXY" ]; then
    echo "ALL_PROXY=$ALL_PROXY" >> "$PROXY_FILE"
  fi
  if [ -n "$HTTP_PROXY" ]; then
    echo "HTTP_PROXY=$HTTP_PROXY" >> "$PROXY_FILE"
  fi
  if [ -n "$HTTPS_PROXY" ]; then
    echo "HTTPS_PROXY=$HTTPS_PROXY" >> "$PROXY_FILE"
  fi
  source $HOME/conf-proxy/proxy-conf.sh
}


# set_mac_proxy sets the mac proxy
# USAGE: set_mac_proxy $PROXY (secure?)
set_mac_proxy() {
  IFS=":"
  read -a proxyarr <<< "$1"
#   echo "Mac ${2}: ${proxyarr[0]}"
#   echo "Mac ${2}: ${proxyarr[1]}"
  networksetup -set${2}webproxystate Wi-Fi on
  networksetup -set${2}webproxy Wi-Fi ${proxyarr[0]} ${proxyarr[1]}
}

unset_mac_proxy() {
  networksetup -set${1}webproxystate Wi-Fi off
}

set_env_proxy

if [ -n "$HTTP_PROXY" ]; then
  echo "Setting Up For Http Proxy: $HTTP_PROXY"
  set_git_proxy "$HTTP_PROXY"
  set_npm_proxy "$HTTP_PROXY"
  set_mac_proxy "$HTTP_PROXY"
else
  echo "No Http Proxy Found"
  unset_git_proxy
  unset_npm_proxy
  unset_mac_proxy
fi

if [ -n "$HTTPS_PROXY" ]; then
  echo "Setting Up for Https Proxy: $HTTPS_PROXY"
  set_git_proxy "$HTTPS_PROXY" "secure"
  set_npm_proxy "$HTTPS_PROXY" "secure"
  set_mac_proxy "$HTTPS_PROXY" "secure"
else
  echo "No Https Proxy Found"
  unset_git_proxy "secure"
  unset_npm_proxy "secure"
  unset_mac_proxy "secure"
fi
