from pathlib import Path
import logging
import sys
import base64

import click
import yaml

from moonlight.net import PacketReader

logger = logging.getLogger(__name__)


@click.group()
def decode():
    """
    Decoding messages and captures

    Decoding individual messages and wireshark PCAP files into a human-readable
    format.
    """


@click.command()
@click.argument(
    "message_def_dir",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True, path_type=Path),
)
@click.argument(
    "input_f",
    type=click.Path(exists=True, file_okay=True, resolve_path=True, path_type=Path),
)
@click.argument(
    "output_f",
    type=click.Path(file_okay=True, resolve_path=True, path_type=Path),
)
@click.option(
    "-t",
    "--typedefs",
    default=None,
    type=click.Path(file_okay=True, exists=True, resolve_path=True, path_type=Path),
)
def pcap(
    message_def_dir: Path,
    input_f: Path,
    output_f: Path,
    typedefs: Path,
):
    """
    Decode pcap to human-readable YAML

    `moonlight decode pcap` takes a compatible packet capture file (wireshark) and converts all
    unencrypted KI packets within it into a representation intended
    to be easily read by a human. By default, this is YAML.

    A packet is naively considered to be of the KI protocol if it starts with
    the \\x0D\\xF0 magic (little endian F00D). This may be improved in the future.

    MSG_DEF_DIR: Directory holding KI DML definitions

    INPUT_F: A valid packet capture file containing KI network traffic

    OUTPUT_F: File to write filtered capture to
    """

    # lazy load since scapy is kinda heavy
    from moonlight.net.scapy import (  # pylint: disable=import-outside-toplevel
        PcapReader,
    )

    rdr = PcapReader(
        pcap_path=input_f,
        typedef_path=typedefs,
        msg_def_folder=message_def_dir,
        silence_decode_errors=True,
    )
    with open(output_f, "w+t", encoding="utf8") as writer:
        # TODO: write metadata
        for i, msg in enumerate(rdr, start=1):
            writer.write(f"---\n# {i}\n")
            if msg is None:
                yaml.dump({"error": "failed to decode packet"}, writer)
            else:
                yaml.dump(
                    msg.to_human_dict(),
                    writer,
                    default_flow_style=False,
                    sort_keys=False,
                )
            writer.write("\n")
            if i % 100 == 0:
                logger.info("Progress: completed %d so far", i)

    rdr.close()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@click.command()
@click.argument(
    "message_def_dir",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True, path_type=Path),
)
@click.option(
    "-i",
    "--input",
    default=None,
    help="Instead of reading from stdin, use this value as the input",
)
@click.option(
    "-t",
    "--typedefs",
    default=None,
    type=click.Path(file_okay=True, exists=True, resolve_path=True, path_type=Path),
    help="Path to wizwalker typedef json",
)
@click.option(
    "-F",
    "--in-fmt",
    default="raw",
    show_default=True,
    type=click.Choice(["base64", "raw", "hex"]),
    help="Format of the input packet data",
)
@click.option(
    "--out-fmt",
    default="yaml",
    show_default=True,
    type=click.Choice(["yaml"]),
    help="Format of the output human representation",
)
@click.option(
    "-c",
    "--compact",
    is_flag=True,
    default=False,
    help="Reduces the amount of information in output",
)
def packet(
    message_def_dir: Path,
    input: str,
    typedefs: Path,
    in_fmt: str,
    out_fmt: str,
    compact: bool,
):
    """
    Decodes packet from stdin

    Takes a variety of encoding formats of KI packets and converts them into
    a supported human-readable format.

    MSG_DEF_DIR: Directory holding KI DML definitions
    """

    if input is None:
        input = sys.stdin.buffer.read()

    if in_fmt == "base64":
        input = base64.decodebytes(input.replace(" ", "").replace("\n", ""))
    elif in_fmt == "hex":
        input = bytes.fromhex(input.replace(" ", "").replace("\n", ""))

    rdr = PacketReader(
        typedef_path=typedefs,
        msg_def_folder=message_def_dir,
    )
    # TODO: write metadata
    msg = rdr.decode_packet(input)
    print()
    if msg is None:
        yaml.dump({"error": "failed to decode packet"}, sys.stdout)
    else:
        yaml.dump(
            msg.as_human_dict(compact=compact),
            sys.stdout,
            default_flow_style=False,
            sort_keys=False,
        )


decode.add_command(pcap)
decode.add_command(packet)


def register(group: click.Group):
    group.add_command(decode)
