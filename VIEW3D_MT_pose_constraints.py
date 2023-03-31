# 「3Dビュー」エリア > 「ポーズ」モード > 「ポーズ」メニュー > 「コンストレイント」メニュー
# "3D View" Area > "Pose" Mode > "Pose" Menu > "Constraints" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class ConstraintIKToLimitRotation(bpy.types.Operator):
	bl_idname = "pose.constraint_ik_to_limit_rotation"
	bl_label = "Convert IK Rotation Limit to Constraint"
	bl_description = "Add to selected bones limit rotation constraints which limits are same as their IK settings"
	bl_options = {'REGISTER', 'UNDO'}

	items = [(it.identifier, it.name, it.description, idx)
		for idx, it in enumerate(bpy.types.LimitRotationConstraint.bl_rna.properties["owner_space"].enum_items)]
	space : EnumProperty(name="Owner Space", items=items, default='LOCAL')
	#DisableSetting : BoolProperty(name="Disable IK rotation limit", default=True)

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			for bone in context.selected_pose_bones:
				if bone.use_ik_limit_x or bone.use_ik_limit_y or bone.use_ik_limit_z:
					return True
		return False

	def execute(self, context):
		for bone in context.selected_pose_bones:
			for const in bone.constraints:
				if (const.type == "LIMIT_ROTATION"):
					limit_const = const
					break
			else:
				bone.constraints.new("LIMIT_ROTATION")
				limit_const = bone.constraints[-1]
			for p in ['limit_x','limit_y','limit_z']:
				exec(f"limit_const.use_{p} = bone.use_ik_{p}")
			for p in ['min_x','min_y','min_z','max_x','max_y','max_z',]:
				exec(f"limit_const.{p} = bone.ik_{p}")
			limit_const.owner_space = self.space
			"""
			# 特定の組み合わせで use_ik_limit を False にするとオペレーターパネルが表示されない
			#対処法が不明なのでとりあえずこのオプションは停止(2.90)
			if self.DisableSetting:
				bone.use_ik_limit_x = False
				bone.use_ik_limit_y = False
				bone.use_ik_limit_z = False
			"""
		return {'FINISHED'}

class LimitRotationToConstraintIK(bpy.types.Operator):
	bl_idname = "pose.limit_rotation_to_constraint_ik"
	bl_label = "Convert Limit Rotation Constraint to IK Limit"
	bl_description = "Set selected bones' IK limit rotation settings based on their limit rotation constraints"
	bl_options = {'REGISTER', 'UNDO'}

	remove_const : BoolProperty(name="Remove Constraint", default=True)

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			for bone in context.selected_pose_bones:
				const_types = [c.type for c in bone.constraints]
				if "LIMIT_ROTATION" in const_types:
					return True
		return False

	def execute(self, context):
		for bone in context.selected_pose_bones:
			for const in bone.constraints:
				if (const.type == "LIMIT_ROTATION"):
					limit_const = const
					break
			else:
				continue
			for p in ['limit_x','limit_y','limit_z']:
				exec(f"bone.use_ik_{p} = limit_const.use_{p}")
			for p in ['min_x','min_y','min_z','max_x','max_y','max_z',]:
				exec(f"bone.ik_{p} = limit_const.{p}")
			if self.remove_const:
				#bone.constraints.remove(limit_const)
				#コンストレイントを削除するとオペレーターパネルが表示されない
				#対処法が不明なのでとりあえずこのオプションは停止(2.90)
				limit_const.mute = True
			else:
				limit_const.mute = True
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	ConstraintIKToLimitRotation,
	LimitRotationToConstraintIK
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
		self.layout.operator(ConstraintIKToLimitRotation.bl_idname, icon="PLUGIN")
		self.layout.operator(LimitRotationToConstraintIK.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
