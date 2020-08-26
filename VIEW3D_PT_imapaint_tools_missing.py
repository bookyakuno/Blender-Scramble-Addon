# 「3Dビュー」エリア > 「テクスチャペイント」モード > ツールシェルフ > 「データなし」パネル
# "3D View" Area > "Texture Paint" Mode > Tool Shelf > "Missing Data" Panel

import bpy

################
# オペレーター #
################

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
		if (context.object):
			if (context.object.active_material):
				if (context.object.active_material.use_nodes):
					self.layout.prop(context.object.active_material, 'use_nodes', icon='PLUGIN', text="Impossible, Because nodes used")
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
