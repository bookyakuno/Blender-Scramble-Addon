# 「3Dビュー」エリア > 「視点を揃える」メニュー > 「アクティブに視点を揃える」メニュー
# "3D View" Area > "View" Menu > "Align View" Menu > "Align View to Active" Menu

import bpy

################
# オペレーター #
################

class Viewnumpad7AlignEX(bpy.types.Operator):
	bl_idname = "view3d.viewnumpad_7_align_ex"
	bl_label = "View Front"
	bl_description = "watch face from selected surface normal direction"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		pre_smooth_view = context.user_preferences.view.smooth_view
		context.user_preferences.view.smooth_view = 0
		bpy.ops.view3d.viewnumpad(type='TOP', align_active=True)
		bpy.ops.view3d.view_selected_ex()
		threshold = 0.01
		angle = 0.001
		while True:
			bpy.ops.view3d.view_roll(angle=angle, type='ROLLANGLE')
			view_rotation = context.region_data.view_rotation.copy().to_euler()
			if (-threshold <= view_rotation.y <= threshold):
					break
		if (view_rotation.x < 0):
			bpy.ops.view3d.view_roll(angle=3.14159, type='ROLLANGLE')
		context.user_preferences.view.smooth_view = pre_smooth_view
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
		self.layout.separator()
		self.layout.operator(Viewnumpad7AlignEX.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
