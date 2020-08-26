# 「3Dビュー」エリア > 「ポーズ」モード > 「選択」メニュー
# "3D View" Area > "Pose" Mode > "Select" Menu

import bpy
import re

################
# オペレーター #
################

class SelectSerialNumberNameBone(bpy.types.Operator):
	bl_idname = "pose.select_serial_number_name_bone"
	bl_label = "Select Numbered Bone"
	bl_description = "Select bones with number names (example x.001)"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.visible_bones:
					bones = context.visible_bones[:]
				if context.visible_pose_bones:
					bones = context.visible_pose_bones[:]
				for bone in bones:
					if re.search(r'\.\d+$', bone.name):
						return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		for bone in context.visible_pose_bones[:]:
			if (re.search(r'\.\d+$', bone.name)):
				arm.bones[bone.name].select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectMoveSymmetryNameBones(bpy.types.Operator):
	bl_idname = "pose.select_move_symmetry_name_bones"
	bl_label = "Symmetrical bones move select"
	bl_description = "If you select X.R change selection to X.L, X.L if to X.R"
	bl_options = {'REGISTER', 'UNDO'}
	
	def GetMirrorBoneName(self, name):
		new_name = re.sub(r'([\._])L$', r"\1R", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])l$', r"\1r", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])R$', r"\1L", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])r$', r"\1l", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])L([\._]\d+)$', r"\1R\2", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])l([\._]\d+)$', r"\1r\2", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])R([\._]\d+)$', r"\1L\2", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])r([\._]\d+)$', r"\1l\2", name)
		if (new_name != name): return new_name
		return name
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.selected_bones:
					bones = context.selected_bones[:]
				if context.selected_pose_bones:
					bones = context.selected_pose_bones[:]
				for bone in bones:
					mirror_name = cls.GetMirrorBoneName(cls, bone.name)
					if mirror_name != bone.name:
						try:
							ob.data.bones[mirror_name]
							return True
						except KeyError:
							pass
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		for bone in context.selected_pose_bones[:]:
			mirror_name = self.GetMirrorBoneName(bone.name)
			if (mirror_name == bone.name):
				self.report(type={'WARNING'}, message="Ignored " + bone.name)
				continue
			try:
				mirror_bone = arm.bones[mirror_name]
			except KeyError:
				self.report(type={'WARNING'}, message="Ignored " + bone.name)
				continue
			mirror_bone.select = True
			arm.bones[bone.name].select = False
			arm.bones[bone.name].select_head = False
			arm.bones[bone.name].select_tail = False
		try:
			arm.bones.active = arm.bones[self.GetMirrorBoneName(arm.bones.active.name)]
		except KeyError:
			arm.bones.active = arm.bones[context.selected_pose_bones[0].name]
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectSameConstraintBone(bpy.types.Operator):
	bl_idname = "pose.select_same_constraint_bone"
	bl_label = "Select bone same constraints"
	bl_description = "Select additional bone with active bone and same kind of constraint"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.selected_bones:
					bones = context.selected_bones[:]
				if context.selected_pose_bones:
					bones = context.selected_pose_bones[:]
				for bone in bones:
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		active_bone = context.active_pose_bone
		active_consts = []
		for const in active_bone.constraints:
			active_consts.append(const.type)
		for bone in context.visible_pose_bones:
			constraints = []
			for const in bone.constraints:
				constraints.append(const.type)
			if (active_consts == constraints):
				arm.bones[bone.name].select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectSameNameBones(bpy.types.Operator):
	bl_idname = "pose.select_same_name_bones"
	bl_label = "Select bone of same name"
	bl_description = "Select bones same names (example X X.001 X.002)"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.selected_bones:
					bones = context.selected_bones[:]
				if context.selected_pose_bones:
					bones = context.selected_pose_bones[:]
				for bone in bones:
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		name_base = context.active_pose_bone.name
		name_base = re.sub(r'\.\d+$', "", name_base)
		for bone in context.visible_pose_bones[:]:
			r = r'^' + name_base + r'\.\d+$'
			if (re.search(r, bone.name) or name_base == bone.name):
				arm.bones[bone.name].select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectSymmetryNameBones(bpy.types.Operator):
	bl_idname = "pose.select_symmetry_name_bones"
	bl_label = "Select add name symmetrical bone"
	bl_description = "If you select X.R X.L also selected X.R X.L you select additional"
	bl_options = {'REGISTER', 'UNDO'}
	
	def GetMirrorBoneName(self, name):
		new_name = re.sub(r'([\._])L$', r"\1R", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])l$', r"\1r", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])R$', r"\1L", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])r$', r"\1l", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])L([\._]\d+)$', r"\1R\2", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])l([\._]\d+)$', r"\1r\2", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])R([\._]\d+)$', r"\1L\2", name)
		if (new_name != name): return new_name
		new_name = re.sub(r'([\._])r([\._]\d+)$', r"\1l\2", name)
		if (new_name != name): return new_name
		return name
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.selected_bones:
					bones = context.selected_bones[:]
				if context.selected_pose_bones:
					bones = context.selected_pose_bones[:]
				for bone in bones:
					mirror_name = cls.GetMirrorBoneName(cls, bone.name)
					if mirror_name != bone.name:
						try:
							ob.data.bones[mirror_name]
							return True
						except KeyError:
							pass
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		for bone in context.selected_pose_bones[:]:
			mirror_name = self.GetMirrorBoneName(bone.name)
			if (mirror_name == bone.name):
				self.report(type={'WARNING'}, message="Ignored " + bone.name)
				continue
			try:
				arm.bones[mirror_name]
			except KeyError:
				self.report(type={'WARNING'}, message="Ignored " + bone.name)
				continue
			arm.bones[mirror_name].select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectChildrenEnd(bpy.types.Operator):
	bl_idname = "pose.select_children_end"
	bl_label = "Select end of bone"
	bl_description = "Select bones child-child child\'s bones. And we will select to end"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.selected_bones:
					bones = context.selected_bones[:]
				if context.selected_pose_bones:
					bones = context.selected_pose_bones[:]
				for bone in bones:
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		for bone in context.selected_pose_bones[:]:
			bone_children = []
			for b in arm.bones[bone.name].children[:]:
				bone_children.append(b)
			bone_queue = bone_children[:]
			while (0 < len(bone_queue)):
				removed_bone = bone_queue.pop(0)
				for b in removed_bone.children[:]:
					bone_queue.append(b)
					bone_children.append(b)
			for b in bone_children:
				b.select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectParentEnd(bpy.types.Operator):
	bl_idname = "pose.select_parent_end"
	bl_label = "Select root of bone"
	bl_description = "Choice bones parent => parent of parent bone. And we will select to end"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.selected_bones:
					bones = context.selected_bones[:]
				if context.selected_pose_bones:
					bones = context.selected_pose_bones[:]
				for bone in bones:
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		for bone in context.selected_pose_bones[:]:
			target_bone = arm.bones[bone.name]
			while target_bone.parent:
				target_bone = target_bone.parent
				target_bone.select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectPath(bpy.types.Operator):
	bl_idname = "pose.select_path"
	bl_label = "Select path of bones"
	bl_description = "Select bones path"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		bones = []
		if (context.selected_bones):
			if (2 == len(context.selected_bones)):
				bones = context.selected_bones
		if (context.selected_pose_bones):
			if (2 == len(context.selected_pose_bones)):
				bones = context.selected_pose_bones
		if (2 == len(bones)):
			parents = []
			for bone in bones:
				parents.append(bone)
				while (parents[-1].parent):
					parents[-1] = parents[-1].parent
			if (parents[0].name == parents[1].name):
				return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		pose = obj.pose
		arm = obj.data
		parents = []
		pre_mode = obj.mode
		if (obj.mode == 'EDIT'):
			bones = context.selected_bones
		else:
			bones = context.selected_pose_bones
		for bone in bones:
			parents.append([bone.name])
			while (pose.bones[parents[-1][-1]].parent):
				parents[-1].append(pose.bones[parents[-1][-1]].parent.name)
		bpy.ops.object.mode_set(mode='OBJECT')
		for bone_name in set(parents[0]) ^ set(parents[1]):
			arm.bones[bone_name].select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectAxisOver(bpy.types.Operator):
	bl_idname = "pose.select_axis_over"
	bl_label = "Select Right Half"
	bl_description = "Select right half of bone (other settings are also available)"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('0', "X", "", 1),
		('1', "Y", "", 2),
		('2', "Z", "", 3),
		]
	axis = bpy.props.EnumProperty(items=items, name="Axis")
	items = [
		('-1', "-(Minus)", "", 1),
		('1', "+(Plus)", "", 2),
		]
	direction = bpy.props.EnumProperty(items=items, name="Direction")
	offset = bpy.props.FloatProperty(name="Offset", default=0, step=10, precision=3)
	threshold = bpy.props.FloatProperty(name="Threshold", default=-0.0001, step=0.01, precision=4)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				bones = []
				if context.visible_bones:
					bones = context.visible_bones[:]
				if context.visible_pose_bones:
					bones = context.visible_pose_bones[:]
				for bone in bones:
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='POSE')
		direction = int(self.direction)
		offset = self.offset
		threshold = self.threshold
		for pbone in context.visible_pose_bones[:]:
			bone = arm.bones[pbone.name]
			hLoc = bone.head_local[int(self.axis)]
			tLoc = bone.tail_local[int(self.axis)]
			if (offset * direction <= hLoc * direction + threshold):
				bone.select = True
			if (offset * direction <= tLoc * direction + threshold):
				bone.select = True
		return {'FINISHED'}

