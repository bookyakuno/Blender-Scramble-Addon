# 「3Dビュー」エリア > 「オブジェクト」モード > 「オブジェクトコンテクストメニュー」 (Wキー)
# "3D View" Area > "Object" Mode > "Object Context Menu" (W Key)

import bpy, bmesh, mathutils, math
import re, random
from bpy.props import *

################
# オペレーター #
################

class VertexGroupTransfer(bpy.types.Operator):
	bl_idname = "object.vertex_group_transfer"
	bl_label = "Transfer Vertex Weight"
	bl_description = "Transfer vertex weights from selected meshes to active one"
	bl_options = {'REGISTER', 'UNDO'}

	remove_existed : BoolProperty(name="Delete existed vertex groups", default=False)
	use_clean : BoolProperty(name="Remove Zero-Weight Vertices", default=True)
	remove_empty : BoolProperty(name="Remove Empty Vertex Groups", default=True)
	items = [(it.identifier, it.name, it.description, idx)
		for idx, it in enumerate(bpy.ops.object.data_transfer.get_rna_type().properties["vert_mapping"].enum_items)]
	mapping : EnumProperty(name="Vertex Mapping", items=items, default='NEAREST')

	@classmethod
	def poll(cls, context):
		return bpy.ops.object.data_transfer.poll()
	def draw(self, context):
		row = self.layout.row()
		row.use_property_split =True
		row.prop(self, 'mapping')
		self.layout.separator()
		for p in ['remove_existed', 'use_clean', 'remove_empty']:
			row = self.layout.row()
			row.separator_spacer()
			row.prop(self, p)

	def execute(self, context):
		if (0 < len(context.active_object.vertex_groups) and self.remove_existed):
			bpy.ops.object.vertex_group_remove(all=True)
		bpy.ops.object.data_transfer(
			use_reverse_transfer=True, data_type='VGROUP_WEIGHTS',
			use_create=True, vert_mapping=self.mapping,
			layers_select_dst='ALL', layers_select_src='NAME')
		if self.use_clean:
			bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0, keep_single=False)
		if self.remove_empty:
			bpy.ops.mesh.remove_empty_vertex_groups()
		return {'FINISHED'}

##########################
# オペレーター(特殊処理) #
_STORE_ITEMS = []#保存用グローバル変数：EnumPropertyの動的なitems作成におけるバグへの対処用
##########################

class CreateVertexToMetaball(bpy.types.Operator):
	bl_idname = "object.create_vertex_to_metaball"
	bl_label = "Place Metaballs on Each Vertex"
	bl_description = "Create metaballs and place them on selected objects' each vertex"
	bl_options = {'REGISTER', 'UNDO'}

	name : StringProperty(name="Metaballs' Names", default="Mball")
	size : FloatProperty(name="Size", default=0.1, min=0.001, max=10, soft_min=0.001, soft_max=10, step=1, precision=3)
	resolution : FloatProperty(name="Resolution", default=0.1, min=0.001, max=10, soft_min=0.001, soft_max=10, step=0.5, precision=3)
	use_vg : BoolProperty(name="Use vertex weight as size", default=False)

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	def draw(self, context):
		for p in ['name','size','resolution']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p)
		self.layout.prop(self, 'use_vg')

	def execute(self, context):
		active_obj = context.active_object
		selected_objs = context.selected_objects[:]
		metaballs = []
		for obj in selected_objs:
			bpy.ops.object.select_all(action='DESELECT')
			if self.use_vg and len(obj.vertex_groups) > 0:
				vg_dic = {idx: dict() for idx, vg in enumerate(obj.vertex_groups)}
				for v in obj.data.vertices:
					for vge in v.groups:
							belonged_vg_dic = vg_dic[vge.group]
							belonged_vg_dic[v.index] = vge.weight
				acti_vg_dic = vg_dic[obj.vertex_groups.active_index]
			else:
				acti_vg_dic = {v.index:1 for v in obj.data.vertices}
			for v_idx in acti_vg_dic.keys():
				meta = bpy.data.metaballs.new(self.name)
				meta.elements.new()
				meta.resolution = self.resolution
				meta_obj = bpy.data.objects.new(self.name, meta)
				metaballs.append(meta_obj)
				if self.use_vg:
					size = self.size * acti_vg_dic[v_idx]
				else:
					size = self.size
				meta_obj.scale = (size, size, size)
				meta_obj.parent = obj
				meta_obj.parent_type = 'VERTEX'
				meta_obj.parent_vertices = (v_idx, 0, 0)
				context.view_layer.active_layer_collection.collection.objects.link(meta_obj)
				meta_obj.select_set(True)
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		for ob in metaballs:
			ob.select_set(True)
		bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name='Metaballs')
		bpy.context.view_layer.objects.active = metaballs[0]
		active_obj.select_set(True)#非選択状態の場合、なぜかオペレーターパネルが出ない(2.90)
		return {'FINISHED'}

