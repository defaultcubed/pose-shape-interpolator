
from math import isclose, sin
from typing import TYPE_CHECKING
from .utils import driver_ensure, normalize
if TYPE_CHECKING:
    from typing import Iterable, TypeVar
    from bpy.types import ID
    from mathutils import Matrix
    from .rna import (
        PoseShapeInterpolator,
        PoseShapeInterpolatorInput,
        PoseShapeInterpolatorPose
    )
    T = TypeVar('T')


def qt_aim_x(quaternion: 'tuple[float, float, float, float]') -> 'tuple[float, float, float]':
    w, x, y, z = quaternion
    return (1.0 - 2.0*(y*y + z*z), 2.0*(x*y + w*z), 2.0*(x*z - w*y))


def qt_aim_y(quaternion: 'tuple[float, float, float, float]') -> 'tuple[float, float, float]':
    w, x, y, z = quaternion
    return (2.0*(x*y - w*z), 1.0 - 2.0*(x*x + z*z), 2.0*(y*z + w*x))


def qt_aim_z(quaternion: 'tuple[float, float, float, float]') -> 'tuple[float, float, float]':
    w, x, y, z = quaternion
    return (2.0*(x*z + w*y), 2.0*(y*z - w*x), 1.0 - 2.0*(x*x + y*y))


QT_AIM = {
    'X': qt_aim_x,
    'Y': qt_aim_y,
    'Z': qt_aim_z,
}


QT_AIM_EXPR = {
    'X': (
        "1.0-2.0*(y*y+z*z)",
        "2.0*(x*y+w*z)",
        "2.0*(x*z-w*y)",
    ),
    'Y': (
        "2.0*(x*y-w*z)",
        "1.0-2.0*(x*x+z*z)",
        "2.0*(y*z+w*x)",
    ),
    'Z': (
        "2.0*(x*z+w*y)",
        "2.0*(y*z-w*x)",
        "1.0-2.0*(x*x+y*y)",
    ),
}


class InputLayer:

    def __init__(self,
            input_: 'PoseShapeInterpolatorInput',
            poses: 'list[PoseShapeInterpolatorPose]') -> None:
        self.channels = []
        self.posedata = []
        self.vecnorms = []
        matrices = [pose.data.get(input_).matrix for pose in poses]
        self._add_location(input_, matrices)
        self._add_rotation(input_, matrices)
        self._add_scale(input_, matrices)

    def _add_location(self, input_: 'PoseShapeInterpolatorInput', matrices: 'list[Matrix]') -> None:
        flags = (
            input_.use_location_x,
            input_.use_location_y,
            input_.use_location_z,
        )
        if not any(flags):
            return
        ob = input_.object
        pb = input_.bone_target
        for flag, axis, data in zip(flags, 'XYZ', zip(*[m.location for m in matrices])):
            if not flag:
                continue
            seq = list(data)
            self.posedata.append(seq)
            self.vecnorms.append(normalize(seq))
            self.channels.append({
                "name": f'l{axis.lower()}',
                "type": 'TRANSFORMS',
                "targets": [{
                    "transform_type": f'LOC_{axis}',
                    "id": ob,
                    "bone_target": pb,
                    "transform_space": 'LOCAL_SPACE'
                }]
            })

    def _add_rotation(self, input_: 'PoseShapeInterpolatorInput', matrices: 'list[Matrix]') -> None:
        if not input_.use_rotation:
            return
        mode = input_.rotation_mode
        axis = input_.rotation_axis
        if mode == 'ANGLE':
            self._add_rotation_angle(input_, matrices, axis)
            return
        if 'SWING' in mode:
            self._add_rotation_swing(input_, matrices, axis)
        if 'TWIST' in mode:
            self._add_rotation_twist(input_, matrices, axis)

    def _add_rotation_angle(self, input_: 'PoseShapeInterpolatorInput', matrices: 'list[Matrix]', axis: str) -> None:
        idx = 'XYZ'.index(axis)
        seq = [m.rotation_euler[idx] for m in matrices]
        self.posedata.append(seq)
        self.vecnorms.append(normalize(seq))
        self.channels.append({
            "name": "a",
            "type": 'TRANSFORMS',
            "targets": [{
                "id": input_.object,
                "bone_target": input_.name,
                "transform_type": f'ROT_{axis}',
                "transform_space": 'LOCAL_SPACE',
                "rotation_mode": 'AUTO'
            }]
        })

    def _add_rotation_swing(self, input_: 'PoseShapeInterpolatorInput', matrices: 'list[Matrix]', axis: str) -> None:
        qts = [mat.rotation_quaternion for mat in matrices]
        mat = map(list, zip(*map(QT_AIM[axis], qts)))
        key = input_.id_data
        propname = input_.handle
        for index, (axis, seq, expr) in enumerate(zip('XYZ', mat, QT_AIM_EXPR[axis])):
            path = f'["{propname}"][{index}]'
            self.posedata.append(seq)
            self.vecnorms.append(normalize(seq))
            self.channels.append({
                "name": f'd{axis.lower()}',
                "type": 'SINGLE_PROP',
                "targets": [{
                    "id_type": 'KEY',
                    "id": key,
                    "data_path": path
                }]
            })
            fc = driver_ensure(key, path, index, clear_variables=True)
            dr = fc.driver
            dr.type = 'SCRIPTED'
            dr.expression = expr
            for axis in 'wxyz':
                if axis not in expr:
                    continue
                var = dr.variables.new()
                var.type = 'TRANSFORMS'
                var.name = axis
                tgt = var.targets[0]
                tgt.id = input_.object
                tgt.bone_target = input_.bone_target
                tgt.rotation_mode = 'QUATERNION'
                tgt.transform_space = 'LOCAL_SPACE'
                tgt.transform_type = f'ROT_{axis.upper()}'


    def _add_rotation_twist(self, input_: 'PoseShapeInterpolatorInput', matrices: 'list[Matrix]', axis: str) -> None:
        qts = [mat.rotation_quaternion for mat in matrices]
        seq = [2.0 * sin(qt.to_swing_twist(axis)[1]) for qt in qts]
        self.posedata.append(seq)
        self.vecnorms.append(normalize(seq))
        self.channels.append({
            "name": "s",
            "type": 'TRANSFORMS',
            "targets": [{
                "id": input_.object,
                "bone_target": input_.name,
                "transform_type": f'ROT_{axis}',
                "transform_space": 'LOCAL_SPACE',
                "rotation_mode": f'SWING_TWIST_{axis}'
            }]
        })

    def _add_scale(self, input_: 'PoseShapeInterpolatorInput', matrices: 'list[Matrix]') -> None:
        flags = (
            input_.use_scale_x,
            input_.use_scale_y,
            input_.use_scale_z,
        )
        if not any(flags):
            return
        ob = input_.object
        pb = input_.bone_target
        for flag, axis, data in zip(flags, 'XYZ', zip(*[m.location for m in matrices])):
            if not flag:
                continue
            seq = list(data)
            self.posedata.append(seq)
            self.vecnorms.append(normalize(seq))
            self.channels.append({
                "name": f's{axis.lower()}',
                "type": 'TRANSFORMS',
                "targets": [{
                    "transform_type": f'SCALE_{axis}',
                    "id": ob,
                    "bone_target": pb,
                    "transform_space": 'LOCAL_SPACE'
                }]
            })







