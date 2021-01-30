# 「プロパティ」エリア > 「物理演算」タブ > 「リジッドボディ」パネル
# "Propaties" Area > "Physics" Tab > "Rigid Body" Panel

import bpy

################
# オペレーター #
################

class CopySetting(bpy.types.Operator):
	bl_idname = "rigidbody.copy_setting"
	bl_label = "Copy Rigid Body Setting"
	bl_description = "Copy active object's Rigid Body settings to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			if context.active_object:
				if context.active_object.rigid_body:
					return True
		return False
	
	def execute(self, context):
		active_ob = context.active_object
		for ob in context.selected_objects:
			if ob.name == active_ob.name:
				continue
			if not ob.rigid_body:
				bpy.ops.rigidbody.object_add({'object':ob})
			for val_name in dir(ob.rigid_body):
				if val_name[0] != '_' and 'rna' not in val_name:
					value = active_ob.rigid_body.__getattribute__(val_name)
					try:
						ob.rigid_body.__setattr__(val_name, value[:])
					except TypeError:
						try:
							ob.rigid_body.__setattr__(val_name, value)
						except AttributeError:
							pass
					except AttributeError:
						pass
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	CopySetting
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
		row = self.layout.split(factor=0.4)
		row.use_property_split = False
		row.operator(CopySetting.bl_idname, icon='LINKED', text="Copy Setting")
		if context.scene.rigidbody_world:
			if context.scene.rigidbody_world.point_cache:
				row_item = row.row(align=True)
				row_item.prop(context.scene.rigidbody_world.point_cache, 'frame_start')
				row_item.prop(context.scene.rigidbody_world.point_cache, 'frame_end')
				row_item.operator('rigidbody.sync_frames', icon='LINKED', text="")# SCENE_PT_rigid_body_world.py で定義
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
