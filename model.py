"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from random import random
import constants
from math import sin, cos, pi
import math


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)

    def distance(self, point2: Point) -> float:
        """Returns distance between two points."""
        return math.sqrt((self.x - point2.x) ** 2 + (self.y - point2.y) ** 2)


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    def tick(self) -> None:
        """Reassign objects location."""
        self.location = self.location.add(self.direction)
        if self.is_infected():
            self.sickness += 1
        if self.sickness > constants.RECOVERY_PERIOD:
            self.immunize()

    def contract_disease(self) -> None:
        """Infect cell."""
        self.sickness = constants.INFECTED

    def is_vulnerable(self) -> bool:
        """Returns true if cell is vulnerable."""
        if self.sickness == constants.VULNERABLE:
            return True
        else:
            return False

    def is_infected(self) -> bool:
        """Returns true if cell is infected."""
        if self.sickness >= constants.INFECTED:
            return True
        else:
            return False

    def color(self) -> str:
        """Return the color representation of a cell."""
        if self.is_vulnerable():
            return "gray"
        if self.is_infected():
            return "red"
        if self.is_immune():
            return "yellow"
        return ""

    def contact_with(self, cell2: Cell) -> None:
        """When two cells make contact and one is infected and the other is vulnerable infect the other."""
        if cell2.is_infected() and self.is_vulnerable():
            self.contract_disease()
        elif self.is_infected() and cell2.is_vulnerable():
            cell2.contract_disease()

    def immunize(self) -> None:
        """Immunize cell."""
        self.sickness = constants.IMMUNE

    def is_immune(self) -> bool:
        """Check if cell is immune."""
        if self.sickness == constants.IMMUNE:
            return True
        else:
            return False


class Model:
    """The state of the simulation."""

    population: list[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, num_infected: int, num_immune: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []
        if num_infected >= cells or num_infected <= 0 or ((num_immune + num_infected) > cells) or num_immune < 0 or num_immune >= cells:
            raise ValueError()
        for _ in range(num_immune):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            cell: Cell = Cell(start_location, start_direction)
            cell.immunize()
            self.population.append(cell)
        for _ in range(num_infected):
            start_location = self.random_location()
            start_direction = self.random_direction(speed)
            cell = Cell(start_location, start_direction)
            cell.contract_disease()
            self.population.append(cell)
        for _ in range(cells - num_infected - num_immune):
            start_location = self.random_location()
            start_direction = self.random_direction(speed)
            cell = Cell(start_location, start_direction)
            self.population.append(cell)

    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
        self.check_contacts()

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x: float = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y: float = random() * constants.BOUNDS_WIDTH - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle: float = 2.0 * pi * random()
        direction_x: float = cos(random_angle) * speed
        direction_y: float = sin(random_angle) * speed
        return Point(direction_x, direction_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1.0
        if cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1.0
        if cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1.0
        if cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1.0

    def check_contacts(self) -> None:
        """Check if any two cells make contact."""
        n: int = len(self.population)
        i: int = 0
        while (i < (n)):
            cell1: Cell = self.population[i]
            j: int = i + 1
            while (j < n):
                cell2: Cell = self.population[j]
                if cell1.location.distance(cell2.location) < constants.CELL_RADIUS:
                    cell1.contact_with(cell2)
                j += 1
            i += 1

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        for cell in self.population:
            if cell.is_infected():
                return False
        return True
