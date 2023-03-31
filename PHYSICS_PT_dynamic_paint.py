# 「プロパティ」エリア > 「物理演算」タブ > 「ダイナミックペイント」パネル
# "Propaties" Area > "Physics" Tab > "Dynamic Paint" Panel

import bpy

################
# オペレーター #
################

class CopyDynamicPaint(bpy.types.Operator):
	bl_idname = "dpaint.copy_dynamic_paint"
	bl_label = "Copy Dynamic Paint Setting"
	bl_description = "Copy active object's Dynamic paint settings to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		active_ob = context.active_object
		if active_ob:
			for mod in active_ob.modifiers:
				if mod.type == 'DYNAMIC_PAINT':
					if mod.brush_settings:
						break
					if mod.canvas_settings:
						break
			else:
				return False
		return True

	def execute(self, context):
		override = context.copy()
		active_ob = context.active_object
		for mod in active_ob.modifiers:
			if mod.type == 'DYNAMIC_PAINT':
				source_modifier_name = mod.name
				source_brush_settings = mod.brush_settings
				source_canvas_settings = mod.canvas_settings
				source_ui_type = mod.ui_type
		for ob in context.selected_objects:
			if ob.name == active_ob.name:
				continue
			for mod in ob.modifiers:
				if mod.type == 'DYNAMIC_PAINT':
					target = mod
					break
			else:
				target = ob.modifiers.new(source_modifier_name, 'DYNAMIC_PAINT')
			override['object'] = ob
			if source_brush_settings and not target.brush_settings:
				bpy.ops.dpaint.type_toggle(override, type='BRUSH')
			if source_canvas_settings and not target.canvas_settings:
				bpy.ops.dpaint.type_toggle(override, type='CANVAS')
			for i in target.canvas_settings.canvas_surfaces:
				bpy.ops.dpaint.surface_slot_remove(override)
			for i in source_canvas_settings.canvas_surfaces:
				bpy.ops.dpaint.surface_slot_add(override)

			for attr_name in dir(source_brush_settings):
				if attr_name[0] == '_':
					continue
				if 'rna' in attr_name:
					continue
				value = getattr(source_brush_settings, attr_name)
				try:
					setattr(target.brush_settings, attr_name, value)
				except AttributeError:
					pass

			for i, canvas_surface in enumerate(source_canvas_settings.canvas_surfaces):
				for attr_name in dir(canvas_surface):
					if attr_name[0] == '_':
						continue
					if 'rna' in attr_name:
						continue
					value = getattr(canvas_surface, attr_name)
					try:
						setattr(target.canvas_settings.canvas_surfaces[i], attr_name, value)
					except AttributeError:
						pass

			target.ui_type = source_ui_type
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	CopyDynamicPaint
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
			self.layout.operator(CopyDynamicPaint.bl_idname, icon='COPY_ID')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
