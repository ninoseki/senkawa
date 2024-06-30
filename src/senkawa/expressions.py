from pyparsing import Char, Literal, Optional, Word, WordEnd, WordStart, alphas, nums

double_dots = Literal("..")
nums_plus_minus = nums + "+-"
optional_increment = Optional(double_dots + Word(nums_plus_minus)("step"))
int_range = (
    WordStart()
    + Word(nums_plus_minus)("left")
    + double_dots
    + Word(nums_plus_minus)("right")
    + optional_increment
    + WordEnd()
)
char_range = (
    WordStart()
    + Char(alphas)("left")
    + double_dots
    + Char(alphas)("right")
    + optional_increment
    + WordEnd()
)
