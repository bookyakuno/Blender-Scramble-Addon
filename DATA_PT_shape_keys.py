# 「プロパティ」エリア > 「オブジェクト」タブ > 「トランスフォーム」パネル
# "Propaties" Area > "Object" Tab > "Transform" Panel

import bpy

################
# オペレーター #
################

class SyncShapeKeysName(bpy.types.Operator):
	bl_idname = "mesh.sync_shape_keys_name"
	bl_label = "Shape key name from object name"
	bl_description = "Same as object name name of shape key"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.shape_keys:
					return True
		return False
	
	def execute(self, context):
		context.active_object.data.shape_keys.name = context.active_object.name
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	SyncShapeKeysName
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
def menu_prepend(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.shape_keys:
					row = self.layout.row()
					row.template_ID(context.active_object.data, 'shape_keys')
					row.operator(SyncShapeKeysName.bl_idname, icon='OBJECT_DATA', text="")
					row.operator('object.select_shape_top', icon='TRIA_UP_BAR', text="")
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
