import pytest
import struct

from ..validators import (validate_response_mbap, validate_function_code,
                          validate_single_bit_value_byte_count,
                          validate_multi_bit_value_byte_count)


def unpack_single_bit_values(response):
    byte_count = struct.unpack('>B', response[8:9])[0]

    fmt = '>' + ('B' * byte_count)
    return struct.unpack(fmt, response[9:])


def unpack_multi_bit_values(response):
    byte_count = struct.unpack('>B', response[8:9])[0]

    fmt = '>' + ('H' * (byte_count // 2))
    return struct.unpack(fmt, response[9:])


@pytest.mark.parametrize('function_code', [
    1,
    2,
])
def test_response_on_single_bit_value_read_requests(sock, mbap, function_code):
    """ Validate response of a succesful Read Coils or Read Discrete Inputs
    request.
    """
    function_code, starting_address, quantity = (function_code, 0, 10)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    validate_function_code(adu, resp)
    validate_single_bit_value_byte_count(adu, resp)

    assert unpack_single_bit_values(resp) == (170, 2)


@pytest.mark.parametrize('function_code', [
    3,
    4,
])
def test_response_on_multi_bit_value_read_requests(sock, mbap, function_code):
    """ Validate response of a succesful Read Holding Registers or Read
    Input Registers request.
    """
    function_code, starting_address, quantity = (function_code, 0, 10)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    validate_function_code(adu, resp)
    validate_multi_bit_value_byte_count(adu, resp)

    assert unpack_multi_bit_values(resp) == (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)


@pytest.mark.parametrize('function_code', [
    5,
    6,
])
def test_response_single_value_write_request(sock, mbap, function_code):
    """ Validate responde of succesful Read Single Coil and Read Single
    Register request.
    """
    function_code, address, value = (function_code, 1, 0)
    adu = mbap + struct.pack('>BHH', function_code, address, value)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert resp == adu


@pytest.mark.parametrize('function_code, pdu', [
    (15, struct.pack('>BHHBB', 15, 0, 2, 1, 3)),
    (16, struct.pack('>BHHBHH', 16, 0, 2, 4, 1337, 15)),
])
def test_response_multi_value_write_request(sock, mbap, function_code, pdu):
    """ Validate response of succesful Write Multiple Coils and Write Multiple
    Registers request.

    Both requests write 2 values, starting address is 0.
    """
    sock.send(mbap + pdu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    # Field 'starting address' should be equal to 0.
    assert struct.unpack('>H', resp[8:10])[0] == 0
    # Field 'quantity' should be equal to 2.
    assert struct.unpack('>H', resp[10:])[0] == 2