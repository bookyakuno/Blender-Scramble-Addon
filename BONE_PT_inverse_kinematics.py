# 「プロパティ」エリア > 「ボーン」タブ > 「インバースキネマティクス (IK)」パネル
# "Propaties" Area > "Bone" Tab > "Inverse Kinematics" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class copy_ik_settings(bpy.types.Operator):
	bl_idname = "pose.copy_ik_settings"
	bl_label = "Copy IK Setting"
	bl_description = "Copies of other selected bone IK settings Active"
	bl_options = {'REGISTER', 'UNDO'}

	lock_ik_x : BoolProperty(name="Lock", default=True)
	ik_stiffness_x : BoolProperty(name="Stiffness", default=True)
	use_ik_limit_x : BoolProperty(name="Limit", default=True)
	ik_min_x : BoolProperty(name="Minimum", default=True)
	ik_max_x : BoolProperty(name="Maximum", default=True)

	lock_ik_y : BoolProperty(name="Lock", default=True)
	ik_stiffness_y : BoolProperty(name="Stiffness", default=True)
	use_ik_limit_y : BoolProperty(name="Limit", default=True)
	ik_min_y : BoolProperty(name="Minimum", default=True)
	ik_max_y : BoolProperty(name="Maximum", default=True)

	lock_ik_z : BoolProperty(name="Lock", default=True)
	ik_stiffness_z : BoolProperty(name="Stiffness", default=True)
	use_ik_limit_z : BoolProperty(name="Limit", default=True)
	ik_min_z : BoolProperty(name="Minimum", default=True)
	ik_max_z : BoolProperty(name="Maximum", default=True)

	ik_stretch : BoolProperty(name="Stretch", default=True)

	@classmethod
	def poll(cls, context):
		if (2 <= len(context.selected_pose_bones)):
			return True
		return False

	def draw(self, context):
		for axis in ['x', 'y', 'z']:
			self.layout.label(text=f"{axis.upper()}")
			row = self.layout.row()
			row.prop(self, 'lock_ik_'+axis)
			row.prop(self, 'ik_stiffness_'+axis)
			row.prop(self, 'use_ik_limit_'+axis)
			row = self.layout.box().row()
			row.label(text="Angles for Limit")		
			row.prop(self, 'ik_min_'+axis)
			row.prop(self, 'ik_max_'+axis)
			self.layout.separator(factor=0.3)
		self.layout.separator(factor=0.7)
		self.layout.prop(self, 'ik_stretch')

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		source = context.active_pose_bone
		for target in context.selected_pose_bones[:]:
			if (source.name != target.name):
				for axis in ['x', 'y', 'z']:
					if (self.__getattribute__('lock_ik_'+axis)):
						target.__setattr__('lock_ik_'+axis, source.__getattribute__('lock_ik_'+axis))
					if (self.__getattribute__('ik_stiffness_'+axis)):
						target.__setattr__('ik_stiffness_'+axis, source.__getattribute__('ik_stiffness_'+axis))
					if (self.__getattribute__('use_ik_limit_'+axis)):
						target.__setattr__('use_ik_limit_'+axis, source.__getattribute__('use_ik_limit_'+axis))
					if (self.__getattribute__('ik_min_'+axis)):
						target.__setattr__('ik_min_'+axis, source.__getattribute__('ik_min_'+axis))
					if (self.__getattribute__('ik_max_'+axis)):
						target.__setattr__('ik_max_'+axis, source.__getattribute__('ik_max_'+axis))
				if (self.ik_stretch):
					target.ik_stretch = source.ik_stretch
		return {'FINISHED'}

