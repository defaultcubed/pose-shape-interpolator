
import bpy
from .interpolable import Interpolable
from .input import PSI_Input
from .pose import PSI_Pose


class PSI_Settings(Interpolable, bpy.types.PropertyGroup):

    active_input_index: bpy.props.IntProperty(
        name="Input",
        min=0,
        default=0,
        options=set()
        )# type: ignore

    @property
    def active_input(self):
        i = self.active_input_index
        inputs = self.inputs
        if i < len(inputs):
            return inputs[i]

    active_pose_index: bpy.props.IntProperty(
        name="Pose",
        min=0,
        default=0,
        options=set()
        )# type: ignore

    @property
    def active_pose(self):
        i = self.active_pose_index
        poses = self.poses
        if i < len(poses):
            return poses[i]

    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=False,
        options=set()
        )# type: ignore

    inputs: bpy.props.CollectionProperty(
        name="Inputs",
        description="Pose shape interpolator inputs",
        type=PSI_Input,
        options=set()
        )# type: ignore

    poses: bpy.props.CollectionProperty(
        name="Poses",
        description="Interpolated poses",
        type=PSI_Pose,
        options=set()
        )# type: ignore
