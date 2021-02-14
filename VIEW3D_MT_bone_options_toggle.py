# 「3Dビュー」エリア > アーマチュアの「編集」モード > 「ボーンオプションを切り替え」メニュー (Shift+W キー)
# "3D View" Area > "Edit" Mode with Armature > "Toggle Bone Options" Menu (Shift + W Key)

import bpy
from bpy.props import *

##############
# その他関数 #
##############

################
# オペレーター #
################

class SetBoneNames(bpy.types.Operator):
	bl_idname = "pose.set_bone_names"
	bl_label = "Rename Selected Bones"
	bl_description = "Change selected bones' names together"
	bl_options = {'REGISTER', 'UNDO'}

	new_name : StringProperty(name="New Name", default="Bone")
	name_sep : EnumProperty(name="Numbering Expression",items=[
		(".",".00X","",1),("_","_00X","",2),("-","-00X","",3)])
	start_from : EnumProperty(name="Numbering Starts from",items=[
		("NO","No number","",1),("ZERO","000","",2),("ONE","001","",3)])

	def draw(self, context):
		row = self.layout.row(align=True)
		row.label(text="New Name")
		row.prop(self, 'new_name', text="")
		row.prop(self, 'name_sep', text="")
		row = self.layout.row(align=True)
		row.label(text="Numbering Starts from")
		row.prop(self, 'start_from', text="")

	def execute(self, context):
		if (context.selected_bones):
			selectedBones = context.selected_bones[:]
		elif (context.selected_pose_bones):
			selectedBones = context.selected_pose_bones[:]
		else:
			return {'CANCELLED'}
		name_head = f"{self.new_name}{self.name_sep}"
		if self.start_from == 'NO':
			new_names = [self.new_name] + [f"{name_head}{num+1:03}" for num in range(len(selectedBones)-1)]
		elif self.start_from == 'ZERO':
			new_names = [f"{name_head}{num:03}" for num in range(len(selectedBones))]
		elif self.start_from == 'ONE':
			new_names = [f"{name_head}{num+1:03}" for num in range(len(selectedBones))]
		for b, nam in zip(selectedBones, new_names):
			try:
				existed_bone = context.active_object.data.bones[nam]
				existed_bone.name = "temp"
				b.name = nam
				existed_bone.name = nam
			except KeyError:
				b.name = nam
		return {'FINISHED'}

class SetCurvedBones(bpy.types.Operator):
	bl_idname = "pose.set_curved_bones"
	bl_label = "Set 'Bendy Bones' of Selected Bones"
	bl_description = "Change selected bones' Bendy Bones together"
	bl_options = {'REGISTER', 'UNDO'}

	bbone_segments : IntProperty(name="Segment", default=1, min=1, soft_min=1)
	bbone_in : FloatProperty(name="Ease In", default=1.0, min=0, max=2, soft_min=0, soft_max=2, step=10, precision=3)
	bbone_out : FloatProperty(name="Ease Out", default=1.0, min=0, max=2, soft_min=0, soft_max=2, step=10, precision=3)

	def execute(self, context):
		obj = bpy.context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "EDIT"):
				for bone in context.selected_bones:
					bone.bbone_segments = self.bbone_segments
					bone.bbone_easein = self.bbone_in
					bone.bbone_easeout = self.bbone_out
			elif (obj.mode == "POSE"):
				for bone in context.selected_pose_bones:
					obj.pose.bones[bone.name].bone.bbone_segments = self.bbone_segments
					obj.pose.bones[bone.name].bbone_easein = self.bbone_in
					obj.pose.bones[bone.name].bbone_easeout = self.bbone_out
		return {'FINISHED'}

class SetBoneRoll(bpy.types.Operator):
	bl_idname = "pose.set_bone_roll"
	bl_label = "Set Selected Bones' Roll"
	bl_description = "Change selected bones' roll together"
	bl_options = {'REGISTER', 'UNDO'}

	roll : FloatProperty(name="Roll", default=0, step=10, precision=3)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob and ob.type == 'ARMATURE':
			if context.selected_bones:
				if 1 <= len(context.selected_bones):
					return True
			elif context.selected_pose_bones:
				if 1 <= len(context.selected_pose_bones):
					return True
		return False

	def execute(self, context):
		ob = context.active_object
		arm = ob.data
		if context.selected_bones:
			bones = context.selected_bones[:]
			for bone in bones:
				bone.roll = self.roll
		elif context.selected_pose_bones:
			names = [b.name for b in context.selected_pose_bones]
			bpy.ops.object.mode_set(mode='EDIT')
			for nam in names:
				arm.edit_bones[nam].roll = self.roll
			bpy.ops.object.mode_set(mode='POSE')
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	SetBoneNames,
	SetCurvedBones,
	SetBoneRoll
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
		self.layout.operator(SetBoneNames.bl_idname, icon="PLUGIN")
		self.layout.operator(SetBoneRoll.bl_idname, icon="PLUGIN")
		self.layout.operator(SetCurvedBones.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
