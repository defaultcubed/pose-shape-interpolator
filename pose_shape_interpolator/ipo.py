
from uuid import uuid4
from typing import TYPE_CHECKING
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty
if TYPE_CHECKING:
    from bpy.types import Context, ShaderNodeTree, ShaderNodeVectorCurve


CURVE_MAPPING_PRESETS = {
    'LINEAR': (
        ((0.0, 0.0), 'VECTOR'),
        ((1.0, 1.0), 'VECTOR'),
    ),
    'SINE_EASE_IN': (
        ((0.0, 0.0) , 'AUTO'),
        ((0.1, 0.03), 'AUTO_CLAMPED'),
        ((1.0, 1.0) , 'AUTO'),
    ),
    'SINE_EASE_OUT': (
        ((0.0, 0.0) , 'AUTO'),
        ((0.9, 0.97), 'AUTO_CLAMPED'),
        ((1.0, 1.0) , 'AUTO'),
    ),
    'SINE_EASE_IN_OUT': (
        ((0.0, 0.0) , 'AUTO'),
        ((0.1, 0.03), 'AUTO_CLAMPED'),
        ((0.9, 0.97), 'AUTO_CLAMPED'),
        ((1.0, 1.0) , 'AUTO'),
    ),
    'QUAD_EASE_IN': (
        ((0.0, 0.0)   , 'AUTO'),
        ((0.15, 0.045), 'AUTO_CLAMPED'),
        ((1.0, 1.0)   , 'AUTO'),
    ),
    'QUAD_EASE_OUT': (
        ((0.0, 0.0)   , 'AUTO'),
        ((0.85, 0.955), 'AUTO_CLAMPED'),
        ((1.0, 1.0)   , 'AUTO'),
    ),
    'QUAD_EASE_IN_OUT': (
        ((0.0, 0.0)   , 'AUTO'),
        ((0.15, 0.045), 'AUTO_CLAMPED'),
        ((0.85, 0.955), 'AUTO_CLAMPED'),
        ((1.0, 1.0)   , 'AUTO'),
    ),
    'CUBIC_EASE_IN': (
        ((0.0, 0.0) , 'AUTO'),
        ((0.2, 0.03), 'AUTO_CLAMPED'),
        ((1.0, 1.0) , 'AUTO'),
    ),
    'CUBIC_EASE_OUT': (
        ((0.0, 0.0) , 'AUTO'),
        ((0.8, 0.97), 'AUTO_CLAMPED'),
        ((1.0, 1.0) , 'AUTO'),
    ),
    'CUBIC_EASE_IN_OUT': (
        ((0.0, 0.0) , 'AUTO'),
        ((0.2, 0.03), 'AUTO_CLAMPED'),
        ((0.8, 0.97), 'AUTO_CLAMPED'),
        ((1.0, 1.0) , 'AUTO'),
    ),
    'QUART_EASE_IN': (
        ((0.0, 0.0)  , 'AUTO'),
        ((0.25, 0.03), 'AUTO_CLAMPED'),
        ((1.0, 1.0)  , 'AUTO'),
    ),
    'QUART_EASE_OUT': (
        ((0.0, 0.0)  , 'AUTO'),
        ((0.75, 0.97), 'AUTO_CLAMPED'),
        ((1.0, 1.0)  , 'AUTO'),
    ),
    'QUART_EASE_IN_OUT': (
        ((0.0, 0.0)  , 'AUTO'),
        ((0.25, 0.03), 'AUTO_CLAMPED'),
        ((0.75, 0.97), 'AUTO_CLAMPED'),
        ((1.0, 1.0)  , 'AUTO'),
    ),
    'QUINT_EASE_IN': (
        ((0.0, 0.0)    , 'AUTO'),
        ((0.275, 0.025), 'AUTO_CLAMPED'),
        ((1.0, 1.0)    , 'AUTO'),
    ),
    'QUINT_EASE_IN': (
        ((0.0, 0.0)    , 'AUTO'),
        ((0.725, 0.975), 'AUTO_CLAMPED'),
        ((1.0, 1.0)    , 'AUTO'),
    ),
    'QUINT_EASE_IN_OUT': (
        ((0.0, 0.0)    , 'AUTO'),
        ((0.275, 0.025), 'AUTO_CLAMPED'),
        ((0.725, 0.975), 'AUTO_CLAMPED'),
        ((1.0, 1.0)    , 'AUTO'),
    )
}


def curve_mapping_node_preset_apply(node: 'ShaderNodeVectorCurve', preset: tuple[tuple[tuple[float, float], str], ...]) -> None:
    mapping = node.mapping
    count = len(preset)
    pts = mapping.curves[0].points
    while len(pts) > count:
        pts.remove(pts[-2])
    while len(pts) < count:
        pts.new(0.0, 0.0)
    for pt, (co, ht) in zip(pts, preset):
        pt.handle_type = ht
        pt.location = co
        pt.select = False
    mapping.update()


