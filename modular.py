import itertools
import operator
from functools import cache, reduce
import math
from typing_extensions import Self


@cache
def Modular(n: int) -> type[int]:
    """Create a integer class to perform computations mod n."""
    if not isinstance(n, int):
        raise TypeError('Modulus must be an integer')
    elif n < 1:
        raise ValueError('Modulus must be positive.')
    critical_magnitude = n // 2
    class _Modular(int):
        def __new__(cls, value: int) -> Self:
            if isinstance(value, _Modular):
                return value
            else:
                return super().__new__(cls, value % n)

        def __add__(self, other: int) -> Self:
            if isinstance(other, int):
                return type(self)(super().__add__(other))
            return NotImplemented

        def __radd__(self, other: int) -> Self:
            if isinstance(other, int):
                return type(self)(super().__add__(other))
            return NotImplemented

        def __mul__(self, other: int) -> Self:
            if isinstance(other, int):
                return type(self)(super().__mul__(other))
            return NotImplemented

        def __rmul__(self, other: int) -> Self:
            if isinstance(other, int):
                return type(self)(super().__mul__(other))

        def __neg__(self) -> Self:
            return type(self)(super().__neg__())

        def __pow__(self, exp: int) -> Self:
            if isinstance(exp, int):
                return type(self)(super().__pow__(exp, n))
            return NotImplemented

        def __sub__(self, other: int) -> Self:
            if isinstance(other, int):
                return type(self)(super().__sub__(other))
            return NotImplemented

        def __rsub__(self, other: int) -> Self:
            if isinstance(other, int):
                return type(self)(other - int(self))

        def __str__(self) -> str:
            return f'{super().__repr__()} (mod {n})'

        def __repr__(self) -> str:
            return f'<{super().__repr__()} Mod({n})>'

        def least_positive(self) -> Self:
            if self < 0:
                return type(self)(self + n)
            else:
                return self

        def __abs__(self) -> Self:
            """Positive value of the least magnitude version of this integer
            mod n.
            """
            a = self.least_magnitude()
            if a < 0:
                return -a
            else:
                return a

        def least_magnitude(self) -> Self:
            if self > critical_magnitude:
                return self - n
            elif self < -critical_magnitude:
                return self + n
            else:
                return self

        def __eq__(self, other: int) -> bool:
            if isinstance(other, int):
                if not isinstance(other, _Modular):
                    other = type(self)(other)
                return int.__eq__(self - other, 0)
            return NotImplemented

        def __ne__(self, other: int) -> bool:
            if isinstance(other, int):
                if not isinstance(other, _Modular):
                    other = type(self)(other)
                return int.__ne__(self - other, 0)
            return NotImplemented

    _Modular.__name__ = f'Modular[{n}]'
    _Modular.__qualname__ = f'Modular[{n}]'
    return _Modular


def primes(n: int) -> list[int]:
    """primes < n"""
    sieve = [True] * n
    for i in range(3, n // 2 + 1, 2):
        if sieve[i]:
            sieve[i**2: : 2*i] = [False] * ((n - i*i - 1) // (2*i) + 1)
    return [2] + [i for i in range(3, n, 2) if sieve[i]]


@cache
def nth_prime(n: int) -> int:
    """Compute the n-th prime."""
    if n == 1:
        return 2
    else:
        start = nth_prime(n - 1) + 1
        for i in itertools.count(start):
            if is_prime(i):
                return i
    raise RuntimeError('Unexpected branch')


def is_prime(n: int) -> bool:
    """Test an integer for primality."""
    max_check = math.floor(math.sqrt(n))
    for n in itertools.count(1):
        p = nth_prime(n)
        if p >= max_check:
            return True
        elif not n % p:
            return False
    return False


@cache
def prime_factors2(n: int) -> tuple[tuple[int, int]]:
    """Compute the prime factorization for an integers.
    The results is a sequence of tuples, each containing a prime factor
    and it's exponent in the canonical prime factorization.
    """
    factors = []
    for p in map(nth_prime, itertools.count(1)):
        if n == 1:
            break
        q, r = divmod(n, p)
        while not r:
            factors.append(p)
            n = q
            q, r = divmod(n, p)
    return tuple((p, len(list(g))) for p, g in itertools.groupby(factors))


@cache
def prime_factors(n: int) -> tuple[tuple[int, int]]:
    print('Factorizing', n)
    ps = primes(math.floor(math.sqrt(n)) + 1)
    factors = []
    for p in ps:
        if n == 1:
            break
        q, r = divmod(n, p)
        if p == 313:
            print(f'division by 313: {n} = 313*{q} + {r}')
        while not r:
            print(' divisible by', p)
            factors.append(p)
            n = q
            q, r = divmod(n, p)
    return tuple((p, len(list(g))) for p, g in itertools.groupby(factors))


def _phi(p: int, exp: int) -> int:
    """Special case of computing phi(p^k)"""
    return (p ** (exp - 1))*(p - 1)


def phi(n: int) -> int:
    """Euler's totient function: Gives the count of integers between 1 and
    n (inclusive) which are relatively prime to n.
    """
    factors = prime_factors(n)
    return reduce(operator.mul, (_phi(p, exp) for p, exp in factors), 1)


def powmod(base: int, exp: int, mod: int) -> int:
    """Compute base^exp (mod mod)"""
    return int(Modular(mod)(base) ** exp)


if __name__ == '__main__':
    for i in range(1, 101):
        print(i)
        print(' prime factors:', prime_factors(i))
        print(' phi:', phi(i))
        Modi = Modular(i)
        print(f' 3^31 mod {i} =', Modi(3)**31)
        print()
        print('3^101 mod 5 =', powmod(3, 101, 5))
        print('3 == 1 (mod 2) ->', Modular(2)(3) == 1)
