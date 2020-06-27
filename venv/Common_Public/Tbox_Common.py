'''
Tbox function
date :2019-7-22
@author: antony weijiang
'''
from Common_Public import Common as co
from Common_Public import Signal_Common as SC
from Common_Public import Signal_List as SL
from log import logger as loger
import os
import subprocess
import serial
import pytest
import sys
import time

tbox_flag = "tbox"
busybox = "/oem/bin/busybox"
adbd_backup = "/system/bin/adbd_bak"
adbd = "/system/bin/adbd"
tbox_message = "/update/tbox/"
tbox_verison = "/data/version.txt"
# tbox_verison = "/wm/update/version.txt"
version_file = "/update/version.txt"
tbox_update_log = "/update/log/."
# tbox_update_log = "/wm/update/log/."
json_name = "/update/data.json"
tbox_mcu = "/update/package/tbox/mcu"
tbox_mpu = "/update/package/tbox/mpu"
mcu_flag = "mcu"
mpu_flag = "mpu"
logcat_object = None

logger = loger.Current_Module()
retry_time = 5
package = co.Install_Package()
platform_information = co.Platform_Information()
adb_sn  = co.ADB_SN()

class Tbox_Information(object):
    def __init__(self,fun):
        self.serial_child = co.Serial()
        # self.serial_child.set_serialport()
        # self.ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        package = co.Install_Package()
        self.fun = fun

    def __enter__(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        str_msg = "mkdir -p %s\r\n" %(tbox_message)
        ser.write(str_msg.encode('utf-8'))
        return self

    @classmethod
    def check_system_version(cls, sn):
        '''
        function:check system version
        :param sn:
        :return:
        '''
        # cls.disable_hu_adb()
        current_version = package.get_tbox_verison(sn)
        filelist = package.update_fota_package()
        print(current_version)
        if current_version == filelist[6]:
            print("0")
            return 0
        elif current_version == filelist[7]:
            print("1")
            return 1

    @classmethod
    def modify_tbox_config(cls,sn):
        filelist = package.update_fota_package()
        str_msg = "echo -en '%s\\n%s\\n' > %s" %(filelist[12],filelist[13],version_file)
        os.system('adb -s %s shell "%s"' %(sn, str_msg))
        os.system('adb -s %s shell "adb push %s %s "' %(sn ,version_file,tbox_verison))

        
    @classmethod    
    def check_ping_value(cls,sn):
        '''
        function: check ping value
        :return:
        '''
        try:
            filelist = package.update_fota_package()
            if co.removal(subprocess.check_output('adb -s %s shell "ping -c 3 %s >/dev/null 2>&1 ;echo $?"' %(sn, filelist[10]),shell=True,stderr=subprocess.PIPE)).strip() == '0':
                return 0
            else :
                return 1
        except Exception as e:
            return 1

    @classmethod
    def copy_version_to_hu(cls,sn):
        os.system('adb -s %s shell "mount -o rw,remount /"' %(sn))
        os.system('adb -s %s shell "adb pull /data/version.txt  /update/"' %(sn))
        # ser.write("adb pull /data/version.txt  /update/\r\n")

    def disable_hu_adb(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        ser.write("mount -o rw,remount /system\r\n".encode('utf-8'))
        str_msg = "mv %s %s\r\n" % (adbd,adbd_backup)
        ser.write(str_msg.encode('utf-8'))
        str_msg = "ps -ef|grep adbd |grep -v grep| %s awk '{print $2}'|xargs kill -9 \r\n" % (busybox)
        ser.write(str_msg.encode('utf-8'))

    def enable_hu_adb(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        ser.write("mount -o rw,remount /system\r\n".encode('utf-8'))
        str_msg = "mv %s %s \r\n" % (adbd_backup,adbd)
        ser.write(str_msg.encode('utf-8'))
        ser.write("reboot\r\n".encode('utf-8'))

    def init_environment(self):
        logger.log_info("start fastboot hu",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        package.down_fastboot_package_to_local(package.update_fota_package(),package.oldDate())
        package.unzip_fastboot_package()
        package.update_system_through_fastboot(retry_time)

    def delete_update_directory(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        ser.write("mount -o rw,remount /;rm -rf /update/*\r\n".encode('utf-8'))

    def reboot(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        ser.write("reboot\r\n".encode('utf-8'))

    def pull_tbox_version(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        str_msg = "adb pull %s %s" %(tbox_verison,tbox_message)
        ser.write(str_msg.encode('utf-8'))

    def pull_tbox_update(self):
        self.serial_child.set_serialport()
        ser = serial.Serial(self.serial_child.get_serialport(), self.serial_child.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        str_msg = "adb pull %s %s" %(tbox_update_log,tbox_message)
        ser.write(str_msg.encode('utf-8'))

    def __call__(self, *args, **kwargs):
        logger.log_info("init tbox test environment",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

        self.fun()
        self.init_environment()

    def __exit__(self, sn, exc_type, exc_val, exc_tb):
        self.delete_update_directory()

@Tbox_Information
def enter_tbox_test():
    logger.log_info("first,fastboot hu version",\
                    sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)


class tbox_common(object):
    def __init__(self):
        # self.get_requestdata_to_file()
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

    def get_requestdata_to_file(self, sn):
        '''
        request json file
        :param sn:
        :return:
        '''
        try:
            global logcat_object
            logcat_object = co.Set_Logcat_Message(sn)
            filelist = package.update_fota_package()
            platform_information.set_device("tbox")
            platform_information.set_vin_version(filelist[5])
            platform_information.set_sw_version_new(filelist[7])
            platform_information.set_sw_version_old(filelist[7])
            platform_information.set_mcu_version(filelist[8])
            data_json = platform_information.temporary_get_port_data(platform_information.get_vin_version(),
                                                                     platform_information.get_device(), \
                                                                     platform_information.get_sw_version_old(),\
                                                                     platform_information.get_mcu_version())
            header = platform_information.get_header(platform_information.get_vin_version())
            # print(header)
            # print(data_json)
            co.post_request(sn, header, data_json)
            return co.post_request_to_file(sn, header, data_json)
        except Exception as e:
            logger.log_error("%s" % (e), sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def get_mcu_and_mpu_name(self, sn, flag, delay_time = 30):
        '''
        get mcu and mpu name
        :param flag:
        :return:
        '''
        if flag == mpu_flag:
            # print("antony@@@debug")
            str_msg = "%s sed 's/.*file_name.\{3\}\(.*\).\{3\}.*file_size.*file_name.*/\\1/' %s"  %(busybox, json_name)
        elif flag == mcu_flag:
            str_msg = "%s sed 's/.*file_name.\{3\}\(.*\).\{3\}.*file_size.*file_name.\{3\}\(.*\).\{3\}file_size.*/\\2/' %s" %(busybox, json_name)
        cmd = 'adb -s %s shell "if [ -f %s ]; then %s;fi"' % (sn, json_name, str_msg)
        while True:
            try:
                if co.removal(subprocess.check_output(cmd)):
                    logger.log_debug("will download package name is %s" % (co.removal(subprocess.check_output(cmd))), \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return co.removal(subprocess.check_output(cmd))
                delay_time = delay_time - 1
                if delay_time >= 0:
                    logger.log_debug("wait ...", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    time.sleep(2)
                else:
                    logger.log_error("Client receive fail,can not find data.json file", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return None
            except Exception as e:
                logger.log_error("%s" % (e), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return None

    def get_mcu_and_mpu_size(self, sn, flag, delay_time = 300):
        '''
        get mcu and mpu size
        :param flag:
        :return:
        '''
        if flag == mpu_flag:
            # print("antony@@@debug")
            str_msg = "%s sed 's/.*file_size.\{2\}\([0-9]*\).*file_size.*/\\1/' %s"  %(busybox, json_name)
        elif flag == mcu_flag:
            str_msg = "%s sed 's/.*file_size.*file_size.\{2\}\([0-9]*\).*/\\1/' %s" %(busybox, json_name)
        cmd = 'adb -s %s shell "if [ -f %s ]; then %s;fi"' % (sn, json_name, str_msg)
        while True:
            try:
                if co.removal(subprocess.check_output(cmd)):
                    logger.log_debug("will download %s package name is %s" % (flag,co.removal(subprocess.check_output(cmd))), \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return co.removal(subprocess.check_output(cmd))
                delay_time = delay_time - 1
                if delay_time >= 0:
                    logger.log_debug("wait ...", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    time.sleep(2)
                else:
                    logger.log_error("Client receive fail,can not find data.json file", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return None
            except Exception as e:
                logger.log_error("%s" %(e), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return None

    def check_package_exist(self,sn,flag,delay_time = 300):
        '''
        get mcu or mpu package size
        :param flag:
        :return:
        '''
        package_name = self.get_mcu_and_mpu_name(sn, flag)
        if flag == mcu_flag:
            cmd = 'adb -s %s shell "ls -al %s/%s |%s wc -l 2>&1"' % (sn, tbox_mcu, package_name, busybox)
        elif flag == mpu_flag:
            cmd = 'adb -s %s shell "ls -al %s/%s |%s wc -l 2>&1"' % (sn, tbox_mpu, package_name, busybox)
        while True:
            try:
                print(co.removal(subprocess.check_output(cmd).strip()))
                if '1' in co.removal(subprocess.check_output(cmd).strip()):
                    logger.log_debug("%s exists and downloading ..." % (package_name), \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 0
                delay_time = delay_time - 1
                if delay_time >= 0:
                    logger.log_debug("wait a minute...", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    time.sleep(2)
                else:
                    logger.log_error("can not find %s," % (package_name), \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
            except Exception as e:
                logger.log_error("%s" % (e), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1


    def current_mcu_and_mpu_size(self, sn, flag):
        try:
            if self.get_mcu_and_mpu_name(sn, flag) != 'None':
                if flag == mcu_flag:
                    str_msg = "ls -al %s/%s |%s awk '{print $5}'" % (tbox_mcu, self.get_mcu_and_mpu_name(sn, flag), busybox)
                elif flag == mpu_flag:
                    str_msg = "ls -al %s/%s |%s awk '{print $5}'" % (tbox_mpu, self.get_mcu_and_mpu_name(sn, flag), busybox)
                cmd = 'adb -s %s shell "%s"' % (sn, str_msg)
                if int(co.removal(subprocess.check_output(cmd)).strip()) >= 0:
                    logger.log_debug("has downloaded %s package size: %s" % (flag,co.removal(subprocess.check_output(cmd))), \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return co.removal(subprocess.check_output(cmd)).strip()
                else:
                    logger.log_debug("can not find package size ,may be has  download well", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1

            else :
                logger.log_error("can not find %s name" %(flag),sys._getframe().f_code.co_filename, \
                                 sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %e,sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,\
                             sys._getframe().f_lineno)
            return 1

    def mcu_mpu_download_status(self,sn,flag,delay_time = 1200):
        '''
        get mcu and mpu download status
        :param sn:
        :param flag:
        :return:
        '''
        try:
            expect_size = int(self.get_mcu_and_mpu_size(sn, flag))
            if self.check_package_exist(sn,flag) == 0:
                while delay_time > 0:
                    actual_size = self.current_mcu_and_mpu_size(sn, flag)
                    if int(actual_size) == expect_size:
                        return 0
                    else:
                        delay_time = delay_time - 1
                return 1
            else:
                logger.log_error("can not find %s package" %(flag), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return  1
        except Exception as e:
            logger.log_error("%s" %(e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)

    def check_hu_network(self, sn):
        '''
        function: check hu network
        :param sn:
        :return:
        '''
        while True:
            if Tbox_Information.check_ping_value(sn) == 0:
                break
            else:
                for i in range(1, 10):
                    if Tbox_Information.check_ping_value(sn) == 0:
                        break
                    else:
                        time.sleep(random.randint(1, 3))
            break

    def check_activeupgrade(self, sn, flag_mcu, flag_mpu):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        co.reboot_device(sn)
        co.wait_hu_recovery(sn)
        self.check_hu_network(sn)
        # time.sleep(5)
        try:
            if self.get_requestdata_to_file(sn) == 1:
                logger.log_error("maybe has no network", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
            pcan = SC.PCAN()
            pcan.poweron_and_clean()
            if self.mcu_mpu_download_status(sn,flag_mpu) == 0 and self.mcu_mpu_download_status(sn,flag_mcu) == 0:
                try:
                    if co.check_md5_status(sn) == 0:
                        if co.send_signal(sn, SL.ActiveUpgrade,tbox_flag) == 0:
                            time.sleep(20)
                            if co.wait_hu_recovery(sn) == 0:
                                while True:
                                    if Tbox_Information.check_ping_value(sn) == 0:
                                        co.open_tbox_adb()
                                        time.sleep(5)
                                        break

                                Tbox_Information.copy_version_to_hu(sn)
                                if Tbox_Information.check_system_version(sn) == 0:
                                    Tbox_Information.modify_tbox_config(sn)
                                    pcan = SC.PCAN()
                                    pcan.poweron_and_clean()
                                    return 0
                                else:
                                    Tbox_Information.modify_tbox_config(sn)
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
                        logger.log_error("check md5 value failed", \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
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
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def check_install_and_sendsignal(self, sn, flag_mcu, flag_mpu):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        co.reboot_device(sn)
        co.wait_hu_recovery(sn)
        self.check_hu_network(sn)
        # time.sleep(5)
        # package.flash_through_system(sn)
        try:
            if self.get_requestdata_to_file(sn) == 1:
                logger.log_error("maybe has no network",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
            pcan = SC.PCAN()
            pcan.poweron_and_clean()
            if self.mcu_mpu_download_status(sn,flag_mpu) == 0 and self.mcu_mpu_download_status(sn,flag_mcu) == 0:
                try:
                    if co.check_md5_status(sn) == 0:
                        if co.send_signal(sn, SL.ActiveUpgrade,tbox_flag) == 0:
                            time.sleep(20)
                            if co.wait_hu_recovery(sn) == 0:
                                while True:
                                    if Tbox_Information.check_ping_value(sn) == 0:
                                        co.open_tbox_adb()
                                        time.sleep(5)
                                        break
                                Tbox_Information.copy_version_to_hu(sn)
                                if Tbox_Information.check_system_version(sn) == 0:
                                    if co.alway_send_signal(sn,SL.ActiveUpgrade) == 1:
                                        Tbox_Information.modify_tbox_config(sn)
                                        return 0
                                    else:
                                        logger.log_error("expect no ui show,but ui has show",\
                                                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                        Tbox_Information.modify_tbox_config(sn)
                                        return 1
                                else:
                                    return 1
                            else:
                                logger.log_error("can not enter system",\
                                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                return 1
                        else:
                            return 1
                    else:
                        logger.log_error("check md5 value failed", \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                         sys._getframe().f_lineno)
                        return 1
                except Exception as e:
                    logger.log_error("%s" %(e),\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("can not find pakcage",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def prepare_activeupgrade_environment(self, sn, flag_mcu, flag_mpu):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        co.reboot_device(sn)
        co.wait_hu_recovery(sn)
        self.check_hu_network(sn)
        # time.sleep(5)
        try:
            if self.get_requestdata_to_file(sn) == 1:
                logger.log_error("maybe has no network", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
            pcan = SC.PCAN()
            pcan.poweron_and_clean()
            if self.mcu_mpu_download_status(sn,flag_mpu) == 0 and self.mcu_mpu_download_status(sn,flag_mcu) == 0:
                try:
                    if co.check_md5_status(sn) == 0:
                        return 0
                    else:
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
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def check_reboot_and_enter_installui(self, sn):
        '''
        :param sn:
        :param flag:
        :return:
        '''
        try:
            # co.reboot_device(sn)
            co.reboot_device(sn)
            # co.wait_hu_recovery(sn)
            time.sleep(5)
            if co.wait_hu_recovery(sn) == 0:
                if co.alway_send_signal(sn, SL.ActiveUpgrade) == 0:
                    return 0
                else:
                    pcan = SC.PCAN()
                    pcan.poweron_and_clean()
                    return 1
            else:
                logger.log_error("wait hu recovery fail", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def check_reboot_and_enter_installui_and_cancle(self, sn):
        '''
        :param sn:
        :param flag:
        :return:
        '''
        try:
            # co.reboot_device(sn)
            co.reboot_device(sn)
            co.wait_hu_recovery(sn)
            time.sleep(5)
            if co.wait_hu_recovery(sn) == 0:
                if co.alway_send_signal(sn, SL.ActiveUpgrade) == 0:
                    if co.cancle_install_through_ui(sn) == 0:
                        return 0
                    else:
                        return 1
                else:
                    logger.log_error("can not find install ui", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return 1
            else:
                logger.log_error("wait hu recovery fail", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def check_reboot_and_install(self, sn, flag_mcu, flag_mpu):
        '''
        function: check active upgrade
        :param sn:
        :return:
        '''
        co.delete_file(sn)
        co.reboot_device(sn)
        co.wait_hu_recovery(sn)
        self.check_hu_network(sn)
        # time.sleep(5)
        # package.flash_through_system(sn)
        try:
            if self.get_requestdata_to_file(sn) == 1:
                logger.log_error("maybe has no network", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
            if self.mcu_mpu_download_status(sn, flag_mpu) == 0 and self.mcu_mpu_download_status(sn, flag_mcu) == 0:
                try:
                    if co.check_md5_status(sn) == 0:
                        if self.check_reboot_and_enter_installui(sn) == 0:
                            if co.upgrade_through_ui(sn, SL.ActiveUpgrade, tbox_flag) == 0:
                                time.sleep(20)
                                if co.wait_hu_recovery(sn) == 0:
                                    while True:
                                        if Tbox_Information.check_ping_value(sn) == 0:
                                            co.open_tbox_adb()
                                            time.sleep(5)
                                            break
                                    Tbox_Information.copy_version_to_hu(sn)
                                    if Tbox_Information.check_system_version(sn) == 0:
                                        Tbox_Information.modify_tbox_config(sn)
                                        pcan = SC.PCAN()
                                        pcan.poweron_and_clean()
                                        return 0
                                    else:
                                        Tbox_Information.modify_tbox_config(sn)
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
                    else:
                        logger.log_error("check md5 value failed", \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
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
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def cancleinstall_through_setting(self, sn):
        '''
        :param sn:
        :param flag:
        :return:
        '''
        try:
            # co.reboot_device(sn)
            co.reboot_device(sn)
            co.wait_hu_recovery(sn)
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
                logger.log_error("wait hu recovery fail", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def upgrade_through_setting(self, sn, flag_mcu, flag_mpu):
        co.delete_file(sn)
        co.reboot_device(sn)
        co.wait_hu_recovery(sn)
        self.check_hu_network(sn)
        # time.sleep(5)
        try:
            if self.get_requestdata_to_file(sn) == 1:
                logger.log_error("maybe has no network", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
            pcan = SC.PCAN()
            pcan.poweron_and_clean()
            if self.mcu_mpu_download_status(sn, flag_mpu) == 0 and self.mcu_mpu_download_status(sn, flag_mcu) == 0:
                try:
                    if co.check_md5_status(sn) == 0:
                        if co.activeupgrade_through_setting(sn, SL.ActiveUpgrade, tbox_flag) == 0:
                            time.sleep(20)
                            if co.wait_hu_recovery(sn) == 0:
                                while True:
                                    if Tbox_Information.check_ping_value(sn) == 0:
                                        co.open_tbox_adb()
                                        time.sleep(5)
                                        break

                                Tbox_Information.copy_version_to_hu(sn)

                                if Tbox_Information.check_system_version(sn) == 0:
                                    Tbox_Information.modify_tbox_config(sn)
                                    pcan = SC.PCAN()
                                    pcan.poweron_and_clean()
                                    return 0
                                else:
                                    Tbox_Information.modify_tbox_config(sn)
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
                    else:
                        logger.log_error("check md5 value failed", \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
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
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1














