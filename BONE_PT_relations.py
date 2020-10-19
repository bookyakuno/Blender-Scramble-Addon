# 「プロパティ」エリア > 「ボーン」タブ > 「関係」パネル
# "Propaties" Area > "Bone" Tab > "Relations" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class copy_bone_relations_settings(bpy.types.Operator):
	bl_idname = "pose.copy_bone_relations_settings"
	bl_label = "Copy Relations Settings"
	bl_description = "Copies of other selected bone affinity of active bone"
	bl_options = {'REGISTER', 'UNDO'}

	layers : BoolProperty(name="Layer", default=True)

	parent : BoolProperty(name="Parent", default=True)
	use_connect : BoolProperty(name="Connection", default=True)
	use_inherit_rotation : BoolProperty(name="Inherit Rotation", default=True)
	use_inherit_scale : BoolProperty(name="Inherit Scale", default=True)
	use_local_location : BoolProperty(name="Local Location", default=True)

	bone_group : BoolProperty(name="Bone Group", default=True)
	use_relative_parent : BoolProperty(name="Relative Parenting", default=True)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if 'selected_pose_bones' in dir(context):
					if context.selected_pose_bones:
						if 2 <= len(context.selected_pose_bones):
							return True
				if 'selected_bones' in dir(context):
					if context.selected_bones:
						if 2 <= len(context.selected_bones):
							return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		row = self.layout.row()
		col = row.column()
		col.prop(self, 'layers')
		col.prop(self, 'parent')
		col.prop(self, 'use_relative_parent')		
		col.prop(self, 'bone_group')
		col = row.column()
		col.prop(self, 'use_connect')
		col.prop(self, 'use_local_location')
		col.prop(self, 'use_inherit_rotation')
		col.prop(self, 'use_inherit_scale')

	def execute(self, context):
		bone_names = []
		if 'selected_pose_bones' in dir(context):
			if context.selected_pose_bones:
				active_bone_name = context.active_pose_bone.name
				for bone in context.selected_pose_bones:
					if active_bone_name != bone.name:
						bone_names.append(bone.name)
		if 'selected_bones' in dir(context):
			if context.selected_bones:
				active_bone_name = context.active_bone.name
				for bone in context.selected_bones:
					if active_bone_name != bone.name:
						bone_names.append(bone.name)
		ob = context.active_object
		arm = ob.data
		bones = []
		pose_bones = []
		for name in bone_names:
			bones.append( arm.bones[name] )
			pose_bones.append( ob.pose.bones[name] )
		active_bone = arm.bones[active_bone_name]
		active_pose_bone = ob.pose.bones[active_bone_name]
		for bone in bones:
			bone.layers = active_bone.layers[:]
			try:
				bone.parent = active_bone.parent
			except AttributeError:
				pass
			try:
				bone.use_connect = active_bone.use_connect
			except AttributeError:
				pass
			bone.use_inherit_rotation = active_bone.use_inherit_rotation
			bone.use_inherit_scale = active_bone.use_inherit_scale
			bone.use_local_location = active_bone.use_local_location
			bone.use_relative_parent = active_bone.use_relative_parent
		for bone in pose_bones:
			bone.bone_group = active_pose_bone.bone_group
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	copy_bone_relations_settings
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
		flag = False
		if 'selected_pose_bones' in dir(context):
			if context.selected_pose_bones:
				if 2 <= len(context.selected_pose_bones):
					flag = True
		if 'selected_bones' in dir(context):
			if context.selected_bones:
				if 2 <= len(context.selected_bones):
					flag = True
		if flag:
			self.layout.operator(copy_bone_relations_settings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
