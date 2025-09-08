
from typing import TYPE_CHECKING
from bpy.types import Operator
if TYPE_CHECKING:
    from bpy.types import Context

__all__ = (
    "PoseShapeInterpolatorAdd",
    "PoseShapeInterpolatorRemove",
    "PoseShapeInterpolatorMoveUp",
    "PoseShapeInterpolatorMoveDown",
    "PoseShapeInterpolatorInputAdd",
    "PoseShapeInterpolatorInputRemove",
    "PoseShapeInterpolatorInputMoveUp",
    "PoseShapeInterpolatorInputMoveDown",
    "PoseShapeInterpolatorPoseAdd",
    "PoseShapeInterpolatorPoseRemove",
    "PoseShapeInterpolatorPoseMoveUp",
    "PoseShapeInterpolatorPoseMoveDown",
)


class PoseShapeInterpolatorAdd(Operator):

    bl_label = "Add"
    bl_idname = 'pose_shape_interpolator.add'
    bl_description = "Add a pose shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and ob.data.shape_keys is not None)

    def execute(self, context: 'Context') -> set[str]:
        context.object.data.shape_keys.pose_shape_interpolators.new()
        return {'FINISHED'}


class PoseShapeInterpolatorRemove(Operator):

    bl_label = "Remove"
    bl_idname = 'pose_shape_interpolator.remove'
    bl_description = "Remove the active pose shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and sk.pose_shape_interpolators.active is not None)

    def execute(self, context: 'Context') -> set[str]:
        ipos = context.object.data.shape_keys.pose_shape_interpolators
        ipos.remove(ipos.active)
        return {'FINISHED'}


class PoseShapeInterpolatorMoveUp(Operator):

    bl_label = "Up"
    bl_idname = 'pose_shape_interpolator.move_up'
    bl_description = "Move the shape interpolator up within the list"

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (ipos := sk.pose_shape_interpolators).active is not None
                and ipos.active_index > 0)

    def execute(self, context: 'Context') -> set[str]:
        ipos = context.object.data.shape_keys.pose_shape_interpolators
        ipos.internal__.move(ipos.active_index, ipos.active_index - 1)
        ipos.active_index -= 1
        return {'FINISHED'}


class PoseShapeInterpolatorMoveDown(Operator):

    bl_label = "Down"
    bl_idname = 'pose_shape_interpolator.move_down'
    bl_description = "Move the shape interpolator down within the list"

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (ipos := sk.pose_shape_interpolators).active is not None
                and ipos.active_index < len(ipos) - 1)

    def execute(self, context: 'Context') -> set[str]:
        ipos = context.object.data.shape_keys.pose_shape_interpolators
        ipos.internal__.move(ipos.active_index, ipos.active_index + 1)
        ipos.active_index += 1
        return {'CONTEXT'}


class PoseShapeInterpolatorInputAdd(Operator):

    bl_label = "Add"
    bl_idname = 'pose_shape_interpolator.input_add'
    bl_description = "Add input"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and sk.pose_shape_interpolators.active is not None)

    def execute(self, context: 'Context') -> set[str]:
        pbs = context.selected_pose_bones
        psi = context.object.data.shape_keys.pose_shape_interpolators.active
        if pbs:
            for pb in pbs:
                psi.inputs.new(pb)
        else:
            psi.inputs.new()
        return {'FINISHED'}


class PoseShapeInterpolatorInputRemove(Operator):

    bl_label = "Remove"
    bl_idname = 'pose_shape_interpolator.input_remove'
    bl_description = "Remove the active input"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) is not None
                and psi.inputs.active is not None)

    def execute(self, context: 'Context') -> set[str]:
        ips = context.object.data.shape_keys.pose_shape_interpolators.active.inputs
        ips.remove(ips.active)
        return {'FINISHED'}


class PoseShapeInterpolatorInputMoveUp(Operator):

    bl_label = "Up"
    bl_idname = 'pose_shape_interpolator.input_move_up'
    bl_description = "Move the input up within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators).active is not None
                and (inps := psi.inputs).active is not None
                and inps.active_index > 0)

    def execute(self, context: 'Context') -> set[str]:
        inps = context.object.data.shape_keys.pose_shape_interpolators.active.inputs
        inps.internal__.move(inps.active_index, inps.active_index - 1)
        inps.active_index -= 1
        return {'FINISHED'}


class PoseShapeInterpolatorInputMoveDown(Operator):

    bl_label = "Down"
    bl_idname = 'pose_shape_interpolator.input_move_down'
    bl_description = "move input down within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) is not None
                and (inps := psi.inputs).active is not None
                and inps.active_index < len(inps) - 1)

    def execute(self, context: 'Context') -> set[str]:
        inps = context.object.data.shape_keys.pose_shape_interpolators.active.inputs
        inps.move(inps.active_index, inps.active_index + 1)
        inps.active_index += 1
        return {'FINISHED'}


class PoseShapeInterpolatorPoseAdd(Operator):

    bl_label = "Add"
    bl_idname = 'pose_shape_interpolator.pose_add'
    bl_description = "Add a pose to the shape interpolator"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) is not None)

    def execute(self, context: 'Context') -> set[str]:
        ob = context.object
        kb = ob.shape_key_add(from_mix=False)
        kb.value = 1
        ob.data.shape_keys.pose_shape_interpolators.active.poses.new(kb.name)
        return {'FINISHED'}


class PoseShapeInterpolatorPoseRemove(Operator):

    bl_label = "Remove"
    bl_idname = 'pose_shape_interpolator.pose_remove'
    bl_description = "Remove the active pose"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) is not None
                and psi.poses.active is not None)

    def execute(self, context: 'Context') -> set[str]:
        poses = context.object.data.shape_keys.pose_shape_interpolators.active.poses
        poses.remove(poses.active)
        return {'FINISHED'}


class PoseShapeInterpolatorPoseMoveUp(Operator):

    bl_label = "Up"
    bl_idname = 'pose_shape_interpolator.pose_move_up'
    bl_description = "Move the pose up within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) != None
                and (poses := psi.poses).active is not None
                and poses.active_index > 0)

    def execute(self, context: 'Context') -> set[str]:
        poses = context.object.data.shape_keys.pose_shape_interpolators.active.poses
        poses.internal__.move(poses.active_index, poses.active_index - 1)
        poses.active_index -= 1
        return {'FINISHED'}


class PoseShapeInterpolatorPoseMoveDown(Operator):

    bl_label = "Down"
    bl_idname = 'pose_shape_interpolator.pose_move_down'
    bl_description = "Move the pose down within the list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) != None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) is not None
                and (poses := psi.poses).active is not None
                and poses.active_index < len(poses) - 1)

    def execute(self, context: 'Context') -> set[str]:
        poses = context.object.data.shape_keys.pose_shape_interpolators.active.poses
        poses.internal__.move(poses.active_index, poses.active_index + 1)
        poses.active_index += 1
        return {'FINISHED'}
