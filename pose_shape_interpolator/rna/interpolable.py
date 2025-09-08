
import bpy
from ..rna_utils import handle_ensure, CMAP_PRESETS, cmapnode_get, cmapnode_apply


def _update(obj):
    k = obj.interpolation
    if k == 'CUSTOM':
        return
    node = cmapnode_get(obj)
    if node is not None:
        if k != 'LINEAR':
            k = f'{k}_{obj.easing}'
        cmapnode_apply(node, CMAP_PRESETS[k])


class Interpolable:

    easing: bpy.props.EnumProperty(
        name="Easing",
        description="Type of easing (in/out) to apply to the interpolation curve",
        items=[
            ('EASE_IN'    , "Ease In"      , "", 'IPO_EASE_IN'    , 0),
            ('EASE_OUT'   , "Ease Out"     , "", 'IPO_EASE_OUT'   , 1),
            ('EASE_IN_OUT', "Ease In & Out", "", 'IPO_EASE_IN_OUT', 2),
        ],
        default='EASE_IN_OUT',
        options=set(),
        update=_update
        )# type: ignore

    handle: bpy.props.StringProperty(
        name="Handle",
        description="Unique struct handle (read-only)",
        get=lambda self: handle_ensure(self),
        options={'HIDDEN'}
        )# type: ignore

    interpolation: bpy.props.EnumProperty(
        name="Interpolation",
        description="Type of interpolation to use between poses",
        items=[
            ('LINEAR', "Linear"     , "", 'IPO_LINEAR', 0),
            ('SINE'  , "Sinusoidal" , "", 'IPO_SINE'  , 1),
            ('QUAD'  , "Quadratic"  , "", 'IPO_QUAD'  , 2),
            ('CUBIC' , "Cubic"      , "", 'IPO_CUBIC' , 3),
            ('QUART' , "Quartic"    , "", 'IPO_QUART' , 4),
            ('QUINT' , "Quintic"    , "", 'IPO_QUINT' , 5),
            ('EXPO'  , "Exponential", "", 'IPO_EXPO'  , 6),
            None,
            ('CUSTOM', "Custom"     , "", 'FCURVE'    , 7),
        ],
        default='LINEAR',
        options=set(),
        update=_update
        )# type: ignore
