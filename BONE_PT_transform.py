# 「プロパティ」エリア > 「ボーン」タブ > 「トランスフォーム」パネル
# "Propaties" Area > "Bone" Tab > "Transform" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyBoneTransform(bpy.types.Operator):
	bl_idname = "pose.copy_bone_transform"
	bl_label = "Copy Bone Transform"
	bl_description = "Copy active bone's location / rotation / scale to other selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	copy_location : BoolProperty(name="Location", default=True)
	copy_rotation : BoolProperty(name="Rotation", default=True)
	copy_scale : BoolProperty(name="Scale", default=True)

	@classmethod
	def poll(cls, context):
		if (context.selected_pose_bones):
			if (2 <= len(context.selected_pose_bones)):
				return True
		return False

	def execute(self, context):
		active_bone = context.active_pose_bone
		for bone in context.selected_pose_bones:
			if (bone.name != active_bone.name):
				if (self.copy_location):
					bone.location = active_bone.location[:]
				if (self.copy_rotation):
					bone.rotation_mode = active_bone.rotation_mode
					if (bone.rotation_mode == 'QUATERNION'):
						bone.rotation_quaternion = active_bone.rotation_quaternion[:]
					elif (bone.rotation_mode == 'AXIS_ANGLE'):
						bone.rotation_axis_angle = active_bone.rotation_axis_angle[:]
					else:
						bone.rotation_euler = active_bone.rotation_euler[:]
				if (self.copy_scale):
					bone.scale = active_bone.scale[:]
		return {'FINISHED'}


class CopyTransformLockSettings(bpy.types.Operator):
	bl_idname = "pose.copy_transform_lock_settings"
	bl_label = "Copy Transform Locks Settings"
	bl_description = "Copy active bone's lock of location / rotation / scale to other selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	lock_location_x : BoolProperty(name="X", default=True)
	lock_location_y : BoolProperty(name="Y", default=True)
	lock_location_z : BoolProperty(name="Z", default=True)

	lock_rotation_x : BoolProperty(name="X", default=True)
	lock_rotation_y : BoolProperty(name="Y", default=True)
	lock_rotation_z : BoolProperty(name="Z", default=True)

	lock_scale_x : BoolProperty(name="X ", default=True)
	lock_scale_y : BoolProperty(name="Y ", default=True)
	lock_scale_z : BoolProperty(name="Z ", default=True)

	ps = bpy.types.PoseBone.bl_rna.properties
	lock_rotations_4d : BoolProperty(name=ps["lock_rotations_4d"].name, description=ps["lock_rotations_4d"].description, default=True)
	lock_rotation_w : BoolProperty(name=ps["lock_rotation_w"].name, description=ps["lock_rotation_w"].description, default=True)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if 'selected_pose_bones' in dir(context):
					if 2 <= len(context.selected_pose_bones):
						return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=350)

	def draw(self, context):
		for p in ['lock_location_', 'lock_rotation_', 'lock_scale_']:
			box = self.layout.box()
			row = box.row()
			row.label(text=p.split("_")[1].capitalize())
			row.prop(self, p+'x')
			row.prop(self, p+'y')
			row.prop(self, p+'z')
		if context.active_pose_bone.rotation_mode in ['QUATERNION', 'AXIS_ANGLE']:
			row = box.row()
			row.prop(self, 'lock_rotation_w')
			row.prop(self, 'lock_rotations_4d')

	def execute(self, context):
		active_pose_bone = context.active_pose_bone
		for pose_bone in context.selected_pose_bones:
			if active_pose_bone.name == pose_bone.name:
				continue
			for i, axis in enumerate(['x', 'y', 'z']):
				if getattr(self, 'lock_location_' + axis):
					pose_bone.lock_location[i] = active_pose_bone.lock_location[i]
				if getattr(self, 'lock_rotation_' + axis):
					pose_bone.lock_rotation[i] = active_pose_bone.lock_rotation[i]
				if getattr(self, 'lock_scale_' + axis):
					pose_bone.lock_scale[i] = active_pose_bone.lock_scale[i]
			if active_pose_bone.rotation_mode in ['QUATERNION', 'AXIS_ANGLE']:
				if self.lock_rotations_4d:
					pose_bone.lock_rotations_4d = active_pose_bone.lock_rotations_4d
				if self.lock_rotation_w:
					pose_bone.lock_rotation_w = active_pose_bone.lock_rotation_w
		return {'FINISHED'}


################
# クラスの登録 #
################

classes = [
	CopyBoneTransform,
	CopyTransformLockSettings
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row(align=True)
		op = row.operator(CopyBoneTransform.bl_idname, icon='CON_LOCLIKE', text="Copy Location")
		op.copy_location, op.copy_rotation, op.copy_scale = True, False, False
		op = row.operator(CopyBoneTransform.bl_idname, icon='CON_ROTLIKE', text="Copy Rotation")
		op.copy_location, op.copy_rotation, op.copy_scale = False, True, False
		op = row.operator(CopyBoneTransform.bl_idname, icon='CON_SIZELIKE', text="Copy Scale")
		op.copy_location, op.copy_rotation, op.copy_scale = False, False, True
		if context.selected_pose_bones:
			if 2 <= len(context.selected_pose_bones):
				self.layout.operator(CopyTransformLockSettings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
