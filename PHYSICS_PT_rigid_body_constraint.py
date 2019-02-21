# 「プロパティ」エリア > 「物理演算」タブ > 「剛体コンストレイント」パネル
# "Propaties" Area > "Physics" Tab > "Rigid Body Constraint" Panel

import bpy

################
# オペレーター #
################

class CopyConstraintSetting(bpy.types.Operator):
	bl_idname = "rigidbody.copy_constraint_setting"
	bl_label = "Copy rigidbody constraints settings"
	bl_description = "Copies selected objects for other rigid constraints on active object"
	bl_options = {'REGISTER', 'UNDO'}
	
	copy_target_objects = bpy.props.BoolProperty(name="Copy Object Targeted", default=False)
	
	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			if context.active_object:
				if context.active_object.rigid_body_constraint:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'copy_target_objects')
	
	def execute(self, context):
		active_ob = context.active_object
		for ob in context.selected_objects:
			if ob.name == active_ob.name:
				continue
			if not ob.rigid_body_constraint:
				context.scene.objects.active = ob
				bpy.ops.rigidbody.constraint_add()
			for val_name in dir(ob.rigid_body_constraint):
				if not self.copy_target_objects:
					if (val_name in ['object1', 'object2']):
						continue
				if val_name[0] != '_' and 'rna' not in val_name:
					value = active_ob.rigid_body_constraint.__getattribute__(val_name)
					try:
						ob.rigid_body_constraint.__setattr__(val_name, value[:])
					except TypeError:
						try:
							ob.rigid_body_constraint.__setattr__(val_name, value)
						except AttributeError:
							pass
					except AttributeError:
						pass
		context.scene.objects.active = active_ob
		return {'FINISHED'}

class ClearConstraintLimits(bpy.types.Operator):
	bl_idname = "rigidbody.clear_constraint_limits"
	bl_label = "Reset rigid body constraint limits"
	bl_description = "Initializes rigid constraints of active object limit settings group"
	bl_options = {'REGISTER', 'UNDO'}
	
	mode = bpy.props.StringProperty(name="Mode", default='', options={'SKIP_SAVE', 'HIDDEN'})
	
	is_lin_x = bpy.props.BoolProperty(name="X Move", default=True, options={'SKIP_SAVE'})
	is_lin_y = bpy.props.BoolProperty(name="Y Move", default=True, options={'SKIP_SAVE'})
	is_lin_z = bpy.props.BoolProperty(name="Z Move", default=True, options={'SKIP_SAVE'})
	
	is_ang_x = bpy.props.BoolProperty(name="X Rot", default=True, options={'SKIP_SAVE'})
	is_ang_y = bpy.props.BoolProperty(name="Y Rot", default=True, options={'SKIP_SAVE'})
	is_ang_z = bpy.props.BoolProperty(name="Z Rot", default=True, options={'SKIP_SAVE'})
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.rigid_body_constraint:
				return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.label("Clear Move Limit")
		row = self.layout.row()
		row.prop(self, 'is_lin_x', text="X")
		row.prop(self, 'is_lin_y', text="Y")
		row.prop(self, 'is_lin_z', text="Z")
		self.layout.label("Clear Rotate Limit")
		row = self.layout.row()
		row.prop(self, 'is_ang_x', text="X")
		row.prop(self, 'is_ang_y', text="Y")
		row.prop(self, 'is_ang_z', text="Z")
	
	def execute(self, context):
		rigid_const = context.active_object.rigid_body_constraint
		if (self.mode != ''):
			rigid_const.type = self.mode
		for axis in ['x', 'y', 'z']:
			if self.__getattribute__('is_lin_' + axis):
				rigid_const.__setattr__('use_limit_lin_' + axis, True)
				rigid_const.__setattr__('limit_lin_' + axis + '_lower', 0.0)
				rigid_const.__setattr__('limit_lin_' + axis + '_upper', 0.0)
			if self.__getattribute__('is_ang_' + axis):
				rigid_const.__setattr__('use_limit_ang_' + axis, True)
				rigid_const.__setattr__('limit_ang_' + axis + '_lower', 0.0)
				rigid_const.__setattr__('limit_ang_' + axis + '_upper', 0.0)
		return {'FINISHED'}

