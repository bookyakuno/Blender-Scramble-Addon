# 「3Dビュー」エリア > 「ポーズ」モード > 「選択」メニュー
# "3D View" Area > "Pose" Mode > "Select" Menu

import bpy
import re
from bpy.props import *

################
# オペレーター #
################

class SelectSerialNumberNameBone(bpy.types.Operator):
	bl_idname = "pose.select_serial_number_name_bone"
	bl_label = "Select Bone (Dot-Number)"
	bl_description = "Select bones which names end with dot-number"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.visible_bones or context.visible_pose_bones:
				return True
		return False

	def execute(self, context):
		if context.active_object.mode == 'POSE':
			for bone in context.visible_pose_bones:
				if (re.search(r'\.\d+$', bone.name)):
					bone.bone.select = True
		elif context.active_object.mode == 'EDIT':
			for bone in context.visible_bones:
				if (re.search(r'\.\d+$', bone.name)):
					bone.select = True
		return {'FINISHED'}

class SelectMoveSymmetryNameBones(bpy.types.Operator):
	bl_idname = "pose.select_move_symmetry_name_bones"
	bl_label = "Select Bones (Flipped-Name)"
	bl_description = "Select bones which have left-right-flipped name of currently selected"
	bl_options = {'REGISTER', 'UNDO'}

	keep_current : BoolProperty(name="Keep Selection", default=True)

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.selected_bones or context.selected_pose_bones:
				return True
		return False

	def execute(self, context):
		arma_bones = context.active_object.data.bones
		pre_active = arma_bones.active
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='POSE')
		selected = context.selected_pose_bones[:]
		symmetrical = []
		pre_names = [b.name for b in selected]
		bpy.ops.pose.flip_names(do_strip_numbers=False)
		for bone, pre_name in zip(selected, pre_names):
			bpy.ops.pose.select_all(action='DESELECT')
			if len(bone.name) > len(pre_name):
				if not re.search(r'([\._-]\d+?)$', bone.name):
					flipped_name = None
				else:
					flipped_name = re.search(r'(.+)([\._-]\d+?)$', bone.name).group(1)
			elif len(bone.name) == len(pre_name):
				if not re.search(r'([\._-]\d+?)$', bone.name):
					flipped_name = None
				else:
					diffs = [a==b for a, b in zip(pre_name, bone.name)]
					if (diffs[-1]==False) and (diffs[-2]==True):
						flipped_name = bone.name[:-1]+pre_name[-1]
					elif (diffs[-1]==False) and (diffs[-2]==False):
						flipped_name = bone.name[:-2]+pre_name[-2:]
					else:
						flipped_name = None
			else:
				flipped_name = None
			if not flipped_name:
				self.report(type={'WARNING'}, message="Ignored " + pre_name)
				bone.name = pre_name
				continue
			try:
				target_b = context.active_object.pose.bones[flipped_name]
				symmetrical.append(target_b)
			except KeyError:
				self.report(type={'WARNING'}, message="Ignored " + pre_name)
			bone.name = pre_name
		bpy.ops.pose.select_all(action='DESELECT')
		for b in symmetrical:
			b.bone.select = True
		if self.keep_current:
			for b in selected:
				b.bone.select = True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectSameConstraintBone(bpy.types.Operator):
	bl_idname = "pose.select_same_constraint_bone"
	bl_label = "Select Bones (Constraint)"
	bl_description = "Select bones which have same constraints as active bone"
	bl_options = {'REGISTER', 'UNDO'}

	all_same : BoolProperty(name="Exactly Same", default=False, options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_pose_bone:
				return True
		return False

	def execute(self, context):
		active_consts = [c.type for c in context.active_pose_bone.constraints]
		for bone in context.visible_pose_bones:
			bone_consts = [c.type for c in bone.constraints]
			if self.all_same:
				if set(active_consts) == set(bone_consts):
					bone.bone.select = True
			else:
				if set(active_consts) & set(bone_consts):
					bone.bone.select = True
		return {'FINISHED'}

class SelectSameNameBones(bpy.types.Operator):
	bl_idname = "pose.select_same_name_bones"
	bl_label = "Select Bones (Sharing Name)"
	bl_description = "Select bones which names are same as active bone except dot-number and left-right suffix"
	bl_options = {'REGISTER', 'UNDO'}

	method : EnumProperty(name="Method", items=[
		("BOTH","Exclude number & suffix","",1),("SUFF","Exclude only suffix","",2),("NUMB","Exclude only dot-number","",3)])

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_bone or context.active_pose_bone:
				return True
		return False

	def execute(self, context):
		arma_bones = context.active_object.data.bones
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='POSE')
		bone = context.active_pose_bone
		pre_name = bone.name
		if self.method in ['BOTH', 'SUFF']:
			bpy.ops.pose.flip_names(do_strip_numbers=False)
			diffs = [a==b for a, b in zip(pre_name, bone.name)]
			try:
				first_diff = diffs.index(False)
				if pre_name[first_diff-1] in ['.','_','-']:
					base_name = pre_name[:first_diff-1]
				else:
					base_name = pre_name[:first_diff]
			except ValueError:
				base_name = pre_name
			bone.name = pre_name
			print(base_name)
		else:
			base_name = pre_name
		if self.method in ['BOTH', 'NUMB']:
			if re.search(r'(.+)([\._-]\d+?)$', base_name):
				base_name = re.search(r'(.+)([\._-]\d+?)$', base_name).group(1)
			print(base_name)
		results = [b for b in arma_bones if b.name.startswith(base_name)]
		bpy.ops.pose.select_all(action='DESELECT')
		for b in results:
			b.select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectChildrenEnd(bpy.types.Operator):
	bl_idname = "pose.select_children_end"
	bl_label = "Select Bones (All Children)"
	bl_description = "Select all children of selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	to_fork : BoolProperty(name="To fork-point", default=False)

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.selected_bones or context.selected_pose_bones:
				return True
		return False

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='EDIT')
		if self.to_fork:
			for bone in context.selected_bones:
				for b in bone.children_recursive:
					b.select = True
					if len(b.children) >= 2:
						break
		else:
			bpy.ops.armature.select_similar(type='CHILDREN')
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectParentEnd(bpy.types.Operator):
	bl_idname = "pose.select_parent_end"
	bl_label = "Select Bones (All Parent)"
	bl_description = "Select all parents of selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	to_fork : BoolProperty(name="To fork-point", default=False)

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.selected_bones or context.selected_pose_bones:
				return True
		return False

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='EDIT')
		for bone in context.selected_bones:
			for b in bone.parent_recursive:
				if self.to_fork and len(b.children) >= 2:
					break
				b.select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectBothEnd(bpy.types.Operator):
	bl_idname = "pose.select_both_end"
	bl_label = "Select Bones (All Parent & Children)"
	bl_description = "Select all parents and children of selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	to_fork : BoolProperty(name="To fork-point", default=False)

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.selected_bones or context.selected_pose_bones:
				return True
		return False

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.pose.select_children_end(to_fork=self.to_fork)
		bpy.ops.pose.select_parent_end(to_fork=self.to_fork)
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectPath(bpy.types.Operator):
	bl_idname = "pose.select_path"
	bl_label = "Select Bones (Between Two)"
	bl_description = "Select bones which exist between two selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.selected_bones and len(context.selected_bones) == 2:
				return True
			if context.selected_pose_bones and len(context.selected_pose_bones) == 2:
				return True
		return False

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='EDIT')
		chils = [b.children_recursive for b in context.selected_bones]
		children_s = set(chils[0] + chils[1])
		pares = [b.parent_recursive for b in context.selected_bones]
		parents_s = set(pares[0] + pares[1])
		betweens = list(children_s & parents_s)
		if not betweens:
			bpy.ops.object.mode_set(mode=pre_mode)
			return {'CANCELLED'}
		else:
			for bone in betweens:
				bone.select = True
			bpy.ops.object.mode_set(mode=pre_mode)
			return {'FINISHED'}

