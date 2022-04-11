import pathlib
from os import PathLike

import click


@click.group()
def pcap():
    """
    Packet capture manipulation

    Commands revolving around the manipulation and processing of PCAP files.
    Decoding PCAP files can be found within the `moonlight decode` subcommand.
    """


@click.command()
@click.argument(
    "input_f",
    type=click.Path(
        exists=True, file_okay=True, resolve_path=True, path_type=pathlib.Path
    ),
)
@click.argument(
    "output_f",
    type=click.Path(file_okay=True, resolve_path=True, path_type=pathlib.Path),
)
@click.option(
    "-z/-Z",
    "--zip/--no-zip",
    default=False,
    show_default=True,
    help="Output file compression via gzip",
)
def filter_cmd(
    input_f: PathLike, output_f: PathLike, zip: bool
):  # pylint: disable=redefined-builtin
    """
    Filter content of pcap files

    Filter takes compatible packet capture files (wireshark) and removes all
      packets that aren't part of the KI network protocol, greatly reducing the
      size of packet captures. Optionally compresses output files as well.
    A packet is naively considered to be of the KI protocol if it starts with
      the \\x0D\\xF0 magic (little endian F00D). This may be improved in the future.

    INPUT_F: A valid packet capture file containing KI network traffic

    OUTPUT_F: File to write filtered capture to
    """

    # lazy load since scapy is kinda heavy
    from moonlight.net.scapy import (  # pylint: disable=import-outside-toplevel
        filter_pcap,
    )

    filter_pcap(input_f, output_f, compress=zip)


pcap.add_command(filter_cmd, name="filter")


def register(group: click.Group):
    group.add_command(pcap)
