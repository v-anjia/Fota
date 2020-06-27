from Test_Tbox import  Test_activeupgrade as TB_Tau
from Test_Tbox import  Test_activeupgrade_install_and_sendsignal as Taias
from Test_Tbox import  Test_activeupgrade_reboot as TB_Tar
from Test_Tbox import  Test_activeupgrade_rebootand_cancleupgrade as TB_Tarcp
from Test_Tbox import  Test_activeupgrade_rebootand_install as TB_Tari
from Test_Tbox import  Test_setting_to_activeupgrade as TB_Tstau
from Test_Tbox import  Test_setting_to_cancleupgrade as TB_Tstcu
from log import logger as loger
import  sys
import time
import os
import pytest
from pytest_html import plugin
from pytest_html import hooks
from pytest_html import extras

logger = loger.Current_Module()
class Test_Tbox_OTA():
    @pytest.fixture(scope='function', autouse=True)
    def message(self):
        '''check test environment'''
        logger.log_info("start Test", sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        yield
        logger.log_info("end Test", sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)

    def test_activeupgrade(self):
        if TB_Tau.test() == 1:
            assert False
        assert True

    def test_activeupgrade_reboot(self):
        if TB_Tar.test() == 1:
            logger.log_error("active upgrade reboot test failed ",sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
            assert  False
        assert  True

    def test_activeupgrade_install_and_sendsignal(self):
        if Taias.test() == 1:
            logger.log_error("active upgrade reboot test failed ", sys._getframe().f_code.co_filename,
                             sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            assert False
        assert True
    
    def test_activeupgrade_rebootand_cancleupgrade(self):
        if TB_Tarcp.test() == 1:
            logger.log_error("active upgrade reboot test failed ", sys._getframe().f_code.co_filename,
                             sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            assert False
        assert  True

    def test_activeupgrade_rebootand_install(self):
        if TB_Tari.test() == 1:
            logger.log_error("active upgrade reboot test failed ", sys._getframe().f_code.co_filename,
                             sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            assert  False
        assert  True

    def test_setting_to_activeupgrade(self):
        if TB_Tstau.test() == 1:
            logger.log_error("active upgrade reboot test failed ", sys._getframe().f_code.co_filename,
                             sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            assert False
        assert True

    def test_setting_to_cancleupgrade(self):
        if TB_Tstcu.test() == 1:
            logger.log_error("active upgrade reboot test failed ", sys._getframe().f_code.co_filename,
                             sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            assert False
        assert  True

