# 「プロパティ」エリア > 「ボーン」タブ > 「トランスフォーム」パネル
# "Propaties" Area > "Bone" Tab > "Transform" Panel

import bpy

################
# オペレーター #
################

class CopyBoneTransform(bpy.types.Operator):
	bl_idname = "pose.copy_bone_transform"
	bl_label = "Copy Bone Transform"
	bl_description = "Copy selected bones of other active bone deformation information"
	bl_options = {'REGISTER', 'UNDO'}
	
	copy_location = bpy.props.BoolProperty(name="Location", default=True)
	copy_rotation = bpy.props.BoolProperty(name="Rotation", default=True)
	copy_scale = bpy.props.BoolProperty(name="Scale", default=True)
	
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

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row(align=True)
		op = row.operator(CopyBoneTransform.bl_idname, icon='MAN_TRANS', text="Copy Location")
		op.copy_location, op.copy_rotation, op.copy_scale = True, False, False
		op = row.operator(CopyBoneTransform.bl_idname, icon='MAN_ROT', text="Copy Rotation")
		op.copy_location, op.copy_rotation, op.copy_scale = False, True, False
		op = row.operator(CopyBoneTransform.bl_idname, icon='MAN_SCALE', text="Copy Scale")
		op.copy_location, op.copy_rotation, op.copy_scale = False, False, True
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
