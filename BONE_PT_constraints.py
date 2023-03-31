# 「プロパティ」エリア > 「ボーンコンストレイント」タブ
# "Propaties" Area > "Bone Constraints" Tab

import bpy

################
# オペレーター #
################

class QuickChildConstraint(bpy.types.Operator):
	bl_idname = "constraint.quick_child_constraint"
	bl_label = "Quick child"
	bl_description = "Add child constraint to the active bone setting the selected bone as parent"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if 'selected_pose_bones' in dir(context):
			if context.selected_pose_bones:
				if 2 == len(context.selected_pose_bones):
					return True
		return False

	def execute(self, context):
		active_ob = context.active_object
		active_bone = context.active_pose_bone
		for target_bone in context.selected_pose_bones:
			if active_bone.name != target_bone.name:
				break
		const = active_bone.constraints.new('CHILD_OF')
		const.target = active_ob
		const.subtarget = target_bone.name
		override = context.copy()
		override = {'constraint':const}
		bpy.ops.constraint.childof_clear_inverse(override, constraint=const.name, owner='BONE')
		bpy.ops.constraint.childof_set_inverse(override, constraint=const.name, owner='BONE')
		return {'FINISHED'}

###############
# 個別処理 IK #
###############

class SetIkChainLength(bpy.types.Operator):
	bl_idname = "pose.set_ik_chain_length"
	bl_label = "Set IK Chain to Selected Bone"
	bl_description = "Set chain length of the active bone's IK so that the chain's end is the selected bone"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			if len(context.selected_pose_bones) == 2:
				for const in context.active_pose_bone.constraints:
					if const.type == 'IK':
						return True
		return False

	def execute(self, context):
		activeBone = context.active_pose_bone
		targetBone = None
		for bone in context.selected_pose_bones:
			if (activeBone.name != bone.name):
				targetBone = bone
		tempBone = activeBone
		i = 0
		while True:
			if (tempBone.parent):
				if (tempBone.name == targetBone.name):
					i += 1
					break
				tempBone = tempBone.parent
				i += 1
			else:
				i = 0
				break
		if (i == 0):
			self.report(type={'ERROR'}, message="Failed to get chain counts")
			return {'CANCELLED'}
		ik = None
		for const in activeBone.constraints:
			if (const.type == "IK"):
				ik = const
		ik.chain_count = i
		return {'FINISHED'}

class SetIkPoleTarget(bpy.types.Operator):
	bl_idname = "pose.set_ik_pole_target"
	bl_label = "Set Selected Bone as IK's Pole Target"
	bl_description = "Set the selected bone as Pole Target of the active bone's IK"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			if len(context.selected_pose_bones) == 2:
				for const in context.active_pose_bone.constraints:
					if const.type == 'IK':
						return True
		return False

	def execute(self, context):
		activeObj = context.active_object
		activeBone = context.active_pose_bone
		for bone in context.selected_pose_bones:
			if (activeBone.name != bone.name):
				for const in activeBone.constraints:
					if (const.type == "IK"):
						ik = const
				ik.pole_target = activeObj
				ik.pole_subtarget = bone.name
		return {'FINISHED'}

class SetIkPoleAngle(bpy.types.Operator):
	bl_idname = "pose.set_ik_pole_angle"
	bl_label = "Set IK's Pole Angle Based on Selected"
	bl_description = "Set pole angle of the selected bone so that its location is equal to the rest position's one"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				if context.selected_pose_bones:
					if 1 <= len(context.selected_pose_bones):
						for const in context.active_pose_bone.constraints:
							if const.type == 'IK':
								if const.pole_target:
									return True
		return False

	def execute(self, context):
		ob = context.active_object
		arm = ob.data
		for pose_bone in context.selected_pose_bones:
			for const in pose_bone.constraints:
				if const.type == 'IK':
					if const.pole_target:
						ik = const
						break
			else:
				continue
			bone = arm.bones[pose_bone.name]
			ik.pole_angle = -3.1415926535897932384626433832795028841971
			min_score = (ik.pole_angle, 9999999)
			pre_angle = ik.pole_angle
			for i in range(9999):
				ik.pole_angle += 0.001
				context.view_layer.update()
				co = ( pose_bone.matrix.to_translation() - bone.head_local ).length
				rot = pose_bone.matrix.to_quaternion().rotation_difference(bone.matrix_local.to_quaternion()).angle
				score = co * rot
				if score <= min_score[1]:
					min_score = (ik.pole_angle, score)
				if pre_angle == ik.pole_angle:
					break
				pre_angle = ik.pole_angle
			ik.pole_angle = min_score[0]
			context.view_layer.update()
		return {'FINISHED'}

################
# サブメニュー #
################

class IKMenu(bpy.types.Menu):
	bl_idname = "BONE_MT_constraints_ik"
	bl_label = "Manipulate IK"

	def draw(self, context):
		self.layout.operator(SetIkChainLength.bl_idname, icon='PLUGIN')
		self.layout.operator(SetIkPoleTarget.bl_idname, icon='PLUGIN')
		self.layout.operator(SetIkPoleAngle.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	QuickChildConstraint,
	SetIkChainLength,
	SetIkPoleTarget,
	SetIkPoleAngle,
	IKMenu
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
		row = self.layout.row()
		row.operator(QuickChildConstraint.bl_idname, icon='CONSTRAINT_BONE')
		row.menu(IKMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
