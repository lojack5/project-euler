from __future__ import annotations
import math
import operator
from functools import cache, reduce
from typing import Callable, Literal
from modular import Modular, prime_factors, primes


def zero() -> Literal[0]:
    return 0


class Delayed:
    eval: Callable[[], int]

    def __init__(self, initial: Callable[[], int] | int, *, _str: str = ''):
        if callable(initial):
            self.eval = initial
            self._str = _str if _str else 'unknown'
        else:
            self.eval = lambda : initial
            self._str = str(initial)

    def __str__(self) -> str:
        return self._str

    def _compute(self, other, op, reverse=False) -> Callable[[], int]:
        if callable(other):
            if reverse:
                def compute() -> int:
                    return op(other(), self.eval())
            else:
                def compute() -> int:
                    return op(self.eval(), other())
        else:
            if reverse:
                def compute() -> int:
                    return op(other, self.eval())
            else:
                def compute() -> int:
                    return op(self.eval(), other)
        return compute

    def __add__(self, other):
        return Delayed(self._compute(other, operator.add), _str=f'({self}+{other})')

    def __radd__(self, other):
        return Delayed(self._compute(other, operator.add, True), _str=f'({other}+{self})')

    def __mul__(self, other):
        return Delayed(self._compute(other, operator.mul), _str=f'({self}*{other})')

    def __rmul__(self, other):
        return Delayed(self._compute(other, operator.mul, True), _str=f'({other}*{self})')

    def __sub__(self, other):
        return Delayed(self._compute(other, operator.sub), _str=f'({self}-{other})')

    def __rsub__(self, other):
        return Delayed(self._compute(other, operator.sub, True), _str=f'({other}-{self})')

    def __neg__(self):
        def compute() -> int:
            return -self.eval()
        return Delayed(compute, _str=f'-{self}')

    def __pow__(self, other):
        return Delayed(self._compute(other, operator.pow), _str=f'{self}**{other}')

    def __rpow__(self, other):
        return Delayed(self._compute(other, operator.pow, True), _str=f'{other}**{self}')

    def __divmod__(self, other):
        ...


@cache
def b(n: int) -> int:
    divisor = 1
    while not n % 2:
        n //= 2
        divisor *= 2
    return divisor


@cache
def A(n: int, mod: int) -> int:
    if n == 0:
        return 1
    q, r = divmod(n, 2)
    if r == 0:
        # even
        return (3*A(q, mod) + 5 * A(n - b(q), mod)) % mod
    else:
        # odd
        return A(q, mod)


@cache
def H(r, t, mod) -> int:
    return A((2**r + 1)**t, mod)



if __name__ == '__main__':
    mod = 1_000_062_031 # Known to be prime
    Mod = Modular(mod)
    print('Creating delayed calculation:')
    calc = Delayed(Mod(10))**14 + 31
    print('calc:', calc)
    print('Evaluating:', calc.eval())
