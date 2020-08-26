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
	bl_label = "Delete bone without confirm"
	bl_description = "Remove bones without confirm"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.armature.delete()
		return {'FINISHED'}

################
# サブメニュー #
################

class ShortcutMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_armature_shortcut"
	bl_label = "By Shortcuts"
	
	def draw(self, context):
		self.layout.operator(DeleteUnmassage.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	DeleteUnmassage,
	ShortcutMenu
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
		self.layout.menu(ShortcutMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
