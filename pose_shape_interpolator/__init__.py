
from .rna import *
from .ops import *
from .gui import *

classes = (
    PoseShapeInterpolatorInput,
    PoseShapeInterpolatorInputs,
    PoseShapeInterpolatorInputPose,
    PoseShapeInterpolatorPoseData,
    PoseShapeInterpolatorPose,
    PoseShapeInterpolatorPoses,
    PoseShapeInterpolator,
    PoseShapeInterpolators,
    PoseShapeInterpolatorAdd,
    PoseShapeInterpolatorRemove,
    PoseShapeInterpolatorMoveUp,
    PoseShapeInterpolatorMoveDown,
    PoseShapeInterpolatorInputAdd,
    PoseShapeInterpolatorInputRemove,
    PoseShapeInterpolatorInputMoveUp,
    PoseShapeInterpolatorInputMoveDown,
    PoseShapeInterpolatorPoseAdd,
    PoseShapeInterpolatorPoseRemove,
    PoseShapeInterpolatorPoseMoveUp,
    PoseShapeInterpolatorPoseMoveDown,
    PSI_UL_pose_shape_interpolators,
    PSI_UL_pose_shape_interpolator_inputs,
    PSI_UL_pose_shape_interpolator_poses,
    DATA_PT_pose_shape_interpolators,
    DATA_PT_pose_shape_interpolator_inputs,
    DATA_PT_pose_shape_interpolator_input_pose_data,
    DATA_PT_pose_shape_interpolator_poses,
    VIEW3D_PT_pose_shape_interpolators,
    VIEW3D_PT_pose_shape_interpolator_inputs,
    VIEW3D_PT_pose_shape_interpolator_input_pose_data,
    VIEW3D_PT_pose_shape_interpolator_poses,
)


def register():
    from bpy.utils import register_class
    from bpy.types import Key
    from bpy.props import PointerProperty

    for cls in classes:
        register_class(cls)

    Key.pose_shape_interpolators = PointerProperty(
        name="Pose Shape Interpolators",
        type=PoseShapeInterpolators,
        options=set()
        )


def unregister():
    from bpy.types import Key
    from bpy.utils import unregister_class

    del Key.pose_shape_interpolators

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()






























def sum_of_squares(values: 'typing.Iterable[float]') -> float:
    return sum(value**2 for value in values)


def normalize(values: list[float]) -> float:
    norm = sum_of_squares(values)
    if math.isclose(norm, 0.0, abs_tol=1e-5):
        return 1.0
    for index in range(len(values)):
        values[index] /= norm
    return norm


class PoseShapeInterpolatorBind(bpy.types.Operator):

    bl_label = "Bind"
    bl_idname = 'pose_shape_interpolator.bind'
    bl_description = "Build and activate drivers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: 'bpy.types.Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and sk.pose_shape_interpolators.active is not None)

    def execute(self, context: 'bpy.types.Context') -> set[str]:

        psi = context.object.data.shape_keys.pose_shape_interpolators.active

        # collect/validate inputs
        inputs = []
        for inp in psi.inputs:
            if not inp.is_valid:
                self.report({'ERROR'}, f'Input "{inp.name}" is not valid')
                return {'CANCELLED'}
            inputs.append(inp)

        if not inputs:
            self.report({'ERROR'}, f'Pose shape interpolator has no inputs')
            return {'CANCELLED'}

        # collect/validate poses
        poses = []
        for pose in psi.poses:
            if not pose.is_valid:
                self.report({'ERROR'}, f'Pose "{pose.name}" is not valid')
                return {'CANCELLED'}
            poses.append(pose)

        if len(poses) < 2:
            self.report({'ERROR'}, f'Pose shape interpolator has no poses')
            return {'CANCELLED'}

        # build the pose & input data matrices
        pdmat = []
        for pose in poses:
            pdmat.append([pd.matrix for pd in pose.data])
        idmat = list(map(list, zip(*pdmat)))

        channels = []
        for inp, data in zip(inputs, idmat):
            flags = (inp.use_location_x, inp.use_location_y, inp.use_location_z)
            if any(flags):
                for use, axis, vec in zip(flags, 'XYZ', zip(*[x.location for x in data])):
                    if not use:
                        continue
                    vec = list(vec)
                    channels.append((inp, f'LOC_{axis}', vec, normalize(vec)))

            if inp.use_rotation:
                axis = inp.rotation_axis
                mode = inp.rotation_mode
                if mode == 'ANGLE':
                    i = 'XYZ'.index(axis)
                    v = [x.rotation_euler[i] for x in data]
                    channels.append((inp, f'ROT_{axis}', v, normalize(v)))
                else:
                    qts = [x.rotation_quaternion for x in data]
                    if mode == 'SINWG_TWIST':


            flags = (inp.use_scale_x, inp.use_scale_y, inp.use_scale_z)
            if any(flags):
                for use, axis, vec in zip(flags, 'XYZ', zip(*[x.scale for x in data])):
                    if not use:
                        continue
                    vec = list(vec)
                    channels.append((inp, f'SCALE_{axis}', vec, normalize(vec)))

        return {'FINISHED'}
