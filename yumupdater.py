import yumhelper;
import subprocess;
import sys;
import re;
import logging;
import logging.config;
import time;
import os;
import errno


#Notice: you have to be root or sudoer to run
# this script

logging.config.fileConfig("yumupdater_logging.conf");
logger = logging.getLogger("yum_updater");

#Standard Sleep time is 30 secs
SLEEP_TIME = 30

SERVICE_PID_PATTERN = "^.*pid.*([0-9]+).*$";
SERVICE_RE = re.compile(SERVICE_PID_PATTERN);
RPMS_SERVICE_TUPLE = (("rpm-test","tomcat"),("rpm-test2","tomcat"));


def execute_command(command_list, ignoreStatusCode=False):
    """
        This executes a command on native os and returns output from stdout.
        Expects  a list. [0] ,command [1..n] arguments

    """
    try:
        if not isinstance(command_list, list):
            raise NameError("Cannot Execute if command is null or if it is not list");
        output = subprocess.check_output(command_list);
        return output;
    except subprocess.CalledProcessError as processError:
        if ignoreStatusCode:
            logger.warn("Returned non zero status code: " + str(processError.returncode) + " for command :" +
                        command_list[0] + " and also with args : " + command_list[1]);
            return processError.output
        else:
            raise;
    except OSError as os:
        logger.error("Cannot Execute Command: " + command_list[0] + " and also with args : " + command_list[1]);
        raise;


def is_pid_running(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except OSError, err:
        if err.errno == errno.ESRCH:
            return False;
        elif err.errno == errno.EPERM:
            raise OSError("Cannot check pid no permission");
        else:
            raise;
    return False;


def get_pid_from_service_status(status_string):
    match = SERVICE_RE.match(status_string);
    if match:
        return match.group(1);
    else:
        return None;


def start_service(name):
    return execute_command(["service", name, "start"]);


def check_service_status(name):
    return execute_command(["service", name, "status"]);


def stop_service(name):
    return execute_command(["service", name, "stop"]);


def stop_long_running_service(name, times=4):
    for x in range(1, (times + 1)):
        logger.debug("Checking Service %s status " % name);
        status = check_service_status(name);
        logger.debug(status);
        pid = get_pid_from_service_status(status);
        if pid:
            if x == 4:
                raise NameError("Cannot Stop Service :" + name);
            logger.debug("Trying to Stop Service for the %s th time " % str(x));
            stop_service(name);
            logger.debug("Will wait for %s secs to stop...." % SLEEP_TIME);
            time.sleep(SLEEP_TIME);
        else:
            if x == 1:
                logger.error("service does not started-up or service does not exist");
            else:
                logger.debug(" Have Successfully stopped Service");
            break;


def start_service_till_nth_time(service_name, times=4):
    for x in range(1, (times + 1)):
        logger.debug("Trying to Stop Service for the %s th time " % str(x));
        start_service(service_name);
        status = check_service_status(name);
        logger.debug(status);
        pid = get_pid_from_service_status(status);
        if pid:
            logger.debug("Service %s has been successfully started.." % service_name);
            break;
        else:
            logger.debug("Service %s not started,trying again..." % service_name);


def update_rpms(service_name, rpm_name):
    logger.debug("==========================Checking for Yum Updates==========================");
    yum = yumhelper.YumHelper(rpm_name);
    pkg = yum.get_update_package();
    if pkg:
        logger.debug("Found an rpm for update %s" % pkg);
        logger.debug("Try to stop service .......");
        stop_long_running_service(service_name);
        logger.debug("Trying to  updating rpm");
        yum.do_update(pkg);
        logger.debug("Will wait for %s secs before starting service:" % (SLEEP_TIME));
        time.sleep(SLEEP_TIME);
        start_service_till_nth_time(service_name);
    else:
        logger.debug("Cannot find Yum Update ....")
        logger.debug("==========================End Checking Yum Updates==========================");


def main():
    for rpm_service in RPMS_SERVICE_TUPLE:
        update_rpms(rpm_name=rpm_service[0],service_name=rpm_service[1]);



if __name__ == "__main__":
    sys.exit(main());
