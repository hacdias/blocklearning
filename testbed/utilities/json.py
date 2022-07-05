import json as sysjson

def read_json(filename):
  with open(filename) as json_file:
    data = sysjson.load(json_file)
  return data

def save_json(filename, data):
  json_string = sysjson.dumps(data, indent=2)
  with open(filename, 'w') as outfile:
    outfile.write(json_string)