class AddGreasePencilPathMetaballs(bpy.types.Operator):
	bl_idname = "object.add_grease_pencil_path_metaballs"
	bl_label = "Place Metaballs on Grease Pencil"
	bl_description = "Create metaballs and place them on active grease pencil or selected annotation"
	bl_options = {'REGISTER', 'UNDO'}

	density : IntProperty(name="Density", default=3, min=1, max=9, soft_min=1, soft_max=9, step=1)
	radius : FloatProperty(name="Size", default=0.05, min=0, max=1, soft_min=0, soft_max=1, step=0.2, precision=3)
	resolution : FloatProperty(name="Resolution", default=0.05, min=0.001, max=1, soft_min=0.001, soft_max=1, step=0.2, precision=3)
	gp_name : StringProperty(name="Target GreasePencil / Annotation", default="")
	gp_obj_name :StringProperty(name="Name of GreasePencil Owner", default="", options={'HIDDEN'})

	def item_callback(self, context):
		_STORE_ITEMS.clear()
		names = [n for n in bpy.data.grease_pencils[self.gp_name].layers.keys()]
		for idx, name in enumerate(names):
			_STORE_ITEMS.append((name, name, "", idx))
		#print(f"Ignore this message: {_STORE_ITEMS[0]}")#作成したリストの要素がうまく認識されないバグ?への一応の対処
		return _STORE_ITEMS
	act_layer : EnumProperty(name="Layers", items=item_callback)

	@classmethod
	def poll(cls, context):
		if context.gpencil_data:
			if context.gpencil_data_owner and context.active_gpencil_layer:
				return True
		elif context.annotation_data:
			if context.active_annotation_layer:
				return True
		return False
	def __init__(self):
		if bpy.context.gpencil_data:
			self.gp_name = bpy.context.gpencil_data.name
			self.gp_obj_name = bpy.context.gpencil_data_owner.name
			self.act_layer = bpy.context.active_gpencil_layer.info
		else:
			self.gp_name = bpy.context.annotation_data.name
			self.act_layer = bpy.context.active_annotation_layer.info
	def invoke(self, context, event):
		if context.gpencil_data:
			return self.execute(context)
		else:
			return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop_search(self, "gp_name", bpy.data, "grease_pencils",text="Target", translate=True, icon='GP_SELECT_STROKES')
		row = self.layout.row()
		row.use_property_split = True
		row.prop(self, "act_layer", expand=True)
		box = self.layout.box()
		box.label(text="Metaball")
		for p in ['density', 'radius', 'resolution']:
			row = box.row()
			row.use_property_split = True
			row.prop(self, p)

	def execute(self, context):
		gpen = bpy.data.grease_pencils[self.gp_name]
		if not gpen.is_annotation:
			obj = bpy.data.objects[self.gp_obj_name]
		else:
			obj = bpy.data.objects.new(name=self.gp_name, object_data=gpen)
			context.view_layer.active_layer_collection.collection.objects.link(obj)
		context.view_layer.objects.active = obj
		gpen.layers.active = gpen.layers[self.act_layer]
		pre_selectable_objects = context.selectable_objects
		try:
			bpy.ops.gpencil.convert(type='CURVE', use_normalize_weights=False, use_link_strokes=False, use_timing_data=True)
		except RuntimeError:
				self.report(type={'ERROR'}, message="Converting GreasePencil failed. Please check GreasePencil's active layer contains some line-like data")
				return {'CANCELLED'}
		for obj in context.selectable_objects:
			if (not obj in pre_selectable_objects):
				curveObj = obj
				break
		bpy.ops.object.select_all(action='DESELECT')
		curveObj.select_set(True)
		bpy.context.view_layer.objects.active = curveObj
		curveObj.data.resolution_u = 1
		bpy.ops.object.convert(target='MESH', keep_original=False)
		pathObj = bpy.context.view_layer.objects.active
		for vert in pathObj.data.vertices:
			if (vert.index % (10-self.density) == 0):
				vert.select = False
			else:
				vert.select = True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.dissolve_verts()
		bpy.ops.object.mode_set(mode='OBJECT')
		metas = []
		for vert in pathObj.data.vertices:
			bpy.ops.object.metaball_add(type='BALL', radius=self.radius, align='WORLD', enter_editmode=False, location=vert.co)
			metas.append(bpy.context.view_layer.objects.active)
			metas[-1].data.resolution = self.resolution
		for obj in metas:
			obj.select_set(True)
		context.view_layer.active_layer_collection.collection.objects.unlink(pathObj)
		return {'FINISHED'}

