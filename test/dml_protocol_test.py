import os
from os.path import isfile, join
from pathlib import Path
from posix import listdir
from .fixtures import dml_update_poi

import pytest
from moonlight.ki.net_common import EncodingType, KIPacketHeader
from moonlight.ki.dml import DMLProtocol


@pytest.fixture
def dml_protocol() -> DMLProtocol:
    res_folder = os.path.join(os.path.dirname(__file__), "fixtures", "dml", "messages")
    protocols = [f for f in listdir(res_folder) if isfile(join(res_folder, f))]
    protocols = map(lambda x: join(res_folder, x), protocols)
    return DMLProtocol(*protocols)


@pytest.fixture
def game_messages_interactable_options() -> bytes:
    return (
        b"\r\xf0\x12\x00\x00\x00\x00\x00\x05\xda\r\x00\xde\xf4" b"r\x02\\\xfbQ.\x00\x00"
    )


@pytest.fixture
def game_messages_correct_loc() -> bytes:
    return (
        b"\r\xf0\x12\x00\x00\x00\x00\x00\x05"
        b"w\r\x003\x18y\x05\x00\x00\x06\x00\x00\x00"
    )


def test_decode_poi(dml_protocol, dml_update_poi):
    obj = dml_protocol.decode_packet(dml_update_poi, has_ki_header=True)
    assert obj != None
    assert obj.msg_id == 31
    assert obj.protocol_id == 53
    assert obj.msg_desc == "Server updating the POI data"
    assert obj.protocol_desc == "Wizard Messages2"
    assert len(obj.fields) == 1
    assert obj.fields[0].name == "Data"
    assert obj.fields[0].src_encoding is EncodingType.STR
    assert (
        obj.fields[0].value
        == b'\xdc\x1d\x91a\x0b\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1f\x00GUI/Minimap/BG_Sigil_Spiral.ddsl^\x0e\x00\x00\x00;"\xf1\x1d@A>;\x07A\x1d\xca\xf8?\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1c\x00GUI/Minimap/BG_Sigil_Sun.ddsx^\x0e\x00\x00\x00;"\xd5:\xa0\xc5\xa6]P\xc5\xeeg\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1c\x00GUI/Minimap/BG_Sigil_Eye.dds\x80^\x0e\x00\x00\x00;"F2gE\xbc\xf1\xc4\xc5\xe9v\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1d\x00GUI/Minimap/BG_Sigil_Moon.dds\x8c^\x0e\x00\x00\x00;"\x85\xf1\x9fE\xe7\xd9OE\x00t\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1d\x00GUI/Minimap/BG_Sigil_Star.dds\x94^\x0e\x00\x00\x00;"H\xc3f\xc5\xac3\xc5E\x00\x80\x16D\x00\x00\x00\x00\xdc\x15!"\x05\x00\x00\x00\x00\x00\x93\x99\xfb\x00\x00\x00\xaa\x02\x00\xa0J\xc6\x00\x80\xf2D\x00\x80\x94\xc5\xcd\xcc\x84@\xdc\x15!"\x05\x00\x00\x00\x00\x00\x03\x9b\x11\x01\x00\x00\xab\x02\x00@)\xc6\x00\x80\x13E\x00\x80\x94\xc5\xcd\xccd@\xdc\x15!"\x05\x00\x00\x00\x00\x00\xfbbK\x04\x00\x00\x07\x00\x000L\xc6\x00\xc0\x07E\x00\x80\x94\xc5ff\x96@\xdc\x15!"\x05\x00\x00\x00\x00\x00~3\r\x01\x00\x00\x06\x00\x00`8\xc6\x00@\x15E\x00\x80\x94\xc5ff\x96@\xdc\x15!"\x05\x00\x00\x00\x00\x003\x18y\x05\x00\x00\x06\x00\x00\xd0-\xc6\x00@\x18E\x00\x80\x94\xc5\x9a\x99\x9d@\xdc\x15!"\x05\x00\x00\x00\x00\x00#\xcb`\x01\x00\x00\xaa\x02\x00 2\xc6\x00\x80\x1cE\x00\x80\x94\xc533\x03@'
    )


