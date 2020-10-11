# 「3Dビュー」エリア > プロパティ >     レイヤーボタンがあるパネル
# "3D View" Area > Propaties > Layer Buttons Panel

import bpy
from bpy.props import *



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
		if (context.object):
			if (context.object.type == 'ARMATURE'):
				self.layout.separator(factor=1.0)
				self.layout.label(text="Bone Layer")
				col = self.layout.column()
				col.use_property_split = False
				col.use_property_decorate = False
				col.scale_y = 0.7
				col.prop(context.object.data, 'layers', text="")

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
