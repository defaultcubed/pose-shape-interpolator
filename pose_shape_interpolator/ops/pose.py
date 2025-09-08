
import bpy
from ..rna_utils import ctx_psi_active, pose_add, pose_remove, posedata_update
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from ..rna.settings import PSI_Settings


class PSI_PoseAdd(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = 'pose_shape_interpolator.pose_add'
    bl_description = "Add a pose to the shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the pose",
        default="Pose",
        options={'SKIP_SAVE'}
        )# type: ignore

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return psi is not None and not psi.enabled

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        pose_add(psi, self.name)
        psi.active_pose_index = len(psi.poses) - 1
        return {'FINISHED'}


class PSI_PoseRemove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "pose_shape_interpolator.pose_remove"
    bl_description = "Remove the active pose from the shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return psi is not None and not psi.enabled and psi.active_pose is not None

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        i = psi.active_pose_index
        pose_remove(psi, i)
        psi.active_pose_index = min(i, len(psi.poses)-1)
        return {'FINISHED'}


class PSI_PoseUpdate(bpy.types.Operator):

    bl_label = "Update"
    bl_idname = "pose_shape_interpolator.pose_update"
    bl_description = "Update the active pose from the current input state"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return psi is not None and not psi.enabled and psi.active_pose is not None

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        posedata_update(psi.active_pose, psi)
        return {'FINISHED'}


class PSI_PoseMoveUp(bpy.types.Operator):

    bl_label = "Up"
    bl_idname = 'pose_shape_interpolator.pose_move_up'
    bl_description = "Move pose up within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return (psi is not None
                and psi.enabled
                and psi.active_pose is not None
                and psi.active_pose_index > 0)

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        poses = psi.poses
        i = psi.active_pose_index
        poses.move(i, i-1)
        psi.active_pose_index -= 1
        return {'FINISHED'}


class PSI_PoseMoveDown(bpy.types.Operator):

    bl_label = "Down"
    bl_idname = 'pose_shape_interpolator.pose_move_down'
    bl_description = "Move pose down within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return (psi is not None
                and psi.enabled
                and psi.active_pose is not None
                and psi.active_pose_index < len(psi.poses)-1)

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        poses = psi.poses
        i = psi.active_pose_index
        poses.move(i, i+1)
        psi.active_pose_index += 1
        return {'FINISHED'}
