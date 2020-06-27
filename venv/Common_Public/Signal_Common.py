'''
deposit public class or function
data:2019-6-3
@author antony weijiang
'''
import can
import time
from Common_Public import Signal_List as SL

class PCAN(object):
    def __enter__(self):
        return self

    def __init__(self):
        self.bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)

    def send(self, id, data):
        id = int(id,16)
        data = list(map(lambda i: int(i), data))
        # print(id, list(data))
        msg = can.Message(arbitration_id=id, dlc=8, data=data, extended_id=True)
        try:
            self.bus.send(msg)
            print("Message sent on {}".format(self.bus.channel_info))
        except can.CanError:
            print('Message NOT sent')

    def send_arry(self, arry_list = []):
        for i in arry_list:
            self.send(i['id'], i['data'])
        time.sleep(0.2)

    def clean(self):
        self.bus.shutdown()
    
    def poweron_and_clean(self):
        for i in range(50):
            self.send(SL.PowerOn[0]['id'],SL.PowerOn[0]['data'])
            time.sleep(0.2)
        self.bus.shutdown()

    def prepare_poweron(self):
        for i in range(5):
            self.send(SL.PowerOn[0]['id'],SL.PowerOn[0]['data'])
            time.sleep(0.2)
        self.bus.shutdown()

    def poweroff_and_clean(self):
        for i in range(100):
            self.send(SL.Poweroff[0]['id'],SL.Poweroff[0]['data'])
            time.sleep(0.2)
        self.bus.shutdown()

    def enterota(self):
        for i in range(100):
            print("send signal:%s" %(i))
            self.send(SL.EnterOtaPattern[0]['id'],SL.EnterOtaPattern[0]['data'])
            time.sleep(0.2)

    def enter_ota_lopper(self):
        self.send(SL.EnterOtaPattern[0]['id'], SL.EnterOtaPattern[0]['data'])
        time.sleep(0.2)

    def exitota(self):
        self.send(SL.ExitOtaPattern[0]['id'],SL.ExitOtaPattern[0]['data'])
        time.sleep(0.2)

    def exit_ota_lopper(self):
        for i in range(50):
            self.send(SL.ExitOtaPattern[0]['id'],SL.ExitOtaPattern[0]['data'])
            time.sleep(0.2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i in range(10):
            self.send(SL.PowerOn[0]['id'],SL.PowerOn[0]['data'])
            time.sleep(0.1)
        self.bus.shutdown()



    

