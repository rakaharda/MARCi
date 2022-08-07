import math
import bpy

def deselect_all():
    """Deselects all bones in current mode"""
    
    if bpy.context.mode == 'EDIT_ARMATURE':
        bpy.ops.armature.select_all(action='DESELECT')
    elif bpy.context.mode == 'POSE':
        bpy.ops.pose.select_all(action='DESELECT')

def objectmode():
    """Switches to object mode if not in it"""
    if bpy.context.mode == "POSE":
        bpy.ops.object.posemode_toggle()
    elif bpy.context.mode == "EDIT_ARMATURE":
        bpy.ops.object.editmode_toggle()


def posemode() -> None:
    """Switches to pose mode if not in it"""

    if bpy.context.mode != "POSE":
        bpy.ops.object.posemode_toggle()


def editmode():
    """Switches to edit mode if not in it"""

    if bpy.context.mode != "EDIT_ARMATURE":
        bpy.ops.object.editmode_toggle()


def select_bone(armature, bone_name, multiple=False, head = True, tail = True):
    """Selects given bone"""

    if not multiple:
        deselect_all()
    if bpy.context.mode == "POSE":
        bone = bpy.context.object.pose.bones[bone_name]
        armature.bones.active = bone.bone
    if bpy.context.mode == "EDIT_ARMATURE":
        armature.edit_bones.active = armature.edit_bones[bone_name]
        armature.edit_bones[bone_name].select = True
        armature.edit_bones[bone_name].select_head = head
        armature.edit_bones[bone_name].select_tail = tail


def extrude_bone(armature, from_bone, vec, name, parent="Root", orient_type="GLOBAL", from_head=False):
    """Extrudes bone from selected bone in direction of given vector,
    renames it, turns off deform, disconnects
    and parents to give bone (Root bone by default),
    expecting that there is no bone with name .001 already exist"""

    editmode()
    deselect_all()
    if not from_head:
        armature.edit_bones[from_bone].select_tail = True
    else:
        armature.edit_bones[from_bone].select_head = True
    bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked": False},
                                  TRANSFORM_OT_translate={"value": vec,
                                  "orient_type": orient_type})
    armature.edit_bones[from_bone + ".001"].name = name
    armature.edit_bones[name].use_deform = False
    armature.edit_bones[name].use_connect = False
    if parent is not None:
        armature.edit_bones[name].parent = armature.edit_bones[parent]
    else:
        armature.edit_bones[name].parent = None
    bpy.ops.object.editmode_toggle()


def duplicate_bone(armature, bone_name, name=None, parent=None, length=None):
    editmode()
    select_bone(armature, bone_name)
    bpy.ops.armature.duplicate()
    bone = bpy.context.selected_bones[0]
    
    if parent is not None:
        bone.parent = armature.edit_bones[parent]
    if name is not None:
        bone.name = name
    if length is not None:
        bone.length = length


def add_bone(bone_name):
    editmode()
    bpy.ops.armature.bone_primitive_add(name=bone_name)


def move_bone(armature, name, position):
    """Moves bone in direction of given vector"""

    editmode()
    armature.edit_bones[name].translate(position)
    bpy.ops.object.editmode_toggle()


def move_to_bone(armature, bone_to_move_name, bone_tail_name, src_head = False, dst_head = False):
    """Moves bone head/tail to tail/head of other bone"""

    editmode()
    vector = armature.edit_bones[bone_to_move_name].vector
    if dst_head:
        vector2 = armature.edit_bones[bone_tail_name].head
    else:
        vector2 = armature.edit_bones[bone_tail_name].tail
    if src_head:
        armature.edit_bones[bone_to_move_name].head = vector2
        armature.edit_bones[bone_to_move_name].tail = vector2 - vector
    else:
        armature.edit_bones[bone_to_move_name].tail = vector2 + vector
        armature.edit_bones[bone_to_move_name].head = vector2
        
    bpy.ops.object.editmode_toggle()    


