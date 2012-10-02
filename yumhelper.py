__author__ = 'mohan'
import  yum;
import os;
import  sys;

#A simple YumHelper class based on
# http://yum.baseurl.org/api/yum/
class YumHelper():
    def __init__(self, rpm_name):
        self._rpm_name = rpm_name;
        self._yb = yum.YumBase();
        ##clear cache for every run so that
        ## we get latest copy all time
        self._yb.cleanExpireCache()

    def findPackageList(self):
        search_list = ["name"];
        pkgs = self._yb.searchGenerator(search_list,self._rpm_name)
        return pkgs;



def main():
    yum = YumHelper("RPM-Test");
    for pk in yum.findPackageList():
        print pk;


if __name__ == "__main__":
    sys.exit(main());
