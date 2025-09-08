
from typing import TYPE_CHECKING
from bpy.types import Panel, UIList
if TYPE_CHECKING:
    from bpy.types import Context, ShaderNodeVectorCurve, UILayout
    from .ipo import InterpolationSettings

__all__ = (
    "PSI_UL_pose_shape_interpolators",
    "PSI_UL_pose_shape_interpolator_inputs",
    "PSI_UL_pose_shape_interpolator_poses",
    "DATA_PT_pose_shape_interpolators",
    "DATA_PT_pose_shape_interpolator_inputs",
    "DATA_PT_pose_shape_interpolator_input_pose_data",
    "DATA_PT_pose_shape_interpolator_poses",
    "VIEW3D_PT_pose_shape_interpolators",
    "VIEW3D_PT_pose_shape_interpolator_inputs",
    "VIEW3D_PT_pose_shape_interpolator_input_pose_data",
    "VIEW3D_PT_pose_shape_interpolator_poses",
)


class PSI_UL_pose_shape_interpolators(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", icon='MOD_ARMATURE', text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MOD_ARMATURE')


class PSI_UL_pose_shape_interpolator_inputs(UIList):

    def draw_item(self, context, layout, data, item, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", icon='BONE_DATA', text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(text="", icon='BONE_DATA')


class PSI_UL_pose_shape_interpolator_poses(UIList):

    def draw_item(self, context, layout, data, item, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            kb = item.resolve()
            row = layout.row()
            row.alert = kb is None
            row.label(text=item.name, icon='SHAPEKEY_DATA')
            if kb is not None:
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.ui_units_x = 6
                sub.prop(kb, "value", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(text="", icon='POSE_HLT')


def split_layout(layout: 'UILayout',
                 align_label: str = 'RIGHT',
                 align_column: bool = True,
                 factor: float = 1/3) -> 'tuple[UILayout, UILayout]':
    split = layout.row().split(factor=factor)
    labels = split.column(align=align_column)
    labels.alignment = align_label
    values = split.column(align=align_column)
    return labels, values


def ipo_curve_mapping_draw(layout: 'UILayout', node: 'ShaderNodeVectorCurve', enabled: bool = False) -> None:
    col = layout.column()
    col.scale_x = 0.01
    col.enabled = enabled
    col.template_curve_mapping(node, "mapping")


def ipo_settings_draw(layout: 'UILayout', settings: 'InterpolationSettings') -> None:
    node = settings._curve_node_get()
    ipo = settings.interpolation
    if ipo in {'LINEAR', 'CUSTOM'}:
        row = layout.row()
        row.ui_units_y = 0.01
        row.prop(settings, "interpolation", text="")
    else:
        row = layout.row()
        row.prop(settings, "interpolation", text="")
        row = layout.row()
        row.ui_units_y = 0.01
        row.prop(settings, "easing", text="")
    if node is not None:
        ipo_curve_mapping_draw(layout, node, ipo=='CUSTOM')


class PoseShapeInterpolatorsPanel:

    bl_label = "Pose Shape Interpolators"

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return ob is not None and ob.type == 'MESH' and ob.data.shape_keys is not None

    def draw(self, context: 'Context') -> None:
        key = context.object.data.shape_keys
        layout = self.layout# type: ignore
        if not key.is_property_set("pose_shape_interpolators"):
            layout.operator("pose_shape_interpolator.add", icon='ADD', text="Add Pose Interpolator")
            return
        ipos = key.pose_shape_interpolators
        row = layout.row()
        col = row.column()
        col.template_list('PSI_UL_pose_shape_interpolators', "", ipos, "internal__", ipos, "active_index")
        ops = row.column(align=True)
        ops.operator('pose_shape_interpolator.add', text="", icon='ADD')
        ops.operator('pose_shape_interpolator.remove', text="", icon='REMOVE')
        ops.separator()
        ops.operator('pose_shape_interpolator.move_up', text="", icon='TRIA_UP')
        ops.operator('pose_shape_interpolator.move_down', text="", icon='TRIA_DOWN')
        psi = ipos.active
        if psi is not None:
            a, b = split_layout(col)
            a.label(text="Interpolation")
            ipo_settings_draw(b, psi)


class PoseShapeInterpolatorInputsPanel:

    bl_label = "Inputs"

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and sk.pose_shape_interpolators.active is not None)

    def draw(self, context: 'Context') -> None:
        layout = self.layout# type: ignore
        psi = context.object.data.shape_keys.pose_shape_interpolators.active
        inputs = psi.inputs
        row = layout.row()
        col = row.column()
        col.template_list('PSI_UL_pose_shape_interpolator_inputs', "",
                          inputs, "internal__",
                          inputs, "active_index")
        ops = row.column(align=True)
        ops.operator('pose_shape_interpolator.input_add', text="", icon='ADD')
        ops.operator('pose_shape_interpolator.input_remove', text="", icon='REMOVE')
        ops.separator()
        ops.operator('pose_shape_interpolator.input_move_up', text="", icon='TRIA_UP')
        ops.operator('pose_shape_interpolator.input_move_down', text="", icon='TRIA_DOWN')
        inp = inputs.active
        if inp is None:
            return
        col.separator()
        a, b = split_layout(col)
        a.label(text="Target")
        b.prop(inp, "object", text="")
        ob = inp.object
        if ob is not None and ob.type == 'ARMATURE':
            tgt = inp.name
            data = ob.data
            row = b.row(align=True)
            row.alert = tgt not in data.bones
            b.prop_search(inp, "name", data, "bones", text="")
        col.separator()
        a, b = split_layout(col)
        a.label(text="Location")
        row = b.row(align=True)
        row.prop(inp, "use_location_x", toggle=True)
        row.prop(inp, "use_location_y", toggle=True)
        row.prop(inp, "use_location_z", toggle=True)
        a.separator(factor=0.5)
        b.separator(factor=0.5)
        a.label(text="Rotation")
        row = b.row(align=True)
        row.prop(inp, "use_rotation", text="")
        sub = row.row(align=True)
        sub.enabled = inp.use_rotation
        sub.prop(inp, "rotation_mode", text="")
        sub = sub.row(align=True)
        sub.ui_units_x = 3
        sub.prop(inp, "rotation_axis", text="")
        a.separator(factor=0.5)
        b.separator(factor=0.5)
        a.label(text="Scale")
        row = b.row(align=True)
        row.prop(inp, "use_scale_x", toggle=True)
        row.prop(inp, "use_scale_y", toggle=True)
        row.prop(inp, "use_scale_z", toggle=True)


class PoseShapeInterpolatorInputPoseDataPanel:

    bl_label = " "

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and (psi := sk.pose_shape_interpolators.active) is not None
                and (inp := psi.inputs.active) is not None
                and (pose := psi.poses.active) is not None
                and pose.data.get(inp) is not None)

    def draw_header(self, context: 'Context') -> None:
        layout = self.layout# type: ignore
        pose = context.object.data.shape_keys.pose_shape_interpolators.active.poses.active
        layout.label(text=f'Pose ({pose.name})')

    def draw(self, context: 'Context') -> None:
        layout = self.layout# type: ignore
        row = layout.row()
        col = row.column()
        row.label(icon='BLANK1')
        psi = context.object.data.shape_keys.pose_shape_interpolators.active
        inp = psi.inputs.active
        pd = psi.poses.active.data.get(inp)
        pb = inp.resolve()
        a, b = split_layout(col)
        a.label(text="Location")
        b.prop(pd, "location", text="")
        a, b = split_layout(col)
        a.label(text="Rotation")
        if pb is None:
            k = "rotation_quaternion"
        else:
            m = pb.rotation_mode
            k = f"rotation_{'euler' if len(m) < 5 else m.lower()}"
        b.prop(pd, k, text="")
        a, b = split_layout(col)
        a.label(text="Scale")
        b.prop(pd, "scale", text="")


class PoseShapeInterpolatorPosesPanel:

    bl_label = "Poses"

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        ob = context.object
        return (ob is not None
                and ob.type == 'MESH'
                and (sk := ob.data.shape_keys) is not None
                and sk.is_property_set("pose_shape_interpolators")
                and sk.pose_shape_interpolators.active is not None)

    def draw(self, context: 'Context') -> None:
        layout = self.layout# type: ignore
        psi = context.object.data.shape_keys.pose_shape_interpolators.active
        poses = psi.poses
        row = layout.row()
        col = row.column()
        col.template_list('PSI_UL_pose_shape_interpolator_poses', "",
                          poses, "internal__",
                          poses, "active_index")
        ops = row.column(align=True)
        ops.operator('pose_shape_interpolator.pose_add', text="", icon='ADD')
        ops.operator('pose_shape_interpolator.pose_remove', text="", icon='REMOVE')
        ops.separator()
        ops.operator('pose_shape_interpolator.pose_move_up', text="", icon='TRIA_UP')
        ops.operator('pose_shape_interpolator.pose_move_down', text="", icon='TRIA_DOWN')
        pose = poses.active
        if pose is not None:
            a, b = split_layout(col)
            a.separator()
            b.separator()
            a.label(text="Shape Key")
            b.prop(pose, "name", text="", icon='SHAPEKEY_DATA')
            a.separator()
            b.separator()
            a.label(text="Range")
            sub = b.row(align=True)
            sub.prop(pose, "range_min")
            sub.prop(pose, "range_max")
            b.prop(pose, "use_clamp", text="Clamp")
            col.separator()
            a, b = split_layout(col)
            a.label(text="Interpolation")
            b.prop(pose, "use_interpolation", text="Override")
            if pose.use_interpolation:
                ipo_settings_draw(b, pose)
            else:
                sub = b.column()
                sub.enabled = False
                ipo_settings_draw(sub, psi)


class DATA_PT_pose_shape_interpolators(PoseShapeInterpolatorsPanel, Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"


class DATA_PT_pose_shape_interpolator_inputs(PoseShapeInterpolatorInputsPanel, Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = 'DATA_PT_pose_shape_interpolators'


class DATA_PT_pose_shape_interpolator_input_pose_data(PoseShapeInterpolatorInputPoseDataPanel, Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = 'DATA_PT_pose_shape_interpolator_inputs'


class DATA_PT_pose_shape_interpolator_poses(PoseShapeInterpolatorPosesPanel, Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = 'DATA_PT_pose_shape_interpolators'


class VIEW3D_PT_pose_shape_interpolators(PoseShapeInterpolatorsPanel, Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_context = "objectmode"


class VIEW3D_PT_pose_shape_interpolator_inputs(PoseShapeInterpolatorInputsPanel, Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_context = "objectmode"
    bl_parent_id = 'VIEW3D_PT_pose_shape_interpolators'


class VIEW3D_PT_pose_shape_interpolator_input_pose_data(PoseShapeInterpolatorInputPoseDataPanel, Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_context = "objectmode"
    bl_parent_id = 'VIEW3D_PT_pose_shape_interpolator_inputs'


class VIEW3D_PT_pose_shape_interpolator_poses(PoseShapeInterpolatorPosesPanel, Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_context = "objectmode"
    bl_parent_id = 'VIEW3D_PT_pose_shape_interpolators'
