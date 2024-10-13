
"""
(((5 * 4) - 3) - (5 ^ 3))
    split -

    split *

    split ^

"""

"""
depth 3  ^ , 2 *, 1 -

calc( split(str) )
"-" is in str  calc( 


"""

operations = [
    ("+", lambda a, b: a + b),
    ( "-", lambda  a,b: a-b ),
    ("*", lambda a, b: a * b),
    ("^", lambda a, b: pow(a, b)),
]

def calc( input_str , depth) :
      if depth >= len(operations):
          return float(input_str)
      split_op, split_operation = operations[depth]

      splitted_input = input_str.split(split_op)  # N  " " " "

      # 4  " " " "

      print(f" {splitted_input}  depth  {depth}" )
      ret = calc( splitted_input[0], depth + 1)

      for each_ith in splitted_input[1:]:
          # 3 - 2 - 1
          next_val = calc( each_ith , depth + 1 )
          ret = split_operation(ret,next_val)

      return ret


if __name__ == '__main__':
    # 2 * 3 - 2 * 3
    #  -
    input_str = "6+5*4-3-5^3 * 6+5*4-3-5^3"
    ret = calc(input_str,0)
    print(ret)
    #print("welcome to whiteboard")