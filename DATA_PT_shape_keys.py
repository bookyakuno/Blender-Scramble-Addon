# 「プロパティ」エリア > 「オブジェクトデータ」タブ > 「シェイプキー」パネル
# "Propaties" Area > "Object Data" Tab > "Shape keys" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class InsertKeyframeAllShapes(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_all_shapes"
	bl_label = "Insert Keyframes for All Shapes"
	bl_description = "Insert keyframe for all shapes' values on the current frame"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.active_shape_key):
					return True
		return False

	def execute(self, context):
		for shape in context.active_object.data.shape_keys.key_blocks:
			shape.keyframe_insert(data_path="value")
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class InsertKeyframeWithInverval(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_with_interval"
	bl_label = "Insert Keyframes for Each with Interval"
	bl_description = "Insert zero-and-positive-value keyframes for each shape keys with designated interval"
	bl_options = {'REGISTER', 'UNDO'}

	interval : IntProperty(name="Interval", default=20, min=0)
	only_enabled : BoolProperty(name="Only Non-Mute Key", default=True)

	target = [("ALL", "All Shape Keys", "", 1), ("FIRST_TO_ACTIVE", "From First To Active", "", 2)]
	target_method : EnumProperty(name="Target Shape Key", items=target)

	value_item = [("CURRENT", "Shape Key's Value", "", 1), ("MAX", "1.0 (Maximum)", "", 2)]
	value_method : EnumProperty(name="Keyframes' Values", items=value_item)

	start_item = [("INORDER", "Start In Order", "", 1), ("ATONCE", "Start At Once", "", 2)]
	start_method : EnumProperty(name="Each Transformation", items=start_item)

	frame_item = [("START", "Start", "", 1), ("END", "End", "", 2)]
	curr_framte_method : EnumProperty(name="Current Frame", items=frame_item)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.active_shape_key):
					return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=360)
	def draw(self, context):
		row = self.layout.split(factor=0.4)
		row.label(text="Interval")
		row.prop(self, 'interval', text="")
		row = self.layout.row()
		row.use_property_split = True
		row.prop(self, 'only_enabled')
		txts = ["Target Shape Key", "Keyframes' Values", "Each Transformation", "Current Frame"]
		ps = ['target_method', 'value_method', 'start_method', 'curr_framte_method']
		for txt, p in zip(txts, ps):
			row = self.layout.row()
			row.label(text=txt)
			row.prop(self, p, expand=True)

	def execute(self, context):
		if self.target_method == 'ALL':
			targets = context.active_object.data.shape_keys.key_blocks[1:]
		elif self.target_method == 'FIRST_TO_ACTIVE':
			targets = context.active_object.data.shape_keys.key_blocks[1:context.object.active_shape_key_index+1]
		if not self.only_enabled:
			keybrocks = targets
		else:
			keybrocks = [x for x in targets if not x.mute]
		if self.value_method == 'CURRENT':
			values = [s.value for s in keybrocks]
		elif self.value_method == 'MAX':
			values = [1] * len(keybrocks)
		if self.curr_framte_method == 'START':
			start = context.scene.frame_current
			end_frames = [start + t*self.interval for t in range(1, len(keybrocks)+1)]
		elif self.curr_framte_method == 'END':
			end = context.scene.frame_current
			end_frames = [end - (t-1)*self.interval for t in range(1, len(keybrocks)+1)][::-1]
			start = end_frames[0] - self.interval
		if self.start_method == 'ATONCE':
			start_frames = [start] * len(keybrocks)
		elif self.start_method == 'INORDER':
			start_frames = [start] + end_frames[:-1]
		for idx, shape in enumerate(keybrocks):
			context.scene.frame_current = start_frames[idx]
			shape.value = 0
			shape.keyframe_insert(data_path="value")
			context.scene.frame_current = end_frames[idx]
			shape.value = values[idx]
			shape.keyframe_insert(data_path="value")
		context.scene.frame_current = start
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class InsertKeyframeToActiveQuick(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_to_active_quick"
	bl_label = "Insert Keyframe for Active with Interval"
	bl_description = "Insert zero-and-positive-value keyframes for active shape key with designated interval"
	bl_options = {'REGISTER', 'UNDO'}

	interval : IntProperty(name="Interval", default=20, min=0)

	value_item = [("CURRENT", "Shape Key's Value", "", 1), ("MAX", "1.0 (Maximum)", "", 2)]
	value_method : EnumProperty(name="Keyframes' Values", items=value_item)

	frame_item = [("START", "Start", "", 1), ("END", "End", "", 2)]
	curr_framte_method : EnumProperty(name="Current Frame", items=frame_item, default='END')

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if ob.type in {'MESH','CURVE'}:
				if (ob.active_shape_key):
					return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=350)
	def draw(self, context):
		row = self.layout.split(factor=0.4)
		row.label(text="Interval")
		row.prop(self, 'interval', text="")
		txts = ["Keyframes' Values", "Current Frame"]
		ps = ['value_method', 'curr_framte_method']
		for txt, p in zip(txts, ps):
			row = self.layout.row()
			row.label(text=txt)
			row.prop(self, p, expand=True)

	def execute(self, context):
		target = context.object.active_shape_key
		pre_frame = context.scene.frame_current
		if self.value_method == 'CURRENT':
			value = target.value
		elif self.value_method == 'MAX':
			value = 1.0
		if self.curr_framte_method == 'START':
			start_frame = context.scene.frame_current
			end_frame = start_frame + self.interval
		elif self.curr_framte_method == 'END':
			end_frame = context.scene.frame_current
			start_frame = end_frame - self.interval
		context.scene.frame_current = start_frame
		target.value = 0
		target.keyframe_insert(data_path="value")
		context.scene.frame_current = end_frame
		target.value = value
		target.keyframe_insert(data_path="value")
		context.scene.frame_current = pre_frame
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ShapeKeyApplyRemoveAll(bpy.types.Operator):
	bl_idname = "object.shape_key_apply_remove_all"
	bl_label = "Merge All Keys into Basis"
	bl_description = "Merge all shape keys and make the current shape as the mesh's basis shape"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob) and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (2 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		bpy.ops.object.shape_key_add(from_mix=True)
		bpy.ops.object.shape_key_move(type='DOWN')
		bpy.ops.object.mode_set(mode='EDIT', toggle=False)
		bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
		bpy.ops.object.shape_key_remove(all=True)
		return {'FINISHED'}

class ShapeKeyApplySwitchBasis(bpy.types.Operator):
	bl_idname = "object.shape_key_apply_switch_basis"
	bl_label = "Merge All Keys and Switch with Basis"
	bl_description = "Merge all shape keys into a new basis key and set the original basis key as a new shape key"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (2 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		obj = context.active_object
		me = obj.data
		name = f"{me.shape_keys.key_blocks[0].name}_original"
		obj.active_shape_key_index = 0
		bpy.ops.mesh.copy_shape()
		me.shape_keys.key_blocks[-1].name = name
		bpy.ops.object.shape_key_add(from_mix=True)
		bpy.ops.object.shape_key_move(type='UP')
		obj.active_shape_key_index = 0
		while len(me.shape_keys.key_blocks) > 2:
			bpy.ops.object.shape_key_remove()
		return {'FINISHED'}

class ShapeKeyMergeAll(bpy.types.Operator):
	bl_idname = "object.shape_key_merge_all_keys"
	bl_label = "Merge All Non-Basis Keys into One"
	bl_description = "Merge all non-basis shape keys into a new key"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (3 <= len(ob.data.shape_keys.key_blocks)):
						return True
		return False

	def execute(self, context):
		obj = context.active_object
		me = obj.data
		name = me.shape_keys.key_blocks[0].name
		obj.active_shape_key_index = 0
		bpy.ops.mesh.copy_shape()
		bpy.ops.object.shape_key_add(from_mix=True)
		obj.active_shape_key_index = 0
		while len(me.shape_keys.key_blocks) > 2:
			bpy.ops.object.shape_key_remove()
		obj.active_shape_key.name = name
		obj.active_shape_key_index = 1
		obj.active_shape_key.value = 1.0
		return {'FINISHED'}

class ShapeKeyMergeAbove(bpy.types.Operator):
	bl_idname = "object.shape_key_merge_above_keys"
	bl_label = "Merge Active and Above Non-Basis Keys into One"
	bl_description = "Merge active and above non-basis shape keys into a new one"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob and ob.mode == 'OBJECT':
			if ob.type in {'MESH','CURVE'}:
				if (ob.data.shape_keys):
					if (4 <= len(ob.data.shape_keys.key_blocks)):
						if 3 <= ob.active_shape_key_index:
							return True
		return False

	def execute(self, context):
		obj = context.active_object
		me = obj.data
		name = me.shape_keys.key_blocks[0].name
		active_idx = obj.active_shape_key_index
		merged_name = f"{me.shape_keys.key_blocks[1].name} to {me.shape_keys.key_blocks[active_idx].name}"
		pre_values = []
		for i in range(active_idx+1, len(me.shape_keys.key_blocks)):
			pre_values.append(me.shape_keys.key_blocks[i].value)
			me.shape_keys.key_blocks[i].value = 0.0
		bpy.ops.object.shape_key_add(from_mix=True)
		obj.active_shape_key.name = merged_name
		while obj.active_shape_key_index != active_idx+1 :
			bpy.ops.object.shape_key_move(type='UP')		
		obj.active_shape_key_index = 0
		bpy.ops.mesh.copy_shape()
		while obj.active_shape_key_index != active_idx+1 :
			bpy.ops.object.shape_key_move(type='UP')
		obj.active_shape_key_index = 0
		for i in range(active_idx+1):
			bpy.ops.object.shape_key_remove()
		obj.active_shape_key.name = name
		me.shape_keys.key_blocks[1].value = 1.0
		for i in range(2, len(me.shape_keys.key_blocks)):
			me.shape_keys.key_blocks[i].value = pre_values[i-2]
		obj.active_shape_key_index = 1
		return {'FINISHED'}

class MuteAllShapeKeys(bpy.types.Operator):
	bl_idname = "object.mute_all_shape_keys"
	bl_label = "Disable / Enable All Shapes"
	bl_description = "Enable or disable all shape keys"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('ENABLE', "Enabled", "", 1),
		('DISABLE', "Disabled", "", 2),
		]
	mode : EnumProperty(items=items, name="Mode")

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type in {'MESH','CURVE'}:
				if ob.data.shape_keys:
					if len(ob.data.shape_keys.key_blocks):
						return True
		return False

	def execute(self, context):
		ob = context.active_object
		for key in ob.data.shape_keys.key_blocks:
			if self.mode == 'ENABLE':
				key.mute = False
			elif self.mode == 'DISABLE':
				key.mute = True
		return {'FINISHED'}

################
# サブメニュー #
################

class MergeShapeMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_merge_shape"
	bl_label = "Merge Shape Keys"
	bl_description = "Functions to merge some shape keys to one"

	def draw(self, context):
		self.layout.operator(ShapeKeyApplyRemoveAll.bl_idname, icon='PLUGIN')
		self.layout.operator(ShapeKeyApplySwitchBasis.bl_idname, icon='PLUGIN')
		self.layout.operator(ShapeKeyMergeAll.bl_idname, icon='PLUGIN')
		self.layout.operator(ShapeKeyMergeAbove.bl_idname, icon='PLUGIN')

class InsetKeyframeMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_insert_keyframe"
	bl_label = "Insert Keyframes"
	bl_description = "Functions to insert keyframes for each shape keys together"

	def draw(self, context):
		self.layout.operator(InsertKeyframeAllShapes.bl_idname, icon='PLUGIN')
		self.layout.operator(InsertKeyframeWithInverval.bl_idname, icon='PLUGIN')
		self.layout.operator(InsertKeyframeToActiveQuick.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	InsertKeyframeAllShapes,
	InsertKeyframeWithInverval,
	InsertKeyframeToActiveQuick,
	ShapeKeyApplyRemoveAll,
	ShapeKeyApplySwitchBasis,
	ShapeKeyMergeAll,
	ShapeKeyMergeAbove,
	MuteAllShapeKeys,
	MergeShapeMenu,
	InsetKeyframeMenu,
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
def menu_prepend(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		if context.active_object:
			obj = context.active_object
			if obj.type == 'MESH' and obj.data.shape_keys:
				row = self.layout.row()
				rowrow = row.row(align=True)
				op = rowrow.operator(MuteAllShapeKeys.bl_idname, text="", icon='HIDE_OFF')
				op.mode = 'ENABLE'
				op = rowrow.operator(MuteAllShapeKeys.bl_idname, text="", icon='HIDE_ON')
				op.mode = 'DISABLE'
				row.menu(MergeShapeMenu.bl_idname, icon='MOD_MESHDEFORM')
				row.menu(InsetKeyframeMenu.bl_idname, icon='KEY_HLT')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
