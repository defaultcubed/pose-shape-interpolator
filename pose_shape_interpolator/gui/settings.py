
import bpy
from ..rna_utils import ctx_key
from ..gui_utils import split_layout, ipo_settings_draw


class PSI_UL_settings(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", icon='MOD_ARMATURE', text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MOD_ARMATURE')


class DATA_PT_psi_settings(bpy.types.Panel):

    bl_label = "Pose Interpolators"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, ctx):
        return ctx_key(ctx) is not None

    def draw(self, ctx):
        key = ctx.object.data.shape_keys
        layout = self.layout
        interpolators = key.pose_shape_interpolators
        row = layout.row()
        col = row.column()
        col.template_list('PSI_UL_settings', "",
                          key, "pose_shape_interpolators",
                          key, "active_pose_shape_interpolator_index")
        ops = row.column(align=True)
        ops.operator('pose_shape_interpolator.add', text="", icon='ADD')
        ops.operator('pose_shape_interpolator.remove', text="", icon='REMOVE')
        ops.separator()
        ops.operator('pose_shape_interpolator.moveup', text="", icon='TRIA_UP')
        ops.operator('pose_shape_interpolator.movedown', text="", icon='TRIA_DOWN')
        psi = interpolators.active
        if psi is not None:
            lbl, val = split_layout(col)
            lbl.label(text="Interpolation")
            ipo_settings_draw(val, psi)
