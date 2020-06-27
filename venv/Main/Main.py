'''
Main.py The main entrance to the project
date :2019-3-27
@author: antony weijiang
'''
#coding=utf-8
import argparse
import subprocess
import sys
import os
import time
import serial
import pytest
from pytest_html import plugin
from pytest_html import hooks
from pytest_html import extras

from Common_Public import Hu_Common as hu_c
from Common_Public import Common as co
from log import logger as loger
from Common_Public import Signal_Common as SC
from Common_Public import Signal_List as SL
from Common_Public import Tbox_Common as TC

from Test_Tbox import Test_activeupgrade as TB_Tau
from Test_Tbox import Test_activeupgrade_install_and_sendsignal as Taias
from Test_Tbox import Test_activeupgrade_reboot as TB_Tar
from Test_Tbox import Test_activeupgrade_rebootand_cancleupgrade as TB_Tarcp
from Test_Tbox import Test_activeupgrade_rebootand_install as TB_Tari
from Test_Tbox import Test_setting_to_activeupgrade as TB_Tstau
from Test_Tbox import Test_setting_to_cancleupgrade as TB_Tstcu

from Common_Public import Tbox_Common as tbc

retry_time = 5
package = co.Install_Package()
logger = loger.Current_Module()
case_dict_diff={'1':['Test_interface_post','Tpost.test'],'2':['Test_delete_updatedirectory','Tdel.test'],\
                '3':['Test_hu_diff_package','Tdiff.test'],'4':['Test_check_diff_package_md5','Td_md5.test'],\
                '5':['Test_diff_package_breakpoint_resume_with_hu_reboot','TDbre_reboot.test'],'6':['Test_diff_package_breakpoint_resume_with_tboxsignal','TDbre_tboxsignal.test']}

case_dict_full={'1':['Test_interface_post','Tpost.test'],'2':['Test_delete_updatedirectory','Tdel.test'],\
                '3':['Test_hu_full_package','Tfull.test'],'4':['Test_check_package_md5','T_md5.test'],\
                '5':['Test_breakpoint_resume_with_tboxsignal','Tbre_signal.test'],'6':['Test_brerakpoint_resume_with_hu_reboot','Tbre_reboot.test'],\
                '7':['Test_activeupgrade','Tau.test'],'8':['Test_activeupgrade_reboot','Tar.test'],\
                '9':['Test_activeupgrade_rebootand_cancleupgrade','Tarcp.test'],'10':['Test_activeupgrade_rebootand_install','Tari.test'],\
                '11':['Test_activeupgrade_install_and_sendsignal','Taias.test'],'12':['Test_setting_to_cancleupgrade','Tstcu.test'],\
                '13':['Test_setting_to_activeupgrade','Tstau.test'],
                }

case_dict_tbox={'1':['Test_activeupgrade','TB_Tau.test'],'2':['Test_activeupgrade_install_and_sendsignal','Taias.test'],\
                '3':['Test_activeupgrade_reboot','TB_Tar.test'],'4':['Test_activeupgrade_rebootand_cancleupgrade','TB_Tarcp'],\
                '5':['Test_activeupgrade_rebootand_install','TB_Tari.test'],'6':['Test_setting_to_activeupgrade','TB_Tstau'],\
                '7':['Test_setting_to_cancleupgrade','TB_Tstcu.test']}

def Main():
    parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]')
    parser.add_argument('--account', dest="account", metavar='account', help="choose capture picture")
    parser.add_argument('--time', dest='time', metavar='run times', help='how long time cases need to run(hours)')
    # arg = parser.parse_args(['--account', '20'])
    arg = parser.parse_args(['--time','24'])
    if arg.time is not None:
        current_time = int(time.time())
        loop_time = current_time + int(arg.time) * 3600
        time.sleep(1)
        while current_time <= loop_time:
            pytest.main(['-s', '%s' % (os.getcwd() + "\..\TestCase"), '--html',
                         'Report_%s.html' % (current_time),'--self-contained-html'])
            current_time = int(time.time())

    if arg.account is not None:
        account = int(arg.account)
        current_time = int(time.time())
        pytest.main(
            ['-s', '--repeat-scope', 'class', '--count', '%s' % (arg.account), '%s' % (os.getcwd() + "\..\TestCase"),
             '--html', 'Report_%s.html' % (current_time),'--self-contained-html'])
        

if __name__ == "__main__":
    # TC.enter_tbox_test()
    Main()
    # TC.Tbox_Information.modify_tbox_config("1201400c5fc40120")






