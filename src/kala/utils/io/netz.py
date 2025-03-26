"""Inputs and outputs."""

import struct
from pathlib import Path
from urllib import request
from urllib.error import HTTPError

import networkx as nx
import zstandard as zstd


CURRENT_DIR = Path(__file__).resolve().parent
CACHE_DIR = CURRENT_DIR / "cache"


class NetzDatabase:
    def __init__(self, max_cache_size_bytes: int = 1024 * 1024 * 1024):  # 1GB default
        self.max_cache_size = max_cache_size_bytes
        if not CACHE_DIR.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def get_file_name(
        self,
        network_name: str,
        net: str | None = None,
    ):
        safe_name = network_name.lower().replace("-", "_").replace(" ", "_")
        safe_net = "_" + net.lower().replace("-", "_").replace(" ", "_") if net else ""
        return CACHE_DIR / f"{safe_name}{safe_net}.gt"

    def _download_file(
        self,
        network_name: str,
        net: str | None = None,
        base_url: str = "https://networks.skewed.de",
        replace: bool = False,
    ):
        file_name = self.get_file_name(network_name, net)
        temp_file = file_name.with_suffix(".tmp")

        if file_name.exists() and not replace:
            return  # File exists, nothing to do

        # retrieve data
        net = net or network_name
        url = base_url + f"/net/{network_name}/files/{net}.gt.zst"
        try:
            # Download to temporary file first
            with request.urlopen(url) as http_f:
                if http_f.status != 200:
                    raise HTTPError(
                        url,
                        http_f.status,
                        f"HTTP {http_f.status}: {http_f.reason}",
                        http_f.headers,
                        http_f,
                    )

                dctx = zstd.ZstdDecompressor()
                reader = dctx.stream_reader(http_f)
                decompressed = reader.readall()

                self._ensure_cache_space(len(decompressed))

                with open(temp_file, "wb") as f:
                    f.write(decompressed)

                # Atomic replace - will fail if another process beat us to it
                try:
                    temp_file.replace(file_name)
                except FileExistsError:
                    if not replace:
                        return  # Another process created the file, that's fine
                    raise  # If replace=True, propagate the error

        except Exception as e:
            # Clean up temp file if something went wrong
            if temp_file.exists():
                temp_file.unlink()
            raise e

    def read_netzschleuder_network(
        self,
        network_name: str,
        net: str | None = None,
        base_url: str = "https://networks.skewed.de",
    ) -> nx.Graph:
        """
        Read-in a network record from the Netzschleuder repository.

        Parameters
        ----------
        network_name : str
            Name of the network data sets to read from.
        net : str | None, optional
            Identifier of the subnetwork within the dataset to read. For data sets
            containing a single network only, this can be set to None (the default).
        base_url : str, optional
            Base URL of Netzschleuder repository

        Returns
        -------
            networkx.Graph

        """
        file_name = self.get_file_name(network_name, net)

        if not file_name.exists():
            self._download_file(network_name, net, base_url=base_url)

        with open(file_name, "rb") as f:
            data = f.read()

        # parse graphtool binary format
        edgelist = parse_graphtool_format_to_edgelist(data)

        return nx.Graph(edgelist, create_using=nx.Graph)  # return g as an undirected graph

    def _ensure_cache_space(self, needed_bytes: int) -> None:
        """Check if there's enough space for the new file, raise error if not."""
        total_size = sum(f.stat().st_size for f in CACHE_DIR.glob("*") if f.is_file())
        if total_size + needed_bytes > self.max_cache_size:
            msg = (
                f"Cache directory would exceed size limit of {self.max_cache_size / 1024 / 1024:.1f}MB. "
                f"Please manually clean the cache at:\n{CACHE_DIR}"
            )
            raise RuntimeError(msg)


def parse_graphtool_format_to_edgelist(data: bytes) -> list:
    """
    Decodes data in graph-tool binary format and returns an edgelist.
    For a documentation of the graphtool binary format, see doc at
    https://graph-tool.skewed.de/static/doc/gt_format.html

    Note: the code was modified from pathpy.

    Parameters
    ----------
    data : bytes
        Array of bytes to be decoded.

    Returns
    -------
    list[tuple]
        The edgelist of the network.
    """

    # check magic bytes
    if data[0:6] != b"\xe2\x9b\xbe\x20\x67\x74":
        print("Invalid graphtool file. Wrong magic bytes.")
        raise Exception("Invalid graphtool file. Wrong magic bytes.")
    ptr = 6

    # read graphtool version byte
    # graphtool_version = int(data[ptr])
    ptr += 1

    # read endianness
    if bool(data[ptr]):
        graphtool_endianness = ">"
    else:
        graphtool_endianness = "<"
    ptr += 1

    # read length of comment
    str_len = struct.unpack(graphtool_endianness + "Q", data[ptr : ptr + 8])[0]
    ptr += 8

    # read string comment
    # comment = data[ptr : ptr + str_len].decode("ascii")
    ptr += str_len

    # read network directedness
    # directed = bool(data[ptr])
    ptr += 1

    # read number of nodes
    n_nodes = struct.unpack(graphtool_endianness + "Q", data[ptr : ptr + 8])[0]
    ptr += 8

    # determine binary representation of neighbour lists
    if n_nodes < 2**8:
        fmt = "B"
        d = 1
    elif n_nodes < 2**16:
        fmt = "H"
        d = 2
    elif n_nodes < 2**32:
        fmt = "I"
        d = 4
    else:
        fmt = "Q"
        d = 8

    sources = []
    targets = []
    # parse lists of out-neighbors for all n nodes
    n_edges = 0
    for v in range(n_nodes):
        # read number of neighbors
        num_neighbors = struct.unpack(graphtool_endianness + "Q", data[ptr : ptr + 8])[0]
        ptr += 8

        # add edges to record
        for _ in range(num_neighbors):
            w = struct.unpack(graphtool_endianness + fmt, data[ptr : ptr + d])[0]
            ptr += d
            sources.append(v)
            targets.append(w)
            n_edges += 1

    return list(zip(sources, targets))
