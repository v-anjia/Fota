'''
prepare any action fo hu devices test
date:2019-3-28
@author: antony weijiang
'''
#coding=utf-8
import time
import requests
from bs4 import BeautifulSoup
import os
import sys
import uiautomator2 as u2
import subprocess
from log import logger as loger
import threading
import re,sys
import random
from atexit import register
from Common_Public import Common as co
from Common_Public import Signal_List as SL
from Common_Public import Signal_Common as SC
action = ["check_sn_status","upgrade_udisk_package","check slience package download and install","reboot and check version","install old package"]
package = co.Install_Package()
adb_sn  = co.ADB_SN()
prepare_ui = co.Prepare_Ui()
check_message = co.Check_message()
platform_information = co.Platform_Information()
logger = loger.Current_Module()
retry_times = 5

class hu_common(object):
    def __init__(self):
        pass

    def check_sn_status(self):
        '''
        function:check device status
        :return: sn serial number
        '''
        if adb_sn.check_adb_status():
            adb_sn.set_sn(adb_sn.get_sn_from_adb_command()[0])
        if adb_sn.isConnecting:
            logger.log_info("hu device(%s) is ready and adb devices works well,you can use it for your testing" %(adb_sn.get_sn()),\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return adb_sn.get_sn()
        else:
            sys.exit(-1)

    def upgrade_udisk_package(self,sn):
        '''
        upgrade disk pakcage
        :param sn:
        :return:
        '''
        package.down_package_to_local(package.update_fota_package(),package.oldDate())
        package.copy_local_to_udisk(sn)


    def check_system_version(self,sn):
        '''
        function:check system version
        :param sn:
        :return:
        '''
        current_version = package.get_software_version(sn)
        filelist = package.update_fota_package()
        print(current_version)
        if current_version == filelist[2]:
            print("0")
            return 0
        elif current_version == filelist[3]:
            print("1")
            return 1

    def prepare_old_system(self,sn):
        '''
        function:restore old version
        :param sn:
        :return:
        '''
        if self.check_system_version(sn) == 0:
            package.flash_through_system(sn)
            time.sleep(5)
            if self.check_system_version(sn) == 1:
                return 0
            else:
                return 1
        else:
            return 0

    def check_data_json(self,sn,delay_time):
        '''
        function: return data.json if exist
        :param sn:
        :return:
        '''
        if self.prepare_old_system(sn) == 0:
            co.delete_file(sn)
            time.sleep(5)
            co.reboot_device(sn)
            time.sleep(2)
            co.wait_hu_recovery(sn)
            return co.check_json_file(sn,delay_time)

    def check_data_json(self,sn):
        '''
        function: return data.json if exist
        :param sn:
        :return:
        '''
        return check_message.check_data_file(sn)

    def check_fota_Client(self,sn,flag):
        '''
        function :check fota_Client.log
        :param self: flag = ['Full','Diff']
        :return:
        '''
        return check_message.check_fota_Client(sn,flag)

    def check_libHu_fota(self,sn):
        '''
        function : check /update/libhufota.log
        :return:
        '''
        return check_message.check_libHUfota(sn)

    def check_package_upgradeprogress(self,sn,flag):
        '''
        function:check full package upgrade progress
        :param sn:
        :param flag:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        try:
            # package.flash_through_system(sn)
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("may be has not network", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn,flag) == 0:
                    time.sleep(5)
                    if package.check_download_progress(sn,flag) == 0 and self.check_libHu_fota(sn):
                        time.sleep(5)
                        co.reboot_device(sn)
                        time.sleep(2)
                        co.wait_hu_recovery(sn)
                        if self.check_system_version(sn) == 0:
                            logger.log_info("upgrade system success",\
                                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                            return 0
                        elif self.check_system_version(sn) == 1:
                            logger.log_error("upgrade system failed",\
                                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                            return 1
                    else:
                        logger.log_error("download failed or install failed",\
                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return 1
                else:
                    logger.log_error("can not find %s" %(co.get_packagename_from_json_file(sn,flag)),\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("flash system failed or start fota module failed",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_break_point_resume_tbox(self, sn, flag):
        '''
        funciton: break point resume through disable/enable network
        :param sn:
        :return:
        '''
        funlist = [co.disable_network,co.enable_network]
        co.delete_file(sn)
        time.sleep(5)
        value_list = []
        # package.flash_through_system(sn)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)

                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("may be has no network",\
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                expect_size = int(co.get_packagesize_from_json_file(sn,flag))
                while True:
                    actual_size = co.check_package_size(sn,flag)
                    logger.log_info("current actual download size is :%s\n\t\texpect download size is :%s" %(actual_size,expect_size),\
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    value_list.append(int(actual_size))
                    if actual_size is not None and int(actual_size) < expect_size:
                        for fun in  funlist:
                           if fun(sn):
                               time.sleep(random.randint(60,100))
                    elif actual_size is None :
                        return 1
                    if int(actual_size) == expect_size:
                        logger.log_info("check break point resume with network successfully",\
                                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return 0
                    if len(value_list) >= 5:
                        i = 0
                        while i <= len(value_list) - 2:
                            if value_list[i] == value_list[i + 1]:
                                i = i + 1
                            else:
                                break
                            if i == len(value_list) - 1:
                                logger.error("package size can not change,and package always is :%s" %(actual_size), \
                                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno )
                                return 1
            else:
                logger.log_error("flash system failed or start fota module failed", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_break_point_resume_with_reboot(self, sn, flag):
        '''
        function : break point resume through reboot
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        value_list = []
        try:
            # package.flash_through_system(sn)
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network",\
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                if co.check_package_exist(sn,flag) == 0:
                    expect_size = int(co.get_packagesize_from_json_file(sn,flag))
                    while True:
                        actual_size = co.check_package_size(sn,flag,30)
                        value_list.append(int(actual_size))
                        # print(actual_size)
                        if actual_size is not None and int(actual_size) < expect_size:
                            time.sleep(random.randint(60,100))
                            co.reboot_device(sn)
                            co.wait_hu_recovery(sn)
                            # co.start_fota_daemon(sn)
                        elif actual_size is None and co.check_package_exist(sn,flag,30) == 1:
                            return 1
                        if int(actual_size) == expect_size:
                            co.start_fota_daemon(sn)
                            logger.log_info("check break point resume with network successfully",\
                                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                            return 0
                        if len(value_list) >=5 :
                            i=0
                            while i <= len(value_list) -2:
                                if value_list[i] == value_list[i+1]:
                                    i = i + 1
                                else :
                                    break
                                if i == len(value_list) -1:
                                    logger.error("package size can not change,and package always is :%s" % (actual_size), \
                                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                    return 1
                else:
                    logger.log_error("can not find package", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("flash system failed or start fota module failed", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1


    def prepare_post_request(self,sn):
        '''
        function:prepare post require
        :param sn:
        :return:
        '''
        try:
            filelist = package.update_fota_package()
            platform_information.set_device("hu")
            # platform_information.set_vin_version(platform_information.get_vin_verbose(sn))
            platform_information.set_vin_version(filelist[5])
            platform_information.set_sw_version_new(filelist[2])
            platform_information.set_sw_version_old(filelist[3])
            platform_information.set_mcu_version(filelist[6])
            data_json = platform_information.temporary_get_port_data(platform_information.get_vin_version(),
                                                                     platform_information.get_device(), \
                                                                     platform_information.get_sw_version_old(),\
                                                                     platform_information.get_mcu_version())
            header = platform_information.get_header(platform_information.get_vin_version())
            return co.post_request(sn,header,data_json)
        except Exception as e:
            logger.log_error("%s" %(e),sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def temporary_prepare_post_request(self,sn):
        try:
            filelist = package.update_fota_package()
            platform_information.set_device("hu")
            # platform_information.set_vin_version(platform_information.get_vin_verbose(sn))
            platform_information.set_vin_version(filelist[5])
            platform_information.set_sw_version_new(filelist[2])
            platform_information.set_sw_version_old(filelist[3])
            platform_information.set_mcu_version(filelist[6])
            data_json = platform_information.temporary_get_port_data(platform_information.get_vin_version(),
                                                                     platform_information.get_device(), \
                                                                     platform_information.get_sw_version_old(),\
                                                                     platform_information.get_mcu_version())
            print(data_json)
            header = platform_information.get_header(platform_information.get_vin_version())

            return co.post_request(sn,header,data_json)
        except Exception as e:
            logger.log_error("%s" %(e),sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def get_requestdata_to_file(self,sn):
        try:
            filelist = package.update_fota_package()
            platform_information.set_device("hu")
            # platform_information.set_vin_version(platform_information.get_vin_verbose(sn))
            platform_information.set_vin_version(filelist[5])
            platform_information.set_sw_version_new(filelist[2])
            platform_information.set_sw_version_old(filelist[3])
            platform_information.set_mcu_version(filelist[6])
            data_json = platform_information.temporary_get_port_data(platform_information.get_vin_version(),
                                                                     platform_information.get_device(), \
                                                                     platform_information.get_sw_version_old(),\
                                                                     platform_information.get_mcu_version())
            header = platform_information.get_header(platform_information.get_vin_version())
            print(header)
            print(data_json)
            return co.post_request_to_file(sn,header,data_json)
        except Exception as e:
            logger.log_error("%s" %(e),sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_md5_file(self,sn, flag):
        '''
        function: check md5 file
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        # package.flash_through_system(sn)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn,flag) == 0:
                    try:
                        sign_value = co.get_md5_value_from_datafile(sn,flag)
                        package_name = co.get_packagename_from_json_file(sn,flag)
                        expect_size = int(co.get_packagesize_from_json_file(sn,flag))
                        while True:
                            time.sleep(random.randint(20,60))
                            co.reboot_device(sn)
                            co.wait_hu_recovery(sn)
                            actual_size = co.check_package_size(sn,flag,30)
                            if int(actual_size) == expect_size:
                                break
                        if co.get_md5_value(sn, package_name, "hu_package.zip") == sign_value:
                            return 0
                        else:
                            return 1
                    except Exception as e:
                        logger.log_error("%s" %(e),\
                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return 1
            else:
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_delete_updatedirectory(self, sn, flag):
        '''
        function: check delete /update directory and reboot system
        :param sn:
        :return:
        '''
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network",\
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn, flag) == 0:
                    expect_size = int(co.get_packagesize_from_json_file(sn, flag))
                    while True:
                        actual_size = co.check_package_size(sn, flag, 30)
                        if int(actual_size) == expect_size:
                            break
                    while True:
                        if check_message.check_libHUfota_exist(sn):
                            time.sleep(random.randint(5,10))
                            co.delete_file(sn)
                            time.sleep(random.randint(5,10))
                            co.reboot_device(sn)
                            return co.wait_hu_recovery(sn)
                        else :
                            logger.log_error("can not find libHUfota log", \
                                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                            return 1
                else:
                    logger.log_error("check delete updated directory failed",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("flash system failed or start fota module failed", \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1

        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_activeupgrade(self,sn, flag):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        # package.flash_through_system(sn)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn,flag) == 0:
                    try:
                        expect_size = int(co.get_packagesize_from_json_file(sn,flag))
                        while True:
                            actual_size = co.check_package_size(sn,flag,30)
                            if int(actual_size) == expect_size:
                                break
                        if co.send_signal(sn, SL.ActiveUpgrade) == 0:
                            time.sleep(20)
                            if co.wait_hu_recovery(sn) == 0:
                                if self.check_system_version(sn) == 0:
                                    pcan = SC.PCAN()
                                    pcan.poweron_and_clean()
                                    return 0
                                else:
                                    return 1
                            else:
                                pcan = SC.PCAN()
                                pcan.poweron_and_clean()
                                logger.log_error("can not enter system",\
                                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                return 1
                        else:
                            pcan = SC.PCAN()
                            pcan.poweron_and_clean()
                            return 1
                    except Exception as e:
                        logger.log_error("%s" %(e),\
                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return 1
                else:
                    logger.log_error("can not find pakcage",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def prepare_activeupgrade_environment(self,sn, flag):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn,flag) == 0:
                    try:
                        expect_size = int(co.get_packagesize_from_json_file(sn,flag))
                        while True:
                            actual_size = co.check_package_size(sn,flag,30)
                            if int(actual_size) == expect_size:
                                break
                        return 0
                    except Exception as e:
                        logger.log_error("%s" %(e),\
                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return 1
                else:
                    logger.log_error("can not find pakcage",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_reboot_and_enter_installui(self, sn):
        '''
        :param sn:
        :param flag:
        :return:
        '''
        try:
            co.reboot_device(sn)
            time.sleep(5)
            if co.wait_hu_recovery(sn) == 0:
                if co.alway_send_signal(sn, SL.ActiveUpgrade) == 0:
                    return 0
                else :
                    pcan = SC.PCAN()
                    pcan.poweron_and_clean()
                    return 1
            else:
                logger.log_error("wait hu recovery fail",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_reboot_and_enter_installui_and_cancle(self, sn):
        '''
        :param sn:
        :param flag:
        :return:
        '''
        try:
            co.reboot_device(sn)
            time.sleep(5)
            if co.wait_hu_recovery(sn) == 0:
                if co.alway_send_signal(sn, SL.ActiveUpgrade) == 0:
                    if co.cancle_install_through_ui(sn) == 0:
                        return 0
                    else :
                        return 1
                else:
                    logger.log_error("can not find install ui", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("wait hu recovery fail",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_reboot_and_install(self, sn, flag):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        # package.flash_through_system(sn)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
                # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn, flag) == 0:
                    try:
                        expect_size = int(co.get_packagesize_from_json_file(sn, flag))
                        while True:
                            actual_size = co.check_package_size(sn, flag, 30)
                            if int(actual_size) == expect_size:
                                break

                        if self.check_reboot_and_enter_installui(sn) == 0:
                            if co.upgrade_through_ui(sn, SL.ActiveUpgrade) == 0:
                                time.sleep(20)
                                if co.wait_hu_recovery(sn) == 0:
                                    if self.check_system_version(sn) == 0:
                                        pcan = SC.PCAN()
                                        pcan.poweron_and_clean()
                                        return 0
                                    else:
                                        return 1
                                else:
                                    pcan = SC.PCAN()
                                    pcan.poweron_and_clean()
                                    logger.log_error("can not enter system", \
                                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                                     sys._getframe().f_lineno)
                                    return 1
                            else:
                                pcan = SC.PCAN()
                                pcan.poweron_and_clean()
                                return 1

                        else:
                            pcan = SC.PCAN()
                            pcan.poweron_and_clean()
                            logger.log_error("can not find install ui", \
                                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,\
                                             sys._getframe().f_lineno)
                            return 1
                    except Exception as e:
                        logger.log_error("%s" % (e), \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                         sys._getframe().f_lineno)
                        return 1
                else:
                    logger.log_error("can not find pakcage", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
            else:
                return 1
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def check_install_and_sendsignal(self, sn, flag):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        time.sleep(5)
        # package.flash_through_system(sn)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn,flag) == 0:
                    try:
                        expect_size = int(co.get_packagesize_from_json_file(sn,flag))
                        while True:
                            actual_size = co.check_package_size(sn,flag,30)
                            if int(actual_size) == expect_size:
                                break
                        if co.send_signal(sn, SL.ActiveUpgrade) == 0:
                            time.sleep(20)
                            if co.wait_hu_recovery(sn) == 0:
                                if self.check_system_version(sn) == 0:
                                    if co.alway_send_signal(sn,SL.ActiveUpgrade) == 1:
                                        return 0
                                    else:
                                        logger.log_error("expect no ui show,but ui has show",\
                                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                        return 1
                                else:
                                    return 1
                            else:
                                logger.log_error("can not enter system",\
                                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                return 1
                        else:
                            return 1
                    except Exception as e:
                        logger.log_error("%s" %(e),\
                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return 1
                else:
                    logger.log_error("can not find pakcage",\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def cancleinstall_through_setting(self, sn):
        '''
        :param sn:
        :param flag:
        :return:
        '''
        try:
            co.reboot_device(sn)
            time.sleep(5)
            if co.wait_hu_recovery(sn) == 0:
                if co.cancleinstall_through_setting(sn, SL.ActiveUpgrade) == 0:
                   return 0
                else:
                    logger.log_error("cancle upgrade failed", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("wait hu recovery fail",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def upgrade_through_setting(self, sn, flag):
        co.delete_file(sn)
        time.sleep(5)
        try:
            if package.update_system_through_fastboot(retry_times) == 0 and co.start_fota_daemon(sn) == 0:
            # if co.start_fota_daemon(sn) == 0:
                time.sleep(5)
                if self.get_requestdata_to_file(sn) == 1:
                    logger.log_error("maybe has no network", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
                if co.check_package_exist(sn, flag) == 0:
                    try:
                        expect_size = int(co.get_packagesize_from_json_file(sn, flag))
                        while True:
                            actual_size = co.check_package_size(sn, flag, 30)
                            if int(actual_size) == expect_size:
                                break

                        if co.activeupgrade_through_setting(sn, SL.ActiveUpgrade) == 0:
                            time.sleep(20)
                            if co.wait_hu_recovery(sn) == 0:
                                if self.check_system_version(sn) == 0:
                                    pcan = SC.PCAN()
                                    pcan.poweron_and_clean()
                                    return 0
                                else:
                                    pcan = SC.PCAN()
                                    pcan.poweron_and_clean()
                                    return 1
                            else:
                                pcan = SC.PCAN()
                                pcan.poweron_and_clean()
                                logger.log_error("can not enter system", \
                                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                                 sys._getframe().f_lineno)
                                return 1
                        else:
                            pcan = SC.PCAN()
                            pcan.poweron_and_clean()
                            return 1
                    except Exception as e:
                        logger.log_error("%s" % (e), \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                         sys._getframe().f_lineno)
                        return 1
                else:
                    logger.log_error("can not find pakcage", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
            else:
                return 1
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1











