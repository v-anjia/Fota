'''
this function capture logcat log
author:antony weijiang
date:2019/7/15
'''
import subprocess
import os
from log import logger as loger
logger = loger.Current_Module()

class logcat(object):
    def __init__(self):
        file_name = None
        file_path = None
        pull_file_path = None

    def set_file_name(self, file_name):
        self.file_name = file_name

    def get_file_name(self):
        return self.file_name


    def set_file_path(self, file_path):
        self.file_path = file_path

    def get_file_path(self):
        return self.file_path

    def set_pull_file_path(self, pull_file_path):
        self.pull_file_path = pull_file_path

    def get_pull_file_path(self):
        return self.pull_file_path

    def pull_logcat_file(self, sn, file_name, file_path, pull_file_path, time_strg):
        try:
            print("%s" %(file_name))

            os.system("adb -s %s pull %s/%s  %s/%s_%s" %(sn, file_path, file_name,  pull_file_path, time_strg, file_name))
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def collect_logcat_file(self, sn, file_path, file_name):
        try:
            os.system('adb -s %s shell "nohup logcat >> %s/%s 2>&1 &"' %(sn , file_path, file_name))
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)









