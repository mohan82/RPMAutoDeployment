__author__ = 'mohan'

import pexpect;
import subprocess;
import logging;
import logging.handlers;
import  sys;
import glob;

#TODO:Add strict validation

#Logging Config
#
rpm_pass_phrase = "mynameismohan";
app_name = 'rpm_signer';
logger = logging.getLogger(app_name);
log_file_name = '/home/mohan/logs/' + app_name + ".log"

#Python functions start
#

def init_logger():
    #fiveMegFileSize = 5 * 1024 * 1024
    #handler = logging.handlers.RotatingFileHandler((log_file_name), 'a', fiveMegFileSize, 5);
    handler = logging.StreamHandler();
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler);
    logger.setLevel(logging.INFO);





def execute_command(command):
    """
        This executes a command on native os and returns output from stdout.
        Expects  a list. [0] ,command [1..n] arguments

    """
    try:
        if not isinstance(command, list):
            raise NameError("Cannot Execute if command is null or if it is not list");
        output = subprocess.check_output(command);
        return output;
    except OSError as os:
        logger.error("Cannot Execute Commond: " + command[0] + " and also with args : " + command[1]);
        raise;


def sign_rpm(rpmPath, timeout=10):
    process = pexpect.spawn("rpm --resign %s" % (rpmPath), [], timeout)
    index = process.expect("Enter pass phrase:");
    try:
        if index == 0:
            process.sendline(rpm_pass_phrase);
            return process;
    except pexpect.EOF:
        logger.info("Connection ended:");
    except  pexpect.TIMEOUT:
        logger.warn("Connection Timed out please increase the given time out " + str(timeout));


def process_rpm(rpm_name) :
    child = sign_rpm(rpm_name)
    if not child is None:
        child.expect(pexpect.EOF);
        logger.info("End Signing RPM")
        logger.info("Testing Signing RPM")
        logger.info(child.before);
        logger.info("Terminating Process Exiting now....")
        child.terminate()


def main():
    init_logger();
    try:
        for rpm in glob.glob(sys.argv[1] + "/*.rpm"):
            print process_rpm(rpm);
    except  Exception as e:
        logger.error(e);
        raise;


#End Python functions
#
if __name__ == "__main__":
    sys.exit(main());
