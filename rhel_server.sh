#!/bin/sh


# Global variables
#
#

TMP_FOLDER="/home/mohan/tmp/";

#Shared folder config
SHARED_FOLDER="/home/mohan/dropin_test_bed/";
RHEL_SHARED_FOLDER="$SHARED_FOLDER/rhel_server";
TEST_SHARED_FOLDER="$SHARED_FOLDER/test";
LOG_FOLDER=$RHEL_SHARED_FOLDER/logs;

#Build Server config
BUILD_SERVER_HOST_NAME="localhost";
BUILD_SERVER_DROPIN_PATH="http://$BUILD_SERVER_HOST_NAME/dropins"

#Loggin Config

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
    if [[ $LOG_LEVEL -le 2 ]]; then
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
        echo "false";
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
function copy_rpm_txt_to_test {
    local txt_file_pattern="$TMP_FOLDER/*.txt";
    local result=$(check_file_exist $txt_file_pattern);
    if [ $result == "false" ]; then
        log_warn "Text file does not here skipping copying test"
        return 1;
    fi;
    for txt_file in $txt_file_pattern
    do
        log_info "Copying rpm from rhel share $RHEL_SHARED_FOLDER to $TEST_SHARED_FOLDER"
        `cp $txt_file $TEST_SHARED_FOLDER`
    done;
}

function cleanup_temp_folder {
    log_info "Cleaning up temp folder $TMP_FOLDER "
    `rm  $TMP_FOLDER/*`
}
function clean_up_log_files {

    log_file_count=`ls $LOG_FOLDER/*.log* |wc -l`
    if [[ $log_file_count -ge 10 ]];then
        log_info "Trying to clean up log files from folder $LOG_FOLDER";
        `find $LOG_FOLDER -name \*log\* -mtime +10|xargs -r rm`
        log_info "End Cleaning up "
    else
        log_info "Skipping Clean up log files not greater than 10"
    fi
}
function process_rpm {
    push_rpm
   copy_rpm_txt_to_test
   cleanup_temp_folder
}

function assert {
          assert_directory_exist "$RHEL_SHARED_FOLDER";
          assert_directory_exist "$LOG_FOLDER";
          assert_directory_exist "$TMP_FOLDER";
          assert_directory_exist "$TEST_SHARED_FOLDER";
          assert_host "$BUILD_SERVER_HOST_NAME";
}

#Main Function Entrypoint of  the script
function main {
    assert
    local result=$(check_file_exist "$TMP_FOLDER/*.rpm");
    echo $result;
    if [ $result == "false" ]; then
        download_rpm
        process_rpm
    else
          log_info "File already exist in $TMP_FOLDER skipping we cannot process more than one file at a time"
    fi
    clean_up_log_files;
}

# End Functions

#Bash Entry Point
 main;

