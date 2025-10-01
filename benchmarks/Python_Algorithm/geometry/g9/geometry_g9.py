from __future__ import annotations

import math
import argparse
from dataclasses import dataclass, field
from types import NoneType
from typing import Self

# Building block classes


@dataclass(slots=True)
class Angle:
    """
    An Angle in degrees (unit of measurement)

    >>> Angle()
    Angle(degrees=90)
    >>> Angle(45.5)
    Angle(degrees=45.5)
    >>> Angle(-1)
    Traceback (most recent call last):
        ...
    TypeError: degrees must be a numeric value between 0 and 360.
    >>> Angle(361)
    Traceback (most recent call last):
        ...
    TypeError: degrees must be a numeric value between 0 and 360.
    """

    degrees: float = 90

    def __post_init__(self) -> None:
        if not isinstance(self.degrees, (int, float)) or not 0 <= self.degrees <= 360:
            raise TypeError("degrees must be a numeric value between 0 and 360.")


@dataclass(slots=True)
class Side:
    """
    A side of a two dimensional Shape such as Polygon, etc.
    adjacent_sides: a list of sides which are adjacent to the current side
    angle: the angle in degrees between each adjacent side
    length: the length of the current side in meters

    >>> Side(5)
    Side(length=5, angle=Angle(degrees=90), next_side=None)
    >>> Side(5, Angle(45.6))
    Side(length=5, angle=Angle(degrees=45.6), next_side=None)
    >>> Side(5, Angle(45.6), Side(1, Angle(2))) # doctest: +ELLIPSIS
    Side(length=5, angle=Angle(degrees=45.6), next_side=Side(length=1, angle=Angle(d...
    >>> Side(-1)
    Traceback (most recent call last):
        ...
    TypeError: length must be a positive numeric value.
    >>> Side(5, None)
    Traceback (most recent call last):
        ...
    TypeError: angle must be an Angle object.
    >>> Side(5, Angle(90), "Invalid next_side")
    Traceback (most recent call last):
        ...
    TypeError: next_side must be a Side or None.
    """

    length: float
    angle: Angle = field(default_factory=Angle)
    next_side: Side | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.length, (int, float)) or self.length <= 0:
            raise TypeError("length must be a positive numeric value.")
        if not isinstance(self.angle, Angle):
            raise TypeError("angle must be an Angle object.")
        if not isinstance(self.next_side, (Side, NoneType)):
            raise TypeError("next_side must be a Side or None.")


@dataclass(slots=True)
class Ellipse:
    """
    A geometric Ellipse on a 2D surface

    >>> Ellipse(5, 10)
    Ellipse(major_radius=5, minor_radius=10)
    >>> Ellipse(5, 10) is Ellipse(5, 10)
    False
    >>> Ellipse(5, 10) == Ellipse(5, 10)
    True
    """

    major_radius: float
    minor_radius: float

    @property
    def area(self) -> float:
        """
        >>> Ellipse(5, 10).area
        157.07963267948966
        """
        return math.pi * self.major_radius * self.minor_radius

    @property
    def perimeter(self) -> float:
        """
        >>> Ellipse(5, 10).perimeter
        47.12388980384689
        """
        return math.pi * (self.major_radius + self.minor_radius)


class Circle(Ellipse):
    """
    A geometric Circle on a 2D surface

    >>> Circle(5)
    Circle(radius=5)
    >>> Circle(5) is Circle(5)
    False
    >>> Circle(5) == Circle(5)
    True
    >>> Circle(5).area
    78.53981633974483
    >>> Circle(5).perimeter
    31.41592653589793
    """
    __slots__ = ('radius',)

    def __init__(self, radius: float) -> None:
        super().__init__(radius, radius)
        self.radius = radius

    def __repr__(self) -> str:
        return f"Circle(radius={self.radius})"

    @property
    def diameter(self) -> float:
        """
        >>> Circle(5).diameter
        10
        """
        return self.radius * 2

    def max_parts(self, num_cuts: float) -> float:
        """
        Return the maximum number of parts that circle can be divided into if cut
        'num_cuts' times.

        >>> circle = Circle(5)
        >>> circle.max_parts(0)
        1.0
        >>> circle.max_parts(7)
        29.0
        >>> circle.max_parts(54)
        1486.0
        >>> circle.max_parts(22.5)
        265.375
        >>> circle.max_parts(-222)
        Traceback (most recent call last):
            ...
        TypeError: num_cuts must be a positive numeric value.
        >>> circle.max_parts("-222")
        Traceback (most recent call last):
            ...
        TypeError: num_cuts must be a positive numeric value.
        """
        if not isinstance(num_cuts, (int, float)) or num_cuts < 0:
            raise TypeError("num_cuts must be a positive numeric value.")
        return (num_cuts + 2 + num_cuts**2) * 0.5


