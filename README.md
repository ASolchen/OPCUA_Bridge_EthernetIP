=======
OPCUA_Bridge_EthernetIP
=======


Introduction
============

``OPCUA_Bridge_EthernetIP`` aims to combine the following libraries in a communication bridge:
.. _pycomm3: https://github.com/ottowayi/pycomm3
.. _python-opcua: https://github.com/FreeOpcUa/python-opcua

Goal
============

The goal of this repo is to create an OPCUA server that bridges to an EtheretIP client. The client could connect to Rockwell PLCs, VFDs, etc. The OPC server can serve this data to an OPC client, and also receive values from the OPC client to set values of the end device.