################################
# ショートカット用オペレーター #
################################

class SelectOneAndPath(bpy.types.Operator):
	bl_idname = "pose.select_one_and_path"
	bl_label = "Select bone and path"
	bl_description = "Select path to it, select cursor part bone and"
	bl_options = {'REGISTER', 'UNDO'}
	
	mouse_pos = bpy.props.IntVectorProperty(name="Mouse Position", size=2, options={'HIDDEN'})
	
	@classmethod
	def poll(cls, context):
		bones = []
		if context.selected_bones:
			if len(context.selected_bones):
				return True
		if context.selected_pose_bones:
			if len(context.selected_pose_bones):
				return True
		return False
	
	def invoke(self, context, event):
		self.mouse_pos = event.mouse_region_x, event.mouse_region_y
		return self.execute(context)
	
	def execute(self, context):
		obj = context.active_object
		pose = obj.pose
		arm = obj.data
		parents = []
		pre_mode = obj.mode
		if obj.mode == 'EDIT':
			bones = [context.active_bone]
		else:
			bones = [context.active_pose_bone]
		bpy.ops.view3d.select(location=self.mouse_pos, extend=True)
		if obj.mode == 'EDIT':
			bones.append(context.active_bone)
		else:
			bones.append(context.active_pose_bone)
		if bones[0].name == bones[1].name:
			return {'CANCELLED'}
		for bone in bones:
			parents.append([bone.name])
			while (pose.bones[parents[-1][-1]].parent):
				parents[-1].append(pose.bones[parents[-1][-1]].parent.name)
		bpy.ops.object.mode_set(mode='OBJECT')
		for bone_name in set(parents[0]) ^ set(parents[1]):
			arm.bones[bone_name].select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# サブメニュー #