class reverse_ik_min_max(bpy.types.Operator):
	bl_idname = "pose.reverse_ik_min_max"
	bl_label = "Invert Minimum/maximum Angle"
	bl_description = "Reverses minimum and maximum angle of IK setup this bone"
	bl_options = {'REGISTER', 'UNDO'}

	is_x : BoolProperty(name="X Invert", default=False)
	is_y : BoolProperty(name="Y Invert", default=False)
	is_z : BoolProperty(name="Z Invert", default=False)

	@classmethod
	def poll(cls, context):
		bone = context.active_pose_bone
		if (bone):
			for axis in ['x', 'y', 'z']:
				diff = bone.__getattribute__('ik_min_' + axis) + bone.__getattribute__('ik_max_' + axis)
				if (diff != 0):
					return True
			return False
		return False

	def invoke(self, context, event):
		bone = context.active_pose_bone
		for axis in ['x', 'y', 'z']:
			diff = bone.__getattribute__('ik_min_' + axis) + bone.__getattribute__('ik_max_' + axis)
			if (diff != 0):
				self.__setattr__('is_' + axis, True)
			else:
				self.__setattr__('is_' + axis, False)
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		bone = context.active_pose_bone
		if (self.is_x):
			ik_min = bone.ik_min_x
			ik_max = bone.ik_max_x
			bone.ik_min_x = -ik_max
			bone.ik_max_x = -ik_min
		if (self.is_y):
			ik_min = bone.ik_min_y
			ik_max = bone.ik_max_y
			bone.ik_min_y = -ik_max
			bone.ik_max_y = -ik_min
		if (self.is_z):
			ik_min = bone.ik_min_z
			ik_max = bone.ik_max_z
			bone.ik_min_z = -ik_max
			bone.ik_max_z = -ik_min
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class copy_ik_axis_setting(bpy.types.Operator):
	bl_idname = "pose.copy_ik_axis_setting"
	bl_label = "Copy axis-setting to other axis"
	bl_description = "Copy settings other axis from one axis"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('x', "X Axis", "", 1),
		('y', "Y Axis", "", 2),
		('z', "Z Axis", "", 3),
		]
	source_axis : EnumProperty(items=items, name="Source Axis")
	target_x : BoolProperty(name="To X", default=True)
	target_y : BoolProperty(name="To Y", default=True)
	target_z : BoolProperty(name="To Z", default=True)

	lock_ik : BoolProperty(name="Lock", default=True)
	ik_stiffness : BoolProperty(name="Stiffness", default=True)
	use_ik_limit : BoolProperty(name="Limit", default=True)
	ik_min : BoolProperty(name="Minimum", default=True)
	ik_max : BoolProperty(name="Maximum", default=True)

	@classmethod
	def poll(cls, context):
		bone = context.active_pose_bone
		if (bone):
			for setting in ['lock_ik', 'ik_stiffness', 'use_ik_limit', 'ik_min', 'ik_max']:
				x = bone.__getattribute__(setting + '_x')
				y = bone.__getattribute__(setting + '_y')
				z = bone.__getattribute__(setting + '_z')
				if (x == y == z):
					pass
				else:
					return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		self.layout.prop(self, 'source_axis')
		row = self.layout.row()
		row.prop(self, 'target_x')
		row.prop(self, 'target_y')
		row.prop(self, 'target_z')
		self.layout.label(text="Copy Setting")
		row = self.layout.row()
		row.prop(self, 'lock_ik')
		row.prop(self, 'ik_stiffness')
		row.prop(self, 'use_ik_limit')
		row = self.layout.box().row()
		row.label(text="Angles for Limit")		
		row.prop(self, 'ik_min')
		row.prop(self, 'ik_max')

	def execute(self, context):
		bone = context.active_pose_bone
		source_axis = self.source_axis
		for axis in ['x', 'y', 'z']:
			if (source_axis == axis):
				continue
			if (self.__getattribute__('target_' + axis)):
				if (self.lock_ik):
					value = bone.__getattribute__('lock_ik_' + source_axis)
					bone.__setattr__('lock_ik_' + axis, value)
				if (self.ik_stiffness):
					value = bone.__getattribute__('ik_stiffness_' + source_axis)
					bone.__setattr__('ik_stiffness_' + axis, value)
				if (self.use_ik_limit):
					value = bone.__getattribute__('use_ik_limit_' + source_axis)
					bone.__setattr__('use_ik_limit_' + axis, value)
				if (self.ik_min):
					value = bone.__getattribute__('ik_min_' + source_axis)
					bone.__setattr__('ik_min_' + axis, value)
				if (self.ik_max):
					value = bone.__getattribute__('ik_max_' + source_axis)
					bone.__setattr__('ik_max_' + axis, value)
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class reset_ik_settings(bpy.types.Operator):
	bl_idname = "pose.reset_ik_settings"
	bl_label = "Reset IK Settings"
	bl_description = "Reset this bone IK settings"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		bone = context.active_pose_bone
		if bone:
			for axis in ['x', 'y', 'z']:
				if getattr(bone, 'lock_ik_' + axis) != False:
					return True
				if getattr(bone, 'ik_stiffness_' + axis) != 0.0:
					return True
				if getattr(bone, 'use_ik_limit_' + axis) != False:
					return True
				if -3.1415927410125 <= getattr(bone, 'ik_min_' + axis):
					return True
				if getattr(bone, 'ik_max_' + axis) <= 3.1415927410125:
					return True
			if bone.ik_stretch != 0.0:
				return True
		return False

	def execute(self, context):
		bone = context.active_pose_bone
		for axis in ['x', 'y', 'z']:
			setattr(bone, 'lock_ik_' + axis, False)
			setattr(bone, 'ik_stiffness_' + axis, 0.0)
			setattr(bone, 'use_ik_limit_' + axis, False)
			setattr(bone, 'ik_min_' + axis, -3.1415927410125732)
			setattr(bone, 'ik_max_' + axis, 3.1415927410125732)
		bone.ik_stretch = 0.0
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	copy_ik_settings,
	reverse_ik_min_max,
	copy_ik_axis_setting,
	reset_ik_settings
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
		spl = self.layout.split(factor=0.8)
		row = spl.row(align=True)
		row.operator(reverse_ik_min_max.bl_idname, icon='ARROW_LEFTRIGHT', text="Reverse min & max")
		row.operator(copy_ik_axis_setting.bl_idname, icon='LINKED', text="Copy to other axes")
		spl.operator(reset_ik_settings.bl_idname, icon='X', text="Reset")
		if 2 <= len(context.selected_pose_bones):
			self.layout.operator(copy_ik_settings.bl_idname, icon='COPY_ID', text="Copy IK Setting")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
