# 「3Dビュー」エリア > 「アーマチュア編集」モード > 「W」キー
# "3D View" Area > "Armature Editor" Mode > "W" Key

import bpy, mathutils
import re
from bpy.props import *

SUFFIX_TPL = (".R",".L",".r",".l","_R","_L","_r","_l",".right",".left",".Right",".Left","_right","_left","_Right","_Left")

################
# オペレーター #
################

class CreateMirror(bpy.types.Operator):
	bl_idname = "armature.create_mirror"
	bl_label = "Add Suffix + Symmetrize"
	bl_description = "Add left-right suffix to selected bones' names, and make their copies at the symmetric positions"
	bl_options = {'REGISTER', 'UNDO'}

	is_connect : BoolProperty(name="Copy 'Connected'", default=True)
	use_autoname : BoolProperty(name="Add Suffix", default=True)
	use_rename : BoolProperty(name="Rename", default=False)
	new_name : StringProperty(name="New Name", default="Bone")
	name_sep : EnumProperty(name="Numbering Expression",items=[
		(".",".00X","",1),("_","_00X","",2),("-","-00X","",3)])
	start_from : EnumProperty(name="Numbering Starts from",items=[
		("NO","No number","",1),("ZERO","000","",2),("ONE","001","",3)])

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if ob.mode == "EDIT":
					return True
		return False
	def draw(self, context):
		for p in ['is_connect', 'use_autoname', 'use_rename']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p)
		box = self.layout.box()
		if self.use_rename:
			row = box.row(align=True)
			row.label(text="New Name")
			row.prop(self, 'new_name', text="")
			row.prop(self, 'name_sep', text="")
			row = box.row(align=True)
			row.label(text="Numbering Starts from")
			row.prop(self, 'start_from', text="")

	def execute(self, context):
		obj = context.active_object
		if self.use_rename:
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.mode_set(mode='EDIT')# 直前に行った名前変更が obj.data.bones に反映されていない場合への対処
		preCursorCo = context.scene.cursor.location[:]
		prePivotPoint = context.scene.tool_settings.transform_pivot_point
		preUseMirror = context.object.data.use_mirror_x
		context.scene.cursor.location = context.object.location
		context.scene.tool_settings.transform_pivot_point = 'CURSOR'
		context.object.data.use_mirror_x = True
		selectedBones = context.selected_bones[:]
		if self.use_rename:
			name_head = f"{self.new_name}{self.name_sep}"
			if self.start_from == 'NO':
				new_names = [self.new_name] + [f"{name_head}{num+1:03}" for num in range(len(selectedBones)-1)]
			elif self.start_from == 'ZERO':
				new_names = [f"{name_head}{num:03}" for num in range(len(selectedBones))]
			elif self.start_from == 'ONE':
				new_names = [f"{name_head}{num+1:03}" for num in range(len(selectedBones))]
			for b, nam in zip(selectedBones, new_names):
				try:
					existed_bone = obj.data.bones[nam]
					existed_bone.name = "temp"
					b.name = nam
					existed_bone.name = nam
				except KeyError:
					b.name = nam
		if self.use_autoname:
			for b in selectedBones:
				if b.name.endswith(SUFFIX_TPL):
					b.select = False
			bpy.ops.armature.autoside_names(type='XAXIS')
			for b in selectedBones:
				b.select = True
		bpy.ops.armature.duplicate(do_flip_names=True)
		axis = (True, False, False)
		bpy.ops.transform.mirror(constraint_axis=axis)
		newBones = set(context.selected_bones) - set(selectedBones)
		newBones = sorted(list(newBones), key=lambda x: x.name)
		selectedBones = sorted(selectedBones, key=lambda x: x.name)
		for orig, copy in zip(selectedBones, newBones):
			bpy.ops.armature.select_all(action='DESELECT')
			orig.select = orig.select_head = orig.select_tail = True
			bpy.ops.transform.transform(mode='BONE_ROLL', value=(0, 0, 0, 0))
			bpy.ops.armature.select_all(action='DESELECT')
			copy.select = copy.select_head = copy.select_tail = True
			if self.is_connect:
				copy.use_connect = orig.use_connect
		for b in newBones:
			b.select = b.select_head = b.select_tail = True
		context.scene.cursor.location = preCursorCo[:]
		context.scene.tool_settings.transform_pivot_point = prePivotPoint
		context.object.data.use_mirror_x = preUseMirror
		return {'FINISHED'}

