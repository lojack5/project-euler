# Delayed computation of algebraic expressions
from __future__ import annotations
from functools import partial, reduce
import itertools
import math
import operator
from tokenize import Exponent
from typing import Callable, ClassVar, Iterable, TypeAlias, TypeGuard, TypeVar, cast
from typing_extensions import Self


def _wrap(value: Expression | int) -> Expression:
    if isinstance(value, Expression):
        return value
    elif isinstance(value, int):
        return Literal(value)
    else:
        raise TypeError(type(value))


def split(filter_fn: Callable[[Expression], bool], expressions: Iterable[Expression]) -> tuple[Iterable[Expression], Iterable[Expression]]:
    return filter(filter_fn, expressions), itertools.filterfalse(filter_fn, expressions)


def is_literal(expression: Expression) -> TypeGuard[Literal]:
    return isinstance(expression, Literal)

def extract_literals(expressions: Iterable[Expression]) -> tuple[Iterable[Literal], Iterable[Expression]]:
    return split(is_literal, expressions)   # type: ignore


class Expression:
    def eval(self) -> int:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __mod__(self, n: int) -> int:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self})'

    # Arithmethic operations
    def __add__(self, other: Expression | int) -> Sum:
        if isinstance(other, (Expression, int)):
            return Sum(self, other)
        return NotImplemented

    def __radd__(self, other: Expression | int) -> Sum:
        if isinstance(other, (Expression, int)):
            return Sum(other, self)
        return NotImplemented

    def __sub__(self, other: Expression | int) -> Sum:
        if isinstance(other, (Expression, int)):
            return Sum(self, Negation(other))
        return NotImplemented

    def __rsub__(self, other: Expression | int) -> Sum:
        if isinstance(other, (Expression, int)):
            return Sum(other, Negation(self))
        return NotImplemented

    def __mul__(self, other: Expression | int) -> Product:
        if isinstance(other, (Expression, int)):
            return Product(self, other)
        return NotImplemented

    def __rmul__(self, other: Expression | int) -> Product:
        if isinstance(other, (Expression, int)):
            return Product(other, self)
        return NotImplemented

    def __floordiv__(self, other: Expression | int) -> FloorDivision:
        if isinstance(other, (Expression, int)):
            return FloorDivision(self, other)
        return NotImplemented

    def __rfloordiv__(self, other: Expression | int) -> FloorDivision:
        if isinstance(other, (Expression, int)):
            return FloorDivision(other, self)
        return NotImplemented

    def __pow__(self, other: Expression | int) -> Power:
        if isinstance(other, (Expression, int)):
            return Power(self, other)
        return NotImplemented

    def __rpow__(self, other: Expression | int) -> Power:
        if isinstance(other, (Expression, int)):
            return Power(other, self)
        return NotImplemented

    def __neg__(self) -> Negation:
        return Negation(self)

    def __abs__(self) -> Absolute:
        return Absolute(self)


    # Evaluation
    def __int__(self) -> int:
        return self.simplify().eval()

    def simplify(self) -> Expression:
        return self