@dataclass(slots=True)
class Polygon:
    """
    An abstract class which represents Polygon on a 2D surface.

    >>> Polygon()
    Polygon(sides=[])
    >>> polygon = Polygon()
    >>> polygon.add_side(Side(5)).get_side(0)
    Side(length=5, angle=Angle(degrees=90), next_side=None)
    >>> polygon.get_side(1)
    Traceback (most recent call last):
        ...
    IndexError: list index out of range
    >>> polygon.set_side(0, Side(10)).get_side(0)
    Side(length=10, angle=Angle(degrees=90), next_side=None)
    >>> polygon.set_side(1, Side(10))
    Traceback (most recent call last):
        ...
    IndexError: list assignment index out of range
    """

    sides: list[Side] = field(default_factory=list)

    def add_side(self, side: Side) -> Self:
        """
        >>> Polygon().add_side(Side(5))
        Polygon(sides=[Side(length=5, angle=Angle(degrees=90), next_side=None)])
        """
        self.sides.append(side)
        return self

    def get_side(self, index: int) -> Side:
        """
        >>> Polygon().get_side(0)
        Traceback (most recent call last):
            ...
        IndexError: list index out of range
        >>> Polygon().add_side(Side(5)).get_side(-1)
        Side(length=5, angle=Angle(degrees=90), next_side=None)
        """
        return self.sides[index]

    def set_side(self, index: int, side: Side) -> Self:
        """
        >>> Polygon().set_side(0, Side(5))
        Traceback (most recent call last):
            ...
        IndexError: list assignment index out of range
        >>> Polygon().add_side(Side(5)).set_side(0, Side(10))
        Polygon(sides=[Side(length=10, angle=Angle(degrees=90), next_side=None)])
        """
        self.sides[index] = side
        return self


@dataclass(slots=True)
class Rectangle:
    """
    A geometric rectangle on a 2D surface.

    >>> rectangle_one = Rectangle(5, 10)
    >>> rectangle_one.perimeter()
    30
    >>> rectangle_one.area()
    50
    >>> Rectangle(-5, 10)
    Traceback (most recent call last):
        ...
    TypeError: Side lengths must be positive numeric values.
    """
    short_side_length: float
    long_side_length: float

    def __post_init__(self) -> None:
        if self.short_side_length <= 0 or self.long_side_length <= 0:
            raise TypeError("Side lengths must be positive numeric values.")

    def perimeter(self) -> float:
        return (self.short_side_length + self.long_side_length) * 2

    def area(self) -> float:
        return self.short_side_length * self.long_side_length


class Square(Rectangle):
    """
    a structure which represents a
    geometrical square on a 2D surface
    >>> square_one = Square(5)
    >>> square_one.perimeter()
    20
    >>> square_one.area()
    25
    """
    __slots__ = () # No new attributes beyond what Rectangle has

    def __init__(self, side_length: float) -> None:
        super().__init__(side_length, side_length)

    def __repr__(self) -> str:
        return f"Square(side_length={self.short_side_length})"


def main(size: str) -> None:
    """
    主执行函数，根据指定的规模运行不同的工作负载。
    """
    print(f"Selected size: '{size}'")

    if size == "small":
        print("Running 'small' workload: Creating a few geometric shapes.")
        # 创建少量对象并计算其属性
        square = Square(10)
        rectangle = Rectangle(5, 20)
        circle = Circle(15)

        print(f"Square area: {square.area()}, perimeter: {square.perimeter()}")
        print(f"Rectangle area: {rectangle.area()}, perimeter: {rectangle.perimeter()}")
        print(f"Circle area: {circle.area}, perimeter: {circle.perimeter}")

    elif size == "large":
        num_objects = 100_000 # 使用下划线提高可读性
        print(f"Running 'large' workload: Creating and processing {num_objects} objects.")
        
        # Procesar objetos sobre la marcha para ahorrar memoria (complejidad de memoria O(1))
        total_area = 0.0
        for i in range(1, num_objects + 1):
            total_area += Square(side_length=i * 0.01).area()

        print(f"Successfully processed {num_objects} squares.")
        print(f"Total area of all squares: {total_area}")

    elif size == "xlarge":
        num_objects = 1_000_000 # 增加到一百万个对象
        print(f"Running 'xlarge' workload: Creating and processing {num_objects} objects.")
        
        # Procesar objetos sobre la marcha para ahorrar memoria
        total_area = 0.0
        total_perimeter = 0.0
        for i in range(1, num_objects + 1):
            # Usar una tupla para la desempaquetación de argumentos es marginalmente más rápido
            args = (i * 0.01, i * 0.02)
            rect = Rectangle(*args)
            total_area += rect.area()
            total_perimeter += rect.perimeter()
        
        print(f"Successfully processed {num_objects} rectangles.")
        print(f"Total area of all rectangles: {total_area}")
        print(f"Total perimeter of all rectangles: {total_perimeter}")


    print("\nProcessing complete.")


if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(
        description="A geometric shapes calculation application to test performance.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--size",
        choices=["small", "large", "xlarge"], # 增加了 'xlarge' 选项
        required=True,
        help=(
            "Select the data scale for the workload:\n"
            "'small': Creates and calculates properties for a few shapes.\n"
            "'large': Creates and calculates properties for 100,000 shapes.\n"
            "'xlarge': Creates and processes 1,000,000 more complex shapes."
        ),
    )

    args = parser.parse_args()
    main(args.size)