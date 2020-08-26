# 「プロパティ」エリア > 「メッシュデータ」タブ > 「UVマップ」パネル
# "Propaties" Area > "Mesh" Tab > "UV Maps" Panel

import bpy

################
# オペレーター #
################

class RenameSpecificNameUV(bpy.types.Operator):
	bl_idname = "object.rename_specific_name_uv"
	bl_label = "Altogether Rename UV"
	bl_description = "Renames selected objects within designated UV together"
	bl_options = {'REGISTER', 'UNDO'}
	
	source_name =  bpy.props.StringProperty(name="Rename UV Name", default="Past UV")
	replace_name =  bpy.props.StringProperty(name="New UV Name", default="New UV")
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) <= 1):
			return False
		return True
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={'WARNING'}, message=obj.name+" mesh object, ignore")
				continue
			me = obj.data
			for uv in me.uv_textures[:]:
				if (uv.name == self.source_name):
					uv.name = self.replace_name
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class DeleteSpecificNameUV(bpy.types.Operator):
	bl_idname = "object.delete_specific_name_uv"
	bl_label = "Delete UVs specify name"
	bl_description = "Removes selection from UV same name as specified"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="Remove UV Name", default="UV")
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) <= 1):
			return False
		return True
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={'WARNING'}, message=obj.name+" mesh object, ignore")
				continue
			me = obj.data
			for uv in me.uv_textures:
				if (uv.name == self.name):
					me.uv_textures.remove(uv)
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class RenameUV(bpy.types.Operator):
	bl_idname = "object.rename_uv"
	bl_label = "Rename UV"
	bl_description = "Renames active UV (UV texture also changes accordingly)"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="New UV Name", default="UV")
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (not obj):
			return False
		if (obj.type != 'MESH'):
			return False
		me = obj.data
		if (not me.uv_layers.active):
			return False
		return True
	def execute(self, context):
		obj = context.active_object
		if (obj.type == 'MESH'):
			me = obj.data
			uv = me.uv_layers.active
			if (uv == None):
				self.report(type={'ERROR'}, message="No UV")
				return {'"CANCELLED'}
			preName = uv.name
			uv.name = self.name
			for mat in me.materials:
				if (mat):
					for slot in mat.texture_slots:
						if (slot != None):
							if (slot.uv_layer == preName):
									slot.uv_layer = uv.name
									self.report(type={"INFO"}, message="Material 「"+mat.name+"] target UV fixed")
					for me2 in bpy.data.meshes:
						for mat2 in me2.materials:
							if (mat2):
								if (mat.name == mat2.name):
									try:
										me2.uv_layers[preName].name = uv.name
										self.report(type={"INFO"}, message="Mesh 「"+me2.name+"] target UV fixed")
									except KeyError: pass
		else:
			self.report(type={'ERROR'}, message="This is not mesh object")
			return {'CANCELLED'}
		return {'FINISHED'}
	def invoke(self, context, event):
		obj = context.active_object
		if (obj.type == 'MESH'):
			me = obj.data
			uv = me.uv_layers.active
			if (uv == None):
				self.report(type={'ERROR'}, message="No UV")
				return {'CANCELLED'}
			self.name = uv.name
		return context.window_manager.invoke_props_dialog(self)

class DeleteEmptyUV(bpy.types.Operator):
	bl_idname = "object.delete_empty_uv"
	bl_label = "Remove Unused UV"
	bl_description = "Active object material (UV is used in other parts disappear) delete unused UV coordinates to all"
	bl_options = {'REGISTER', 'UNDO'}
	
	isAllSelected =  bpy.props.BoolProperty(name="All Selected Mesh", default=False)
	
	def execute(self, context):
		objs = [context.active_object]
		if (self.isAllSelected):
			objs = context.selected_objects
		for obj in objs:
			if (obj.type == "MESH"):
				uvs = []
				for mat in obj.material_slots:
					if (mat):
						for slot in mat.material.texture_slots:
							if (slot):
								if (not slot.uv_layer in uvs):
									uvs.append(slot.uv_layer)
				me = obj.data
				preUV = me.uv_layers.active
				u = me.uv_layers[:]
				for uv in u:
					if (not uv.name in uvs):
						self.report(type={"INFO"}, message=uv.name+" Removed")
						me.uv_layers.active = uv
						bpy.ops.mesh.uv_texture_remove()
				me.uv_layers.active = preUV
			else:
				self.report(type={"WARNING"}, message=obj.name+" is not mesh object")
		return {'FINISHED'}

