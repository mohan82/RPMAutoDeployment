__author__ = 'mohan'

import pexpect;
import logging;
import logging.config;
import os;
import re;
import  sys;
import fnmatch;
import shutil;

"""
RPM Signer
This module depends on gpg
"""
#Logging Config
#

app_name = 'rpm_signer';
rpm_file_name_pattern = "*.rpm"

logging.config.fileConfig("/home/mohan/All_Projects/PythonScripts/rpmsigner_logging.conf");
logger = logging.getLogger(app_name);


class RPMFileNameRetriever():
    """
      A class which helps you to retrieve rpm package
      name from a given file name.  It expects just the file name
      not path. (eg)jdk-1.7.noarch.rpm not /usr/share/jdk-1.7.noarch.rpm
      Also does strict
      validation on the class name and raise value error
      if file name doesn't match rpm file format http://www.rpm.org/max-rpm/ch-rpm-file-format.html
    """

    def __init__(self, file_name):
        self._file_name = file_name;
        self. _rpm_name_pattern = re.compile("^.*\.[a-zA-Z][0-9a-zA-Z]+\.rpm$");
        self._error_msg = "Given rpm :" + file_name + " should be of format <name>-<version>-<release>.<architecture>.rpm";

    def get_rpm_name_from_file_name(self):
        """
        RPM is of format
        <name>-<version>-<release>.<architecture>.rpm
        we are going to rsplit characters from right until
        we get the name.
        """
        temp = [];
        self._validate_arch_and_rpm();
        #Split <name>-<version>-<release>.<architecture>.rpm to
        # 1) <name>-<version>-<release> 2) architecture 3) rpm

        if not self._file_name.endswith("rpm"):
            raise ValueError(self._error_msg);
        temp = self._file_name.rsplit(".", 2);

        #Split  <name>-<version>-<release>
        # to 1) name 2)version 3)release
        temp = temp[0].rsplit("-", 2);

        if  len(temp) != 3:
            raise ValueError(self._error_msg);
        return  temp[0];


    #Private method
    def _validate_arch_and_rpm(self):
        """
          A naive validator which will check for
        we  will assume all architecture starts with lower or uppercase case alphabet, we support thereby,
        i386,sparc,mips,m68l,noarch..etc
        we don't support if it is of format 386 please refer  http://www.rpm.org/max-rpm/ch-rpm-file-format.html
        here or your server /usr/lib/rpmrc
        """
        if self._rpm_name_pattern.match(self._file_name) is None:
            raise ValueError(self._error_msg);


class RPMProcessor:
    """
        A class which process rpm and does following operations
        1)Moves the rpm to given drop-in location
        2) Signs the RPM
        3)Creates a text file with RPM-Package name on it
    """

    def __init__(self, rpm_file_info, rpm_pass_phrase, rpm_dropin, rpm_sign_timeout=10):
        """
            rpm_path==> Absolute or relative path where rpm can be found
            rpm_pass_phrase==> RPM pass-phrase required by rpm sign refer to RPM signing fedora doc
            (http://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/ch11s04.html)
            rpm_sign_timeout==> In seconds,How long  it should wait for inbuilt rpm --resign to sign by
                                default 10 seconds

        """
        self._rpm_file_info = rpm_file_info;
        self._rpm_sign_timeout = rpm_sign_timeout;
        self._rpm_pass_phrase = rpm_pass_phrase;
        self._rpm_dropin = rpm_dropin;
        self._rpm_retriever = RPMFileNameRetriever(rpm_file_info.get_file_name());

    def sign_rpm(self, rpm_path):
        """
            Signs the given rpm but it relies on rhel/linux internal tools
            to sign the rpm wil throw native python exceptions if it doesnt exist
        """
        logger.info("Trying to sign rpm :" + rpm_path);
        process = pexpect.spawn("rpm --resign %s" % (rpm_path), [], self._rpm_sign_timeout)
        index = process.expect("Enter pass phrase:");
        try:
            if index == 0:
                process.sendline(self._rpm_pass_phrase);
                return process;
        except pexpect.EOF:
            logger.info("Connection ended:");
        except  pexpect.TIMEOUT:
            logger.warn("Connection Timed out please increase the given time out " + str(self._rpm_sign_timeout));

    ##Should be in  file util remove it from here
    def copy_file(self):
        """
            Moves the given the rpm file to dropin location
        """
        shutil.copy(self._rpm_file_info.get_file_path(), self._rpm_dropin);

    ## Not needed anymore leaving it for reference
    def create_rpm_info_txt(self):
        rpm_info_txt = self._rpm_retriever.get_rpm_name_from_file_name();
        rpm_info_txt_file_name = self._rpm_dropin + "/" + rpm_info_txt + ".txt";
        logger.info("Creating text file for reference:" + rpm_info_txt_file_name);
        handle = file(rpm_info_txt_file_name, 'a');
        try:
            handle.write(self._rpm_file_info.get_file_name());
        finally:
            handle.close()

    def _run_sign_rpm(self):
        logger.info("Creating Child Process for Signing");
        new_rpm_path = self._rpm_dropin + "/" + self._rpm_file_info.get_file_name();
        child = self.sign_rpm(new_rpm_path)
        if not child is None:
            child.expect(pexpect.EOF);
            logger.info("End Signing RPM")
            logger.info("Testing Signing RPM")
            logger.info(child.before);
            logger.info("Terminating  Child Process created for Signing Exiting now....")
            child.terminate()

    def process_rpm(self):
        logger.info("Processing RPM :" + self._rpm_file_info.get_file_path());
        logger.info("Copying RPM to given dropin path :" + self._rpm_dropin);
        self.copy_file()
        self._run_sign_rpm();


class RPMFileInfo():
    """
        A container class which holds
        rpm file name and file path respectively
    """

    def __init__(self, file_name, file_path):
        self._file_name = file_name;
        self._file_path = file_path;

    def get_file_name(self):
        return self._file_name;

    def get_file_path(self):
        return self._file_path;


def get_rpms(path):
    logger.info("Getting RPMS");
    rpm_file_info_list = [];
    for root, dirs, files in os.walk(path):
        for file_name in files:
            if fnmatch.fnmatch(file_name, rpm_file_name_pattern):
                file_path = os.path.join(root, file_name)
                rpm_file_info_list.append(RPMFileInfo(file_name, file_path));
    logger.info("Finishing Getting RPMS found :" + str(len(rpm_file_info_list)) + " for processing");
    return rpm_file_info_list;


def main():
    dropin_path = "/var/www/dropins"
    rpm_pass_phrase = sys.argv[2];
    logger.debug("RPM Pass phrase is %s"%rpm_pass_phrase);
    for rpm_file_info in get_rpms(sys.argv[1]):
        try:
            RPMProcessor(rpm_file_info, rpm_pass_phrase, dropin_path).process_rpm();
        except  Exception as e:
            logger.warn("Cannot process given rpm_file  with name: %s path: %s because of : %s \n",
                rpm_file_info.get_file_name(),
                rpm_file_info.get_file_path(), e, exc_info=e);


#End Python functions
#
if __name__ == "__main__":
    sys.exit(main());
