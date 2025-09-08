
from uuid import uuid4
from typing import TYPE_CHECKING
from bpy.types import Object, PoseBone, PropertyGroup, ShaderNodeTree, ShapeKey
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    StringProperty,
    PointerProperty
    )
from mathutils import Euler, Matrix, Quaternion, Vector
from .ipo import InterpolationSettings, curve_mapping_tree_get, curve_mapping_tree_ensure
if TYPE_CHECKING:
    from typing import Iterable, Iterator
    from bpy.types import Context

__all__ = (
    "PoseShapeInterpolatorInput",
    "PoseShapeInterpolatorInputs",
    "PoseShapeInterpolatorInputPose",
    "PoseShapeInterpolatorPoseData",
    "PoseShapeInterpolatorPose",
    "PoseShapeInterpolatorPoses",
    "PoseShapeInterpolator",
    "PoseShapeInterpolators",
)


class PoseShapeInterpolatorInput(PropertyGroup):

    def _handle_ensure(self) -> str:
        handle = self.get("handle", "")
        if not handle:
            handle = str(uuid4())
            self["handle"] = handle
        return handle

    def _init(self, target: 'str|PoseBone') -> None:
        if isinstance(target, str):
            self["name"] = target
        else:
            self["object"] = target.id_data
            self["name"] = target.name

    def _is_enabled(self) -> bool:
        return (
            self.use_location_x
            or self.use_location_y
            or self.use_location_z
            or self.use_rotation
            or self.use_scale_x
            or self.use_scale_y
            or self.use_scale_z
        )

    def _is_valid(self) -> bool:
        return self.resolve() is not None

    def _name_search(self, context: 'Context', edit_text: str) -> 'Iterable[str]':
        o = self.object
        if o is None:
            return tuple()
        s = set(o.data.bones.keys())
        for x in self.id_data.pose_shape_interpolator_settings:
            if x.object != o:
                continue
            for i in x.inputs:
                if i != self:
                    s.discard(i.name)
        return s

    def _object_poll(self, object_: 'Object') -> bool:
        return object_.type == 'ARMATURE'

    handle: StringProperty(
        name="Handle",
        description="Unique input identifier (read-only)",
        get=_handle_ensure,
        options={'HIDDEN'}
        )# type: ignore

    is_enabled: BoolProperty(
        name="Enabled",
        description="True if any input channels are in use (read-only)",
        get=_is_enabled,
        optinos=set()
        )# type: ignore

    is_valid: BoolProperty(
        name="Valid",
        description="True if an associated pose bone exists for this input (readonly)",
        get=_is_valid,
        options=set()
        )# type: ignore

    name: StringProperty(
        name="Name",
        description="The name of the pose bone to use as input",
        search=_name_search,
        options=set()
        )# type: ignore

    object: PointerProperty(
        name="Object",
        description="The (armature) object to use as input",
        type=Object,
        poll=_object_poll,
        options=set()
        )# type: ignore

    rotation_axis: EnumProperty(
        name="Axis",
        description="Rotation axis",
        items=[
            ('X', "X", "X Axis"),
            ('Y', "Y", "Y Axis"),
            ('Z', "Z", "Z Axis"),
        ],
        default='Y',
        options=set()
        )# type: ignore

    rotation_mode: EnumProperty(
        name="Mode",
        description="Rotation channels to include in interpolation",
        items=[
            ('ANGLE', "Angle", "Single rotation angle (euler)"),
            ('SWING', "Swing", "Swing rotation around axis"),
            ('TWIST', "Twist", "Twist rotation around axis"),
            ('SWING_TWIST', "Swing & Twist", "Use all rotation channels"),
        ],
        default='SWING_TWIST',
        options=set()
        )# type: ignore

    use_location_x: BoolProperty(
        name="X",
        description="X location input",
        default=False,
        options=set()
        )# type: ignore

    use_location_y: BoolProperty(
        name="Y",
        description="Y location input",
        default=False,
        options=set()
        )# type: ignore

    use_location_z: BoolProperty(
        name="Z",
        description="Z location input",
        default=False,
        options=set()
        )# type: ignore

    use_rotation: BoolProperty(
        name="Rotation",
        description="Rotation input",
        default=False,
        options=set()
        )# type: ignore

    use_scale_x: BoolProperty(
        name="X",
        description="X scale input",
        default=False,
        options=set()
        )# type: ignore

    use_scale_y: BoolProperty(
        name="Y",
        description="Y scale input",
        default=False,
        options=set()
        )# type: ignore

    use_scale_z: BoolProperty(
        name="Z",
        description="Z scale input",
        default=False,
        options=set()
        )# type: ignore

    def matrix_resolve(self) -> 'Matrix':
        pb = self.resolve()
        if pb is None:
            return Matrix.Identity(4)
        return pb.id_data.convert_space(
            pose_bone=pb,
            matrix=pb.matrix,
            from_space='POSE',
            to_space='LOCAL'
        )

    def resolve(self) -> 'PoseBone|None':
        ob = self.object
        if ob is not None and ob.type == 'ARMATURE':
            return ob.pose.bones.get(self.name)


