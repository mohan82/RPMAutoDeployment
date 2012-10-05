__author__ = 'mohan'

import  sys;
import re;
import  rpmsigner;


def main():
    rpm_retriever = rpmsigner.RPMFileNameRetriever("abc-cae-radionational-webapp-WCMS-12.12.noarch.rpm");
    print rpm_retriever.get_rpm_name_from_file_name();


if __name__ == "__main__":
    sys.exit(main());



