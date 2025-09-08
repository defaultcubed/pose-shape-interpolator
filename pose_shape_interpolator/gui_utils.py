
from .rna_utils import cmapnode_get


def split_layout(layout, label_alignment='RIGHT', align=True, factor=1/3):
    split = layout.row().split(factor=factor)
    label = split.column(align=align)
    value = split.column(align=align)
    label.alignment = label_alignment
    return label, value


def ipo_cmapnode_draw(layout, node, enabled=False):
    col = layout.column()
    col.scale_x = 0.01
    col.enabled = enabled
    col.template_curve_mapping(node, "mapping")


def ipo_settings_draw(layout, obj):
    node = cmapnode_get(obj)
    ipo = obj.interpolation
    row = layout.row()
    if ipo in {'LINEAR', 'CUSTOM'}:
        row.ui_units_y = 0.01
        row.prop(obj, "interpolation", text="")
    else:
        row.prop(obj, "interpolation", text="")
        row = layout.row()
        row.ui_units_y = 0.01
        row.prop(obj, "easing", text="")
    if node is not None:
        ipo_cmapnode_draw(layout, node, ipo=='CUSTOM')

