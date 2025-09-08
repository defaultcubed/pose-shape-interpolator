
from bpy.types import FCurve, ID
from math import isclose, sqrt
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable


def driver_find(id_: 'ID', path: str, index: int=-1) -> 'FCurve|None':
    ad = id_.animation_data
    if ad is None:
        return
    fx = ad.drivers
    return fx.find(path) if index < 0 else fx.find(path, index=index)


def driver_remove(id_: 'ID', path: str, index: int=-1) -> None:
    fc = driver_find(id_, path, index)
    if fc is not None:
        fc.id_data.animation_data.drivers.remove(fc)


def driver_ensure(id_: 'ID',
                  path: str,
                  index: int=-1,
                  clear_variables: bool=False,
                  reset_keyframes: bool=False) -> 'FCurve':
    fc = driver_find(id_, path, index)

    if fc is None:
        fx = id_.animation_data_create().drivers
        fc = fx.new(path, index=index) if index >= 0 else fx.new(path)

    if clear_variables:
        vars = fc.driver.variables
        size = len(vars)
        while size:
            size -= 1
            vars.remove(vars[size])

    if reset_keyframes:
        kfs = fc.keyframe_points
        kfs.clear()

        kf1 = kfs.insert(0.0, 1.0)
        kf1.interpolation = 'BEZIER'
        kf1.handle_left_type = 'FREE'
        kf1.handle_left = (-1/3, 1+1/3)
        kf1.handle_right_type = 'FREE'
        kf1.handle_right = (1/3, 2/3)

        kf2 = kfs.insert(1.0, 0.0)
        kf2.interpolation='BEZIER'
        kf2.handle_left_type = 'FREE'
        kf2.handle_left = (2/3, 1/3)
        kf2.handle_right_type = 'FREE'
        kf2.handle_right = (1+1/3, -1/3)

    return fc


def sum_of_squares(vec: list[float]) -> float:
    return sum(x**2 for x in vec)


def normalize(vec: list[float]) -> float:
    norm = sum_of_squares(vec)
    if isclose(norm, 0.0, abs_tol=1e-5):
        return 1.0
    for i in range(len(vec)):
        vec[i] /= norm
    return norm


def distance(a: 'Iterable[float]', b: 'Iterable[float]') -> float:
    return sqrt(sum_of_squares([x-y for x, y in zip(a, b)]))