class PoseShapeInterpolatorInputs(PropertyGroup):

    def __contains__(self, name: str) -> bool:
        for input_ in self:
            if input_.name == name:
                return True
        return False

    def __len__(self) -> int:
        return len(self.internal__)

    def __iter__(self) -> 'Iterator[PoseShapeInterpolatorInput]':
        return iter(self.internal__)

    def __getitem__(self, key: str|int|slice) -> 'PoseShapeInterpolatorInput|list[PoseShapeInterpolatorInput]':
        return self.internal__[key]

    @property
    def active(self) -> 'PoseShapeInterpolatorInput|None':
        index = self.active_index
        inputs = self.internal__
        if index < len(inputs):
            return inputs[index]

    active_index: IntProperty(
        name="Input",
        description="Interpolated input source",
        min=0,
        default=0,
        options=set()
        )# type: ignore

    internal__: CollectionProperty(
        type=PoseShapeInterpolatorInput,
        options={'HIDDEN'}
        )# type: ignore

    def clear(self) -> None:
        path = self.path_from_id()
        psi = self.id_data.path_resolve(path[:path.rfind(".")])
        for pose in psi.poses:
            pose.data._clear()
        self.internal__.clear()

    def find(self, name: str) -> int:
        return next((i for i, x in enumerate(self) if x.name == name), -1)

    def get(self, name: str, fallback: object = None) -> object:
        for input_ in self:
            if input_.name == name:
                return input_
        return fallback

    def keys(self) -> 'Iterator[str]':
        for input_ in self:
            yield input_.name

    def items(self) -> 'Iterator[tuple[str, PoseShapeInterpolatorInput]]':
        for input_ in self:
            yield input_.name, input_

    def new(self, pose_bone: 'PoseBone|None' = None) -> 'PoseShapeInterpolatorInput':
        if pose_bone is not None and not isinstance(pose_bone, PoseBone):
            raise TypeError((f'PoseShapeInterpolatorInputs.new(pose_bone): '
                             f'Expected pose_bone to be None or PoseBone, '
                             f'not {type(pose_bone)}'))
        input_ = self.internal__.add()
        input_._init("" if pose_bone is None else pose_bone)
        path = self.path_from_id()
        psi = self.id_data.path_resolve(path[:path.rfind(".")])
        for pose in psi.poses:
            pose.data._add(input_)
        self.active_index = len(self) - 1
        return input_

    def remove(self, input: 'PoseShapeInterpolatorInput') -> None:
        if not isinstance(input, PoseShapeInterpolatorInput):
            raise TypeError((f'PoseShapeInterpolatorInputs.remove(input): '
                             f'Expected input to be PoseShapeInterpolatorInput, not {type(input)}'))
        index = next((i for i, x in enumerate(self) if x == input), -1)
        if index == -1:
            raise ValueError((f'PoseShapeInterpolatorInputs.remove(input): '
                              f'{input} is not a member of this collection'))
        path = self.path_from_id()
        psi = self.id_data.path_resolve(path[:path.rfind(".")])
        for pose in psi.poses:
            pose.data._remove(input)
        self.internal__.remove(index)
        self.active_index = min(self.active_index, len(self) -1)


