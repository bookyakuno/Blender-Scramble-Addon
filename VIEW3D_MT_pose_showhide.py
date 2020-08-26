# 「3Dビュー」エリア > 「ポーズ」モード > 「ポーズ」メニュー > 「表示/隠す」メニュー
# "3D View" Area > "Pose" Mode > "Pose" Menu > "Show/Hide" Menu

import bpy

################
# オペレーター #
################

class HideSelectBones(bpy.types.Operator):
	bl_idname = "armature.hide_select_bones"
	bl_label = "Selected to Unselectible"
	bl_description = "Choose bone has selected impossible"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for bone in context.selected_pose_bones:
			obj = context.active_object
			if (obj.type == "ARMATURE"):
				obj.data.bones[bone.name].hide_select = True
		return {'FINISHED'}

class HideSelectAllReset(bpy.types.Operator):
	bl_idname = "armature.hide_select_all_reset"
	bl_label = "Unlock All Unselect"
	bl_description = "non-selection of all bone"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "ARMATURE"):
			for bone in context.active_object.data.bones:
				bone.hide_select = False
				bone.select = False
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	HideSelectBones,
	HideSelectAllReset
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
		self.layout.operator(HideSelectBones.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(HideSelectAllReset.bl_idname, icon="PLUGIN")
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
