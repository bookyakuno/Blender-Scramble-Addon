# 「3Dビュー」エリア > 「ポーズ」モード > 「ポーズ」メニュー > 「コンストレイント」メニュー
# "3D View" Area > "Pose" Mode > "Pose" Menu > "Constraints" Menu

import bpy

################
# オペレーター #
################

class ConstraintIKToLimitRotation(bpy.types.Operator):
	bl_idname = "pose.constraint_ik_to_limit_rotation"
	bl_label = "IK Rotation Limit to Constraints"
	bl_description = "Copy rotation constraint restrictions IK rotation restriction settings"
	bl_options = {'REGISTER', 'UNDO'}
	
	isAdd = bpy.props.BoolProperty(name="If not add constraints", default=True)
	isLocal = bpy.props.BoolProperty(name="Local Space", default=True)
	
	def execute(self, context):
		for bone in context.selected_pose_bones:
			if (self.isAdd):
				for const in bone.constraints:
					if (const.type == "LIMIT_ROTATION"):
						break
				else:
					bone.constraints.new("LIMIT_ROTATION")
			for const in bone.constraints:
				if (const.type == "LIMIT_ROTATION"):
					const.use_limit_x = bone.use_ik_limit_x
					const.use_limit_y = bone.use_ik_limit_y
					const.use_limit_z = bone.use_ik_limit_z
					const.min_x = bone.ik_min_x
					const.min_y = bone.ik_min_y
					const.min_z = bone.ik_min_z
					const.max_x = bone.ik_max_x
					const.max_y = bone.ik_max_y
					const.max_z = bone.ik_max_z
					if (self.isLocal):
						const.owner_space = "LOCAL"
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	ConstraintIKToLimitRotation
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
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator(ConstraintIKToLimitRotation.bl_idname, icon="PLUGIN")
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
