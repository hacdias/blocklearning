factor = 1e18

def float_to_int(n, factor=factor):
  return int(n * factor)

def int_to_float(n, factor=factor):
  return n / factor

def floats_to_ints(arr, factor=factor):
  return list(map(lambda n: int(n * factor), arr))

def ints_to_floats(arr, factor=factor):
  return list(map(lambda n: n / factor, arr))