class CreateMeshImitateArmature(bpy.types.Operator):
	bl_idname = "object.create_mesh_imitate_armature"
	bl_label = "Add Armature Following to Each Vertex"
	bl_description = "Create armature which bones follow to active object's each vertex"
	bl_options = {'REGISTER', 'UNDO'}

	bone_length : FloatProperty(name="Length", default=0.1, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	use_normal : BoolProperty(name="Rotate From Normal", default=False)
	add_edge : BoolProperty(name="Add bones to edges", default=False)
	vert_bone_name : StringProperty(name="Name", default="Vertex")
	edge_bone_name : StringProperty(name="Name", default="Edge")

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	def draw(self, context):
		box = self.layout.box()
		row = box.split(factor=0.25)
		row.label(text="Bone")
		row.prop(self, 'vert_bone_name')
		for p in ['bone_length', 'use_normal']:
			row = box.row()
			row.use_property_split = True
			row.prop(self, p)
		self.layout.prop(self, 'add_edge')
		box = self.layout.box()
		if self.add_edge:
			box.prop(self, 'edge_bone_name')

	def execute(self, context):
		pre_active_obj = context.active_object
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				continue
			arm = bpy.data.armatures.new(f"Imitation of {obj.name}")
			arm_obj = bpy.data.objects.new(f"Imitation-Armature of {obj.name}", arm)
			context.view_layer.active_layer_collection.collection.objects.link(arm_obj)
			bpy.context.view_layer.objects.active = arm_obj
			bpy.ops.object.mode_set(mode='EDIT')
			bone_names = []
			for vert in obj.data.vertices:
				bone = arm.edit_bones.new(self.vert_bone_name+str(vert.index))
				bone.head = obj.matrix_world @ vert.co
				bone.tail = bone.head + (obj.matrix_world @ vert.normal * self.bone_length)
				bone_names.append(bone.name)
			bpy.ops.object.mode_set(mode='OBJECT')
			for vert, name in zip(obj.data.vertices, bone_names):
				vg = obj.vertex_groups.new(name=name)
				vg.add([vert.index], 1.0, 'REPLACE')
				const = arm_obj.pose.bones[name].constraints.new('COPY_LOCATION')
				const.target = obj
				const.subtarget = vg.name
				if (self.use_normal):
					const_rot = arm_obj.pose.bones[name].constraints.new('COPY_ROTATION')
					const_rot.target = obj
					const_rot.subtarget = vg.name
			bpy.context.view_layer.objects.active = obj
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.context.view_layer.objects.active = arm_obj
			if (self.use_normal):
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.pose.armature_apply()
				bpy.ops.object.mode_set(mode='OBJECT')
			if (self.add_edge):
				edge_bone_names = []
				bpy.ops.object.mode_set(mode='EDIT')
				for edge in obj.data.edges:
					vert0 = obj.data.vertices[edge.vertices[0]]
					vert1 = obj.data.vertices[edge.vertices[1]]
					bone = arm.edit_bones.new(self.edge_bone_name+str(edge.index))
					bone.head = obj.matrix_world @ vert0.co
					bone.tail = obj.matrix_world @ vert1.co
					bone.layers = (False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
					bone.parent = arm.edit_bones[self.vert_bone_name + str(vert0.index)]
					edge_bone_names.append(bone.name)
				bpy.ops.object.mode_set(mode='OBJECT')
				arm.layers[1] = True
				for edge, name in zip(obj.data.edges, edge_bone_names):
					const = arm_obj.pose.bones[name].constraints.new('STRETCH_TO')
					const.target = arm_obj
					const.subtarget = self.vert_bone_name + str(edge.vertices[1])
		bpy.context.view_layer.objects.active = pre_active_obj
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}

class CreateVertexGroupsArmature(bpy.types.Operator):
	bl_idname = "object.create_vertex_groups_armature"
	bl_label = "Add Armature Placing Bones on Weighted Vertex"
	bl_description = "Create armature which bones are placed on active object's each vertex that has weight"
	bl_options = {'REGISTER', 'UNDO'}

	armature_name : StringProperty(name="Armature Name", default="Armature")
	use_vertex_group_name : BoolProperty(name="Use vertex group name as bone name", default=True)
	bone_length : FloatProperty(name="Bone Length", default=0.5, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)

	@classmethod
	def poll(cls, context):
		if not context.active_object:
			return False
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				if (0 < len(obj.vertex_groups)):
					return True
		return False
	def draw(self, context):
		for p in ['armature_name', 'bone_length']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p)
		row = self.layout.row()
		row.separator_spacer()
		row.prop(self, 'use_vertex_group_name')

	def execute(self, context):
		pre_active_obj = context.active_object
		pre_mode = pre_active_obj.mode
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				continue
			if (len(obj.vertex_groups) <= 0):
				continue
			arm = bpy.data.armatures.new(self.armature_name)
			arm_obj = bpy.data.objects.new(self.armature_name, arm)
			context.view_layer.active_layer_collection.collection.objects.link(arm_obj)
			arm_obj.select_set(True)
			bpy.context.view_layer.objects.active = arm_obj
			me = obj.data
			bpy.ops.object.mode_set(mode='EDIT')
			for vert in me.vertices:
				for vg in vert.groups:
					if (0.0 < vg.weight):
						if (self.use_vertex_group_name):
							bone_name = obj.vertex_groups[vg.group].name
						else:
							bone_name = "Bone"
						bone = arm.edit_bones.new(bone_name)
						vert_co = obj.matrix_world @ vert.co
						vert_no = obj.matrix_world.to_quaternion() @ vert.normal * self.bone_length
						bone.head = vert_co
						bone.tail = vert_co + vert_no
			bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.view_layer.objects.active = pre_active_obj
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class CreateSolidifyEdge(bpy.types.Operator):
	bl_idname = "object.create_solidify_edge"
	bl_label = "Extract Contours by Solidify"
	bl_description = "Extract selected objects' contours by using solidify modifier"
	bl_options = {'REGISTER', 'UNDO'}

	thickness : FloatProperty(name="Thickness", default=0.07, min=0, max=1, soft_min=0, soft_max=1, step=0.1, precision=3)
	color : FloatVectorProperty(name="Color", default=(0.0, 0.0, 0.0, 1.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA', size=4)
	use_rim : BoolProperty(name="Fill Rim", default=False)

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		pre_active_obj = context.active_object
		selected_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
		for obj in selected_objs:
			context.view_layer.objects.active = obj
			mat = bpy.data.materials.new(f"Line of {obj.name}")
			mat.use_nodes = True
			bpy.ops.object.material_slot_add()
			slot = obj.material_slots[-1]
			slot.material = mat
			nodes = mat.node_tree.nodes
			for n in nodes:
				if n.type == 'BSDF_PRINCIPLED':
					bsdf_node = n
					break
			output_node = bsdf_node.outputs[0].links[0].to_node
			if context.scene.render.engine == 'BLENDER_EEVEE':
				nodes.remove(bsdf_node)
				emit_node = nodes.new('ShaderNodeEmission')
				emit_node.inputs["Color"].default_value = self.color
				mat.node_tree.links.new(emit_node.outputs[0], output_node.inputs[0])
			elif context.scene.render.engine == 'CYCLES':
				first_loc = (output_node.location[0]-200, output_node.location[1])
				second_loc = (first_loc[0]-200, first_loc[1])
				third_loc = (second_loc[0]-200, second_loc[1])
				nodes.remove(bsdf_node)
				geom_node = nodes.new('ShaderNodeNewGeometry')
				diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
				trans_node_one = nodes.new('ShaderNodeBsdfTransparent')
				geom_node.location = diffuse_node.location = trans_node_one.location = third_loc
				mix_node_one = nodes.new('ShaderNodeMixShader')
				diffuse_node.inputs["Color"].default_value = self.color
				mat.node_tree.links.new(geom_node.outputs["Backfacing"], mix_node_one.inputs[0])
				mat.node_tree.links.new(diffuse_node.outputs[0], mix_node_one.inputs[1])
				mat.node_tree.links.new(trans_node_one.outputs[0], mix_node_one.inputs[2])
				lpath_node = nodes.new('ShaderNodeLightPath')
				trans_node_two = nodes.new('ShaderNodeBsdfTransparent')
				mix_node_one.location = lpath_node.location = trans_node_two.location = second_loc
				mix_node_two = nodes.new('ShaderNodeMixShader')
				mat.node_tree.links.new(lpath_node.outputs["Is Camera Ray"], mix_node_two.inputs[0])
				mat.node_tree.links.new(trans_node_two.outputs[0], mix_node_two.inputs[1])
				mat.node_tree.links.new(mix_node_one.outputs[0], mix_node_two.inputs[2])
				mat.node_tree.links.new(mix_node_two.outputs[0], output_node.inputs[0])
				mix_node_two.location = first_loc
			mod = obj.modifiers.new("Line", 'SOLIDIFY')
			mod.use_flip_normals = True
			mod.material_offset = len(obj.material_slots)
			mod.material_offset_rim = len(obj.material_slots)
			mod.offset = 1
			mod.thickness = self.thickness
			mod.use_rim = self.use_rim
		mat.use_backface_culling = True
		context.view_layer.objects.active = pre_active_obj
		return {'FINISHED'}

##################################
# オペレーター(レンダリング制限) #
##################################

class SetRenderHide(bpy.types.Operator):
	bl_idname = "object.set_render_hide"
	bl_label = "Restrict Rendering (Selected)"
	bl_description = "Restrict rendering selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	reverse : BoolProperty(name="No Render", default=True, options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			obj.hide_render = self.reverse
		return {'FINISHED'}

class SyncRenderHide(bpy.types.Operator):
	bl_idname = "object.sync_render_hide"
	bl_label = "Allow Rendering (Only Displayed)"
	bl_description = "Allow to render displayed objects, and restrict rendering hidden objects"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False
	def flatten(self, layer_collection):
		flat_view = []
		for coll in layer_collection.children:
			if not coll.exclude and not coll.hide_viewport:
				if len(coll.children) > 0:
					flat_view.append(coll)
					flat_view += self.flatten(coll)
				else:
					flat_view.append(coll)
		return flat_view

	def execute(self, context):
		for obj in context.view_layer.objects:
			obj.hide_render = True
		master_col = context.view_layer.layer_collection
		views = self.flatten(master_col)
		for col in views:
			for obj in col.collection.objects:
				obj.hide_render = obj.hide_get()
		return {'FINISHED'}

##########################
# オペレーター(選択制限) #
##########################

class AllResetHideSelect(bpy.types.Operator):
	bl_idname = "object.all_reset_hide_select"
	bl_label = "Allow Selecting (All)"
	bl_description = "Make all objects selectable"
	bl_options = {'REGISTER', 'UNDO'}

	reverse : BoolProperty(name="Make All Unselectble", default=False)

	@classmethod
	def poll(cls, context):
		for obj in bpy.data.objects:
			if (obj.hide_select):
				return True
		return False

	def execute(self, context):
		for obj in bpy.data.objects:
			obj.hide_select = self.reverse
			if (self.reverse):
				obj.select_set(False)
		return {'FINISHED'}

class SetUnselectHideSelect(bpy.types.Operator):
	bl_idname = "object.set_unselect_hide_select"
	bl_label = "Restrict Selecting (Non-Selected)"
	bl_description = "Make unselected objects unselectable"
	bl_options = {'REGISTER', 'UNDO'}

	limit_to_view : BoolProperty(name="Not apply to hidden objects", default=True)

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False
	def draw(self, layout):
		self.layout.prop(self, 'limit_to_view')
	def flatten(self, layer_collection):
		flat_view = []
		for coll in layer_collection.children:
			if not coll.exclude and not coll.hide_viewport:
				if len(coll.children) > 0:
					flat_view.append(coll)
					flat_view += self.flatten(coll)
				else:
					flat_view.append(coll)
		return flat_view

	def execute(self, context):
		if not self.limit_to_view:
			for obj in context.view_layer.objects:
				obj.hide_select = True
		master_col = context.view_layer.layer_collection
		views = self.flatten(master_col)
		for col in views:
			for obj in col.collection.objects:
				if self.limit_to_view or not obj.hide_get():
					obj.hide_select = not obj.select_get()
		return {'FINISHED'}

class SetHideSelect(bpy.types.Operator):
	bl_idname = "object.set_hide_select"
	bl_label = "Restrict Selecting (Selected)"
	bl_description = "Make selected objects unselectable"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			obj.hide_select = True
		return {'FINISHED'}

################################
# オペレーター(オブジェクト名) #
################################

class RenameObjectRegularExpression(bpy.types.Operator):
	bl_idname = "object.rename_object_regular_expression"
	bl_label = "Rename Objects by Regular Expression"
	bl_description = "Replace selected objects' names by using regular expression"
	bl_options = {'REGISTER', 'UNDO'}

	pattern : StringProperty(name="Target text", default="^")
	repl : StringProperty(name="New Text", default="")

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False

	def execute(self, context):
		for obj in context.selected_objects:
			try:
				new_name = re.sub(self.pattern, self.repl, obj.name)
			except:
				continue
			obj.name = new_name
		return {'FINISHED'}

class AddPrefixSuffix(bpy.types.Operator):
	bl_idname = "object.add_prefix_and_suffix"
	bl_label = "Add Prefix / Suffix to Objects Names"
	bl_description = "Add designated text as prefix / suffix to selected_objects' names"
	bl_options = {'REGISTER', 'UNDO'}

	add_prefix : BoolProperty(name="Add Prefix", default=True)
	prefix : StringProperty(name="Prefix", default="")
	add_suffix : BoolProperty(name="Add Prefix", default=True)
	suffix : StringProperty(name="Suffix", default="")
	use_fstring : BoolProperty(name="Use f-string  ({context.~} and {object.~})", default=False)
	change_data :  BoolProperty(name="Change Data's Name to Object's Name", default=False)

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'use_fstring')
		for ps in [['add_prefix', 'prefix'], ['add_suffix', 'suffix']]:
			row = self.layout.row()
			row.prop(self, ps[0], text="")
			row.prop(self, ps[1])
		self.layout.prop(self, 'change_data')

	def execute(self, context):
		for object in context.selected_objects:
			if self.use_fstring:
				object.name = eval(f'f"{self.prefix}"') + object.name + eval(f'f"{self.suffix}"')
			else:
				object.name = self.prefix + object.name + self.suffix
		return {'FINISHED'}

####################################
# オペレーター(オブジェクトカラー) #
####################################

class ApplyObjectColor(bpy.types.Operator):
	bl_idname = "object.apply_object_color"
	bl_label = "Enable / Disable Object Color"
	bl_description = "Switch display state of object color, and set colors of selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	color : FloatVectorProperty(name="Color", default=(0, 0, 0, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA', size=4)
	at_rondom : BoolProperty(name="Random color", default=False)
	swtich : EnumProperty(name="Switch", items=[
		("ENABLE","Enable","",1),("DISABLE","Disable","",2),("RANDOM","Random","",3)])

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			return True
		return False
	def __init__(self):
		if bpy.context.space_data.shading.color_type == 'OBJECT':
			self.swtich = "DISABLE"
		else:
			self.switch = "ENABLE"
	def draw(self, context):
		self.layout.prop(self, 'swtich', expand=True)
		box = self.layout.box()
		box.label(text="Selected Objects")
		box.enabled = (self.swtich=='ENABLE')
		row = box.split(factor=0.25)
		row.label(text="Color")
		row.prop(self, 'color', text="")
		row.prop(self, 'at_rondom', toggle=1)

	def execute(self, context):
		space = context.space_data
		if self.swtich == 'ENABLE':
			space.shading.color_type = 'OBJECT'
			if self.at_rondom:
				for obj in context.selected_objects:
					obj.color = (random.random(), random.random(), random.random(), 1)
			else:
				for obj in context.selected_objects:
					obj.color = self.color
		elif self.swtich == 'DISABLE':
			space.shading.color_type = 'MATERIAL'
		elif self.swtich == 'RANDOM':
			space.shading.color_type = 'RANDOM'
		pre_type = space.shading.type
		space.shading.type = 'SOLID'
		if not pre_type == 'SOLID':
			self.report(type={'WARNING'},message="Viewport shading has been changed to 'Solid' mode")
		return {'FINISHED'}

####################
# オペレーター(親) #
####################

class ParentSetApplyModifiers(bpy.types.Operator):
	bl_idname = "object.parent_set_apply_modifiers"
	bl_label = "Set Parent to Modifier-Applied"
	bl_description = "Set selected objects' parenting to active object based on modifiers-applied state"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('VERTEX', "Vertex", "", 1),
		('VERTEX_TRI', "3 Vertices", "", 2),
		]
	type : EnumProperty(items=items, name="Parent Type")

	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (context.object.type != 'MESH'):
			return False
		if (len(context.selected_objects) != 2):
			return False
		for obj in context.selected_objects:
			if (obj.name != context.object.name):
				if (obj.type == 'MESH'):
					return True
		return False

	def execute(self, context):
		active_obj = context.active_object
		active_obj.select_set(False)
		enable_modifiers = [mod.name for mod in active_obj.modifiers if mod.show_viewport]
		bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
		active_obj.select_set(True)
		old_me = active_obj.data
		depsgraph = context.evaluated_depsgraph_get()
		object_eval = active_obj.evaluated_get(depsgraph)
		new_me = object_eval.to_mesh()
		if (len(old_me.vertices) != len(new_me.vertices)):
			self.report(type={'WARNING'}, message="Number of vertices have been changed after applying modifier")
		#active_obj.data = new_me
		for mod in object_eval.modifiers:
			if (mod.show_viewport):
				mod.show_viewport = False
		bpy.ops.object.parent_set(type=self.type)
		object_eval.to_mesh_clear()
		active_obj.data = old_me
		for name in enable_modifiers:
			active_obj.modifiers[name].show_viewport = True
		#active_obj.select_set(False)
		return {'FINISHED'}
		"""
		bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
		active_obj.select_set(True)
		bpy.ops.object.parent_set(type=self.type)
		for name in enable_modifiers:
			active_obj.modifiers[name].show_viewport = True
		return {'FINISHED'}
		"""

