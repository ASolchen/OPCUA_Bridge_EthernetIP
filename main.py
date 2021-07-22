import sys
sys.path.insert(0, "..")
import time

from opcua import ua, Server
from opcua.ua.object_ids import ObjectIds as dt
from opcua.ua.uaerrors import BadNoMatch

from pycomm3 import LogixDriver
import json



class OpcConnection(object):
    def __init__(self, dev_conx) -> None:
        super().__init__()
        self.dev_conx = dev_conx
        # setup our server
        self.server = Server()
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840/ethernetip/server/")
        # setup our own namespace, not really necessary but should as spec
        uri = "https://github.com/ASolchen"
        idx = server.register_namespace("ETHIP_BRIDGE")

        # get Objects node, this is where we should put our nodes
        self.objects_node = server.get_objects_node()

        # populating our address space
        self.tag_root_node = self.objects_node.add_object(idx, "PYCOMM")

        try:

            # starting!
            self.server.start()
            while True:
                time.sleep(0.01) #EthernetIP pollrate
                #poll EthernetIP here
        finally:
            #close connection, remove subcsriptions, etc
            self.server.stop()

class LogixAtomicTag(object):
    def __init__(self, tag_obj) -> None:
        super().__init__()
        self.tag_name = tag_obj['tag_name']
        self.dim = tag_obj['dim']
        self.symbol_address = tag_obj['symbol_address']
        self.symbol_object_address = tag_obj['symbol_object_address']
        self.software_control = tag_obj['software_control']
        self.alias = tag_obj['alias']
        self.external_access = tag_obj['external_access']
        self.dimensions = tag_obj['dimensions']
        self.tag_type = tag_obj['tag_type']
        self.data_type = tag_obj['data_type']



class DeviceConnection(object):

    def __init__(self) -> None:
        super().__init__()
        self.tags = {}
        try:
            with LogixDriver('10.10.90.169') as plc:
                l = plc.get_tag_list()
                with open("PLC_getlist.json", "w") as fp:
                    fp.write(json.dumps(l, sort_keys=True, indent=4))
                
        except Exception as e:
            print(e)
            try:
                with open("PLC_getlist.json", "r") as fp:
                    l = json.loads(fp.read())

            except Exception as e:
                print(e)
                sys.exit()
        for tag_obj in l:
                    if tag_obj['tag_type'] == 'atomic':
                        tag = tag_obj['tag_name']
                        self.tags[tag] = LogixAtomicTag(tag_obj)
                    else:
                        print(tag_obj)

if __name__ == "__main__":
    DeviceConnection()