# def test_decode_correct_loc(dml_protocol, game_messages_correct_loc):
#     #header = KIPacketHeader(game_messages_correct_loc)
#     obj = dml_protocol.decode_packet(game_messages_correct_loc, has_ki_header=True)
#     assert obj != None
#     assert obj.msg_id == 31
#     assert obj.protocol_id == 53
#     assert obj.msg_desc == 'Server updating the POI data'
#     assert obj.protocol_desc == 'Wizard Messages2'
#     assert len(obj.fields) == 1
#     assert obj.fields[0].name == 'Data'
#     assert obj.fields[0].src_encoding is EncodingType.STR
#     assert obj.fields[0].value == b'\xdc\x1d\x91a\x0b\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1f\x00GUI/Minimap/BG_Sigil_Spiral.ddsl^\x0e\x00\x00\x00;"\xf1\x1d@A>;\x07A\x1d\xca\xf8?\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1c\x00GUI/Minimap/BG_Sigil_Sun.ddsx^\x0e\x00\x00\x00;"\xd5:\xa0\xc5\xa6]P\xc5\xeeg\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1c\x00GUI/Minimap/BG_Sigil_Eye.dds\x80^\x0e\x00\x00\x00;"F2gE\xbc\xf1\xc4\xc5\xe9v\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1d\x00GUI/Minimap/BG_Sigil_Moon.dds\x8c^\x0e\x00\x00\x00;"\x85\xf1\x9fE\xe7\xd9OE\x00t\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1d\x00GUI/Minimap/BG_Sigil_Star.dds\x94^\x0e\x00\x00\x00;"H\xc3f\xc5\xac3\xc5E\x00\x80\x16D\x00\x00\x00\x00\xdc\x15!"\x05\x00\x00\x00\x00\x00\x93\x99\xfb\x00\x00\x00\xaa\x02\x00\xa0J\xc6\x00\x80\xf2D\x00\x80\x94\xc5\xcd\xcc\x84@\xdc\x15!"\x05\x00\x00\x00\x00\x00\x03\x9b\x11\x01\x00\x00\xab\x02\x00@)\xc6\x00\x80\x13E\x00\x80\x94\xc5\xcd\xccd@\xdc\x15!"\x05\x00\x00\x00\x00\x00\xfbbK\x04\x00\x00\x07\x00\x000L\xc6\x00\xc0\x07E\x00\x80\x94\xc5ff\x96@\xdc\x15!"\x05\x00\x00\x00\x00\x00~3\r\x01\x00\x00\x06\x00\x00`8\xc6\x00@\x15E\x00\x80\x94\xc5ff\x96@\xdc\x15!"\x05\x00\x00\x00\x00\x003\x18y\x05\x00\x00\x06\x00\x00\xd0-\xc6\x00@\x18E\x00\x80\x94\xc5\x9a\x99\x9d@\xdc\x15!"\x05\x00\x00\x00\x00\x00#\xcb`\x01\x00\x00\xaa\x02\x00 2\xc6\x00\x80\x1cE\x00\x80\x94\xc533\x03@'


def test_decode_interact_options(dml_protocol, dml_update_poi):
    obj = dml_protocol.decode_packet(dml_update_poi, has_ki_header=True)
    assert obj != None
    assert obj.msg_id == 31
    assert obj.protocol_id == 53
    assert obj.msg_desc == "Server updating the POI data"
    assert obj.protocol_desc == "Wizard Messages2"
    assert len(obj.fields) == 1
    assert obj.fields[0].name == "Data"
    assert obj.fields[0].src_encoding is EncodingType.STR
    assert (
        obj.fields[0].value
        == b'\xdc\x1d\x91a\x0b\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1f\x00GUI/Minimap/BG_Sigil_Spiral.ddsl^\x0e\x00\x00\x00;"\xf1\x1d@A>;\x07A\x1d\xca\xf8?\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1c\x00GUI/Minimap/BG_Sigil_Sun.ddsx^\x0e\x00\x00\x00;"\xd5:\xa0\xc5\xa6]P\xc5\xeeg\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1c\x00GUI/Minimap/BG_Sigil_Eye.dds\x80^\x0e\x00\x00\x00;"F2gE\xbc\xf1\xc4\xc5\xe9v\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1d\x00GUI/Minimap/BG_Sigil_Moon.dds\x8c^\x0e\x00\x00\x00;"\x85\xf1\x9fE\xe7\xd9OE\x00t\x16D\x00\x00\x00\x00\xdc\x15!"\x08\x00\x00\x00\x1d\x00GUI/Minimap/BG_Sigil_Star.dds\x94^\x0e\x00\x00\x00;"H\xc3f\xc5\xac3\xc5E\x00\x80\x16D\x00\x00\x00\x00\xdc\x15!"\x05\x00\x00\x00\x00\x00\x93\x99\xfb\x00\x00\x00\xaa\x02\x00\xa0J\xc6\x00\x80\xf2D\x00\x80\x94\xc5\xcd\xcc\x84@\xdc\x15!"\x05\x00\x00\x00\x00\x00\x03\x9b\x11\x01\x00\x00\xab\x02\x00@)\xc6\x00\x80\x13E\x00\x80\x94\xc5\xcd\xccd@\xdc\x15!"\x05\x00\x00\x00\x00\x00\xfbbK\x04\x00\x00\x07\x00\x000L\xc6\x00\xc0\x07E\x00\x80\x94\xc5ff\x96@\xdc\x15!"\x05\x00\x00\x00\x00\x00~3\r\x01\x00\x00\x06\x00\x00`8\xc6\x00@\x15E\x00\x80\x94\xc5ff\x96@\xdc\x15!"\x05\x00\x00\x00\x00\x003\x18y\x05\x00\x00\x06\x00\x00\xd0-\xc6\x00@\x18E\x00\x80\x94\xc5\x9a\x99\x9d@\xdc\x15!"\x05\x00\x00\x00\x00\x00#\xcb`\x01\x00\x00\xaa\x02\x00 2\xc6\x00\x80\x1cE\x00\x80\x94\xc533\x03@'
    )