class PoseShapeInterpolatorInputPose(PropertyGroup):

    def _init(self, input_: 'PoseShapeInterpolatorInput') -> None:
        self._input_handle_set(input_.handle)
        self._update(input_)

    def _input_handle_get(self) -> str:
        return self.get("input_handle", "")

    def _input_handle_set(self, value: str) -> None:
        self["input_handle"] = value

    def _location_get(self) -> 'Vector':
        return self.matrix.to_translation()

    def _location_set(self, value: tuple[float, float, float]) -> None:
        self.matrix = Matrix.LocRotScale(
            value,
            self._rotation_quaternion_get(),
            self._scale_get()
        )

    def _rotation_axis_angle_get(self) -> 'Vector':
        axis, angle = self._rotation_quaternion_get().to_axis_angle()
        return Vector((angle, axis[0], axis[1], axis[2]))

    def _rotation_axis_angle_set(self, value: tuple[float, float, float, float]) -> None:
        self.matrix = Matrix.LocRotScale(
            self._location_get(),
            Quaternion((value[1], value[2], value[3]), value[0]),
            self._scale_get()
        )

    def _rotation_euler_get(self) -> 'Euler':
        return self.matrix.to_euler()

    def _rotation_euler_set(self, value: tuple[float, float, float]) -> None:
        self.matrix = Matrix.LocRotScale(
            self._location_get(),
            Euler(value).to_quaternion(),
            self._scale_get()
        )

    def _rotation_quaternion_get(self) -> 'Quaternion':
        return self.matrix.to_quaternion()

    def _rotation_quaternion_set(self, value: tuple[float, float, float, float]) -> None:
        self.matrix = Matrix.LocRotScale(
            self._location_get(),
            Quaternion(value),
            self._scale_get()
        )

    def _scale_get(self) -> 'Vector':
        return self.matrix.to_scale()

    def _scale_set(self, value: tuple[float, float, float]) -> None:
        self.matrix = Matrix.LocRotScale(
            self._location_get(),
            self._rotation_quaternion_get(),
            value
        )

    def _update(self, input_: 'PoseShapeInterpolatorInput') -> None:
        self.matrix = input_.matrix_resolve()

    input_handle: StringProperty(
        name="Input Handle",
        description="The unique handle of the associated input (read-only)",
        get=_input_handle_get,
        options={'HIDDEN'}
        )# type: ignore

    location: FloatVectorProperty(
        name="Location",
        description="Interpolated pose location",
        get=_location_get,
        set=_location_set,
        subtype='TRANSLATION',
        options=set()
        )# type: ignore

    matrix: FloatVectorProperty(
        name="Matrix",
        description="Pose transform matrix",
        size=(4, 4),
        subtype='MATRIX',
        options=set()
        )# type: ignore

    rotation_axis_angle: FloatVectorProperty(
        name="Rotation",
        description="Interpolated pose rotation as axis angle",
        size=4,
        get=_rotation_axis_angle_get,
        set=_rotation_axis_angle_set,
        subtype='AXISANGLE',
        options=set()
        )# type: ignore

    rotation_euler: FloatVectorProperty(
        name="Rotation",
        description="Interpolated pose rotation in euler angles",
        get=_rotation_euler_get,
        set=_rotation_euler_set,
        subtype='EULER',
        options=set()
        )# type: ignore

    rotation_quaternion: FloatVectorProperty(
        name="Rotation",
        description="Interplated pose rotation quaternion",
        get=_rotation_quaternion_get,
        set=_rotation_quaternion_set,
        size=4,
        subtype='QUATERNION',
        options=set()
        )# type: ignore

    scale: FloatVectorProperty(
        name="Scale",
        description="Interpolated pose scale",
        get=_scale_get,
        set=_scale_set,
        subtype='XYZ',
        options=set()
        )# type: ignore


