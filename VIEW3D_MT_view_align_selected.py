# 「3Dビュー」エリア > 「ビュー」メニュー > 「視点を揃える」メニュー > 「アクティブに視点を揃える」メニュー
# "3D View" Area > "View" Menu > "Align View" Menu > "Align View to Active" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class Viewnumpad7AlignEX(bpy.types.Operator):
	bl_idname = "view3d.viewnumpad_7_align_ex"
	bl_label = "Align View to Active Face"
	bl_description = "Rotate view based on active face's normal direction"
	bl_options = {'REGISTER', 'UNDO'}
	items = [
		("FRONT", "Front", "", 1),
		("BACK", "Back", "", 2),
		("LEFT", "Left", "", 3),
		("RIGHT", "Right", "", 4),
		("TOP", "Top", "", 5),
		("BOTTOM", "Bottom", "", 6),
	]

	method : EnumProperty(name="Direction", items=items)
	
	def execute(self, context):
		pre_smooth_view = context.preferences.view.smooth_view
		context.preferences.view.smooth_view = 0
		bpy.ops.view3d.view_axis(type=self.method, align_active=True)
		bpy.ops.view3d.view_selected_ex()
		threshold = 0.01
		angle = 0.001
		while True:
			bpy.ops.view3d.view_roll(angle=angle, type='ANGLE')
			view_rotation = context.region_data.view_rotation.copy().to_euler()
			if (-threshold <= view_rotation.y <= threshold):
					break
		if (view_rotation.x < 0):
			bpy.ops.view3d.view_roll(angle=3.14159, type='ANGLE')
		context.preferences.view.smooth_view = pre_smooth_view
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	Viewnumpad7AlignEX
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
		self.layout.operator(Viewnumpad7AlignEX.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