class RenameBoneRegularExpression(bpy.types.Operator):
	bl_idname = "armature.rename_bone_regular_expression"
	bl_label = "Rename Bones by Regular Expression"
	bl_description = "Replace selected bones' names by using regular expression"
	bl_options = {'REGISTER', 'UNDO'}

	isAll : BoolProperty(name="Apply to All Bones", default=False)
	pattern : StringProperty(name="Target text", default="^")
	repl : StringProperty(name="New Text", default="")

	@classmethod
	def poll(cls, context):
		if context.active_object and context.active_object.type == 'ARMATURE':
			return True
		return False

	def execute(self, context):
		obj = context.active_object
		bones = context.selected_bones
		if not bones:
			bones = [b.bone for b in context.selected_pose_bones]
		if (self.isAll):
			bones = obj.data.bones
		for bone in bones:
			try:
				new_name = re.sub(self.pattern, self.repl, bone.name)
			except:
				continue
			bone.name = new_name
		return {'FINISHED'}

class RenameOppositeBone(bpy.types.Operator):
	bl_idname = "armature.rename_opposite_bone"
	bl_label = "Manipulate Symmetric Bones' Names"
	bl_description = "Change names of selected bones and its opposite-side ones in a specific way"
	bl_options = {'REGISTER', 'UNDO'}

	threshold : FloatProperty(name="Position of Threshold", default=0.00001, min=0, soft_min=0, step=0.001, precision=5)
	use_rename : EnumProperty(name="Manipulate",items=[
		("False","Add Suffix","",1),("True","Rename + Add Suffix","",2)])
	order : EnumProperty(name="Bones' Order",items=[
		("DEFAULT","Default","",1),("NAME","Sort by original name","",2)])
	use_root : BoolProperty(name="Use Root Bones' Names as New Names", default=False)
	new_name : StringProperty(name="New Name", default="Bone")
	name_sep : EnumProperty(name="Numbering Expression",items=[
		(".",".00X","",1),("_","_00X","",2),("-","-00X","",3)])
	start_from : EnumProperty(name="Numbering Starts from",items=[
		("NO","No number","",1),("ZERO","000","",2),("ONE","001","",3)])

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if ob.mode == "EDIT":
					return True
		return False
	def draw(self, context):
		row = self.layout.row()
		row.use_property_split = True
		row.prop(self, 'threshold')
		self.layout.prop(self, 'use_rename', expand=True)
		box = self.layout.box()
		if self.use_rename == 'True':
			row = box.row(align=True)
			row.label(text="Use Root Bones' Names as New Names")
			row.prop(self, 'use_root', text="")
			row = box.split(factor=0.4, align=True)
			row.label(text="Bones' Order")
			row.prop(self, 'order', text="")
			row.enabled = not self.use_root
			sp = box.split(factor=0.66, align=True)
			sp_row = sp.row(align=True)
			sp_row.label(text="New Name")
			sp_row.prop(self, 'new_name', text="")
			sp_row.enabled = not self.use_root
			sp.prop(self, 'name_sep', text="")
			row = box.row(align=True)
			row.label(text="Numbering Starts from")
			row.prop(self, 'start_from', text="")

	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		selectedBones = context.selected_bones[:]
		if self.use_rename:
			if self.use_root:
				roots = [b for b in selectedBones if (not b.parent) or (b.parent not in selectedBones)]
				root_names=[]
				for ro in roots:
					pre_name = ro.name
					bpy.ops.armature.select_all(action='DESELECT')
					ro.select = True
					bpy.ops.armature.flip_names(do_strip_numbers=True)
					for idx,(x,y) in enumerate(zip(pre_name, ro.name)):
						if not x == y:
							if pre_name[:idx][-1] in ['.','_','-']:
								root_names.append(pre_name[:idx-1])
							else:
								root_names.append(pre_name[:idx])
							ro.name = pre_name
							break
					else:
						root_names.append(pre_name)
				target_bones = []
				for b in roots:
					b_chain = [b] + b.children_recursive
					target_bones.append([b for b in b_chain if b in selectedBones])
			else:
				root_names = [self.new_name]
				if self.order == 'DEFAULT':
					target_bones = [selectedBones]
				elif self.order == 'NAME':
					target_bones = [sorted(selectedBones, key=lambda x:x.name)]
			for root_name, bone_list in zip(root_names, target_bones):
				name_head = f"{root_name}{self.name_sep}"
				if self.start_from == 'NO':
					new_names = [root_name] + [f"{name_head}{num+1:03}" for num in range(len(selectedBones)-1)]
				elif self.start_from == 'ZERO':
					new_names = [f"{name_head}{num:03}" for num in range(len(selectedBones))]
				elif self.start_from == 'ONE':
					new_names = [f"{name_head}{num+1:03}" for num in range(len(selectedBones))]
				for b, nam in zip(bone_list, new_names):
					try:
						existed_bone = obj.data.bones[nam]
						existed_bone.name = "temp"
						b.name = nam
						existed_bone.name = nam
					except KeyError:
						b.name = nam
		bpy.ops.armature.select_all(action='DESELECT')
		for b in selectedBones:
			if not b.name.endswith(SUFFIX_TPL):
				b.select = True
		bpy.ops.armature.autoside_names(type='XAXIS')
		bpy.ops.armature.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')
		threshold = self.threshold
		for bone in selectedBones:
			bone = arm.bones[bone.name]
			temp = [x for x in bone.head_local]
			head_interval = [(x-threshold, x+threshold) for x in [temp[0]*(-1)] + temp[1:]]
			temp = [x for x in bone.tail_local]
			tail_interval = [(x-threshold, x+threshold) for x in [temp[0]*(-1)] + temp[1:]]
			for b in arm.bones:
				if b == bone:
					continue
				for value, limits in zip(b.head_local, head_interval):
					if not limits[0] <= value <= limits[1]:
						break
				else:
					for value, limits in zip(b.tail_local, tail_interval):
						if not limits[0] <= value <= limits[1]:
							break
					else:
						b.name = bone.name
						b.select = True
						b.select_head = True
						b.select_tail = True
						break
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.armature.flip_names(do_strip_numbers=True)
		return {'FINISHED'}

class ExtendBone(bpy.types.Operator):
	bl_idname = "armature.extend_bone"
	bl_label = "Extend Bone"
	bl_description = "Stretch new bone in the direction of selected bone"
	bl_options = {'REGISTER', 'UNDO'}

	length : FloatProperty(name="Length", default=1.0, min=-10, max=10, soft_min=-10, soft_max=10, step=10, precision=3)
	is_parent : BoolProperty(name="Set Original as Parent", default=True)
	is_connect : BoolProperty(name="Connected", default=True)

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
# クラスの登録 #
################

classes = [
	CreateMirror,
	RenameBoneRegularExpression,
	RenameOppositeBone,
	ExtendBone
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
		self.layout.separator()
		self.layout.operator(ExtendBone.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.prop(context.object.data, 'use_mirror_x', icon='PLUGIN')
		self.layout.operator(CreateMirror.bl_idname, icon='PLUGIN')
		self.layout.operator(RenameOppositeBone.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator('object.copy_bone_name', icon='PLUGIN')#BONE_PT_context_bone で定義
		self.layout.operator(RenameBoneRegularExpression.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
