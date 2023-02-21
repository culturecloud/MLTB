#!/bin/bash

RED_FONT_PREFIX="\033[31m"
GREEN_FONT_PREFIX="\033[32m"
LIGHT_PURPLE_FONT_PREFIX="\033[1;35m"
BOLD_FONT_PREFIX="\033[1m"
STYLE_SUFFIX="\033[0m"
INFO="${BOLD_FONT_PREFIX}INFO${STYLE_SUFFIX}"
ERROR="${BOLD_FONT_PREFIX}${RED_FONT_PREFIX}ERROR${STYLE_SUFFIX}"
ARIA2_CONF=/culturecloud/mltb/aria2/aria2.conf
DOWNLOADER="curl -fsSL --connect-timeout 3 --max-time 3 --retry 2"
NL=$'\n'

DATE_TIME() {
    date +"${GREEN_FONT_PREFIX}%F %T${STYLE_SUFFIX}"
}

GET_TRACKERS() {
    
    if [[ -z "${CUSTOM_TRACKER_URL}" ]]; then
        echo && echo -e "$(DATE_TIME) | ${INFO} | ${BOLD_FONT_PREFIX}Get BT trackers...${STYLE_SUFFIX}"
        TRACKER=$(
            ${DOWNLOADER} https://trackerslist.com/all_aria2.txt ||
            ${DOWNLOADER} https://cdn.staticaly.com/gh/XIU2/TrackersListCollection@master/all_aria2.txt ||
            ${DOWNLOADER} https://trackers.p3terx.com/all_aria2.txt
        )
    else
        echo && echo -e "$(DATE_TIME) | ${INFO} | ${BOLD_FONT_PREFIX}Get BT trackers from url(s):${STYLE_SUFFIX}${CUSTOM_TRACKER_URL} ..."
        URLS=$(echo ${CUSTOM_TRACKER_URL} | tr "," "$NL")
        for URL in $URLS; do
            TRACKER+="$(${DOWNLOADER} ${URL} | tr "," "\n")$NL"
        done
        TRACKER="$(echo "$TRACKER" | awk NF | sort -u | sed 'H;1h;$!d;x;y/\n/,/' )"
    fi

    [[ -z "${TRACKER}" ]] && {
        echo
        echo -e "$(DATE_TIME) | ${ERROR} | ${RED_FONT_PREFIX}${BOLD_FONT_PREFIX}Unable to get trackers, network failure or invalid links.${STYLE_SUFFIX}" && exit 1
    }
}

ECHO_TRACKERS() {
    echo -e "
--------------------[BitTorrent Trackers]--------------------
${TRACKER}
--------------------[BitTorrent Trackers]--------------------
"
}

ADD_TRACKERS() {
    echo -e "$(DATE_TIME) | ${INFO} | ${BOLD_FONT_PREFIX}Adding BT trackers to Aria2 configuration file ${LIGHT_PURPLE_FONT_PREFIX}${ARIA2_CONF}${STYLE_SUFFIX} ..." && echo
    if [ ! -f ${ARIA2_CONF} ]; then
        echo -e "$(DATE_TIME) | ${ERROR} | ${RED_FONT_PREFIX}${BOLD_FONT_PREFIX}'${ARIA2_CONF}' does not exist.${STYLE_SUFFIX}"
        exit 1
    else
        [ -z $(grep "bt-tracker=" ${ARIA2_CONF}) ] && echo "bt-tracker=" >>${ARIA2_CONF}
        sed -i "s@^\(bt-tracker=\).*@\1${TRACKER}@" ${ARIA2_CONF} && echo -e "$(DATE_TIME) | ${INFO} | ${BOLD_FONT_PREFIX}BT trackers successfully added to Aria2 configuration file.${STYLE_SUFFIX}"
    fi
}

[ $(command -v curl) ] || {
    echo -e "$(DATE_TIME) | ${ERROR} | ${RED_FONT_PREFIX}${BOLD_FONT_PREFIX}curl is not installed.${STYLE_SUFFIX}"
    exit 1
}

if [ "$1" = "cat" ]; then
    GET_TRACKERS
    ECHO_TRACKERS
else
    GET_TRACKERS
    ECHO_TRACKERS
    ADD_TRACKERS
fi

exit 0