def curve_mapping_node_clone(node1: 'ShaderNodeVectorCurve', node2: 'ShaderNodeVectorCurve') -> None:
    mapping1 = node1.mapping
    mapping2 = node2.mapping
    points1 = mapping1.curves[0].points
    points2 = mapping2.curves[0].points
    count = len(points1)
    while len(points2) > count:
        points2.remove(points2[-2])
    for index, point1 in enumerate(points1):
        if len(points2) <= index:
            point2 = points2.new(*point1.location)
        else:
            point2 = points2[index]
            point2.location = point1.location
        point2.handle_type = point1.handle_type
        point2.select = False
    mapping2.update()


def curve_mapping_tree_get(settings: 'InterpolationSettings') -> 'ShaderNodeTree|None':
    return settings.id_data.pose_shape_interpolators.internal__curve_node_tree


def curve_mapping_tree_ensure(settings: 'InterpolationSettings') -> 'ShaderNodeTree':
    tree = curve_mapping_tree_get(settings)
    if tree is None:
        import bpy
        tree = bpy.data.node_groups.new('POSE_INTERPOLATION', 'ShaderNodeTree')
        settings.id_data.pose_shape_interpolators.internal__curve_node_tree = tree
    return tree


def curve_mapping_node_get(settings: 'InterpolationSettings', name: str) -> 'ShaderNodeVectorCurve|None':
    tree = curve_mapping_tree_get(settings)
    if tree is not None:
        return tree.nodes.get(name)


def curve_mapping_node_ensure(settings: 'InterpolationSettings', name: str) -> 'ShaderNodeVectorCurve':
    tree = curve_mapping_tree_ensure(settings)
    node = tree.nodes.get(name)
    if node is None:
        node = tree.nodes.new('ShaderNodeVectorCurve')
        node.name = name
        curve_mapping_node_init(node)
    return node


def curve_mapping_node_init(node: 'ShaderNodeVectorCurve') -> None:
    mapping = node.mapping
    mapping.clip_min_x = 0.0
    mapping.clip_max_x = 1.0
    mapping.clip_min_y = 0.0
    mapping.clip_max_y = 1.0
    mapping.use_clip = True
    mapping.initialize()
    for pt in mapping.curves[0].points:
        pt.select = False
    mapping.reset_view()


def curve_mapping_node_remove(settings: 'InterpolationSettings', name: str) -> None:
    node = curve_mapping_node_get(settings, name)
    if node is not None:
        node.id_data.nodes.remove(node)


class InterpolationSettings(PropertyGroup):

    def _ipo_property_update(self, context: 'Context') -> None:
        ipo = self.interpolation
        if ipo != 'CUSTOM':
            key = ipo if ipo == 'LINEAR' else f'{ipo}_{self.easing}'
            node = self._curve_node_ensure()
            preset = CURVE_MAPPING_PRESETS[key]
            curve_mapping_node_preset_apply(node, preset)

    easing: EnumProperty(
        name="Easing",
        description="Type of easing (in/out) to apply to the interpolation curve",
        items=[
            ('EASE_IN'    , "Ease In"      , "", 'IPO_EASE_IN'    , 0),
            ('EASE_OUT'   , "Ease Out"     , "", 'IPO_EASE_OUT'   , 1),
            ('EASE_IN_OUT', "Ease In & Out", "", 'IPO_EASE_IN_OUT', 2),
        ],
        default='EASE_IN_OUT',
        options=set(),
        update=_ipo_property_update
        )# type: ignore

    def _internal__curve_node_handle_get(self) -> str:
        return self.get("internal__curve_node_handle", "")

    internal__curve_node_handle: StringProperty(
        get=_internal__curve_node_handle_get,
        options=set()
        )# type: ignore

    interpolation: EnumProperty(
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
        update=_ipo_property_update
        )# type: ignore

    def _curve_node_get(self) -> 'ShaderNodeVectorCurve|None':
        return curve_mapping_node_get(self, self._internal__curve_node_handle_get())

    def _curve_node_ensure(self) -> 'ShaderNodeVectorCurve':
        return curve_mapping_node_ensure(self, self._internal__curve_node_handle_get())

    def _init_interpolation_settings(self) -> None:
        self["internal__curve_node_handle"] = str(uuid4())
        node = curve_mapping_node_ensure(self, self.internal__curve_node_handle)
        curve_mapping_node_preset_apply(node, CURVE_MAPPING_PRESETS['LINEAR'])
