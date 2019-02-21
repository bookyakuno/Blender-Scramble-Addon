# 「プロパティ」エリア > 「テクスチャ」タブ > 「画像」パネル
# "Propaties" Area > "Texture" Tab > "Image" Panel

import bpy

################
# オペレーター #
################

class ShowTextureImage(bpy.types.Operator):
	bl_idname = "texture.show_texture_image"
	bl_label = "Texture images show in UV / image editor"
	bl_description = "Image is used in active texture shows UV / image editor"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (not context.texture):
			return False
		if (context.texture.type != 'IMAGE'):
			return False
		if (not context.texture.image):
			return False
		for area in context.screen.areas:
			if (area.type == 'IMAGE_EDITOR'):
				return True
		return False
	def execute(self, context):
		for area in context.screen.areas:
			if (area.type == 'IMAGE_EDITOR'):
				for space in area.spaces:
					if (space.type == 'IMAGE_EDITOR'):
						space.image = context.texture.image
		return {'FINISHED'}

class StartTexturePaint(bpy.types.Operator):
	bl_idname = "texture.start_texture_paint"
	bl_label = "Texture paint by this texture"
	bl_description = "Active texture provides texture paint"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (context.object.active_material.paint_active_slot == context.object.active_material.active_texture_index):
			if (context.object.mode == 'TEXTURE_PAINT'):
				return False
		if (not context.texture):
			return False
		if (context.texture.type != 'IMAGE'):
			return False
		if (not context.texture.image):
			return False
		return True
	def execute(self, context):
		bpy.ops.object.set_object_mode(mode='TEXTURE_PAINT')
		context.object.active_material.paint_active_slot = context.object.active_material.active_texture_index
		bpy.context.object.active_material.use_nodes = False
		return {'FINISHED'}

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.operator(ShowTextureImage.bl_idname, icon='IMAGE_COL', text="Show image UV/Image editor")
		self.layout.operator(StartTexturePaint.bl_idname, icon='TPAINT_HLT')
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
