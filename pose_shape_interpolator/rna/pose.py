
import bpy
from .interpolable import Interpolable
from .input_pose import PSI_InputPose


def _name_get(p):
    return p.get("name", "")


def _name_set(pose, v):
    kb = pose.shape_key_resolve()
    if kb is None:
        pose["name"] = v
    else:
        kb.name = v
        pose["name"] = kb.name


def _name_search(pose, ctx, txt):
    key = pose.id_data
    used = set()
    for psi in key.pose_shape_interpolators:
        for p_ in psi.poses:
            if p_ != pose:
                used.add(p_.name)
    ad = key.animation_data
    if ad is not None:
        for fc in ad.drivers:
            dp = fc.data_path
            if dp.startswith('key_blocks["') and dp.endswith('.value'):
                used.add(dp[12:-6])
    return tuple(k for k in key.key_blocks.keys() if k not in used)


class PSI_Pose(Interpolable, bpy.types.PropertyGroup):

    data: bpy.props.CollectionProperty(
        name="Data",
        description="Pose input data",
        type=PSI_InputPose,
        options=set()
        )# type: ignore

    name: bpy.props.StringProperty(
        name="Name",
        description="Unique pose name (matches the shape key name)",
        get=_name_get,
        set=_name_set,
        search=_name_search,
        options=set()
        )# type: ignore

    range_max: bpy.props.FloatProperty(
        name="Max",
        description="The output value when the bone's pose exactly matches this pose",
        default=1.0,
        precision=3,
        options=set(),
        )# type: ignore

    range_min: bpy.props.FloatProperty(
        name="Min",
        description="The output value when the bone's pose is outside of this pose's radius",
        default=0.0,
        precision=3,
        options=set(),
        )# type: ignore

    use_clamp: bpy.props.BoolProperty(
        name="Clamp",
        description="Restrict the output value to the output range",
        default=True,
        options=set(),
        )# type: ignore

    use_interpolation: bpy.props.BoolProperty(
        name="Override",
        description="Override the default interpolation",
        default=False,
        options=set()
        )# type: ignore

    def shape_key_resolve(self):
        return self.id_data.key_blocks.get(self.name)