class IDProperty:

    def __init__(self, name: str, key: 'ID', propname: str) -> None:
        key[propname] = 0.0
        self.name = name
        self.targets = [{
            "id_type": 'KEY',
            "id": key,
            "data_path": f'["{propname}"]'
        }]


def transpose_matrix(m: Iterable[Iterable[T]]) -> list[list[T]]:
    return list(map(list, zip(*m)))


def read_inputs(
        psi: 'PoseShapeInterpolator'
        ) -> 'list[PoseShapeInterpolatorInput]':
    inputs = []
    for inp in psi.inputs:
        if not inp.is_valid:
            raise RuntimeError(f'Invalid input: "{inp.name}"')
        if inp.is_enabled:
            inputs.append(inp)
    if not inputs:
        raise RuntimeError('No enabled inputs')
    return inputs


def read_poses(
        psi: 'PoseShapeInterpolator'
        ) -> 'list[PoseShapeInterpolatorPose]':
    poses = []
    for pose in psi.poses:
        if not pose.is_valid:
            raise RuntimeError(f'Invalid pose: "{pose.name}"')
        poses.append(pose)
    if len(poses) < 2:
        raise RuntimeError('No poses defined')
    return poses


def read_data_matrices(
        poses: 'Iterable[PoseShapeInterpolatorPose]'
        ) -> 'tuple[list[list[Matrix]], list[list[Matrix]]]':
    pose_data_matrix: 'list[list[Matrix]]' = []
    for pose in poses:
        pose_data_matrix.append([x.matrix for x in pose.data])
    input_data_matrix: 'list[list[Matrix]]' = transpose_matrix(pose_data_matrix)
    return pose_data_matrix, input_data_matrix


def unbind(psi: 'PoseShapeInterpolator') -> None:
    pass


def bind(psi: 'PoseShapeInterpolator') -> None:

    inputs = read_inputs(psi)
    poses = read_poses(psi)
    pose_data_matrix, input_data_matrix = read_data_matrices(poses)

    layers = []

    for input_, pose_data in zip(inputs, input_data_matrix):
        flags = (
            input_.use_location_x,
            input_.use_location_y,
            input_.use_location_z,
        )
        if any(flags):
            vectors = list(zip(*[matrix.location for matrix in pose_data]))
            for in_use, axis, vector in zip(flags, 'XYZ', vectors):
                if not in_use:
                    continue
                # Template :