class SelectAxisOver(bpy.types.Operator):
	bl_idname = "pose.select_axis_over"
	bl_label = "Select Bones (Right Side)"
	bl_description = "Select bones on right side"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('0', "X", "", 1),
		('1', "Y", "", 2),
		('2', "Z", "", 3),
		]
	axis : EnumProperty(items=items, name="Axis")
	direction : EnumProperty(name="Direction", items=[
		("1", "Right / Top", "", 2),("-1", "Left / Bottom", "", 1)])
	offset : FloatProperty(name="Offset", default=0, step=10, precision=3)
	threshold : FloatProperty(name="Threshold", default=-0.0001, step=0.01, precision=4)

	@classmethod
	def poll(cls, context):
		if context.visible_bones or context.visible_pose_bones:
			return True
		return False

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='POSE')
		direction = int(self.direction)
		offset = self.offset
		threshold = self.threshold
		for pbone in context.visible_pose_bones[:]:
			bone = context.active_object.data.bones[pbone.name]
			hLoc = bone.head_local[int(self.axis)]
			tLoc = bone.tail_local[int(self.axis)]
			if (offset * direction <= hLoc * direction + threshold):
				bone.select = True
			if (offset * direction <= tLoc * direction + threshold):
				bone.select = True
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SelectSimilarForPose(bpy.types.Operator):
	bl_idname = "pose.select_similar_for_pose"
	bl_label = "Select Similar Bones"
	bl_description = "Select similar bones by property types"
	bl_options = {'REGISTER', 'UNDO'}

	selection_type : StringProperty(name="Type", default="", options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_pose_bone:
				return True
		return False

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.armature.select_similar(type=self.selection_type)
		bpy.ops.object.mode_set(mode='POSE')
		return {'FINISHED'}

################################
# ショートカット用オペレーター #
################################

class SelectOneAndPath(bpy.types.Operator):
	bl_idname = "pose.select_one_and_path"
	bl_label = "Select Bones to Cursor"
	bl_description = "Select bones which exist between selected bones and cursor position"
	bl_options = {'REGISTER', 'UNDO'}

	mouse_pos : IntVectorProperty(name="Mouse Position", size=2, options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		if context.selected_bones or context.selected_pose_bones:
			return True
		return False
	def invoke(self, context, event):
		self.mouse_pos = event.mouse_region_x, event.mouse_region_y
		return self.execute(context)

	def execute(self, context):
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.view3d.select(location=self.mouse_pos, extend=True)
		if len(context.selected_bones) == 1:
			return {'CANCELLED'}
		chils = [b.children_recursive for b in context.selected_bones]
		children_s = set(sum(chils, []))
		pares = [b.parent_recursive for b in context.selected_bones]
		parents_s = set(sum(pares, []))
		betweens = list(children_s & parents_s)
		if not betweens:
			bpy.ops.object.mode_set(mode=pre_mode)
			return {'CANCELLED'}
		else:
			for bone in betweens:
				bone.select = True
			bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# サブメニュー #
################

class SelectGroupedMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_pose_grouped"
	bl_label = "Grouped (Extra)"

	def draw(self, context):
		self.layout.operator('pose.select_grouped', text="Layer", icon='PLUGIN').type = 'LAYER'
		self.layout.operator('pose.select_grouped', text="Group", icon='PLUGIN').type = 'GROUP'
		self.layout.operator('pose.select_grouped', text="Keying Set", icon='PLUGIN').type = 'KEYINGSET'
		self.layout.separator()
		self.layout.operator(SelectSameNameBones.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectMoveSymmetryNameBones.bl_idname, icon='PLUGIN').keep_current = True
		self.layout.operator(SelectSameConstraintBone.bl_idname, icon='PLUGIN').all_same = False
		self.layout.operator(SelectSameConstraintBone.bl_idname, text="Select Bones (All Constraints)", icon='PLUGIN').all_same = True

class SelectSimilarForPoseMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_similar_for_pose"
	bl_label = "Similar"

	def draw(self, context):
		for item in bpy.ops.armature.select_similar.get_rna_type().properties["type"].enum_items:
			self.layout.operator(SelectSimilarForPose.bl_idname, text=item.name).selection_type = item.identifier

################
# クラスの登録 #
################

classes = [
	SelectSerialNumberNameBone,
	SelectMoveSymmetryNameBones,
	SelectSameConstraintBone,
	SelectSameNameBones,
	SelectChildrenEnd,
	SelectParentEnd,
	SelectBothEnd,
	SelectPath,
	SelectAxisOver,
	SelectSimilarForPose,
	SelectOneAndPath,
	SelectGroupedMenu,
	SelectSimilarForPoseMenu
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
		if context.mode == 'POSE':
			self.layout.separator()
			self.layout.menu(SelectSimilarForPoseMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SelectPath.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectParentEnd.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectChildrenEnd.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectBothEnd.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SelectAxisOver.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectSerialNumberNameBone.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectMoveSymmetryNameBones.bl_idname, icon='PLUGIN').keep_current = True
		self.layout.separator()
		self.layout.operator(SelectMoveSymmetryNameBones.bl_idname, text="Change Selection (Flipped-Name)", icon='PLUGIN').keep_current = False
		self.layout.menu(SelectGroupedMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SelectOneAndPath.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
