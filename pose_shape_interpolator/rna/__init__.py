
import bpy

from .input import PSI_Input
from .input_pose import PSI_InputPose
from .pose import PSI_Pose
from .settings import PSI_Settings


classes = (
    PSI_Input,
    PSI_InputPose,
    PSI_Pose,
    PSI_Settings
)


def rna_register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Key.pose_shape_interpolators = bpy.props.CollectionProperty(
        name="Pose Shape Interpolators",
        type=PSI_Settings,
        options=set()
    )

    bpy.types.Key.active_pose_shape_interpolator_index = bpy.props.IntProperty(
        name="Pose Shape Interpolator",
        min=0,
        default=0,
        options=set()
    )

    bpy.types.Key.pose_shape_interpolator_curves = bpy.props.PointerProperty(
        name="Pose shape interplation curves (internal use)",
        type=bpy.types.ShaderNodeTree,
        options={'HIDDEN'}
    )


def rna_unregister():
    del bpy.types.Key.pose_shape_interpolator_curves
    del bpy.types.Key.pose_shape_interpolators
    del bpy.types.Key.active_pose_shape_interpolator_index

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

