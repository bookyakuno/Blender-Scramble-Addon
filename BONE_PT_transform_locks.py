# 「プロパティ」エリア > 「ボーン」タブ > 「トランスフォーム」パネル
# "Propaties" Area > "Bone" Tab > "Transform" Panel

import bpy

################
# オペレーター #
################

class copy_transform_lock_settings(bpy.types.Operator):
	bl_idname = "pose.copy_transform_lock_settings"
	bl_label = "Copy Transform Locks Settings"
	bl_description = "Copies of other selected bone lock setting active bone transform"
	bl_options = {'REGISTER', 'UNDO'}
	
	lock_location_x = bpy.props.BoolProperty(name="Loc X", default=True)
	lock_location_y = bpy.props.BoolProperty(name="Loc Y", default=True)
	lock_location_z = bpy.props.BoolProperty(name="Loc Z", default=True)
	
	lock_rotation_x = bpy.props.BoolProperty(name="Rot X", default=True)
	lock_rotation_y = bpy.props.BoolProperty(name="Rot Y", default=True)
	lock_rotation_z = bpy.props.BoolProperty(name="Rot Z", default=True)
	
	lock_scale_x = bpy.props.BoolProperty(name="Scale X", default=True)
	lock_scale_y = bpy.props.BoolProperty(name="Scale Y", default=True)
	lock_scale_z = bpy.props.BoolProperty(name="Scale Z", default=True)
	
	lock_rotations_4d = bpy.props.BoolProperty(name="Lock Rotation", default=True)
	lock_rotation_w = bpy.props.BoolProperty(name="Rot W", default=True)
	
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
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		for axis in ['x', 'y', 'z']:
			row = self.layout.row()
			row.prop(self, 'lock_location_' + axis)
			row.prop(self, 'lock_rotation_' + axis)
			row.prop(self, 'lock_scale_' + axis)
		row = self.layout.row()
		row.prop(self, 'lock_rotations_4d')
		row.prop(self, 'lock_rotation_w')
	
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
			if self.lock_rotations_4d:
				pose_bone.lock_rotations_4d = active_pose_bone.lock_rotations_4d
			if self.lock_rotation_w:
				pose_bone.lock_rotation_w = active_pose_bone.lock_rotation_w
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	copy_transform_lock_settings
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
		if 'selected_pose_bones' in dir(context):
			if 2 <= len(context.selected_pose_bones):
				self.layout.operator(copy_transform_lock_settings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
