
import bpy
from ..rna_utils import ctx_key, ctx_psi_active, psi_add, psi_remove
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from ..rna.settings import PSI_Settings


class PSI_Add(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = "pose_shape_interpolator.add"
    bl_description = "Add a pose shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    name: bpy.props.StringProperty(
        name="Name",
        description="Name of pose interpolator",
        default="PoseInterpolator",
        options={'SKIP_SAVE'}
        )# type: ignore

    @classmethod
    def poll(cls, ctx):
        return ctx_key(ctx) is not None

    def execute(self, ctx):
        key = cast(bpy.types.Key, ctx_key(ctx))
        psi_add(key, self.name)
        key.active_pose_shape_interpolator_index = len(key.pose_shape_interpolators)-1
        return {'FINISHED'}


class PSI_Remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "pose_shape_interpolator.remove"
    bl_description = "Remove the active pose shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, ctx):
        return ctx_psi_active(ctx) is not None

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        key = psi.id_data
        psi_remove(psi)
        key.active_pose_shape_interpolator_index = min(
            key.active_pose_shape_interpolator_index,
            len(key.pose_shape_interpolators)-1)
        return {'FINISHED'}


class PSI_MoveUp(bpy.types.Operator):

    bl_label = "Up"
    bl_idname = "pose_shape_interpolator.moveup"
    bl_description = "Move up within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        if psi is None:
            return False
        return psi.id_data.active_pose_shape_interpolator_index > 0

    def execute(self, ctx):
        key = cast(bpy.types.Key, ctx_key(ctx))
        i = key.active_pose_shape_interpolator_index
        key.pose_shape_interpolators.move(i, i-1)
        key.active_pose_shape_interpolator_index -= 1
        return {'FINISHED'}


class PSI_MoveDown(bpy.types.Operator):

    bl_label = "Down"
    bl_idname = "pose_shape_interpolator.movedown"
    bl_description = "Move down within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        if psi is None:
            return False
        i = psi.id_data.active_pose_shape_interpolator_index
        return i < len(psi.id_data.pose_shape_interpolators)

    def execute(self, ctx):
        key = cast(bpy.types.Key, ctx_key(ctx))
        i = key.active_pose_shape_interpolator_index
        key.pose_shape_interpolators.move(i, i+1)
        key.active_pose_shape_interpolator_index += 1
        return {'FINISHED'}
