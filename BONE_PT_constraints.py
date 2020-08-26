# 「プロパティ」エリア > 「ボーンコンストレイント」タブ
# "Propaties" Area > "Bone Constraints" Tab

import bpy

################
# オペレーター #
################

class quick_child_constraint(bpy.types.Operator):
	bl_idname = "constraint.quick_child_constraint"
	bl_label = "Quick child"
	bl_description = "Quickly add child constraint"
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

class set_ik_chain_length(bpy.types.Operator):
	bl_idname = "pose.set_ik_chain_length"
	bl_label = "Set length of IK chain"
	bl_description = "Chose second length of active bone IK chain to length to bones and set the"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
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
			self.report(type={'ERROR'}, message="Could not get chain well")
			return {'CANCELLED'}
		ik = None
		for const in activeBone.constraints:
			if (const.type == "IK"):
				ik = const
		ik.chain_count = i
		return {'FINISHED'}

class set_ik_pole_target(bpy.types.Operator):
	bl_idname = "pose.set_ik_pole_target"
	bl_label = "Set pole target of IK"
	bl_description = "Chose second Paul target of active bone IK bones sets"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
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

class set_ik_pole_angle(bpy.types.Operator):
	bl_idname = "pose.set_ik_pole_angle"
	bl_label = "Setting IK Paul angles"
	bl_description = "Set auto-choice bone IK Paul angles"
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

class SubMenu(bpy.types.Menu):
	bl_idname = "BONE_MT_constraints_sub"
	bl_label = "Individual processing"

	def draw(self, context):
		self.layout.menu(IKMenu.bl_idname, icon='PLUGIN')

class IKMenu(bpy.types.Menu):
	bl_idname = "BONE_MT_constraints_ik"
	bl_label = "IK"

	def draw(self, context):
		self.layout.operator(set_ik_chain_length.bl_idname, icon='PLUGIN')
		self.layout.operator(set_ik_pole_target.bl_idname, icon='PLUGIN')
		self.layout.operator(set_ik_pole_angle.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	quick_child_constraint,
	set_ik_chain_length,
	set_ik_pole_target,
	set_ik_pole_angle,
	SubMenu,
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
		row.operator(quick_child_constraint.bl_idname, icon='CONSTRAINT_BONE')
		row.menu(SubMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
