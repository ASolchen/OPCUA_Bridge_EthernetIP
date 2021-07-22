import sys
sys.path.insert(0, "..")
import time
import threading

from opcua import ua, Server
from opcua.ua.object_ids import ObjectIds
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
        self.uri = "https://github.com/ASolchen"
        self.idx = self.server.register_namespace("ETHIP_BRIDGE")

        # get Objects node, this is where we should put our nodes
        self.objects_node = self.server.get_objects_node()

        # populating our address space
        self.tag_root_node = self.objects_node.add_object(self.idx, "PYCOMM")

    def start(self):
        try:
            self.dev_conx.subcribed_tags.append({'tag_name':'Tag1', 'tag_obj': None, 'node': None})
            self.dev_conx.subcribed_tags.append({'tag_name':'Tag2', 'tag_obj': None, 'node': None})
            self.dev_conx.subcribed_tags.append({'tag_name':'Tag3', 'tag_obj': None, 'node': None})
            # starting!
            self.server.start()
            while True:
                for tag in self.dev_conx.subcribed_tags:
                    if tag['tag_obj']:
                        if not tag['node']:
                            tag['node'] = self.tag_root_node.add_variable(self.idx, tag['tag_name'], tag['tag_obj'][1])
                            tag['node'].set_writable()
                        tag['node'].set_value(tag['tag_obj'][1])
                        print(tag)
                time.sleep(0.5) #OPC pollrate
        finally:
            #close connection, remove subcsriptions, etc
            self.server.stop()



class DeviceConnection(object):

    def __init__(self) -> None:
        super().__init__()
        self.tags = None
        self.pollrate = 0.5
        self.poll_thread = threading.Thread(target=self.poll, daemon=False)
        # try to connect and get a taglist
        try:
            with LogixDriver('10.10.90.179') as eip_dev:
                l = eip_dev.get_tag_list()
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
        self.tags = l
        self.subcribed_tags = []
        self.tag_writes = []
    
    def start_polling(self):
        self.polling = True
        if not self.poll_thread.is_alive():
            self.poll_thread.start()
        return self.poll_thread.is_alive()
    
    def poll(self):
        try:
            with LogixDriver('10.10.90.179') as eip_dev:
                while self.polling:
                    t = time.time() #get start time        
                    for idx in self.tag_writes:
                        eip_dev.write(*self.tag_writes[idx])
                    for idx in range(len(self.subcribed_tags)):
                        self.subcribed_tags[idx]['tag_obj'] = eip_dev.read(self.subcribed_tags[idx]['tag_name'])
                    print(f'Polled {t}')
                    dt = time.time() - t #get delta time
                    time.sleep(max(0,self.pollrate-dt))
        except Exception as e:
            print(e)

if __name__ == "__main__":

    eip_conx = DeviceConnection()
    print(f'EIP polling? {eip_conx.start_polling()}')
    time.sleep(2)
    opc_conx = OpcConnection(eip_conx)
    opc_conx.start()