class PoseShapeInterpolatorPoseData(PropertyGroup):

    def _add(self, input_: 'PoseShapeInterpolatorInput') -> None:
        self.internal__.add()._init(input_)

    def _clear(self) -> None:
        self.internal__.clear()

    def _remove(self, input_: 'PoseShapeInterpolatorInput') -> None:
        data = self.internal__
        handle = input_.handle
        for i, x in enumerate(data):
            if x.input_handle == handle:
                data.remove(i)
                return

    internal__: CollectionProperty(
        type=PoseShapeInterpolatorInputPose,
        options={'HIDDEN'}
        )# type: ignore

    def get(self, input: 'PoseShapeInterpolatorInput') -> 'PoseShapeInterpolatorInputPose|None':
        if not isinstance(input, PoseShapeInterpolatorInput):
            raise TypeError((f'PoseShapeInterpolatorPoseData.get(input): '
                             f'Expected input to be PoseShapeInterpolatorInput, '
                             f'not {type(input)}'))
        handle = input.handle
        for item in self.internal__:
            if item._input_handle_get() == handle:
                return item


class PoseShapeInterpolatorPose(InterpolationSettings):

    def _init(self, name: str) -> None:
        self["name"] = name
        self._init_interpolation_settings()
        data = self.data
        path = self.path_from_id()
        psi = self.id_data.path_resolve(path[:path.rfind(".poses")])
        for input_ in psi.inputs:
            data._add(input_)

    def _is_valid_get(self) -> bool:
        return self.resolve() is not None

    def _name_get(self) -> str:
        return self.get("name", "")

    def _name_set(self, value: str) -> None:
        kb = self.resolve()
        if kb is None:
            self["name"] = value
        else:
            kb.name = value
            self["name"] = kb.name

    def _name_search(self, context: 'Context', edit_text: str) -> 'tuple[str, ...]':
        key = self.id_data
        used = set()
        for psi in key.pose_shape_interpolators:
            for pose in psi.poses:
                if pose != self:
                    used.add(pose.name)
        ad = key.animation_data
        if ad is not None:
            for fc in ad.drivers:
                dp: str = fc.data_path
                if dp.startswith('key_blocks["') and dp.endswith('.value'):
                    used.add(dp[12:-6])
        return tuple(k for k in key.key_blocks.keys() if k not in used)

    data: PointerProperty(
        name="Data",
        description="Pose input data",
        type=PoseShapeInterpolatorPoseData,
        options=set()
        )# type: ignore

    is_valid: BoolProperty(
        name="Valid",
        description="True if a shape key exists for this pose",
        get=_is_valid_get,
        options=set()
        )# type: ignore

    name: StringProperty(
        name="Name",
        description="Unique pose name (matches the shape key name)",
        get=_name_get,
        set=_name_set,
        search=_name_search,
        options=set()
        )# type: ignore

    range_max: FloatProperty(
        name="Max",
        description="The output value when the bone's pose exactly matches this pose",
        default=1.0,
        precision=3,
        options=set(),
        )# type: ignore

    range_min: FloatProperty(
        name="Min",
        description="The output value when the bone's pose is outside of this pose's radius",
        default=0.0,
        precision=3,
        options=set(),
        )# type: ignore

    use_clamp: BoolProperty(
        name="Clamp",
        description="Restrict the output value to the output range",
        default=True,
        options=set(),
        )# type: ignore

    use_interpolation: BoolProperty(
        name="Override",
        description="Override the default interpolation (set on the interpolator)",
        default=False,
        options=set()
        )# type: ignore

    def resolve(self) -> 'ShapeKey|None':
        return self.id_data.key_blocks.get(self.name)


