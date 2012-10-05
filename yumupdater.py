import yumhelper;
import subprocess;
import sys;
import logging;
import logging.config;

logging.config.fileConfig("yumupdater_logging.conf");

logger = logging.getLogger("yum_updater");

def execute_command(command_list):
    """
        This executes a command on native os and returns output from stdout.
        Expects  a list. [0] ,command [1..n] arguments

    """
    try:
        if not isinstance(command_list, list):
            raise NameError("Cannot Execute if command is null or if it is not list");
        output = subprocess.check_output(command_list);
        return output;
    except OSError as os:
        logger.error("Cannot Execute Commond: " + command_list[0] + " and also with args : " + command_list[1]);
        raise;


def main():
    print execute_command(["service", "apache2","status"])
    yum = yumhelper.YumHelper("rpm-test");
    print execute_command(["service", "apache2","status"])
    pkg = yum.get_update_package();
    print pkg;
    #yum.do_update(pkg);


if __name__ == "__main__":
    sys.exit(main());