def add_ik_modifier(rig, bone_name, chain_length=0,
                    target_name=None, pole_name=None, pole_angle=0):
    """Adds IK modifier to bone"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='IK')
    constraint = bone.constraints[-1]
    constraint.chain_count = chain_length
    if target_name is not None:
        constraint.target = rig
        constraint.subtarget = target_name
    if pole_name is not None:
        constraint.pole_target = rig
        constraint.pole_subtarget = pole_name
    constraint.pole_angle = math.radians(pole_angle)
    bpy.ops.object.posemode_toggle()


def remove_constraint(rig, bone_name, constraint):
    posemode()
    bone = rig.pose.bones[bone_name]
    try:
        bone.constraints.remove(bone.constraints[constraint])
    except KeyError:
        print(f"Constraint {constraint} in bone {bone_name} not found")


def add_limit_loc_constraint(armature, bone_name, 
                             min_x=None, min_y=None, min_z=None,
                             max_x=None, max_y=None, max_z=None):
    """Adds Limit Location Constraint to a bone
    and sets it to local and to affect transform"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='LIMIT_LOCATION')
    constraint = bone.constraints[-1]
    constraint.owner_space = 'LOCAL'
    constraint.use_transform_limit = True
    if min_x is not None:
        constraint.use_min_x = True
        constraint.min_x = min_x
    if min_y is not None:
        constraint.use_min_y = True
        constraint.min_y = min_y
    if min_z is not None:
        constraint.use_min_z = True
        constraint.min_z = min_z
    if max_x is not None:
        constraint.use_max_x = True
        constraint.max_x = max_x
    if max_y is not None:
        constraint.use_max_y = True
        constraint.max_y = max_y
    if max_z is not None:
        constraint.use_max_z = True
        constraint.max_z = max_z


def add_limit_rotation_constraint(armature, bone_name, axis="xyz",
                                  min_x=0, min_y=0, min_z=0,
                                  max_x=0, max_y=0, max_z=0,
                                  affect_transform=True):
    """Adds Limit Rotation constraint to the bone in local space"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='LIMIT_ROTATION')
    constraint = bone.constraints[-1]
    constraint.use_limit_x = axis.lower().__contains__("x")
    constraint.min_x = math.radians(min_x)
    constraint.max_x = math.radians(max_x)
    constraint.use_limit_y = axis.lower().__contains__("y")
    constraint.min_y = math.radians(min_y)
    constraint.max_y = math.radians(max_y)
    constraint.use_limit_z = axis.lower().__contains__("z")
    constraint.min_z = math.radians(min_z)
    constraint.max_z = math.radians(max_z)
    constraint.use_transform_limit = affect_transform
    constraint.owner_space = 'LOCAL'
    return constraint


def add_copy_transforms_constraint(rig, bone_name, subtarget, influence=1.0):
    """Adds Copy Transforms modifier to the bone"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='COPY_TRANSFORMS')
    bone.constraints[-1].target = rig
    bone.constraints[-1].subtarget = subtarget
    bone.constraints[-1].influence = influence


def add_damped_track_modifier(rig, bone_name, subtarget):
    """Adds Damped Track modifier to the bone"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='DAMPED_TRACK')
    constraint = bone.constraints[-1]
    constraint.target = rig
    constraint.subtarget = subtarget


def add_locked_track_constraint(rig, bone_name, subtarget, head_tail = 0.0, track_axis = 'TRACK_Y', lock_axis = 'LOCK_Z'):
    """Adds Locked Track constraint to the bone
       Track axes - TRACK_X, TRACK_NEGATIVE_X, TRACK_Y, TRACK_NEGATIVE_Y, TRACK_Z, TRACK_NEGATIVE_Z
       Locked axes - LOCK_X, LOCK_Y, LOCK_Z"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='LOCKED_TRACK')
    constraint = bone.constraints[-1]
    constraint.target = rig
    constraint.subtarget = subtarget
    constraint.head_tail = head_tail
    constraint.track_axis = track_axis
    constraint.lock_axis = lock_axis


def constraint_ik_rotation(armature, bone_name, x_axis = True, y_axis = False, z_axis = True):
    """Constraints rotation of bone"""

    posemode()
    deselect_all()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bone.lock_ik_x = x_axis
    bone.lock_ik_y = y_axis
    bone.lock_ik_z = z_axis
    bpy.ops.object.posemode_toggle()


def add_copy_rotation_constraint(rig, bone_name, target_name, axis='xyz', mix_mode='ADD', target_space='LOCAL_WITH_PARENT', owner_space='LOCAL', name=''):
    """Adds Copy Rotation constraint to the bone in local space"""
    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='COPY_ROTATION')
    constraint = bone.constraints[-1]
    if name is not '':
        constraint.name = name
    constraint.target = rig
    constraint.subtarget = target_name
    constraint.use_x = "x" in axis.lower()
    constraint.use_y = "y" in axis.lower()
    constraint.use_z = "z" in axis.lower()
    constraint.mix_mode = mix_mode
    constraint.target_space = target_space
    constraint.owner_space = owner_space


def add_shrinkwrap(armature, bone_name, target):
    """Adds Shrinkwrap Relationship to bone with object as target"""
    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='SHRINKWRAP')
    constraint = bone.constraints[-1]
    constraint.target = bpy.data.objects[target]
    bpy.ops.constraint.move_to_index(constraint=constraint.name, owner='BONE', index=0)
    constraint.shrinkwrap_type = 'PROJECT'
    constraint.project_axis = 'POS_Y'
    constraint.project_limit = 0.05
    