class PoseShapeInterpolatorPoses(PropertyGroup):

    def _root_resolve(self) -> 'PoseShapeInterpolator':
        path: str = self.path_from_id()
        return self.id_data.path_resolve(path[:path.rfind(".")])

    def __contains__(self, name: str) -> bool:
        return name in self.internal__

    def __len__(self) -> int:
        return len(self.internal__)

    def __iter__(self) -> 'Iterator[PoseShapeInterpolatorPose]':
        return iter(self.internal__)

    def __getitem__(self, key: str|int|slice) -> 'PoseShapeInterpolatorPose|list[PoseShapeInterpolatorPose]':
        return self.internal__[key]

    @property
    def active(self) -> 'PoseShapeInterpolatorPose|None':
        index = self.active_index
        poses = self.internal__
        if index < len(poses):
            return poses[index]

    active_index: IntProperty(
        name="Pose",
        description="Interpolated pose",
        min=0,
        default=0,
        options=set()
        )# type: ignore

    internal__: CollectionProperty(
        type=PoseShapeInterpolatorPose,
        options={'HIDDEN'}
        )# type: ignore

    def clear(self) -> None:
        self.internal__.clear()

    def find(self, name: str) -> int:
        return self.internal__.find(name)

    def get(self, name: str, fallback: object = None) -> object:
        return self.internal__.get(name, fallback)

    def keys(self) -> 'Iterator[str]':
        return self.internal__.keys()

    def items(self) -> 'Iterator[tuple[str, PoseShapeInterpolatorPose]]':
        return self.internal__.items()

    def new(self, name: str = "") -> 'PoseShapeInterpolatorPose':
        if not isinstance(name, str):
            raise TypeError((f'PoseShapeInterpolatorPoses.new(name): '
                             f'Expected name to be str, not {type(name)}'))
        psi = self._root_resolve()
        if psi.is_bound:
            raise RuntimeError((f'PoseShapeInterpolatorPoses.new(name): '
                                f'Cannot add new poses to bound interpolator'))
        pose = self.internal__.add()
        pose._init(name)
        self.active_index = len(self) - 1
        return pose

    def remove(self, pose: 'PoseShapeInterpolatorPose') -> None:
        if not isinstance(pose, PoseShapeInterpolatorPose):
            raise TypeError((f'PoseShapeInterpolatorPoses.remove(pose): '
                             f'Expected pose to be PoseShapeInterpolatorPose, not {type(pose)}'))
        index = next((i for i, x in enumerate(self) if x == pose), -1)
        if index == -1:
            raise ValueError((f'PoseShapeInterpolatorPoses.remove(pose): '
                              f'{pose} is not a member of this collection'))
        self.internal__.remove(index)
        self.active_index = min(self.active_index, len(self)-1)