class Literal(Expression):
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    def eval(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __mod__(self, n: int) -> int:
        return self.value % n

    def __eq__(self, other: Literal) -> bool:
        if isinstance(other, Literal):
            return self.value == other.value
        return NotImplemented

    def __ne__(self, other: Literal) -> bool:
        if isinstance(other, Literal):
            return self.value != other.value
        return NotImplemented

ZERO = Literal(0)
ONE = Literal(1)


class Unary(Expression):
    value: Expression

    def __init__(self, value: Expression | int) -> None:
        self.value = _wrap(value)


class Binary(Expression):
    left: Expression
    right: Expression

    def __init__(self, left: Expression | int, right: Expression | int) -> None:
        self.left = _wrap(left)
        self.right = _wrap(right)

    def unwrap_parens(self) -> Iterable[Expression]:
        """Unwrap parenthesis.  Use for associative binary operations."""
        unwrap_type = type(self)
        if isinstance(self.left, unwrap_type):
            left = self.left.unwrap_parens()
        else:
            left = [self.left]
        if isinstance(self.right, unwrap_type):
            right = self.right.unwrap_parens()
        else:
            right = [self.right]
        return itertools.chain(left, right)


class Sum(Binary):
    def eval(self) -> int:
        return self.left.eval() + self.right.eval()

    def __str__(self) -> str:
        summands = self.unwrap_parens()
        return '(' + ' + '.join(map(str, summands)) + ')'

    def __mod__(self, n: int) -> int:
        return ((self.left % n) + (self.right % n)) % n

    def simplify(self) -> Expression:
        summands = (x.simplify() for x in self.unwrap_parens())
        literals, nonliterals = extract_literals(summands)
        # Add all the literals up
        literal = Literal(sum(x.eval() for x in literals))
        if literal == ZERO:
            final_summands = nonliterals
        else:
            final_summands = itertools.chain(nonliterals, [literal])
        return reduce(operator.add, final_summands)


class Product(Binary):
    def eval(self) -> int:
        return self.left.eval() * self.right.eval()

    def __str__(self) -> str:
        factors = self.unwrap_parens()
        return '(' + '*'.join(map(str, factors)) + ')'

    def __mod__(self, n: int) -> int:
        return ((self.left % n)*(self.right % n)) % n

    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        if left == ONE:
            return right
        elif right == ONE:
            return left
        elif left == ZERO or right == ZERO:
            return ZERO
        elif isinstance(left, FloorDivision):
            if isinstance(right, FloorDivision):
                numerator = left.left * right.left
                denominator = left.right * right.right
            else:
                numerator = left.left * right
                denominator = left.right
            return (numerator // denominator).simplify()
        elif isinstance(right, FloorDivision):
            numerator = left * right.left
            denominator = right.right
            return (numerator // denominator).simplify()
        else:
            return left * right


class Power(Binary):
    def eval(self) -> int:
        return self.left.eval() ** self.right.eval()

    def __str__(self) -> str:
        return f'{self.left}^{self.right}'

    def __mod__(self, n: int) -> int:
        # TODO: Optimize?
        return pow(self.left % n, self.right.eval(), n)

    def simplify(self) -> Expression:
        base = self.left.simplify()
        exp = self.right.simplify()
        if base == ONE:
            return base
        elif base == Literal(-1):
            if exp % 2:
                return ONE
            else:
                return base
        elif exp == ONE:
            return base
        elif exp == ZERO:
            return ONE
        # No other simplifications
        return base ** exp


class FloorDivision(Binary):
    def eval(self) -> int:
        return self.left.eval() // self.right.eval()

    def __str__(self) -> str:
        return f'({self.left}/{self.right})'

    def __mod__(self, n: int) -> int:
        return self.eval() % n

    def simplify(self) -> Expression:
        numerator = self.left.simplify()
        denominator = self.right.simplify()
        if denominator == ONE:
            return numerator
        if numerator == ZERO:
            return ZERO
        if isinstance(denominator, FloorDivision):
            return (numerator *(denominator.right // denominator.left)).simplify()
        if isinstance(numerator, FloorDivision):
            return (numerator.left // (numerator.right * denominator)).simplify()
        # Look for cancellations
        numerators: list[Expression] = []
        denominators: list[Expression] = []
        if isinstance(numerator, Product):
            numerators = list(numerator.unwrap_parens())
        elif isinstance(numerator, Literal):
            numerators = [numerator]
        if isinstance(denominator, Product):
            denominators = list(denominator.unwrap_parens())
        else:
            denominators = [denominator]
        if numerators and denominators:
            num_literals, num_others = extract_literals(numerators)
            num_literals = list(num_literals)
            den_literals, den_others = extract_literals(denominators)
            den_literals = list(den_literals)
            for i, num in enumerate(num_literals):
                num = num.eval()
                for j, den in enumerate(den_literals):
                    den = den.eval()
                    d = math.gcd(num, den)
                    num_literals[i] = Literal(num // d)
                    den_literals[j] = Literal(den // d)
            numerator = reduce(operator.mul, itertools.chain(num_literals, num_others)).simplify()
            denominator = reduce(operator.mul, itertools.chain(den_literals, den_others)).simplify()
            if denominator == ONE:
                return numerator
        return numerator // denominator


class Negation(Unary):
    def eval(self) -> int:
        return -self.value.eval()

    def __str__(self) -> str:
        return f'-{self.value}'

    def __mod__(self, n: int) -> int:
        return -(self.value % n)

    def simplify(self) -> Expression:
        value = self.value.simplify()
        if isinstance(value, Negation):
            return value.value
        elif isinstance(value, Literal):
            return Literal(-value.value)
        return -value


class Absolute(Unary):
    def eval(self) -> int:
        return abs(self.value.eval())

    def __str__(self) -> str:
        return f'|{self.value}|'

    def __mod__(self, n: int) -> int:
        return abs(self.value.eval() % n)

    def simplify(self) -> Expression:
        value = self.value.simplify()
        if isinstance(value, Absolute):
            return value
        elif isinstance(value, Literal):
            return Literal(abs(value.eval()))
        elif isinstance(value, Negation):
            return value.value
        elif isinstance(value, FloorDivision):
            return (abs(value.left) // abs(value.right)).simplify()
        elif isinstance(value, Product):
            return (abs(value.left) * abs(value.right)).simplify()
        return self


def b(n: Expression) -> int:
    divisor = 1
    while not n % divisor:
        divisor *= 2
    return divisor


if __name__ == '__main__':
    exp = abs(Literal(-2) // -3) // (Literal(2) // 3)
    print('Expression:', exp)
    simp = exp.simplify()
    print('Simplified:', simp)
    try:
        print('Evaluated (original):', exp.eval())
    except (ValueError, ZeroDivisionError):
        print('Cannot evalute original without simplifying')
    print('Evaluated (simplified):', int(exp))
