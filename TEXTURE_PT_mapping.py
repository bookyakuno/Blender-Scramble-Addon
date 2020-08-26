# 「プロパティ」エリア > 「テクスチャ」タブ > 「マッピング」パネル
# "Propaties" Area > "Texture" Tab > "Mapping" Panel

import bpy

################
# オペレーター #
################

class UseActiveUV(bpy.types.Operator):
	bl_idname = "texture.use_active_uv"
	bl_label = "Use Active UV"
	bl_description = "Active UV mesh used in this slot"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.texture_slot):
			return False
		if (context.texture_slot.texture_coords != 'UV'):
			return False
		if (context.object.type != 'MESH'):
			return False
		if (not context.object.data.uv_layers.active):
			return False
		return True
	def execute(self, context):
		context.texture_slot.uv_layer = context.object.data.uv_layers.active.name
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	UseActiveUV
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
		if (context.texture_slot):
			if (context.texture_slot.texture_coords == 'UV'):
				self.layout.operator(UseActiveUV.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
