import zlib
from deca.file import ArchiveFile
from deca.ff_adf import Adf
from deca.ff_rtpc import RtpcNode, rtpc_from_binary
from pathlib import Path
from typing import Tuple

APP_DIR_PATH = Path(__file__).resolve().parent

def _open_reserve(filename: Path) -> Tuple[RtpcNode, bytearray]:
  with(filename.open("rb") as f):
    data = rtpc_from_binary(f) 
  f_bytes = bytearray(filename.read_bytes())
  return (data.root_node, f_bytes)

def _save_file(filename: Path, data_bytes: bytearray):
    Path(filename.parent).mkdir(exist_ok=True, parents=True)
    filename.write_bytes(data_bytes) 

def _parse_adf(filename: Path) -> Adf:
  obj = Adf()
  with ArchiveFile(open(filename, 'rb')) as f:
    obj.deserialize(f) 
  content = obj.dump_to_string()
  suffix = ".txt"
  txt_filename = APP_DIR_PATH / f".working/{filename.name}{suffix}"
  _save_file(txt_filename, bytearray(content, 'utf-8'))    
  return obj  

def find_water_zones() -> None:
  _open_reserve(APP_DIR_PATH / "reserve_1.bin")

def main() -> None:
  find_water_zones()