# 「プロパティ」エリア > ヘッダー
# "Propaties" Area > Header

import bpy
from bpy.props import *

################
# オペレーター #
################

class ChangeContextTab(bpy.types.Operator):
	bl_idname = "buttons.change_context_tab"
	bl_label = "Switch Properties Tab"
	bl_description = "Switch properties tab in turn"
	bl_options = {'REGISTER'}

	is_left : BoolProperty(name="To Left", default=False)

	def execute(self, context):
		space_data = None
		for area in context.screen.areas:
			if (area.type == 'PROPERTIES'):
				for space in area.spaces:
					if (space.type == 'PROPERTIES'):
						space_data = space
						break
				else:
					continue
				break
		if (not space_data):
			self.report(type={'ERROR'}, message="Cannot find properties area")
			return {'CANCELLED'}
		now_tab = space_data.context
		tabs = ['RENDER', 'RENDER_LAYER', 'SCENE', 'WORLD', 'OBJECT', 'CONSTRAINT', 'MODIFIER', 'DATA', 'BONE', 'BONE_CONSTRAINT', 'MATERIAL', 'TEXTURE', 'PARTICLES', 'PHYSICS']
		if (now_tab not in tabs):
			self.report(type={'ERROR'}, message="Unexpected Tab Now")
			return {'CANCELLED'}
		if (self.is_left):
			tabs.reverse()
		index = tabs.index(now_tab) + 1
		for i in range(len(tabs)):
			try:
				space_data.context = tabs[index]
				break
			except TypeError:
				index += 1
			except IndexError:
				index = 0
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	ChangeContextTab
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
		row = self.layout.row(align=True)
		row.operator(ChangeContextTab.bl_idname, text="", icon='TRIA_LEFT').is_left = True
		row.operator(ChangeContextTab.bl_idname, text="", icon='TRIA_RIGHT').is_left = False
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
