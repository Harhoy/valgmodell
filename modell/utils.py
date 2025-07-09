
from random import shuffle

def randomIntegerList(integers):
  tot = 2000
  l = []
  for i in integers:
    t = [i['val']] * int(i['prop'] * tot)
    l += t
  shuffle(l)
  return l
    
if __name__ == "__main__":

  l = [{'prop': 0.1, 'val': 0},
      {'prop': 0.3, 'val': 1},
      {'prop': 0.6, 'val': 2}]

  print(randomIntegerList(l))
