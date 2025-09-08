
import bpy
from ..rna_utils import ctx_psi_active, input_add, input_remove
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from ..rna.settings import PSI_Settings


class PSI_InputAdd(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = 'pose_shape_interpolator.input_add'
    bl_description = "Add input"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return psi is not None and not psi.enabled

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        ips = psi.inputs
        pbs = ctx.selected_pose_bones
        if pbs:
            for pb in pbs:
                input_add(ips, pb)
        else:
            input_add(ips)
        return {'FINISHED'}


class PSI_InputRemove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = 'pose_shape_interpolator.input_remove'
    bl_description = "Remove the active input"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return (psi is not None
                and not psi.enabled
                and psi.active_input is not None)

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        input_remove(psi.inputs, psi.active_input_index)
        return {'FINISHED'}


class PSI_InputMoveUp(bpy.types.Operator):

    bl_label = "Up"
    bl_idname = 'pose_shape_interpolator.input_move_up'
    bl_description = "Move the input up within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return (psi is not None
                and psi.enabled
                and psi.active_input is not None
                and psi.active_input_index > 0)

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        ips = psi.inputs
        idx = psi.active_input_index
        ips.move(idx, idx-1)
        psi.active_input_index -= 1
        return {'FINISHED'}


class PSI_InputMoveDown(bpy.types.Operator):

    bl_label = "Down"
    bl_idname = 'pose_shape_interpolator.input_move_down'
    bl_description = "move input down within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return (psi is not None
                and psi.enabled
                and psi.active_input is not None
                and psi.active_input_index < len(psi.inputs)-1)

    def execute(self, ctx):
        psi = cast(PSI_Settings, ctx_psi_active(ctx))
        ips = psi.inputs
        idx = psi.active_input_index
        ips.move(idx, idx+1)
        psi.active_input_index += 1
        return {'FINISHED'}
