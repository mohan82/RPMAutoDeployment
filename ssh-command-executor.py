__author__ = 'mohan'

import pexpect;
import subprocess;
import logging;
import logging.handlers;
import  sys;
import getpass



# Python functions brings here
#
app_name = 'ssh_executor';
logger = logging.getLogger(app_name);
log_file_name = 'logs/' + app_name + ".log"

def init_logger():
    fiveMegFileSize = 5 * 1024 * 1024
    handler = logging.handlers.RotatingFileHandler((log_file_name), 'a', fiveMegFileSize, 5);
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler);
    logger.setLevel(logging.INFO);





def connect_new_ssh(child, password):
    """
        Connects a new ssh session by saying
        'yes' and sendiung the given password
    """
    child.sendline('yes');
    index = child.expect('password: ');
    if index == 0:
        child.sendline(password);


def disconnect_process(process):
    if not process is None:
        process.terminate();


def execute_command_in_ssh(user, host, password, command, timeout=1000):
    try:
        child = pexpect.spawn('ssh -l %s %s %s' % (user, host, command), [], timeout);
        index = child.expect(['Are you sure you want to continue connecting', 'password: ', 'Permission denied',
                              ' Could not resolve hostname']);
        logger.info(" Trying to connect ..............");
        if index == 0:
            connect_new_ssh(child, password);
        elif index == 1:
            child.sendline(password);
        elif index == 2:
            logger.info("Permission Denied Invalid Password given ");
        elif index == 3:
            logger.warn("Could not resolve hostname :" + host);
        else:
            logger.warn("Didnt match the parameters");
        return child;
    except pexpect.EOF:
        logger.info("Connection ended:");
    except  pexpect.TIMEOUT:
        logger.warn("Connection Timed out please increase the given time out " + str(timeout));


def log_ssh_output(child):
    if not child is None:
        child.expect(pexpect.EOF);
        logger.info("Output from the Session")
        logger.info(child.before);
        logger.info("Terminating Process Exiting now....")


def execute_script_in_ssh(user, host, password, script_full_path, timeout=50000):
    command = "/bin/bash  " + script_full_path;
    return execute_command_in_ssh(user, host, password, command);


def main():
    init_logger();
    try:
        host = raw_input('Hostname: ')
        user = raw_input('User: ')
        password = getpass.getpass('Password: ')
        test_ssh_process = execute_script_in_ssh(user, host, password, "/home/mohan/test.sh");
        log_ssh_output(test_ssh_process);
        disconnect_process(test_ssh_process);
        log_ssh_process = execute_script_in_ssh(user, host, password, "/home/mohan/logs.sh");
        log_ssh_output(log_ssh_process);
        disconnect_process(log_ssh_process);
    except  Exception as e:
        logger.error(e);
        raise;


#End Python functions
#
if __name__ == "__main__":
    sys.exit(main());
