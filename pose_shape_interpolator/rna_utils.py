
import bpy
from mathutils import Matrix
from uuid import uuid4


CMAP_PRESETS = {
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


def uniqname(collection, basename):
    k = basename
    i = 0
    while k in collection:
        i += 1
        k = f'{basename}.{str(i).zfill(3)}'
    return k


def handle_generate():
    return str(uuid4())


def handle_get(obj, key='handle'):
    return obj.get(key)


def handle_ensure(obj, key='handle'):
    id_ = obj.get(key)
    if not id_:
        id_ = handle_generate()
        obj[key] = id_
    return id_


def cmaptree_get(obj):
    return obj.id_data.pose_shape_interpolator_curves


def cmaptree_ensure(obj):
    tree = cmaptree_get(obj)
    if tree is None:
        tree = bpy.data.node_groups.new('POSE_SHAPE_IPO', 'ShaderNodeTree')
        obj.id_data.pose_shape_interpolator_curves = tree
    return tree


def cmapnode_get(obj, name=""):
    tree = cmaptree_get(obj)
    if tree is not None:
        return tree.nodes.get(name or handle_get(obj))


def cmapnode_ensure(obj, name=""):
    tree = cmaptree_ensure(obj)
    name = name or handle_ensure(obj)
    node = tree.nodes.get(name)
    if node is None:
        node = tree.nodes.new('ShaderNodeVectorCurve')
        node.name = name
        cmap_node_init(node)
    return node


def cmapnode_init(node):
    m = node.mapping
    m.clip_min_x = 0.0
    m.clip_max_x = 1.0
    m.clip_min_y = 0.0
    m.clip_max_y = 1.0
    m.use_clip = True
    m.initialize()
    for pt in m.curves[0].points:
        pt.select = False
    m.reset_view()


def cmapnode_remove(obj, name=""):
    node = cmapnode_get(obj, name)
    if node is not None:
        node.id_data.nodes.remove(node)


def cmapnode_apply(node, preset):
    m = node.mapping
    n = len(preset)
    pts = m.curves[0].points
    while len(pts) > n: pts.remove(pts[-2])
    while len(pts) < n: pts.new(0.0, 0.0)
    for pt, (co, ht) in zip(pts, preset):
        pt.handle_type = ht
        pt.location = co
        pt.select = False
    m.update()


def cmapnode_copy(a, b):
    ma = a.mapping
    mb = b.mapping
    ptsa = ma.curves[0].points
    ptsb = mb.curves[0].points
    n = len(ptsa)
    while len(ptsb) > n:
        ptsb.remove(ptsb[-2])
    for i, pa in enumerate(ptsa):
        if len(ptsb) <= i:
            pb = ptsb.new(*pa.location)
        else:
            pb = ptsb[i]
            pb.location = pa.location
        pb.handle_type = pa.handle_type
        pb.select = False
    mb.update()


def input_is_enabled(input_):
    return (
        input_.use_rotation
        or input_.use_location_x
        or input_.use_location_y
        or input_.use_location_z
        or input_.use_scale_x
        or input_.use_scale_y
        or input_.use_scale_z)


def input_posebone_get(inp):
    ob = inp.object
    if ob is not None and ob.type == 'ARMATURE':
        return ob.pose.bones.get(inp.name)


def input_matrix_get(inp):
    pb = input_posebone_get(inp)
    if pb is None:
        return Matrix.Identity(4)
    return pb.id_data.convert_space(
        pose_bone=pb,
        matrix=pb.matrix,
        from_space='POSE',
        to_space='LOCAL')


def input_is_valid(inp):
    return input_posebone_get(inp) is not None


def input_psi(i):
    p = i.path_from_id()
    return i.id_data.path_resolve(p[:p.rfind('.')])


def input_add(inputs, pb=None):
    i = inputs.add()
    if pb:
        i.object = pb.id_data
        i.name = pb.name
    psi = input_psi(i)
    for p in psi.poses:
        input_pose_init(p.data.add(), i)
    psi.active_input_index = len(psi.poses)-1
    return i


def input_remove(inputs, i):
    inp = inputs[i]
    psi = input_psi(inp)
    for pose in psi.poses:
        input_pose_remove(pose, inp)
    inputs.remove(i)


def input_pose_handle_assign(ip, inp):
    ip['input_handle'] = handle_ensure(inp)


def input_pose_update(ip, inp):
    ip.matrix = input_matrix_get(inp)


def input_pose_get(pose, inp):
    k = inp.handle
    for ip in pose.data:
        if ip.input_handle == k:
            return ip


def input_pose_find(pose, inp):
    k = inp.handle
    for i, ip in pose.data:
        if ip.input_handle == k:
            return i
    return -1


def input_pose_remove(pose, inp):
    i = input_pose_find(pose, inp)
    if i >= 0:
        pose.data.remove(i)


def input_pose_init(ip, inp):
    input_pose_handle_assign(ip, inp)
    input_pose_update(ip, inp)


def pose_psi(pose):
    p = pose.path_from_id()
    return pose.id_data.path_resolve(p[:p.rfind('.')])


def pose_is_valid(pose):
    return pose.shape_key_resolve() is not None


def pose_add(psi, name='Pose'):
    pose = psi.poses.add()
    data = pose.data
    pose['name'] = uniqname(psi.poses, name)
    cmapnode_ensure(pose)
    for inp in psi.inputs:
        input_pose_update(data.add(), inp)


def pose_remove(psi, i):
    poses = psi.poses
    cmapnode_remove(poses[i])
    poses.remove(i)


def posedata_update(pose, psi=None):
    data = pose.data
    for inp in (psi or pose_psi(pose)).inputs:
        ip = input_pose_get(pose, inp)
        if ip is not None:
            input_pose_update(ip, inp)


def ctx_key(ctx):
    ob = ctx.object
    if ob is not None and ob.type == 'MESH':
        return ob.data.shape_keys


def ctx_psi_active(ctx):
    key = ctx_key(ctx)
    if key is not None:
        return psi_active(key)


def psi_active(key):
    i = key.active_pose_shape_interpolator_index
    o = key.pose_shape_interpolators
    if 0 <= i < len(o):
        return o[i]


def psi_add(key, name="PoseInterpolator"):
    interpolators = key.pose_shape_interpolators
    psi = interpolators.add()
    psi['name'] = uniqname(interpolators, name)
    cmapnode_ensure(psi)
    pose_add(psi, "Rest")


def psi_index(psi):
    interpolators = psi.id_data.pose_shape_interpolators
    return next(i for i, x in enumerate(interpolators) if x == psi)


def psi_remove(psi):
    for pose in psi.poses:
        cmapnode_remove(pose)
    cmapnode_remove(psi)
    psi.id_data.pose_shape_interpolators.remove(psi_index(psi))


def psi_toggle(psi):
    if psi.enabled:
        psi_enable(psi)
    else:
        psi_disable(psi)


def psi_enable(psi):
    pass


def psi_disable(psi):
    pass


def mxpose(m):
    return list(map(list, zip(*m)))


def qt_aim_x(q):
    w, x, y, z = q
    return (1.0 - 2.0*(y*y + z*z), 2.0*(x*y + w*z), 2.0*(x*z - w*y))


def qt_aim_y(q):
    w, x, y, z = q
    return (2.0*(x*y - w*z), 1.0 - 2.0*(x*x + z*z), 2.0*(y*z + w*x))


def qt_aim_z(q):
    w, x, y, z = q
    return (2.0*(x*z + w*y), 2.0*(y*z - w*x), 1.0 - 2.0*(x*x + y*y))


QT_AIM = {
    'X': qt_aim_x,
    'Y': qt_aim_y,
    'Z': qt_aim_z,
}


QT_AIM_EXPR = {
    'X': (
        "1.0-2.0*(y*y+z*z)",
        "2.0*(x*y+w*z)",
        "2.0*(x*z-w*y)",
    ),
    'Y': (
        "2.0*(x*y-w*z)",
        "1.0-2.0*(x*x+z*z)",
        "2.0*(y*z+w*x)",
    ),
    'Z': (
        "2.0*(x*z+w*y)",
        "2.0*(y*z-w*x)",
        "1.0-2.0*(x*x+y*y)",
    ),
}