class MoveActiveUV(bpy.types.Operator):
	bl_idname = "object.move_active_uv"
	bl_label = "Move UV"
	bl_description = "Sorts, by moving active object\'s UV"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('UP', "To Up", "", 1),
		('DOWN', "To Down", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Direction", default="UP")
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (not obj):
			return False
		if (obj.type != 'MESH'):
			return False
		me = obj.data
		if (len(me.uv_layers) <= 1):
			return False
		return True
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		if (self.mode == 'UP'):
			if (me.uv_layers.active_index <= 0):
				return {'CANCELLED'}
			target_index = me.uv_layers.active_index - 1
		elif (self.mode == 'DOWN'):
			target_index = me.uv_layers.active_index + 1
			if (len(me.uv_layers) <= target_index):
				return {'CANCELLED'}
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		uv_layer = me.uv_layers.active
		target_uv_layer = me.uv_layers[target_index]
		uv_tex = me.uv_textures.active
		target_uv_tex = me.uv_textures[target_index]
		for data_name in dir(uv_tex):
			if (data_name[0] != '_' and data_name != 'bl_rna' and data_name != 'rna_type' and data_name != 'data'):
				temp = uv_tex.__getattribute__(data_name)
				target_temp = target_uv_tex.__getattribute__(data_name)
				target_uv_tex.__setattr__(data_name, temp)
				uv_tex.__setattr__(data_name, target_temp)
				target_uv_tex.__setattr__(data_name, temp)
				uv_tex.__setattr__(data_name, target_temp)
		for i in range(len(uv_layer.data)):
			for data_name in dir(uv_layer.data[i]):
				if (data_name[0] != '_' and data_name != 'bl_rna' and data_name != 'rna_type'):
					try:
						temp = target_uv_layer.data[i].__getattribute__(data_name)[:]
					except TypeError:
						temp = target_uv_layer.data[i].__getattribute__(data_name)
					target_uv_layer.data[i].__setattr__(data_name, uv_layer.data[i].__getattribute__(data_name))
					uv_layer.data[i].__setattr__(data_name, temp)
		for i in range(len(uv_tex.data)):
			temp = uv_tex.data[i].image
			uv_tex.data[i].image = target_uv_tex.data[i].image
			target_uv_tex.data[i].image = temp
		me.uv_textures.active_index = target_index
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# サブメニュー #
################

class UVMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_uv"
	bl_label = "UV Operations"
	bl_description = "UV Operations"
	
	def draw(self, context):
		self.layout.operator(DeleteEmptyUV.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RenameSpecificNameUV.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteSpecificNameUV.bl_idname, icon="PLUGIN")

################
# クラスの登録 #
################

classes = [
	RenameSpecificNameUV,
	DeleteSpecificNameUV,
	RenameUV,
	DeleteEmptyUV,
	MoveActiveUV,
	UVMenu
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
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		if (context.active_object.type == 'MESH'):
			if (context.active_object.data.uv_layers.active):
				row = self.layout.row()
				sub = row.row(align=True)
				sub.operator(MoveActiveUV.bl_idname, icon='TRIA_UP', text="").mode = 'UP'
				sub.operator(MoveActiveUV.bl_idname, icon='TRIA_DOWN', text="").mode = 'DOWN'
				row.operator(RenameUV.bl_idname, icon="PLUGIN")
				row.menu(UVMenu.bl_idname, icon="PLUGIN")
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
