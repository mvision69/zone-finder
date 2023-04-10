from deca.file import ArchiveFile
from deca.ff_adf import Adf
from pathlib import Path
import struct

  # s8,  b, 1
  # u8,  B, 1
  # s16, h, 2
  # u16, H, 2
  # s32, i, 4
  # u32, I, 4
  # s64, q, 8
  # u64, Q, 8
  # f32, f, 4
  # f64, d, 8
  
  # header (64)                        0
  #   magic (4 chars)
  #   version (4 u32)
  #   instance_count (4 u32)
  #   instance_offset (4 u32)
  #   typedef_count (4 u32)
  #   *typedef_offset (4 u32)
  #   stringhash_count (4 u32)
  #   stringhash_offset (4 u32)
  #   nametable_count (4 u32)
  #   *nametable_offset (4 u32)
  #   *total_size (4 u32)
  #   unknown (20 (5*4) u32)
  #   comment (31 reads until b'\00')  94

  # instance 248
  #   name_hash (4, u32)
  #   type_hash (4, u32)
  #   offset (4 u32)
  #   *size (4 u32)
  #   name (8 u64) given table name index
  #   ... for every instance
  #   (seek instance)
  #   NeedZoneSave_2
  #   *NeedZoneReserveData_2
  #   ... for every reserve
  #   *NeedZoneBaseData_2
  #     Vector3_1
  #     ... for every zone
  
  # typedef 272,0x110 (structure, array, structure, array, structure, structure)
  #   metatype (4 u32)
  #   size  (4 u32)
  #   alignment (4 u32)
  #   type_hash (4 u32)
  #   name  (8 u64) index of named tables
  #   flags (4 u32)
  #   element_type_hash (4 u32)
  #   element_length  (4 u32)
  #   ... for each typedef   
  #   if metatype == 1, structure:
  #     member_count (4 u32)
  #     name (8 u64) index of named tables
  #     type_hash (4 u32)
  #     size (4 u32)
  #     offset (4 u32) creates bit_offset
  #     default_type (4 u32)
  #     default_value (8 u64)
  #     ... for each member
  #   if metatype == 3, Array:
  #     count (4 u32) == 0
  #   ... for each typedef

  # nametables 992 (0x3e0)
  #   table_name_size (1 u8) size of each table name; 22 tables [992,0x3e0 - 1013,0x3f5]
  #   ... for each table
  #   table_name  [1014,0x3f6 - 1314,0x522]
  #     name\00
  #     ... for each table

def open_adf(filename: str) -> None:
  obj = Adf()
  with ArchiveFile(open(filename, 'rb')) as f:
    obj.deserialize(f)    

def read_data(f, fmt, elen, n):
    if n is None:
        buf = f.read(elen)
        v = struct.unpack(fmt, buf)[0]
    else:
        buf = f.read(elen * n)
        v = struct.unpack(fmt * n, buf)

    return v

def peek(offset):
  with open("found_need_zones_adf_one_sliced", "rb") as fp:
    fp.seek(offset)
    print(struct.unpack("f", fp.read(4))[0])

def mod() -> None:
  data = bytearray(Path("found_need_zones_adf_one_sliced").read_bytes())
  X = 2354.0
  Y = 4532.0
  Z = 1234.0
  NeedZoneId = 1234 #sint32, i
  NeedType = 2 #sint32
  MapIconId = 483229195610198265 #uint64, Q
  NeedZoneStartTimeHours = 8.0
  NeedZoneEndTimeHours = 12.0
  AnimalTypeLocalizationname = 1124598738
  NeedZoneScheduleIndex = 2 #sint08, b w/ 3 00 at end
  
  zone_data = struct.pack("fffiiQffIb0i", X, Y, Z, NeedZoneId, NeedType, MapIconId, NeedZoneStartTimeHours, NeedZoneEndTimeHours, AnimalTypeLocalizationname, NeedZoneScheduleIndex)
  data_added = struct.calcsize("fffiiQffIb0i")
  
  # TODO: calc these offsets
  instance_offset = 12
  typedef_offset = 20
  nametable_offset = 36
  totalsize_offset = 40
  end_of_last_zone_in_reserve_offset = 240
  reserve_size_offset = 260  
  
  typedef = struct.unpack("I", data[typedef_offset:typedef_offset+4])[0]
  nametable = struct.unpack("I", data[nametable_offset:nametable_offset+4])[0]
  instance = struct.unpack("I", data[instance_offset:instance_offset+4])[0]
  totalsize = struct.unpack("I", data[totalsize_offset:totalsize_offset+4])[0]
  reserve_size = struct.unpack("I", data[reserve_size_offset:reserve_size_offset+4])[0]
  
  instance_data_offset = instance + 8
  instance_data = struct.unpack("I", data[instance_data_offset:instance_data_offset+4])[0]
  instance_reserve_one_length_offset = instance_data + 40
  instance_reserve_one_length = struct.unpack("I", data[instance_reserve_one_length_offset:instance_reserve_one_length_offset+4])[0]
  new_instance_reserve_one_length = instance_reserve_one_length + 1
  
  new_totalsize = totalsize + data_added  
  new_reserve_size = reserve_size + data_added
  
  new_typedef_offset = typedef + data_added
  new_nametable_offset = nametable + data_added
  new_instance_offset = instance + data_added
  
  data[instance_offset:instance_offset+4] = struct.pack("I", new_instance_offset)
  data[typedef_offset:typedef_offset+4] = struct.pack("I", new_typedef_offset)
  data[nametable_offset:nametable_offset+4] = struct.pack("I", new_nametable_offset)
  data[totalsize_offset:totalsize_offset+4] = struct.pack("I", new_totalsize)
  data[reserve_size_offset:reserve_size_offset+4] = struct.pack('I', new_reserve_size)   
  data[instance_reserve_one_length_offset:instance_reserve_one_length_offset+4] = struct.pack("I", new_instance_reserve_one_length) 
  data[end_of_last_zone_in_reserve_offset:end_of_last_zone_in_reserve_offset] = zone_data 
  
  print(f"{'instance_offset':<20} {hex(instance_offset):>5} {instance:>5} {new_instance_offset:>5}")
  print(f"{'typedef_offset':<20} {hex(typedef_offset):>5} {typedef:>5} {new_typedef_offset:>5}")
  print(f"{'nametable_offset':<20} {hex(nametable_offset):>5} {nametable:>5} {new_nametable_offset:>5}")
  print(f"{'totalsize':<20} {hex(totalsize_offset):>5} {totalsize:>5} {new_totalsize:>5}")
  print(f"{'reserve_size':<20} {hex(reserve_size_offset+data_added):>5} {reserve_size:>5} {new_reserve_size:>5}")
  print(f"{'zone_size':<20} {hex(instance_reserve_one_length_offset):>5} {instance_reserve_one_length:>5} {new_instance_reserve_one_length:>5}")
  
  Path("found_need_zones_adf_one_sliced_mine").write_bytes(data)  

if __name__ == "__main__":
  mod()
  # open_adf("found_need_zones_adf_one_sliced")
  open_adf("found_need_zones_adf_one_sliced_mine")
  # open_adf("found_need_zones_adf_two_sliced")  
  # peek(136)
  