########################
# オペレーター(カーブ) #
########################

class CreateRopeMesh(bpy.types.Operator):
	bl_idname = "object.create_rope_mesh"
	bl_label = "Create Tube along Curve"
	bl_description = "Creates tube-like mesh along selected curves"
	bl_options = {'REGISTER', 'UNDO'}

	vertices : IntProperty(name="Vertices", default=32, min=3, soft_min=3, max=999, soft_max=999, step=1)
	radius : FloatProperty(name="Radius", default=0.1, step=1, precision=3, min=0, soft_min=0, max=99, soft_max=99)
	number_cuts : IntProperty(name="Number of Subdivisions", default=32, min=2, soft_min=2, max=999, soft_max=999, step=1)
	resolution_u : IntProperty(name="Resolution of Curve", default=64, min=1, soft_min=1, max=999, soft_max=999, step=1)

	@classmethod
	def poll(cls, context):
		if context.selected_objects and context.object.type == 'CURVE':
			return True
		return False

	def execute(self, context):
		pre_act = context.active_object
		for obj in context.selected_objects:
			if not obj.type == 'CURVE':
				continue
			activeObj = obj
			bpy.context.view_layer.objects.active = obj
			pre_use_stretch = activeObj.data.use_stretch
			pre_use_deform_bounds = activeObj.data.use_deform_bounds
			bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
			bpy.ops.mesh.primitive_cylinder_add(vertices=self.vertices, radius=self.radius, depth=1, end_fill_type='NOTHING', align='WORLD', enter_editmode=True, location=(0, 0, 0), rotation=(0, 1.5708, 0))
			bpy.ops.mesh.select_all(action='DESELECT')
			context.tool_settings.mesh_select_mode = [False, True, False]
			bpy.ops.mesh.select_non_manifold()
			bpy.ops.mesh.select_all(action='INVERT')
			bpy.ops.mesh.subdivide(number_cuts=self.number_cuts, smoothness=0)
			bpy.ops.object.mode_set(mode='OBJECT')
			meshObj = context.active_object
			modi = meshObj.modifiers.new("temp", 'CURVE')
			modi.object = activeObj
			activeObj.data.use_stretch = True
			activeObj.data.use_deform_bounds = True
			activeObj.data.resolution_u = self.resolution_u
			bpy.ops.object.modifier_apply(modifier=modi.name)
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
			activeObj.data.use_stretch = pre_use_stretch
			activeObj.data.use_deform_bounds = pre_use_deform_bounds
		bpy.context.view_layer.objects.active =	pre_act#アクティブが変わると、なぜかオペレーターパネルが出ない(2.90)
		return {'FINISHED'}

