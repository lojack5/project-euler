from typing import Iterable
import itertools

# NOTE: These are *infinite* generators, use itertools.dropwhile/takewhile
# to make finite sub generators
def triangular_numbers(n: int = 1) -> Iterable[int]:
    """Generate triangular numbers starting with the n-th one."""
    return (n*(n+1)//2 for n in itertools.count(n))


def square_numbers(n: int = 1) -> Iterable[int]:
    """Generate square numbers starting with the n-th one."""
    return (n**2 for n in itertools.count(n))


def pentagonal_numbers(n: int = 1) -> Iterable[int]:
    """Generate pentagonal numbers starting with the n-th one."""
    return (n*(3*n-1)//2 for n in itertools.count(n))


def hexagonal_numbers(n: int = 1) -> Iterable[int]:
    """Generate pentagonal numbers starting with the n-th one."""
    return (n*(2*n - 1) for n in itertools.count(n))


def heptagonal_numbers(n: int = 1) -> Iterable[int]:
    """Generate heptagonal numbers starting with the n-th one."""
    return (n*(5*n - 2)//2 for n in itertools.count(n))


def octagonal_numbers(n: int = 1) -> Iterable[int]:
    """Generate octagonal numbers starting with the n-th one."""
    return (n*(3*n - 2) for n in itertools.count(n))


def is_cyclic_pair(a: int, b: int, divisor: int = 10**2) -> bool:
    """Test if two numbers are cyclic pairs.  This is tested by division,
    to compute the divisor raise the base to represent the numbers in raised to
    the power of how many digits need to match to be cyclic.
    """
    return (a % divisor) == (b // divisor)


def filter_four_digit(generator) -> tuple[int, ...]:
    """Specific to this problem: filter a generator of numbers to only 4-digit
    numbers in base 10.
    """
    return tuple(
        itertools.takewhile(lambda x: x <= 9999,
            itertools.dropwhile(lambda x: x < 1000,
                generator())
        )
    )


def build_next_cyclic_numbers(seed: int, *candidates: tuple[int, ...]) -> Iterable[list[int]]:
    """Recursively build candidate chains of cyclic numbers.  The seed is the
    first number in the chain.  candidates are the collections of numbers to
    choose successive numbers from.  The first and last numbers are not checked
    for cyclic behavior.
    """
    if not candidates:
        yield []
    else:
        next_options = candidates[0]
        remaining_collections = candidates[1:]
        for next_number in next_options:
            if is_cyclic_pair(seed, next_number):
                for tail in build_next_cyclic_numbers(next_number, *remaining_collections):
                    yield [next_number] + tail


def find_the_answer() -> list[int]:
    """Find 6 distinct numbers, one from each type of geometric number
    (trangular, square, ...) that for a two digit cycle in base 10.
    """
    types = list(map(filter_four_digit, (triangular_numbers, square_numbers,
        pentagonal_numbers, hexagonal_numbers, heptagonal_numbers,
        octagonal_numbers))
    )

    first = types[0]
    rest = types[1:]
    for first_number in first:
        # Gotta test all possible ways to order the remaining sets:
        for remaining_sets in itertools.permutations(rest, 5):
            for tail in build_next_cyclic_numbers(first_number, *remaining_sets):
                # Test the correct number of ints
                if len(tail) == len(rest):
                    # And that it cyles around
                    if is_cyclic_pair(tail[-1], first_number):
                        cycle = [first_number] + tail
                        # Finally check no duplicates
                        if len(set(cycle)) == len(cycle):
                            return cycle
    return []


def classify_number(n: int) -> list[str]:
    """Generate a list of descriptions for a number ('triangular', 'square',
    etc)
    """
    classifications = []
    for name, generator in [
        ('triangular', triangular_numbers),
        ('square', square_numbers),
        ('pentagonal', pentagonal_numbers),
        ('hexagonal', hexagonal_numbers),
        ('heptagonal', heptagonal_numbers),
        ('octagonal', octagonal_numbers)
    ]:
        filtered = itertools.dropwhile(lambda x: x < n, generator())
        filtered = itertools.takewhile(lambda x: x == n, filtered)
        if n in filtered:
            classifications.append(name)
    return classifications


if __name__ == '__main__':
    cycle = find_the_answer()
    print('Cycle:', cycle)
    for n in cycle:
        print(f' {n} is', ', '.join(classify_number(n)))
