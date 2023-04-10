import json
from pathlib import Path

APP_DIR_PATH = Path(__file__).resolve().parent

if __name__ == "__main__":
  data = json.load((APP_DIR_PATH / "config/reserve_1.json").open())
  pop_info = data["population_info"]
  areas = data["areas"]
  final = {}
  populations = {}
  animals = {}
  for pop, values in pop_info.items():
    populations[pop] = values
  for area, values in areas.items():
    animals[area] = {
      "drink": {}
    }    
    if "drinking" in values["layers"]:
      for zone, values in values["layers"]["drinking"].items():
        x = values["AabbMin"][0] + (values["AabbMax"][0] - values["AabbMin"][0])
        y = values["AabbMin"][1] + (values["AabbMax"][1] - values["AabbMin"][1])
        z = values["AabbMin"][2] + (values["AabbMax"][2] - values["AabbMin"][2])
        animals[area]["drink"][zone] =  { "x": x, "y": y, "z": z }
  final["populations"] = populations
  final["animals"] = animals
  # print(final)
  Path(APP_DIR_PATH / "config/reserve_1_m.json").write_text(json.dumps(final, indent=2)) 