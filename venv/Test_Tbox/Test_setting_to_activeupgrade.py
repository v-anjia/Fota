'''
Main.py The main entrance to the project
date :2019-6-11
@author: antony weijiang
'''
from log import logger as loger
from Common_Public import Common as co
from Common_Public import Tbox_Common as tb_c
import time
import os
import sys

tbox_common = tb_c.tbox_common()
logger = loger.Current_Module()

def test():
    logger.log_info("start tbox active upgrade test", \
                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    co.ADB_SN().check_adb_device_isalive()
    sn = tbox_common.check_sn_status()
    count_pass = 0
    count_fail = 0
    Result = tbox_common.upgrade_through_setting(sn, "mcu", "mpu")
    if Result == 0:
        count_pass = count_pass + 1
        # scp = co.Set_Screencap_Message(sn)
        # # co.Get_Logcat_Message(sn, co.logcat_object)
        # co.Get_Screencap_Message(sn, scp)
        # co.Get_libHU_Message(sn)
        logger.Current_Result(count_fail + count_pass, count_pass, count_fail,
                              os.path.basename(__file__).strip('.py'))
        return 0
        # print(count_pass)
    elif Result == 1:
        co.ADB_SN().check_adb_device_isalive()
        co.open_tbox_adb()
        time.sleep(10)
        tb_c.Tbox_Information.modify_tbox_config(sn)
        count_fail = count_fail + 1
        scp = co.Set_Screencap_Message(sn)
        # co.Get_Logcat_Message(sn, co.logcat_object)
        co.Get_Screencap_Message(sn, scp)
        co.Get_libHU_Message(sn)
        logger.Current_Result(count_fail + count_pass, count_pass, count_fail,
                              os.path.basename(__file__).strip('.py'))
        return 1
    
# def test(date_time = None, loop_count = None):
#     '''
#     function: this function for hu active upgrade test
#     :return:
#     '''
#     logger.log_info("start hu active upgrade test", \
#                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
#     count_pass = 0
#     count_fail = 0
#     sn = tbox_common.check_sn_status()
#     if date_time == None and loop_count == None:
#         logger.log_error("has no right argument",\
#                          sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
#         sys.exit(-1)
#     elif date_time != None and loop_count == None:
#         current_time = int(time.time())
#         loop_time = current_time + date_time*3600
#         time.sleep(1)
#         while current_time <= loop_time:
#             Result = tbox_common.upgrade_through_setting(sn, "mcu", "mpu")
#             if Result == 0:
#                 count_pass = count_pass + 1
#                 logger.Current_Result(count_fail + count_pass, count_pass, count_fail,
#                                     os.path.basename(__file__).strip('.py'))
#             elif Result == 1:
#                 count_fail = count_fail + 1
#                 scp = co.Set_Screencap_Message(sn)
#                 # co.Get_Logcat_Message(sn, co.logcat_object)
#                 co.Get_Screencap_Message(sn, scp)
#                 co.Get_libHU_Message(sn)
#                 logger.Current_Result(count_fail + count_pass, count_pass, count_fail,
#                                       os.path.basename(__file__).strip('.py'))
#             current_time = int(time.time())
#     elif date_time == None and loop_count != None:
#         time.sleep(1)
#         while loop_count > 0:
#             Result = tbox_common.upgrade_through_setting(sn, "mcu", "mpu")
#             if Result == 0:
#                 count_pass = count_pass + 1
#                 scp = co.Set_Screencap_Message(sn)
#                 # co.Get_Logcat_Message(sn, co.logcat_object)
#                 co.Get_Screencap_Message(sn, scp)
#                 co.Get_libHU_Message(sn)
#                 logger.Current_Result(count_fail + count_pass, count_pass, count_fail,
#                                       os.path.basename(__file__).strip('.py'))
#                 # print(count_pass)
#             elif Result == 1:
#                 count_fail = count_fail + 1
#                 scp = co.Set_Screencap_Message(sn)
#                 # co.Get_Logcat_Message(sn, co.logcat_object)
#                 co.Get_Screencap_Message(sn, scp)
#                 co.Get_libHU_Message(sn)
#                 logger.Current_Result(count_fail + count_pass, count_pass, count_fail,
#                                       os.path.basename(__file__).strip('.py'))
#             loop_count = loop_count - 1
# 
#     print ("summary:\n")
#     logger.Total_Result(count_fail + count_pass,count_pass,count_fail,os.path.basename(__file__).strip('.py'))