class ReverseConstraintLimits(bpy.types.Operator):
	bl_idname = "rigidbody.reverse_constraint_limits"
	bl_label = "Invert rigidbody constraints limits"
	bl_description = "Minimum limit settings of rigid constraints of active object and reverses maximum"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_lin_x = bpy.props.BoolProperty(name="X Move", default=False, options={'SKIP_SAVE'})
	is_lin_y = bpy.props.BoolProperty(name="Y Move", default=False, options={'SKIP_SAVE'})
	is_lin_z = bpy.props.BoolProperty(name="Z Move", default=False, options={'SKIP_SAVE'})
	
	is_ang_x = bpy.props.BoolProperty(name="X Rot", default=False, options={'SKIP_SAVE'})
	is_ang_y = bpy.props.BoolProperty(name="Y Rot", default=False, options={'SKIP_SAVE'})
	is_ang_z = bpy.props.BoolProperty(name="Z Rot", default=False, options={'SKIP_SAVE'})
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.rigid_body_constraint:
				return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.label("Invert Move Limit")
		row = self.layout.row()
		row.prop(self, 'is_lin_x', text="X")
		row.prop(self, 'is_lin_y', text="Y")
		row.prop(self, 'is_lin_z', text="Z")
		self.layout.label("Invert Rotate Limit")
		row = self.layout.row()
		row.prop(self, 'is_ang_x', text="X")
		row.prop(self, 'is_ang_y', text="Y")
		row.prop(self, 'is_ang_z', text="Z")
	
	def execute(self, context):
		rigid_const = context.active_object.rigid_body_constraint
		for axis in ['x', 'y', 'z']:
			if self.__getattribute__('is_lin_' + axis):
				lower = rigid_const.__getattribute__('limit_lin_' + axis + '_lower')
				upper = rigid_const.__getattribute__('limit_lin_' + axis + '_upper')
				rigid_const.__setattr__('limit_lin_' + axis + '_lower', -upper)
				rigid_const.__setattr__('limit_lin_' + axis + '_upper', -lower)
			if self.__getattribute__('is_ang_' + axis):
				lower = rigid_const.__getattribute__('limit_ang_' + axis + '_lower')
				upper = rigid_const.__getattribute__('limit_ang_' + axis + '_upper')
				rigid_const.__setattr__('limit_ang_' + axis + '_lower', -upper)
				rigid_const.__setattr__('limit_ang_' + axis + '_upper', -lower)
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
		if context.active_object:
			if context.active_object.rigid_body_constraint:
				if context.active_object.rigid_body_constraint.type in ['GENERIC', 'GENERIC_SPRING']:
					row = self.layout.row(align=True)
					row.operator(ClearConstraintLimits.bl_idname, icon='X', text="Limit Clear")
					row.operator(ReverseConstraintLimits.bl_idname, icon='ARROW_LEFTRIGHT', text="Limit Reverse")
				elif context.active_object.rigid_body_constraint.type == 'FIXED':
					row = self.layout.row(align=True)
					row.operator(ClearConstraintLimits.bl_idname, icon='IPO_LINEAR', text="Initialize Generic").mode = 'GENERIC'
					row.operator(ClearConstraintLimits.bl_idname, icon='DRIVER', text="Initialize Generic Spring").mode = 'GENERIC_SPRING'
		row = self.layout.row(align=True)
		op = row.operator('wm.context_set_string', icon='SCENE_DATA', text="")
		op.data_path = 'space_data.context'
		op.value = 'SCENE'
		row.operator(CopyConstraintSetting.bl_idname, icon='LINKED')
		if context.scene.rigidbody_world:
			if context.scene.rigidbody_world.point_cache:
				row = self.layout.row(align=True)
				row.prop(context.scene.rigidbody_world.point_cache, 'frame_start')
				row.prop(context.scene.rigidbody_world.point_cache, 'frame_end')
				row.operator('rigidbody.sync_frames', icon='LINKED', text="")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
