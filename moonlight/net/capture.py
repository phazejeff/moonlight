"""
    Provides capture utilities for working with KI game network data
"""

import logging
import os
import sys
import traceback
from email import message
from os import PathLike, listdir
from os.path import isfile, join

from scapy.layers.inet import TCP
from scapy.packet import Packet, Raw
from scapy.sendrecv import AsyncSniffer, sniff
from scapy.sessions import TCPSession
from scapy.utils import PcapReader as Scapy_PcapReader

from .common import BytestreamReader, PacketHeader
from .control import ControlMessage, ControlProtocol
from .dml import DMLMessage, DMLProtocolRegistry


class PacketReader:
    def __init__(
        self,
        msg_def_folder: PathLike,
        typedef_path: PathLike = None,
    ):
        self.msg_def_folder = msg_def_folder

        # Load dml decoder
        dml_services = [
            f for f in listdir(msg_def_folder) if isfile(join(msg_def_folder, f))
        ]
        dml_services = map(lambda x: join(msg_def_folder, x), dml_services)
        self.dml_protocol = DMLProtocolRegistry(
            *dml_services, typedef_path=typedef_path
        )

        # Load control decoder
        self.control_protocol: ControlProtocol = ControlProtocol()

    def decode_packet(self, bites: bytes) -> ControlMessage | DMLMessage:
        if isinstance(bites, bytes):
            reader = BytestreamReader(bites)
        else:
            raise ValueError("bites is not of type bytes")

        try:
            header = PacketHeader(reader)
        except ValueError:
            logging.debug("Invalid packet received: bad KI header")
            return None

        if header.content_is_control != 0:
            return self.control_protocol.decode_packet(
                reader, header, original_data=bites
            )

        return self.dml_protocol.decode_packet(bites)


class PcapReader:
    def __init__(
        self,
        pcap_path: PathLike,
        typedef_path: PathLike = None,
        msg_def_folder: PathLike = os.path.join(
            os.path.dirname(__file__), "..", "..", "res", "dml", "messages"
        ),
    ) -> None:
        if not isfile(pcap_path):
            raise ValueError("Provided pcap filepath doesn't exist")

        self.pcap_path = pcap_path
        self.ki_packet_reader = PacketReader(
            typedef_path=typedef_path, msg_def_folder=msg_def_folder
        )
        self.pcap_reader = Scapy_PcapReader(filename=pcap_path)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            packet = self.pcap_reader.next()
            if packet.layers()[-1] is not TCP:
                logging.trace("Capture packet isn't of the KI protocol")
                continue

    def decode_packet(self, bites: bytes) -> ControlMessage | DMLMessage:
        bites = None
        header = None
        if isinstance(bites, bytes):
            reader = BytestreamReader(bites)
        else:
            raise ValueError("bites is not of type bytes")

        try:
            header = PacketHeader(reader)
        except ValueError:
            logging.debug("Invalid packet received: bad KI header")
            return None

        if header.content_is_control != 0:
            return self.control_protocol.decode_packet(
                reader, header, original_data=bites
            )

        return self.dml_protocol.decode_packet(bites)


class LiveSniffer:
    def __init__(
        self,
        dml_def_folder: PathLike = os.path.join(
            os.path.dirname(__file__), "..", "res", "dml", "messages"
        ),
    ):
        self.stream = None
        protocols = [
            f for f in listdir(dml_def_folder) if isfile(join(dml_def_folder, f))
        ]
        protocols = map(lambda x: join(dml_def_folder, x), protocols)
        self.decoder = PcapReader(msg_def_folder=dml_def_folder)

    def scapy_callback(self, pkt: Packet):
        if type(pkt[TCP].payload) is not Raw:
            return
        try:
            bites = bytes(pkt[TCP].payload)
            PacketHeader
            message = self.decoder.decode_packet(bites)
            logging.info(message)
        except ValueError as err:
            if err.message.startswith("Not a KI game protocol packet."):
                logging.trace(err.message)
                return
            logging.error(f"Cannot parse packet: {traceback.print_exc()}")

    def open_livestream(self):
        self.stream = AsyncSniffer(
            filter="dst host 79.110.83.12 or src host 79.110.83.12",
            session=TCPSession,
            prn=self.scapy_callback,
        )
        logging.info("Starting sniffer")
        self.stream.start()
        logging.info("Waiting for end signal")
        self.stream.join()

    def close_livestream(self):
        self.stream.stop()


if __name__ == "__main__":
    logging.basicConfig(
        # format="[%(asctime)s] %(levelname)s: %(message)s",
        format="%(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
        handlers=[
            # logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'log', 'out.log')),
            logging.StreamHandler(sys.stdout),
        ],
    )
    print("hi")
    s = LiveSniffer()
    print("Opening packet stream")

    s.open_livestream()


# class PcapReader:
#     def __init__(
#         self,
#         typedef_file: PathLike = None,
#         pcap_file: PathLike = None,
#         msg_def_folder: PathLike = os.path.join(
#             os.path.dirname(__file__), "..", "..", "res", "dml", "messages"
#         ),
#     ) -> None:
#         self.pcap_file = pcap_file
#         self.msg_def_folder = msg_def_folder
#         self.pcap_reader: PcapReader = None

#         if isfile(pcap_file):
#             self.pcap_reader: PcapReader = PcapReader(pcap_file)
#         else:
#             raise ValueError("Provided pcap filepath doesn't exist")

#         # Load dml decoder
#         dml_services = [
#             f for f in listdir(msg_def_folder) if isfile(join(msg_def_folder, f))
#         ]
#         dml_services = map(lambda x: join(msg_def_folder, x), dml_services)
#         self.dml_decoder = DMLProtocol(*dml_services)

#         # Load control decoder
#         self.control_decoder: ControlProtocol = ControlProtocol()

#     # def __iter__(self):
#     #     return self

#     # def __next__(self):
#     #     self.pcap_reader.

#     def decode_packet(self, bites: bytes) -> ControlMessage | DMLMessage:
#         bites = None
#         header = None
#         if isinstance(bites, bytes):
#             reader = BytestreamReader(bites)
#         else:
#             raise ValueError("bites is not of type bytes")

#         try:
#             header = PacketHeader(reader)
#         except ValueError:
#             logging.debug("Invalid packet received: bad KI header")
#             return None

#         if header.content_is_control != 0:
#             return self.control_decoder.decode_packet(
#                 reader, header, original_data=bites
#             )

#         return self.dml_decoder.decode_packet(reader, header, packet_bytes=bites)
