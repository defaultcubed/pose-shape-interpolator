
import bpy
from ..rna_utils import ctx_psi_active
from ..gui_utils import split_layout


class PSI_UL_inputs(bpy.types.UIList):

    def draw_item(self, ctx, layout, data, item, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, 'name', icon='BONE_DATA', text="", emboss=False)
        elif layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(text="", icon='BONE_DATA')


class DATA_PT_psi_inputs(bpy.types.Panel):

    bl_label = "Inputs"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = 'DATA_PT_psi_settings'

    @classmethod
    def poll(cls, ctx):
        return ctx_psi_active(ctx) is not None

    def draw(self, ctx):
        psi = ctx_psi_active(ctx)
        inputs = psi.inputs
        layout = self.layout

        row = layout.row()
        
        col = row.column()
        col.template_list('PSI_UL_inputs', "", psi, "inputs", psi, "active_input_index")
        
        ops = row.column(align=True)
        ops.operator('pose_shape_interpolator.input_add', text="", icon='ADD')
        ops.operator('pose_shape_interpolator.input_remove', text="", icon='REMPVE')
        ops.separator()
        ops.operator('pose_shape_interpolator.input_moveup', text="", icon'TRIA_UP')
        ops.operator('pose_shape_interpolator.input_movedown', text="", icon='TRIA_DOWN')
        
        inp = psi.active_input
        if inp is None:
            return
        
        enabled = psi.enabled
        col.separator()
        lbl, val = split_layout(col)
        val.enabled = enabled
        
        lbl.label(text="Location")
        row = val.row(align=True)
        row.prop(inp, "use_location_x", toggle=True)
        row.prop(inp, "use_location_y", toggle=True)
        row.prop(inp, "use_location_z", toggle=True)
        
        lbl.separator(factor=0.5)
        val.separator(factor=0.5)

        lbl.label(text="Rotation")
        row = val.row(align=True)
        row.prop(inp, "use_rotation", text="")
        sub = row.row(align=True)
        sub.enabled = enabled and inp.use_rotation
        sub.prop(inp, "rotation_mode", text="")
        sub = sub.row(align=True)
        sub.ui_units_x = 3
        sub.prop(inp, "rotation_axis", text="")

        lbl.separator(factor=0.5)
        val.separator(factor=0.5)

        lbl.label(text="Scale")
        row = val.row(align=True)
        row.prop(inp, "use_scale_x", toggle=True)
        row.prop(inp, "use_scale_y", toggle=True)
        row.prop(inp, "use_scale_z", toggle=True)
        