################

class SelectGroupedMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_pose_grouped"
	bl_label = "Select by relation (Extra)"
	bl_description = "Ability to select all visible bones together with same properties menu"
	
	def draw(self, context):
		self.layout.operator('pose.select_grouped', text="Layer", icon='PLUGIN').type = 'LAYER'
		self.layout.operator('pose.select_grouped', text="Group", icon='PLUGIN').type = 'GROUP'
		self.layout.operator('pose.select_grouped', text="Keying Set", icon='PLUGIN').type = 'KEYINGSET'
		self.layout.separator()
		self.layout.operator(SelectSameNameBones.bl_idname, text="Bone Name", icon='PLUGIN')
		self.layout.operator(SelectSymmetryNameBones.bl_idname, text="Mirror Name", icon='PLUGIN')
		self.layout.operator(SelectSameConstraintBone.bl_idname, text="Constraints", icon='PLUGIN')

class ShortcutsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_pose_shortcuts"
	bl_label = "By Shortcuts"
	bl_description = "Registering shortcut feature that might come in handy"
	
	def draw(self, context):
		self.layout.operator(SelectOneAndPath.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	SelectSerialNumberNameBone,
	SelectMoveSymmetryNameBones,
	SelectSameConstraintBone,
	SelectSameNameBones,
	SelectSymmetryNameBones,
	SelectChildrenEnd,
	SelectParentEnd,
	SelectPath,
	SelectAxisOver,
	SelectOneAndPath,
	SelectGroupedMenu,
	ShortcutsMenu
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
	for id in bpy.context.preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator('pose.select_path', icon='PLUGIN')
		self.layout.operator('pose.select_parent_end', icon='PLUGIN')
		self.layout.operator('pose.select_children_end', icon='PLUGIN')
		self.layout.separator()
		self.layout.operator('pose.select_axis_over', icon='PLUGIN')
		self.layout.operator('pose.select_serial_number_name_bone', icon='PLUGIN')
		self.layout.operator('pose.select_move_symmetry_name_bones', icon='PLUGIN')
		self.layout.separator()
		self.layout.menu('VIEW3D_MT_select_pose_grouped', icon='PLUGIN')
		self.layout.separator()
		self.layout.menu('VIEW3D_MT_select_pose_shortcuts', icon='PLUGIN')
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
