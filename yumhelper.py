__author__ = 'mohan'
import  yum;
import  sys;

class YumHelper():
    """
        A simple YumHelper class based on
         http://yum.baseurl.org/api/yum/
         For a given rpm name it allows you to query and
         find if it is installed/available/updateable in your configured
         yum repo
         NOTICE:
                Write or Delete operations require root or super permissions

                Works only on YUM based machines such as Cent-OS,RHEL etc..
                In debian,  you could install createrepo,yum,rpm from aptitude
                and configure /etc/yum/yum.conf and configure your own
                yum repository using createrepo

        """

    def __init__(self, rpm_name):
        self._rpm_name = rpm_name;
        self._yb = yum.YumBase();
        ##clear cache for every run so that
        ## we get latest copy all time
        self._yb.cleanExpireCache();


    def get_available_package(self):
        """
                Get the available package
        """
        return self._get_first_item_or_none(self._do_package_list('available').available);


    def get_installed_package(self):
        """
              Gets installed package
        """
        return self._get_first_item_or_none(self._do_package_list('installed').installed);

    def get_update_package(self):
        """
              Returns the latest version of the given package object
              for the given rpm name
        """
        return self._get_first_item_or_none(self._do_package_list('updates').updates);


    def _do_package_list(self, narrow_name):
        return self._yb.doPackageLists(pkgnarrow=narrow_name, patterns=[self._rpm_name], ignore_case=True);

    def _get_first_item_or_none(self, list):
        if len(list) >= 1:
            return list[0];
        else:
            return None;

    #TODO :Learn and use lambdas to avoid ugly repetition

    def do_install(self, pkg_obj):
        """
            Installs the  given pkg obj to your local yum repo
            requires special  permission for this operation
        """
        self._yb.doTsSetup();
        self._yb.install(pkg_obj);
        self._yb.buildTransaction();
        self._yb.processTransaction();

    def do_remove(self, pkg_obj):
        """
            Removes the  given pkg obj to your local yum repo
            requires special  permission for this operation
        """

        self._yb.doTsSetup();
        self._yb.remove(pkg_obj);
        self._yb.buildTransaction();
        self._yb.processTransaction();


    def do_update(self, pkg_obj):
        """
            Updates the  given pkg obj to your local yum repo
            requires special  permission for this operation
        """

        self._yb.doTsSetup();
        self._yb.update(pkg_obj);
        self._yb.buildTransaction();
        self._yb.processTransaction();


def main():
    yum = YumHelper("rpm-test");
    pkg = yum.get_update_package();
    yum.do_update(pkg);


if __name__ == "__main__":
    sys.exit(main());