def add_transformation_constraint(
    context: bpy.types.Context, 
    bone_name: str, 
    target: str,
    target_space = 'LOCAL',
    owner_space = 'LOCAL' ,
    map_from = 'LOCATION',
    map_to = 'LOCATION',
    from_min_x = 0,
    from_max_x = 0,
    from_min_y = 0,
    from_max_y = 0,
    from_min_z = 0,
    from_max_z = 0,
    to_min_x = 0,
    to_max_x = 0,
    to_min_y = 0,
    to_max_y = 0,
    to_min_z = 0,
    to_max_z = 0,
    map_to_x_from = 'X',
    map_to_y_from = 'Y',
    map_to_z_from = 'Z',
    mix = 'ADD',
    name = ''):
    """Adds Transformation constraint"""
    posemode()
    rig = context.active_object
    armature = rig.data
    bone = context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='TRANSFORM')
    constraint = bone.constraints[-1]
    constraint.target = rig
    constraint.subtarget = target
    if name is not '':
        constraint.name = name
    constraint.target_space = target_space
    constraint.owner_space = owner_space
    constraint.map_from = map_from
    if map_from is 'LOCATION':
        constraint.from_min_x = from_min_x
        constraint.from_max_x = from_max_x
        constraint.from_min_y = from_min_y
        constraint.from_max_y = from_max_y
        constraint.from_min_z = from_min_z
        constraint.from_max_z = from_max_z
    elif map_from is 'ROTATION':
        constraint.from_min_x_rot = math.radians(from_min_x)
        constraint.from_max_x_rot = math.radians(from_max_x)
        constraint.from_min_y_rot = math.radians(from_min_y)
        constraint.from_max_y_rot = math.radians(from_max_y)
        constraint.from_min_z_rot = math.radians(from_min_z)
        constraint.from_max_z_rot = math.radians(from_max_z)
    elif map_from is 'SCALE':
        constraint.from_min_x_scale = from_min_x
        constraint.from_max_x_scale = from_max_x
        constraint.from_min_y_scale = from_min_y
        constraint.from_max_y_scale = from_max_y
        constraint.from_min_z_scale = from_min_z
        constraint.from_max_z_scale = from_max_z
    constraint.map_to = map_to
    constraint.map_to_x_from = map_to_x_from
    constraint.map_to_y_from = map_to_y_from
    constraint.map_to_z_from = map_to_z_from
    if map_to is 'LOCATION':
        constraint.to_min_x = to_min_x
        constraint.to_max_x = to_max_x
        constraint.to_min_y = to_min_y
        constraint.to_max_y = to_max_y
        constraint.to_min_z = to_min_z
        constraint.to_max_z = to_max_z
        constraint.mix_mode = mix
    elif map_to is 'ROTATION':
        constraint.to_min_x_rot = math.radians(to_min_x)
        constraint.to_max_x_rot = math.radians(to_max_x)
        constraint.to_min_y_rot = math.radians(to_min_y)
        constraint.to_max_y_rot = math.radians(to_max_y)
        constraint.to_min_z_rot = math.radians(to_min_z)
        constraint.to_max_z_rot = math.radians(to_max_z)
        constraint.mix_mode_rot = mix
    elif map_to is 'SCALE':
        constraint.to_min_x_scale = to_min_x
        constraint.to_max_x_scale = to_max_x
        constraint.to_min_y_scale = to_min_y
        constraint.to_max_y_scale = to_max_y
        constraint.to_min_z_scale = to_min_z
        constraint.to_max_z_scale = to_max_z
        constraint.mix_mode_scale = mix


def add_vertex_subtract(from_group, group, prefix = ""):
    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
    modifier = bpy.context.object.modifiers[-1]
    modifier.name = prefix + modifier.name
    modifier.vertex_group_a = from_group
    modifier.vertex_group_b = group
    modifier.mix_set = 'ALL'
    modifier.mix_mode = 'SUB'
    bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)


def lock_bone_rot(armature, bone_name, axis = 'xyz'):
    """Locks bone rotation along given axis"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bone.lock_rotation[0] = axis.lower().__contains__("x")
    bone.lock_rotation[1] = axis.lower().__contains__("y")
    bone.lock_rotation[2] = axis.lower().__contains__("z")


def assign_selected_to_bone_group(context, bone_group):
    posemode()
    for i, group in enumerate(context.active_object.pose.bone_groups):
        if group.name == bone_group:
            bpy.ops.pose.group_assign(type=i + 1)
            return
    print(f"Bone group with name {bone_group} not found")


def create_bone_group(bone_groups, name='Group', color_set='DEFAULT'):
    for group in bone_groups:
        if group.name == name:
            group.color_set = color_set
            return
    bone_groups.new(name=name)
    bone_groups[-1].color_set = color_set