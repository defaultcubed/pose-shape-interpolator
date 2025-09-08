
import bpy


# Returns a set of input armature bone names, excluding any bones that have been
# selected as inputs for this input, or other inputs that reference the same
# armature object.
def _name_search(self, context, edit_text):
    o = self.object
    if o is None:
        return tuple()
    s = set(o.data.bones.keys())
    for x in self.id_data.pose_shape_interpolator_settings:
        if x.object != o:
            continue
        for i in x.inputs:
            if i != self:
                s.discard(i.name)
    return s


# Checks whether or not the object is an armature
def _object_poll(self, object_):
    return object_.type == 'ARMATURE'


# Getter function for the input's handle property
def _handle_get(input_):
    return input_.get('handle', '')


class PSI_Input(bpy.types.PropertyGroup):

    handle: bpy.props.StringProperty(
        name="Handle",
        description="Unique internal handle for the input struct",
        get=_handle_get,
        options={'HIDDEN'}
        )# type: ignore

    name: bpy.props.StringProperty(
        name="Name",
        description="The name of the input PoseBone",
        search=_name_search,
        options=set()
        )# type: ignore

    object: bpy.props.PointerProperty(
        name="Object",
        description="The (armature) object to use as input",
        type=bpy.types.Object,
        poll=_object_poll,
        options=set()
        )# type: ignore

    rotation_axis: bpy.props.EnumProperty(
        name="Axis",
        description="Rotation axis",
        items=[
            ('X', "X", "X Axis"),
            ('Y', "Y", "Y Axis"),
            ('Z', "Z", "Z Axis"),
        ],
        default='Y',
        options=set()
        )# type: ignore

    rotation_mode: bpy.props.EnumProperty(
        name="Mode",
        description="Rotation channels to include in interpolation",
        items=[
            ('ANGLE'      , "Angle"         , "Single rotation angle (euler)"),
            ('SWING'      , "Swing"         , "Swing rotation around axis"   ),
            ('TWIST'      , "Twist"         , "Twist rotation around axis"   ),
            ('SWING_TWIST', "Swing & Twist" , "Use all rotation channels"    ),
        ],
        default='SWING_TWIST',
        options=set()
        )# type: ignore

    use_location_x: bpy.props.BoolProperty(
        name="X",
        description="X location input",
        default=False,
        options=set()
        )# type: ignore

    use_location_y: bpy.props.BoolProperty(
        name="Y",
        description="Y location input",
        default=False,
        options=set()
        )# type: ignore

    use_location_z: bpy.props.BoolProperty(
        name="Z",
        description="Z location input",
        default=False,
        options=set()
        )# type: ignore

    use_rotation: bpy.props.BoolProperty(
        name="Rotation",
        description="Rotation input",
        default=False,
        options=set()
        )# type: ignore

    use_scale_x: bpy.props.BoolProperty(
        name="X",
        description="X scale input",
        default=False,
        options=set()
        )# type: ignore

    use_scale_y: bpy.props.BoolProperty(
        name="Y",
        description="Y scale input",
        default=False,
        options=set()
        )# type: ignore

    use_scale_z: bpy.props.BoolProperty(
        name="Z",
        description="Z scale input",
        default=False,
        options=set()
        )# type: ignore
