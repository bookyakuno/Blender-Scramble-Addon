# 「プロパティ」エリア > 「物理演算」タブ > 「フォースフィールド」パネル
# "Propaties" Area > "Physics" Tab > "Force Fields" Panel

import bpy

################
# オペレーター #
################

class forcefield_copy(bpy.types.Operator):
	bl_idname = "object.forcefield_copy"
	bl_label = "Copy ForceField Settings"
	bl_description = "Copy selection of other force field for active object"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		active_ob = context.object
		if active_ob:
			if active_ob.field:
				if 2 <= len(context.selected_objects):
					return True
		return False
	
	def execute(self, context):
		active_ob = context.object
		source = active_ob.field
		for ob in context.selected_objects:
			if ob.name == active_ob.name:
				continue
			if not ob.field:
				override = context.copy()
				override['object'] = ob
				bpy.ops.object.forcefield_toggle(override)
			for attr_name in dir(source):
				if attr_name[0] == '_' or 'rna' in attr_name:
					continue
				value = getattr(source, attr_name)
				try:
					setattr(ob.field, attr_name, value)
				except AttributeError:
					pass
		for area in context.screen.areas:
			area.tag_redraw()
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
		if 2 <= len(context.selected_objects):
			self.layout.operator(forcefield_copy.bl_idname, icon='COPY_ID')
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
