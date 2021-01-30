# 「3Dビュー」エリア > 「アーマチュア編集」モード > 「アーマチュア」メニュー
# "3D View" Area > "Armature Editor" Mode > "Armature" Menu

import bpy

##############
# その他関数 #
##############

################
# オペレーター #
################

class DeleteUnmassage(bpy.types.Operator):
	bl_idname = "armature.delete_unmassage"
	bl_label = "Delete Bone (without confirming)"
	bl_description = "Remove all selected bones without displaying the confirmation message"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.armature.delete()
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	DeleteUnmassage
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
		self.layout.operator(DeleteUnmassage.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
