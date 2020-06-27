'''
this function for save picture
anthor : antony weijiang
date: 2019/7/15
'''
import os
from log import logger as loger
# logger = loger.Current_Module()
class screen_cap(object):
    def __init__(self):
        picture_name = None
        picture_path = None
        pull_picture_path = None

    def set_picture_name(self, picture_name):
        self.picture_name = picture_name

    def get_picture_name(self):
        return self.picture_name

    def set_picture_path(self, picture_path):
        self.picture_path = picture_path

    def get_picture_path(self):
        return self.picture_path

    def set_pull_picture_path(self, pull_picture_path):
        self.pull_picture_path = pull_picture_path

    def get_pull_picture_path(self):
        return self.pull_picture_path

    def get_screencap(self, sn, picture_name, picture_path):
        try:
            os.system('adb -s %s shell "screencap -p %s/%s"' %(sn, picture_path, picture_name))
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def pull_screencap(self, sn, pull_picture_path, picture_path, picture_name, time_strg):
        try:
            os.system("adb -s %s pull %s/%s %s/%s_%s" %(sn ,picture_path ,picture_name ,pull_picture_path , time_strg, picture_name))
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)




