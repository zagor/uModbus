"""

.. note:: This section is based on `MODBUS Messaging on TCP/IP
    Implementation Guide V1.0b`_.

The Application Data Unit (ADU) for Modbus responses carried over a TCP/IP are
build out of two components: a MBAP header and a PDU. The Modbus Application
Header (MBAP) is what makes Modbus TCP/IP requests and responsen different from
their counterparts send over a serial line.  Below the components of the Modbus
TCP/IP are listed together with their size in bytes:

+---------------+-----------------+
| **Component** | **Size** (bytes)|
+---------------+-----------------+
| MBAP Header   | 7               |
+---------------+-----------------+
| PDU           | N               |
+---------------+-----------------+

Below you see an hexidecimal presentation of request over TCP/IP with Modbus
function code 1. It requests data of slave with 1, starting at coil 100, for
the length of 3 coils::

    >>> # Read coils, starting from coil 100 for the length of 3 coils.
    >>> adu = b'\x00\x08\x00\x00\x00\x06\x01\x01\x00d\x00\x03'

The length of the ADU is 12 bytes::

    >>> len(adu)
    12

The MBAP header is 7 bytes long::

    >>> mbap = adu[:7]
    >>> mbap
    b'\x00\x08\x00\x00\x00\x06\x01'

The MBAP header contains the following fields:

+------------------------+--------------------+--------------------------------------+
| **Field**              | **Length** (bytes) | **Description**                      |
+------------------------+--------------------+--------------------------------------+
| Transaction identifier | 2                  | Identification of a                  |
|                        |                    | Modbus request/response transaction. |
+------------------------+--------------------+--------------------------------------+
| Protocol identifier    | 2                  | Protocol ID, is 0 for Modbus.        |
+------------------------+--------------------+--------------------------------------+
| Length                 | 2                  | Number of following bytes            |
+------------------------+--------------------+--------------------------------------+
| Unit identifier        | 1                  | Identification of a                  |
|                        |                    | remote slave                         |
+------------------------+--------------------+--------------------------------------+

When unpacked, these fields have the following values::

    >>> transaction_id = mbap[:2]
    >>> transaction_id
    b'\x00\x08'
    >>> protocol_id = mbap[2:4]
    >>> protocol_id
    b'\x00\x00'
    >>> length = mbap[4:6]
    >>> length
    b'\x00\x06'
    >>> unit_id = mbap[6:]
    >>> unit_id
    b'\0x01'

The request in words: a request with Transaction ID 8 for slave 1. The
request uses Protocol ID 0, which is the Modbus protocol. The length of the
bytes after the Length field is 6 bytes. These 6 bytes are Unit Identifier (1
byte) + PDU (5 bytes).

"""
import struct
from random import randint

from umodbus._functions import (create_function_from_response_pdu, ReadCoils,
                                ReadDiscreteInputs, ReadHoldingRegisters,
                                ReadInputRegisters, WriteSingleCoil,
                                WriteSingleRegister, WriteMultipleCoils,
                                WriteMultipleRegisters)


def create_request_adu(slave_id, pdu):
    """ Create MBAP header and combine it with PDU to return ADU.

    :param slave_id: Number of slave.
    :param pdu: Byte array with PDU.
    :return: Byte array with ADU.
    """
    return create_mbap_header(slave_id, pdu) + pdu


def create_mbap_header(slave_id, pdu):
    """ Return byte array with MBAP header for PDU.

    :param slave_id: Number of slave.
    :param pdu: Byte array with PDU.
    :return: Byte array of 7 bytes with MBAP header.
    """
    # 65536 = 2**16 aka maximum number that fits in 2 bytes.
    transaction_id = randint(0, 65536)
    length = len(pdu) + 1

    return struct.pack('>HHHB', transaction_id, 0, length, slave_id)


def read_coils(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 01: Read Coils.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadCoils()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def read_discrete_inputs(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 02: Read Discrete Inputs.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadDiscreteInputs()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def read_holding_registers(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 03: Read Holding Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadHoldingRegisters()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def read_input_registers(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 04: Read Input Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadInputRegisters()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def write_single_coil(slave_id, address, value):
    """ Return ADU for Modbus function code 05: Write Single Coil.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteSingleCoil()
    function.address = address
    function.value = value

    return create_request_adu(slave_id, function.request_pdu)


def write_single_register(slave_id, address, value):
    """ Return ADU for Modbus function code 06: Write Single Register.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteSingleRegister()
    function.address = address
    function.value = value

    return create_request_adu(slave_id, function.request_pdu)


def write_multiple_coils(slave_id, starting_address, values):
    """ Return ADU for Modbus function code 15: Write Multiple Coils.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteMultipleCoils()
    function.starting_address = starting_address
    function.values = values

    return create_request_adu(slave_id, function.request_pdu)


def write_multiple_registers(slave_id, starting_address, values):
    """ Return ADU for Modbus function code 16: Write Multiple Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteMultipleRegisters()
    function.starting_address = starting_address
    function.values = values

    return create_request_adu(slave_id, function.request_pdu)


def parse_response_adu(resp_adu, *args, **kwargs):
    resp_pdu = resp_adu[7:]
    function = create_function_from_response_pdu(resp_pdu, *args, **kwargs)

    return function.data
