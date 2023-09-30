import pygame
from math import sqrt, gcd

pygame.init()


def block_size(num1, num2, max_size):
    factors = []
    highest_factor = gcd(num1, num2)

    for value in range(1, int(sqrt(highest_factor)) + 1):

        if highest_factor % value == 0:
            factors.append(value)
            if highest_factor != value * value:
                factors.append(int(highest_factor / value))

    for value in sorted(factors, reverse=True):
        if value <= max_size:
            return value

