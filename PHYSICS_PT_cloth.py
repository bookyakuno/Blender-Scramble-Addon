# 「プロパティ」エリア > 「物理演算」タブ > 「クロス」パネル
# "Propaties" Area > "Physics" Tab > "Cloth" Panel

import bpy

################
# オペレーター #
################

class MakeLinkClothSettings(bpy.types.Operator):
	bl_idname = "object.make_link_cloth_settings"
	bl_label = "Link Cloth Setting"
	bl_description = "Cloth simulation for active object copies to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		for mod in context.object.modifiers:
			if (mod.type == 'CLOTH'):
				break
		else:
			return False
		return True
	
	def execute(self, context):
		active_obj = context.active_object
		active_cloth = None
		for mod in active_obj.modifiers:
			if (mod.type == 'CLOTH'):
				active_cloth = mod
				break
		target_objs = []
		for obj in context.selected_objects:
			if (active_obj.name != obj.name):
				target_objs.append(obj)
		for obj in target_objs:
			target_cloth = None
			for mod in obj.modifiers:
				if (mod.type == 'CLOTH'):
					target_cloth = mod
					break
			else:
				target_cloth = obj.modifiers.new("Cloth", 'CLOTH')
			for name in dir(active_cloth.settings):
				if (name[0] != '_'):
					if name != "effector_weights":
						try:
							value = active_cloth.settings.__getattribute__(name)
							target_cloth.settings.__setattr__(name, value)
						except AttributeError:
							pass
					else:
						for nam in dir(active_cloth.settings.effector_weights):
							if (nam[0] != '_'):
								try:
									value = active_cloth.settings.effector_weights.__getattribute__(nam)
									target_cloth.settings.effector_weights.__setattr__(nam, value)
								except AttributeError:
									pass
			for name in dir(active_cloth.point_cache):
				if (name[0] != '_'):
					try:
						value = active_cloth.point_cache.__getattribute__(name)
						target_cloth.point_cache.__setattr__(name, value)
					except AttributeError:
						pass
			for name in dir(active_cloth.collision_settings):
				if (name[0] != '_'):
					try:
						value = active_cloth.collision_settings.__getattribute__(name)
						target_cloth.collision_settings.__setattr__(name, value)
					except AttributeError:
						pass
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	MakeLinkClothSettings
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
		if 2 <= len(context.selected_objects):
			self.layout.operator(MakeLinkClothSettings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
