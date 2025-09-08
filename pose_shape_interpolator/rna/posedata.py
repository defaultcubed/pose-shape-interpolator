
import bpy
from mathutils import Vector, Matrix, Quaternion, Euler


def _handle_get(i):
    return i.get('input_handle', '')


def _loc_get(i):
    return i.matrix.to_translation()


def _loc_set(i, v):
    i.matrix = Matrix.LocRotScale(Vector(v), _rot_qt_get(i), _scale_get(i))


def _rot_aa_get(i):
    axis, angle = _rot_qt_get(i).to_axis_angle()
    return Vector((angle, axis[0], axis[1], axis[2]))


def _rot_aa_set(i, v):
    i.matrix = Matrix.LocRotScale(_loc_get(i), Quaternion((v[1], v[2], v[3]), v[0]), _scale_get(i))


def _rot_eul_get(i):
    return i.matrix.to_euler(i)


def _rot_eul_set(i, v):
    i.matrix = Matrix.LocRotScale(_loc_get(i), Euler(v).to_quaternion(), _scale_get(i))


def _rot_qt_get(i):
    return i.matrix.to_quaternion()


def _rot_qt_set(i, v):
    i.matrix = Matrix.LocRotScale(_loc_get(i), Quaternion(v), _scale_get(i))


def _scale_get(i):
    return i.matrix.to_scale()


def _scale_set(i, v):
    i.matrix = Matrix.LocRotScale(_loc_get(i), _rot_qt_get(i), v)


class PSI_InputPose(bpy.types.PropertyGroup):

    input_handle: bpy.props.StringProperty(
        name="Input Handle",
        description="The unique handle of the associated input (read-only)",
        get=_handle_get,
        options={'HIDDEN'}
        )#type: ignore

    matrix: bpy.props.FloatVectorProperty(
        name="Matrix",
        description="Pose transform matrix",
        size=(4, 4),
        subtype='MATRIX',
        options=set()
        )#type: ignore

    rotation_axis_angle: bpy.props.FloatVectorProperty(
        name="Rotation",
        description="Interpolated pose rotation as axis angle",
        size=4,
        get=_rot_aa_get,
        set=_rot_aa_set,
        subtype='AXISANGLE',
        options=set()
        )#type: ignore

    rotation_euler: bpy.props.FloatVectorProperty(
        name="Rotation",
        description="Interpolated pose rotation in euler angles",
        get=_rot_eul_get,
        set=_rot_eul_set,
        subtype='EULER',
        options=set()
        )#type: ignore

    rotation_quaternion: bpy.props.FloatVectorProperty(
        name="Rotation",
        description="Interplated pose rotation quaternion",
        get=_rot_qt_get,
        set=_rot_qt_set,
        size=4,
        subtype='QUATERNION',
        options=set()
        )#type: ignore

    scale: bpy.props.FloatVectorProperty(
        name="Scale",
        description="Interpolated pose scale",
        get=_scale_get,
        set=_scale_set,
        subtype='XYZ',
        options=set()
        )#type: ignore
