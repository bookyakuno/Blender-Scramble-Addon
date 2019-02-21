# 「3Dビュー」エリア > 「アーマチュア編集」モード > 「W」キー
# "3D View" Area > "Armature Editor" Mode > "W" Key

import bpy, mathutils
import re

################
# オペレーター #
################

class CreateMirror(bpy.types.Operator):
	bl_idname = "armature.create_mirror"
	bl_label = "Select Bones Mirroring"
	bl_description = "Mirrored at any axes selected bone"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "EDIT"):
				preCursorCo = context.space_data.cursor_location[:]
				prePivotPoint = context.space_data.pivot_point
				preUseMirror = context.object.data.use_mirror_x
				
				context.space_data.cursor_location = (0, 0, 0)
				context.space_data.pivot_point = 'CURSOR'
				context.object.data.use_mirror_x = True
				
				selectedBones = context.selected_bones[:]
				bpy.ops.armature.autoside_names(type='XAXIS')
				bpy.ops.armature.duplicate()
				axis = (True, False, False)
				bpy.ops.transform.mirror(constraint_axis=axis)
				bpy.ops.armature.flip_names()
				newBones = []
				for bone in context.selected_bones:
					for pre in selectedBones:
						if (bone.name == pre.name):
							break
					else:
						newBones.append(bone)
				bpy.ops.armature.select_all(action='DESELECT')
				for bone in selectedBones:
					bone.select = True
					bone.select_head = True
					bone.select_tail = True
				bpy.ops.transform.transform(mode='BONE_ROLL', value=(0, 0, 0, 0))
				bpy.ops.armature.select_all(action='DESELECT')
				for bone in newBones:
					bone.select = True
					bone.select_head = True
					bone.select_tail = True
				
				context.space_data.cursor_location = preCursorCo[:]
				context.space_data.pivot_point = prePivotPoint
				context.object.data.use_mirror_x = preUseMirror
			else:
				self.report(type={"ERROR"}, message="Please run in edit mode")
		else:
			self.report(type={"ERROR"}, message="Not an armature object")
		return {'FINISHED'}

class CopyBoneName(bpy.types.Operator):
	bl_idname = "armature.copy_bone_name"
	bl_label = "Bone name to Clipboard"
	bl_description = "Copies Clipboard name of active bone"
	bl_options = {'REGISTER', 'UNDO'}
	
	isObject = bpy.props.BoolProperty(name="And Object Name", default=False)
	
	def execute(self, context):
		if (self.isObject):
			context.window_manager.clipboard = context.active_object.name + ":" + context.active_bone.name
		else:
			context.window_manager.clipboard = context.active_bone.name
		return {'FINISHED'}

class RenameBoneRegularExpression(bpy.types.Operator):
	bl_idname = "armature.rename_bone_regular_expression"
	bl_label = "Replace bone names by regular expression"
	bl_description = "In bone name (of choice) to match regular expression replace"
	bl_options = {'REGISTER', 'UNDO'}
	
	isAll = bpy.props.BoolProperty(name="Include Non-select", default=False)
	pattern = bpy.props.StringProperty(name="Before replace (regular expressions)", default="^")
	repl = bpy.props.StringProperty(name="After", default="@")
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "EDIT"):
				bones = context.selected_bones
				if (self.isAll):
					bones = obj.data.bones
				for bone in bones:
					try:
						new_name = re.sub(self.pattern, self.repl, bone.name)
					except:
						continue
					bone.name = new_name
			else:
				self.report(type={"ERROR"}, message="Please run in edit mode")
		else:
			self.report(type={"ERROR"}, message="Not an armature object")
		return {'FINISHED'}

class RenameOppositeBone(bpy.types.Operator):
	bl_idname = "armature.rename_opposite_bone"
	bl_label = "Rename bone symmetry position"
	bl_description = "Bone is located opposite X axis selection in bone \"1.R longs 1.L \' of so versus the"
	bl_options = {'REGISTER', 'UNDO'}
	
	threshold = bpy.props.FloatProperty(name="Position of Threshold", default=0.00001, min=0, soft_min=0, step=0.001, precision=5)
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "EDIT"):
				arm = obj.data
				bpy.ops.armature.autoside_names(type='XAXIS')
				selectedBones = context.selected_bones[:]
				bpy.ops.armature.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
				threshold = self.threshold
				for bone in selectedBones:
					bone = arm.bones[bone.name]
					head = (-bone.head_local[0], bone.head_local[1], bone.head_local[2])
					tail = (-bone.tail_local[0], bone.tail_local[1], bone.tail_local[2])
					for b in arm.bones:
						if ( (head[0]-threshold) <= b.head_local[0] <= (head[0]+threshold)):
							if ( (head[1]-threshold) <= b.head_local[1] <= (head[1]+threshold)):
								if ( (head[2]-threshold) <= b.head_local[2] <= (head[2]+threshold)):
									if ( (tail[0]-threshold) <= b.tail_local[0] <= (tail[0]+threshold)):
										if ( (tail[1]-threshold) <= b.tail_local[1] <= (tail[1]+threshold)):
											if ( (tail[2]-threshold) <= b.tail_local[2] <= (tail[2]+threshold)):
												b.name = bone.name
												b.select = True
												b.select_head = True
												b.select_tail = True
												break
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.armature.flip_names()
			else:
				self.report(type={"ERROR"}, message="Please run in edit mode")
		else:
			self.report(type={"ERROR"}, message="Not an armature object")
		return {'FINISHED'}
		return {'FINISHED'}

class extend_bone(bpy.types.Operator):
	bl_idname = "armature.extend_bone"
	bl_label = "Extend Bone"
	bl_description = "Stretch new bone in direction of selected bone"
	bl_options = {'REGISTER', 'UNDO'}
	
	length = bpy.props.FloatProperty(name="Length", default=0.1, min=-10, max=10, soft_min=-10, soft_max=10, step=10, precision=3)
	is_parent = bpy.props.BoolProperty(name="Source Parent", default=True)
	is_connect = bpy.props.BoolProperty(name="Connection", default=True)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if 'selected_bones' in dir(context):
					if context.selected_bones:
						if 1 <= len(context.selected_bones):
							return True
		return False
	
	def execute(self, context):
		ob = context.active_object
		arm = ob.data
		for bone in context.selected_bones[:]:
			new_bone = arm.edit_bones.new(bone.name)
			new_bone.head = bone.tail[:]
			rot = bone.matrix.to_quaternion()
			tail = mathutils.Vector((0, 1, 0)) * self.length
			tail.rotate(rot)
			new_bone.tail = bone.tail + tail
			new_bone.roll = bone.roll
			if self.is_parent:
				new_bone.parent = bone
			if self.is_connect:
				new_bone.use_connect = True
			bone.select = False
			bone.select_head = False
			if bone.use_connect:
				bone.parent.select_tail = False
			if self.is_connect:
				bone.select_tail = True
			new_bone.select = True
			new_bone.select_head = True
			new_bone.select_tail = True
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
		self.layout.separator()
		self.layout.operator(extend_bone.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.prop(context.object.data, 'use_mirror_x', icon='PLUGIN', text="X axis mirror edit")
		self.layout.operator(CreateMirror.bl_idname, icon='PLUGIN')
		self.layout.operator(RenameOppositeBone.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(CopyBoneName.bl_idname, icon='PLUGIN')
		self.layout.operator(RenameBoneRegularExpression.bl_idname, icon='PLUGIN')
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