class MoveBevelObject(bpy.types.Operator):
	bl_idname = "object.move_bevel_object"
	bl_label = "Move Bevel-Curve to Start / End Point"
	bl_description = "Move curve objects used as bevel to start or end points of selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('START', "Bevel Start", "", 1),
		('END', "Bevel End", "", 2),
		('CENTER', "Center", "", 3),
		]
	move_position : EnumProperty(items=items, name="Move to", default='END')
	method : EnumProperty(name="Method", items=[
		("COPIED","Move copied curve","",1),("ORIGIN","Move original curve","",2)])
	tilt : FloatProperty(name="Rotation", default=0.0, min=-3.14159265359, max=3.14159265359, soft_min=-3.14159265359, soft_max=3.14159265359, step=1, precision=1, subtype='ANGLE')
	quick_0 : BoolProperty(name="0", default=False)
	quick_m90 : BoolProperty(name="-90", default=False)
	quick_p90 : BoolProperty(name="+90", default=False)
	quick_180 : BoolProperty(name="180", default=False)

	@classmethod
	def poll(cls, context):
		if context.selected_objects:
			for obj in context.selected_objects:
				if (obj.type == 'CURVE'):
					if (obj.data.bevel_object):
						return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		for p in ['move_position', 'method', 'tilt']:
			layout.prop(self, p)
		row = self.layout.row()
		for p in ['quick_m90', 'quick_0', 'quick_p90','quick_180']:
			row.prop(self, p, toggle=1)

	def execute(self, context):
		pre_act = context.active_object
		bpy.ops.object.mode_set(mode='OBJECT')
		selected_objects = context.selected_objects[:]
		for obj in selected_objects:
			if not obj.type == 'CURVE' or not obj.data.bevel_object:
				continue
			curve = obj.data
			bevel_object = curve.bevel_object
			if self.method == 'COPIED':
				bevel_object.hide_set(False)
				bpy.ops.object.select_all(action='DESELECT')
				bevel_object.select_set(True)
				bpy.ops.object.duplicate()
				bevel_object = context.selected_objects[0]
				curve.bevel_object = bevel_object
			spline = curve.splines[0]
			if (spline.type == 'NURBS'):
				if (self.move_position == 'START'):
					base_point = obj.matrix_world @ spline.points[0].co
					sub_point = obj.matrix_world @ spline.points[1].co
					tilt = spline.points[0].tilt
				elif (self.move_position == 'END'):
					base_point = obj.matrix_world @ spline.points[-1].co
					sub_point = obj.matrix_world @ spline.points[-2].co
					tilt = spline.points[-1].tilt
				elif (self.move_position == 'CENTER'):
					i = int(len(spline.points) / 2)
					base_point = obj.matrix_world @ spline.points[i].co
					sub_point = obj.matrix_world @ spline.points[i-1].co
					tilt = spline.points[i].tilt
			elif (spline.type == 'BEZIER'):
				if (self.move_position == 'START'):
					base_point = obj.matrix_world @ spline.bezier_points[0].co
					sub_point = obj.matrix_world @ spline.bezier_points[0].handle_left
					tilt = spline.bezier_points[0].tilt
				elif (self.move_position == 'END'):
					base_point = obj.matrix_world @ spline.bezier_points[-1].co
					sub_point = obj.matrix_world @ spline.bezier_points[-1].handle_left
					tilt = spline.bezier_points[-1].tilt
				elif (self.move_position == 'CENTER'):
					i = int(len(spline.bezier_points) / 2)
					base_point = obj.matrix_world @ spline.bezier_points[i].co
					sub_point = obj.matrix_world @ spline.bezier_points[i-1].handle_left
					tilt = spline.bezier_points[i].tilt
			else:
				self.report(type={'WARNING'}, message="Cannot apply to curves other than Bezier and Nurbs")
				continue
			base_point.resize_3d()
			sub_point.resize_3d()
			bevel_object.location = base_point
			vec = sub_point - base_point
			vec.normalize()
			up = mathutils.Vector((0,0,1))
			quat = up.rotation_difference(vec)
			eul = quat.to_euler('XYZ')
			#eul.rotate_axis('Z', 3.141592653589793)
			eul.rotate_axis('Z', tilt)
			try:
				index = [self.quick_m90, self.quick_0, self.quick_p90, self.quick_180].index(True)
				self.tilt = math.radians([-90,0,90,180][index])
			except ValueError:
				pass
			eul.rotate_axis('Z', self.tilt)
			bevel_object.rotation_mode = 'XYZ'
			bevel_object.rotation_euler = eul.copy()
		self.quick_m90=self.quick_0=self.quick_p90=self.quick_180 = False
		bpy.ops.object.select_all(action='DESELECT')
		for obj in selected_objects:
			obj.data.bevel_object.select_set(True)
		pre_act.select_set(True)#選択状態が変わると、なぜかオペレーターパネルが出ない(2.90)
		return {'FINISHED'}

