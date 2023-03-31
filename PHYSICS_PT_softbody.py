# 「プロパティ」エリア > 「物理演算」タブ > 「ソフトボディ」パネル
# "Propaties" Area > "Physics" Tab > "Soft Body" Panel

import bpy

################
# オペレーター #
################

class MakeLinkSoftbodySettings(bpy.types.Operator):
	bl_idname = "object.make_link_softbody_settings"
	bl_label = "Copy Soft Body Setting"
	bl_description = "Copy active object's Soft Body settings to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.object:
			for mod in context.object.modifiers:
				if (mod.type == 'SOFT_BODY'):
					break
			else:
				return False
		return True

	def execute(self, context):
		active_obj = context.active_object
		active_softbody = None
		for mod in active_obj.modifiers:
			if (mod.type == 'SOFT_BODY'):
				active_softbody = mod
				break
		target_objs = []
		for obj in context.selected_objects:
			if (active_obj.name != obj.name):
				target_objs.append(obj)
		for obj in target_objs:
			target_softbody = None
			for mod in obj.modifiers:
				if (mod.type == 'SOFT_BODY'):
					target_softbody = mod
					break
			else:
				target_softbody = obj.modifiers.new("Softbody", 'SOFT_BODY')
			for name in dir(active_softbody.settings):
				if (name[0] != '_'):
					if name != "effector_weights":
						try:
							value = active_softbody.settings.__getattribute__(name)
							target_softbody.settings.__setattr__(name, value)
						except AttributeError:
							pass
					else:
						for nam in dir(active_softbody.settings.effector_weights):
							if (nam[0] != '_'):
								try:
									value = active_softbody.settings.effector_weights.__getattribute__(nam)
									target_softbody.settings.effector_weights.__setattr__(nam, value)
								except AttributeError:
									pass
			for name in dir(active_softbody.point_cache):
				if (name[0] != '_'):
					try:
						value = active_softbody.point_cache.__getattribute__(name)
						target_softbody.point_cache.__setattr__(name, value)
					except AttributeError:
						pass
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	MakeLinkSoftbodySettings
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
			self.layout.operator(MakeLinkSoftbodySettings.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
