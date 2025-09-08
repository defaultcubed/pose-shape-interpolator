
import bpy
from ..rna_utils import ctx_psi_active
from ..gui_utils import split_layout, ipo_settings_draw


class PSI_UL_poses(bpy.types.UIList):

    def draw_item(self, ctx, layout, data, item, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            kb = item.shape_key_resolve()
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


class DATA_PT_psi_poses(bpy.types.Panel):

    bl_label = "Poses"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = 'DATA_PT_psi_poses'

    @classmethod
    def poll(cls, ctx):
        return ctx_psi_active(ctx) is not None

    def draw(self, ctx):
        layout = self.layout
        psi = ctx_psi_active(ctx)
        poses = psi.poses
        row = layout.row()
        col = row.column()
        col.template_list('PSI_UL_poses', "", psi, "poses", psi, "active_pose_index")
        ops = row.column(align=True)
        ops.operator('pose_shape_interpolator.pose_add', text="", icon='ADD')
        ops.operator('pose_shape_interpolator.pose_remove', text="", icon='REMOVE')
        ops.operator('pose_shape_interpolator.pose_update', text="", icon='KEYFRAME_HLT')
        ops.separator()
        ops.operator('pose_shape_interpolator.pose_moveup', text="", icon='TRIA_UP')
        ops.operator('pose_shape_interpolator.pose_movedown', text="", icon='TRIA_DOWN')
        pose = poses.active
        if pose is not None:
            lbl, val = split_layout(col)
            lbl.separator()
            val.separator()
            lbl.label(text="Shape Key")
            val.prop(pose, "name", text="", icon='SHAPEKEY_DATA')
            
            lbl.separator()
            val.separator()
            
            lbl.label(text="Range")
            sub = val.row(align=True)
            sub.prop(pose, "range_min")
            sub.prop(pose, "range_max")
            val.prop(pose, "use_clamp", text="Clamp")
            col.separator()
            
            lbl, val = split_layout(col)
            lbl.label(text="Interpolation")
            val.prop(pose, "use_interpolation", text="Override")
            if pose.use_interpolation:
                ipo_settings_draw(val, pose)
            else:
                sub = val.column()
                sub.enabled = False
                ipo_settings_draw(sub, psi)
