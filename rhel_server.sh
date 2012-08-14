#!/bin/sh


# Global variables
#
#

TMP_FOLDER="/home/mohan/tmp/";
RHEL_SHARED_FOLDER="/home/mohan/dropin_test_bed/rhel_server";
LOG_FOLDER=$RHEL_SHARED_FOLDER/logs;
HOST_NAME="localhost";
BUILD_SERVER_DROPIN_PATH="http://$HOST_NAME/dropins"
#Simple log level
# 1 -->Info
# 2 --->Warn
# Always will log  --->ERROR
LOG_LEVEL=1;
TODAY=`date +%Y%m%d`;
LOG_FILE="$LOG_FOLDER/rhel_process_$TODAY.log";

#End Global Variables
#

#
# Functions
#
#
function log {
    local level=$1;
    local msg=$2;
    local cur_time=`date +%Y/%m/%d-%r`;
    #Log into stdout if one exist and file as well
    echo "$cur_time  $level: $msg"
    `echo "$cur_time  $level: $msg">> $LOG_FILE`;

}

function log_info {
    if [[ $LOG_LEVEL -ge 1 ]];then
      log "INFO" "$1";
    fi
}

function log_warn {
    if [[ $LOG_LEVEL -ge 2 ]]; then
        log "WARN" "$1";
    fi
}

function log_error {
    log "ERROR" "$1";
    exit 1;
}

function assert_file_exist {
    local file_name=$1;
    if [ ! -f $file_name ]
    then
        log_error "File does not exist $file_name"
    fi

}
function check_file_exist {
    local file_name=$1;
    if [ -f $file_name ]
    then
        echo "true";
    else
        echo "false"
    fi
}

function assert_directory_exist {
    local dir_name=$1;
    if [ ! -d $dir_name ]
    then
        log_error "Directory does not exist $dir_name"
    fi

}

function assert_variable_exist {
    echo "he;l"

}
function assert_host {
     local ip_addr=$1;
     #Faster way to check if host exist then
     # ping ,ping does not timeout,quicker if it cant
     # resolve the host.

     host_check_result=`host -t a -W 0.05  $ip_addr`;
     local error_expr=".*no.*";
     if  [[ $host_check_result =~ $error_expr ]];then
        log_error "Cannot Resolve host: $ip_addr"
     fi
     if ! [ "`ping -c 1 $ip_addr`" ]
     then
        log_error "Cannot Connect to host :$ip_addr"
     fi
}

function download_rpm
{
    log_info "Downloading RPM from $BUILD_SERVER_DROPIN_PATH";
    log_info " Begin WGET Log ";
    #Wget  Explanation
    # -nd dont download directory
    # -A -- accept list s only rpm,txt
    # -nc dont clobber, ie stop creating rpm.1,rpm.2 if it downloads again
    #--recursive ,--level --no-parent -->Recursively download tos one level and will not attempt to
    # download from upper level
    ` wget --no-verbose --recursive --level 1 --no-parent $BUILD_SERVER_DROPIN_PATH -A rpm,txt -nc -nd -a $LOG_FILE --directory $TMP_FOLDER`
    log_info " End WGET log ";
}
function push_rpm {

    echo "TODO"
}
function copy_rpm_txt {
        echo "TODO:"

}

function assert {
          assert_directory_exist "$RHEL_SHARED_FOLDER";
          assert_directory_exist "$LOG_FOLDER";
          assert_directory_exist "$TMP_FOLDER";
          assert_host "$HOST_NAME";

}

#Main Function Entrypoint of  the script
function main {
    assert
    if $(check_file_exist $LOG_FILE)
    download_rpm

}

# End Functions

#Bash Entry Point
 main;

