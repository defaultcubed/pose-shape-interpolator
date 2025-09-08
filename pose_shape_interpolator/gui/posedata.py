
import bpy
from ..rna_utils import ctx_psi_active, input_pose_find, input_posebone_get
from ..gui_utils import split_layout


class DATA_PT_psi_posedata(bpy.types.Panel):

    bl_label = "Inputs"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = 'DATA_PT_psi_settings'

    @classmethod
    def poll(cls, ctx):
        psi = ctx_psi_active(ctx)
        return (psi is not None
                and (inp := psi.active_input) is not None
                and (pose := psi.active_pose) is not None
                and input_pose_find(pose, inp) >= 0)

    def draw(self, ctx):
        layout = self.layout
        row = layout.row()
        col = row.column()
        row.label(icon='BLNK1')
        psi = ctx_psi_active(ctx)
        inp = psi.active_input
        i = input_pose_find(pose, inp)
        ip = psi.active_pose.data[i]
        pb = input_posebone_get(inp)

        lbl, val = split_layout(col)
        lbl.label(text="Location")
        val.prop(ip, "location", text="")

        lbl, val = split_layout(col)
        lbl.label(text="Rotation")
        if pb is None:
            propname = "rotation_quaterion"
        else:
            rm = pb.rotation_mode
            propname = f"rotation_{'euler' if len(rm) < 5 else rm.lower()}"
        val.prop(ip, propname, text="")

        lbl, val = split_layout(col)
        lbl.label(text="Scale")
        val.prop(ip, "scale", text="")