################
# サブメニュー #
################

class RenderSelectHideMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_render_hide"
	bl_label = "Allow / Restrict Rendering & Selecting"

	def draw(self, context):
		self.layout.operator(SetRenderHide.bl_idname, icon="PLUGIN").reverse = True
		self.layout.operator('object.isolate_type_render', text="Restrict Rendering (Non-Selected)")
		self.layout.separator()
		self.layout.operator(SetRenderHide.bl_idname, text="Allow Rendering (Selected)", icon="PLUGIN").reverse = False
		self.layout.operator('object.hide_render_clear_all', text="Allow Rendering (All)")
		self.layout.operator(SyncRenderHide.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SetHideSelect.bl_idname, icon="PLUGIN")
		self.layout.operator(SetUnselectHideSelect.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(AllResetHideSelect.bl_idname, icon="PLUGIN").reverse = False

class ObjectNameMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_object_name"
	bl_label = "Change Object Name"

	def draw(self, context):
		self.layout.operator(RenameObjectRegularExpression.bl_idname, icon="PLUGIN")
		self.layout.operator(AddPrefixSuffix.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator('object.data_name_to_object_name', icon="PLUGIN").apply_selected = True#OBJECT_PT_context_object で定義
		self.layout.operator('object.object_name_to_data_name', icon="PLUGIN").apply_selected = True#OBJECT_PT_context_object で定義

class SpecialsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_specials"
	bl_label = "Advanced Manipulation"

	def draw(self, context):
		self.layout.operator(CreateVertexToMetaball.bl_idname, icon="PLUGIN")
		row = self.layout.row()
		row.operator_context = 'INVOKE_DEFAULT'
		row.operator(AddGreasePencilPathMetaballs.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreateMeshImitateArmature.bl_idname, icon="PLUGIN")
		self.layout.operator(CreateVertexGroupsArmature.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreateSolidifyEdge.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreateRopeMesh.bl_idname, icon="PLUGIN")
		self.layout.operator(MoveBevelObject.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ParentSetApplyModifiers.bl_idname, icon="PLUGIN").type = 'VERTEX_TRI'

################
# クラスの登録 #
################

classes = [
	VertexGroupTransfer,
	CreateVertexToMetaball,
	AddGreasePencilPathMetaballs,
	CreateMeshImitateArmature,
	CreateVertexGroupsArmature,
	CreateSolidifyEdge,
	SetRenderHide,
	SyncRenderHide,
	AllResetHideSelect,
	SetUnselectHideSelect,
	SetHideSelect,
	RenameObjectRegularExpression,
	AddPrefixSuffix,
	ApplyObjectColor,
	ParentSetApplyModifiers,
	CreateRopeMesh,
	MoveBevelObject,
	RenderSelectHideMenu,
	ObjectNameMenu,
	SpecialsMenu
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
		self.layout.operator(VertexGroupTransfer.bl_idname, icon="PLUGIN")
		self.layout.operator('paint.vertex_group_average_all', icon="PLUGIN")# VIEW3D_MT_paint_weight で定義
		self.layout.separator()
		self.layout.menu(SpecialsMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(RenderSelectHideMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(ObjectNameMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ApplyObjectColor.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
