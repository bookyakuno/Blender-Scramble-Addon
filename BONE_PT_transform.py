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

################
# クラスの登録 #
################

classes = [
	CopyBoneTransform
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
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