class PoseShapeInterpolator(InterpolationSettings):

    def _handle_get(self) -> str:
        handle = self.get("handle", "")
        if not handle:
            handle = str(uuid4())
            self["handle"] = handle
        return handle

    def _is_bound(self) -> bool:
        return self.get("is_bound", False)

    handle: StringProperty(
        name="Handle",
        description="Unique pose shape interpolator identifier (read-only)",
        get=_handle_get,
        options={'HIDDEN'}
        )# type: ignore

    inputs: PointerProperty(
        name="Inputs",
        description="Pose shape interpolator inputs",
        type=PoseShapeInterpolatorInputs,
        options=set()
        )# type: ignore

    is_bound: BoolProperty(
        name="Bound",
        description="True if the pose shape interpolator has active drivers",
        get=_is_bound,
        options=set()
        )# type: ignore

    poses: PointerProperty(
        name="Poses",
        description="Interpolated poses",
        type=PoseShapeInterpolatorPoses,
        options=set()
        )# type: ignore

    def bind(self) -> None:
        pass

    def unbind(self) -> None:
        # TODO remove idprops and idprop drivers
        key = self.id_data
        pfx = self.handle
        for k in key.keys():
            if k.startswith(pfx):
                del key[k]
        ad = key.animation_data
        if ad is None:
            return
        fx = ad.drivers
        for pose in self.poses:
            kb = pose.resolve()
            if kb is None:
                continue
            fc = fx.find(f'key_blocks["{kb.name}"].value')
            if fc is not None:
                fx.remove(fc)
        pfx = f'["{pfx}'
        for fc in reversed(tuple(fx)):
            dp = fc.data_path
            if dp.startsith(pfx):
                fx.remove(fc)

    def _curve_node_tree_get(self) -> 'ShaderNodeTree':
        return curve_mapping_tree_get(self)

    def _curve_node_tree_ensure(self) -> 'ShaderNodeTree':
        return curve_mapping_tree_ensure(self)

    def _init(self, name: str) -> None:
        self.name = name
        self._init_interpolation_settings()


class PoseShapeInterpolators(PropertyGroup):

    def __len__(self) -> int:
        return len(self.internal__)

    def __iter__(self) -> 'Iterator[PoseShapeInterpolator]':
        return iter(self.internal__)

    def __getitem__(self, key: str|int|slice) -> 'PoseShapeInterpolator|list[PoseShapeInterpolator]':
        return self.internal__[key]

    @property
    def active(self) -> 'PoseShapeInterpolator|None':
        index = self.active_index
        items = self.internal__
        if index < len(items):
            return items[index]

    active_index: IntProperty(
        name="Pose Shape Interpolator",
        description="",
        min=0,
        default=0,
        options=set()
        )# type: ignore

    internal__: CollectionProperty(
        type=PoseShapeInterpolator,
        options={'HIDDEN'}
        )# type: ignore

    internal__curve_node_tree: PointerProperty(
        type=ShaderNodeTree,
        options={'HIDDEN'}
        )# type: ignore

    def clear(self, unbind: bool = True) -> None:
        if unbind:
            for psi in self:
                psi.unbind()
        self.internal__.clear()
        self.active_index = 0

    def find(self, name: str) -> int:
        return self.internal__.find(name)

    def get(self, name: str, fallback: object = None) -> object:
        return self.internal__.get(name, fallback)

    def keys(self) -> 'Iterator[str]':
        return self.internal__.keys()

    def items(self) -> 'Iterator[tuple[str, PoseShapeInterpolator]]':
        return self.internal__.items()

    def new(self, name: str = "Pose Interpolator") -> 'PoseShapeInterpolator':
        if not isinstance(name, str):
            raise TypeError((f'PoseInterpolators.new(name): '
                             f'Expected name to be str, not {type(name)}'))
        psi = self.internal__.add()
        psi._init(name)
        self.active_index = len(self) - 1
        return psi

    def remove(self, interpolator: 'PoseShapeInterpolator', unbind: bool = True) -> None:
        if not isinstance(interpolator, PoseShapeInterpolator):
            raise TypeError((f'PoseInterpolators.remove(interpolator): '
                             f'Expected interpolator to be PoseInterpolator, '
                             f'not {type(interpolator)}'))
        index = next((i for i, x in enumerate(self) if x == interpolator), -1)
        if index == -1:
            raise ValueError((f'PoseInterpolators.remove(interpolator): '
                              f'{interpolator} is not a member of this collection'))
        if unbind:
            interpolator.unbind()
        self.internal__.remove(index)
        self.active_index = min(self.active_index, len(self) - 1)

    def values(self) -> 'Iterator[PoseShapeInterpolator]':
        return self.internal__.values()
