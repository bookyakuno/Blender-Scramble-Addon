# 「3Dビュー」エリア > 「アーマチュア編集」モード > 「Shift + W」キー
# "3D View" Area > "Armature Editor" Mode > "Shift + W" Key

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
	bl_label = "Set Bone Names"
	bl_description = "name of selected bone sets together"
	bl_options = {'REGISTER', 'UNDO'}

	name : StringProperty(name="Bone Name", default="Bone")

	def execute(self, context):
		context.active_bone.name = "temp"
		context.active_bone.name = self.name
		if (context.selected_bones):
			for bone in context.selected_bones:
				bone.name = self.name
		if (context.selected_pose_bones):
			for bone in context.selected_pose_bones:
				bone.name = self.name
		return {'FINISHED'}

class SetCurvedBones(bpy.types.Operator):
	bl_idname = "pose.set_curved_bones"
	bl_label = "Set Curve Bones"
	bl_description = "Bones of selected curve born sets"
	bl_options = {'REGISTER', 'UNDO'}

	bbone_segments : IntProperty(name="Segment", default=1, min=1, soft_min=1)
	bbone_in : FloatProperty(name="Ease In", default=1.0, min=0, max=2, soft_min=0, soft_max=2, step=10, precision=3)
	bbone_out : FloatProperty(name="Ease Out", default=1.0, min=0, max=2, soft_min=0, soft_max=2, step=10, precision=3)

	def execute(self, context):
		obj = bpy.context.active_object
		if (obj.type == "ARMATURE"):
			for bone in context.selected_pose_bones:
				obj.data.bones[bone.name].bbone_segments = self.bbone_segments
				obj.data.bones[bone.name].bbone_in = self.bbone_in
				obj.data.bones[bone.name].bbone_out = self.bbone_out
		return {'FINISHED'}

class SetBoneRoll(bpy.types.Operator):
	bl_idname = "pose.set_bone_roll"
	bl_label = "Set Rolls"
	bl_description = "Set selected bone rolls"
	bl_options = {'REGISTER', 'UNDO'}

	roll : FloatProperty(name="Roll", default=0, step=10, precision=3)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if 'selected_bones' in dir(context):
					if context.selected_bones:
						if 1 <= len(context.selected_bones):
							return True
				if 'selected_pose_bones' in dir(context):
					if context.selected_pose_bones:
						if 1 <= len(context.selected_pose_bones):
							return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		ob = context.active_object
		arm = ob.data
		bones = []
		if 'selected_bones' in dir(context):
			if context.selected_bones:
				bones = context.selected_bones[:]
		if bones == []:
			for bone in context.selected_pose_bones:
				bones.append(arm.bones[bone.name])
		for bone in bones:
			bone.roll = self.roll
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
