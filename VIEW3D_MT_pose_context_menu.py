# 「3Dビュー」エリア > 「ポーズ」モード > 「ポーズコンテクストメニュー」 (Wキー)
# "3D View" Area > "Pose" Mode > "Pose Context Menu" (W Key)

import bpy
import re, math
from bpy.props import *

################
# オペレーター #
_STORE_ITEMS = [] #保存用グローバル変数：EnumPropertyの動的なitems作成におけるバグへの対処用
################

class CreateCustomShape(bpy.types.Operator):
	bl_idname = "pose.create_custom_shape"
	bl_label = "Create Custom Shape"
	bl_description = "Creates custom shapes of selected bones"
	bl_options = {'REGISTER', 'UNDO'}

	name : StringProperty(name="Name", default="CustomShape")
	items = [
		('1', "Line", "", 1),
		('2', "Rhombus", "", 2),
		]
	shape : EnumProperty(items=items, name="Shape")
	after_method : EnumProperty(name="After execution",	items=[
		("POSE","Pose Mode","",1),("OBJECT","Object Mode","",2),
		("HIDE","Object Mode & Hide Armature","",3),], options={'SKIP_SAVE'})
	#'SKIP_SAVE'オプション：ポーズモードから出るとオペレーターパネルが表示されない(2.90)ので、常に最初は"POSE"を選択させてプロパティがロックされるのを防ぐ

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False

	def execute(self, context):
		obj = bpy.context.active_object
		meObjs = []
		bpy.ops.object.mode_set(mode='OBJECT')
		for bone in obj.data.bones:
			if(bone.select == True):
				bpy.ops.object.select_all(action='DESELECT')
				bone.show_wire = True
				me = bpy.data.meshes.new(self.name)
				if self.shape == '1':
					me.from_pydata([(0,0,0), (0,1,0)], [(0,1)], [])
				elif self.shape == '2':
					me.from_pydata([(0,0,0), (0,1,0), (0.1,0.5,0), (0,0.5,0.1), (-0.1,0.5,0), (0,0.5,-0.1)], [(0,1), (0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5), (2,3), (3,4), (4,5), (5,2)], [])
				me.update()
				meObj = bpy.data.objects.new(me.name, me)
				meObj.data = me
				context.view_layer.active_layer_collection.collection.objects.link(meObj)
				meObj.select_set(True)
				bpy.context.view_layer.objects.active = meObj
				meObj.display_type = 'WIRE'
				meObj.show_in_front = True
				meObj.constraints.new('COPY_TRANSFORMS')
				meObj.constraints[-1].target = obj
				meObj.constraints[-1].subtarget = bone.name
				bpy.ops.object.visual_transform_apply()
				meObj.constraints.remove(meObj.constraints[-1])
				obj.pose.bones[bone.name].custom_shape = meObj
				len = bone.length
				bpy.ops.transform.resize(value=(len, len, len))
				meObjs.append(meObj)
		bpy.ops.object.select_all(action='DESELECT')
		obj.select_set(True)
		bpy.context.view_layer.objects.active = obj
		bpy.ops.object.mode_set(mode='POSE')
		if not self.after_method == 'POSE':
			bpy.ops.object.mode_set(mode='OBJECT')
			for meobj in meObjs:
				meobj.select_set(True)
			obj.select_set(False)
			if self.after_method == 'HIDE':
				obj.select_set(False)
				obj.hide_set(True)
				context.view_layer.objects.active = meObjs[0]
		return {'FINISHED'}

class CreateWeightCopyMesh(bpy.types.Operator):
	bl_idname = "pose.create_weight_copy_mesh"
	bl_label = "Create mesh for weight copy"
	bl_description = "Creates mesh to use with copy of selected bone weight"
	bl_options = {'REGISTER', 'UNDO'}

	name : StringProperty(name="Name", default="Object for weight copy")
	items = [
		('TAIL', "Tail", "", 1),
		('HEAD', "Head", "", 2),
		]
	mode : EnumProperty(items=items, name="Position of Weight")

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False

	def execute(self, context):
		obj = bpy.context.active_object
		bpy.ops.object.mode_set(mode='OBJECT')
		bones = [b for b in obj.data.bones if b.select and not b.hide]
		me = bpy.data.meshes.new(self.name)
		verts = []
		edges = []
		for idx, bone in enumerate(bones):
			co = bone.tail_local
			if self.mode == 'HEAD':
				co = bone.head_local
			verts.append(co)
			if bone.parent and bone.parent in bones:
				parent_idx = bones.index(bone.parent)
				edges.append((idx, parent_idx))
		me.from_pydata(verts, edges, [])
		me.update()
		meObj = bpy.data.objects.new(self.name, me)
		meObj.data = me
		context.view_layer.active_layer_collection.collection.objects.link(meObj)
		bpy.ops.object.select_all(action='DESELECT')
		meObj.select_set(True)
		bpy.context.view_layer.objects.active = meObj
		for idx, bone in enumerate(bones):
			meObj.vertex_groups.new(name=bone.name)
			meObj.vertex_groups[bone.name].add([idx], 1.0, 'REPLACE')
		#ポーズモードから出るとオペレーターパネルが表示されない(2.9)問題への対処
		bpy.context.view_layer.objects.active = obj
		bpy.ops.object.mode_set(mode='POSE')
		return {'FINISHED'}

class SplineAnnotation(bpy.types.Operator):
	bl_idname = "pose.spline_annotation"
	bl_label = "Place Bones along Grease Pencil"
	bl_description = "Place selected bones along designated grease pencil or annotation"
	bl_properties = "act_layer"
	bl_options = {'REGISTER', 'UNDO'}

	gp_name : StringProperty(name="Target GreasePencil / Annotation", default="")
	use_radius : BoolProperty(name="Use Curve Radius", default=False)
	use_even_div : BoolProperty(name="Even Divisions", default=False)
	y_items = [(it.identifier, it.name, it.description, idx)
		for idx, it in enumerate(bpy.types.SplineIKConstraint.bl_rna.properties["y_scale_mode"].enum_items)]
	y_mode : EnumProperty(name="Y Scale Mode", items=y_items, default='NONE')
	keep_loc : BoolProperty(name="Stay current location", default=False)
	reverse : BoolProperty(name="Switch Direction", default=False)
	remove_gp : BoolProperty(name="Remove target grease pencil", default=False)

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
		if not context.selected_pose_bones:
			return False
		if not len(bpy.data.grease_pencils):
			return False
		return True
	def __init__(self):
		if bpy.context.annotation_data:
			self.gp_name = bpy.context.annotation_data.name
			self.act_layer = bpy.context.active_annotation_layer.info
		else:
			self.gp_name = bpy.data.grease_pencils[0].name
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop_search(self, "gp_name", bpy.data, "grease_pencils",text="Target", translate=True, icon='GP_SELECT_STROKES')
		self.layout.prop(self, "act_layer", expand=True)
		box = self.layout.box()
		box.label(text="Spline IK")
		row = box.row()
		row.prop(self, 'use_radius')
		row.prop(self, 'use_even_div')
		row = box.row()
		row.prop(self, 'keep_loc')
		row.prop(self, 'reverse')
		row = box.row()
		row.use_property_split = True
		row.prop(self, 'y_mode')
		self.layout.prop(self, 'remove_gp')

	def execute(self, context):
		activeObj = context.active_object
		bones = context.selected_pose_bones
		bpy.ops.object.mode_set(mode='OBJECT')
		gpen = bpy.data.grease_pencils[self.gp_name]
		new_obj = bpy.data.objects.new(name=self.gp_name+"_temp", object_data=gpen)
		context.view_layer.active_layer_collection.collection.objects.link(new_obj)
		context.view_layer.objects.active = new_obj
		gpen.layers.active = gpen.layers[self.act_layer]
		pre_selectable_objects = context.selectable_objects[:]
		try:
			bpy.ops.gpencil.convert(type='CURVE', use_normalize_weights=False, use_link_strokes=False, use_timing_data=True)
		except RuntimeError:
				self.report(type={'ERROR'}, message="Converting GreasePencil failed. Please check GreasePencil's active layer contains some line-like data")
				return {'CANCELLED'}
		for obj in context.selectable_objects:
			if (not obj in pre_selectable_objects):
				curveObj = obj
				break
		if self.reverse:
			context.view_layer.objects.active = curveObj
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.curve.switch_direction()
			bpy.ops.object.mode_set(mode='OBJECT')
		context.view_layer.objects.active = activeObj
		bpy.ops.object.mode_set(mode='POSE')
		tails_dic = {}
		for bone in context.selected_pose_bones:
			if bone.children:
				for child in bone.children:
					if child in context.selected_pose_bones:
						break
				else:
					tails_dic[bone] = None
			else:
				tails_dic[bone] = None
		for bone in tails_dic.keys():
			const = bone.constraints.new('SPLINE_IK')
			const.target = curveObj
			const.use_curve_radius = self.use_radius
			const.y_scale_mode = self.y_mode
			const.chain_count = len(context.selected_pose_bones)
			const.use_even_divisions = self.use_even_div
			tails_dic[bone] = const
		bpy.ops.pose.visual_transform_apply()
		for bone, const in tails_dic.items():
			bone.constraints.remove(const)
		bpy.ops.pose.scale_clear()
		bpy.data.objects.remove(curveObj)
		bpy.data.objects.remove(new_obj)
		if self.remove_gp:
			gpen.layers.remove(gpen.layers.active)
		if self.keep_loc:
			bpy.ops.pose.loc_clear()
		return {'FINISHED'}

class SetSlowParentBone(bpy.types.Operator):
	bl_idname = "pose.set_slow_parent_bone"
	bl_label = "Set Slow Parent"
	bl_description = "Set slow parent to selected bone"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('DAMPED_TRACK', "Damped Track", "", 1),
		('IK', "IK", "", 2),
		('STRETCH_TO', "Stretch", "", 3),
		]#('COPY_LOCATION', "Copy Location", "", 4),
	constraint : EnumProperty(items=items, name="Constraints")
	radius : FloatProperty(name="Empty Size", default=0.5, min=0.01, max=10, soft_min=0.01, soft_max=10, step=10, precision=3)
	slow_parent_offset : FloatProperty(name="Strength", default=4, min=1, max=10, soft_min=1, soft_max=10, step=1)
	is_use_driver : BoolProperty(name="Set 'Strength' by custom property", default=True)

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False
	def draw(self, context):
		for p in ['constraint','slow_parent_offset','radius']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p)
		self.layout.prop(self, 'is_use_driver')

	def execute(self, context):
		pre_cursor_location = context.scene.cursor.location[:]
		pre_active_pose_bone = context.active_pose_bone
		obj = context.active_object
		arm = obj.data
		bones = context.selected_pose_bones[:]
		for bone in bones:
			if not bone.parent:
				self.report(type={'WARNING'}, message="Ignored " + bone.name)
				continue
			#if self.constraint == 'COPY_LOCATION':
			#	context.scene.cursor.location = obj.matrix_world @ arm.bones[bone.name].head_local
			#else:
			context.scene.cursor.location = obj.matrix_world @ arm.bones[bone.name].tail_local
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.empty_add(type='SPHERE', radius=self.radius*0.5)
			empty_child = context.active_object
			empty_child.name = bone.parent.name+" child"
			obj.select_set(True)
			bpy.context.view_layer.objects.active = obj
			bpy.ops.object.mode_set(mode='POSE')
			pre_parent_select = arm.bones[bone.parent.name].select
			arm.bones.active = arm.bones[bone.parent.name]
			bpy.ops.object.parent_set(type='BONE')
			arm.bones[bone.parent.name].select = pre_parent_select
			arm.bones.active = arm.bones[bone.name]
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.empty_add(type='PLAIN_AXES', radius=self.radius)
			empty_obj = context.active_object
			empty_obj.name = bone.name+" slow parent"
			const = bone.constraints.new(self.constraint)
			const.target = empty_obj
			if self.constraint == 'IK':
				const.chain_count = 1
			empty_obj.select_set(False)
			if self.is_use_driver:
				bone["Slow Parent Strength"] = self.slow_parent_offset
			var_suff = ["_X", "_Y", "_Z"]
			fcurves = empty_obj.driver_add('location')
			for idx, fc in enumerate(fcurves):
				fc.driver.type = 'SCRIPTED'
				fc.driver.use_self = True
				variable = fc.driver.variables.new()
				variable.name = "var" + var_suff[idx]
				variable.type = 'TRANSFORMS'
				variable.targets[0].id = empty_child
				variable.targets[0].transform_type = 'LOC' + var_suff[idx]
				if self.is_use_driver:
					var_off = fc.driver.variables.new()
					var_off.name = "offset"
					var_off.targets[0].id = obj
					var_off.targets[0].data_path = f'pose.bones["{bone.name}"]["Slow Parent Strength"]'
					fc.driver.expression = f"(self.location.{var_suff[idx][-1].lower()}*offset+{variable.name})/(offset+1)"
				else:
					fc.driver.expression = f"(self.location.{var_suff[idx][-1].lower()}*{self.slow_parent_offset}+{variable.name})/{self.slow_parent_offset+1}"
		context.view_layer.objects.active = obj
		bpy.ops.object.mode_set(mode='POSE')
		arm.bones.active = arm.bones[pre_active_pose_bone.name]
		context.scene.cursor.location = pre_cursor_location[:]
		return {'FINISHED'}

class RenameBoneNameEnd(bpy.types.Operator):
	bl_idname = "pose.rename_bone_name_end"
	bl_label = "Change Suffix"
	bl_description = "Change selected bones suffixes to designated ones"
	bl_options = {'REGISTER', 'UNDO'}

	is_all : BoolProperty(name="Apply to All Bones", default=False)
	separation : EnumProperty(name="Separation", items=[
			(".","XXX.","",1),("_","XXX_","",2),("-","XXX-","",3)])
	suffix : EnumProperty(name="Suffix", items=[
			("R/L","R / L","",1),("r/l","r / l","",2),
			("Right/Left","Right / Left","",3), ("right/left","right / left","",4),
			("RIGHT/LEFT","RIGHT / LEFT","",5)])

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False
	def draw(self, context):
		row = self.layout.row()
		row.use_property_split = True
		row.prop(self, 'is_all')
		row = self.layout.row(align=True)
		row.label(text="New Suffix")
		row.prop(self, 'separation', text="")
		row.prop(self, 'suffix', text="")

	def execute(self, context):
		if not self.is_all:
			targets = context.selected_pose_bones[:]
		else:
			targets = context.active_object.data.bones[:]
		pre_names = [b.name for b in targets]
		if self.is_all:
			pre_selects = context.selected_pose_bones[:]
			for b in targets:
				b.select = True
		bpy.ops.pose.flip_names(do_strip_numbers=False)
		for bone, pre_name in zip(targets, pre_names):
			for index, (a,b) in enumerate(zip(pre_name, bone.name)):
				if not a == b:
					if a in ["R", "r"] and b in ["L", "l"]:
						new_suffix = self.suffix.split("/")[0]
					elif a in ["L", "l"] and b in ["R", "r"]:
						new_suffix = self.suffix.split("/")[1]
					else:
						bone.name = pre_name
						base = None
						continue
					if pre_name[index-1] in [".","_","-"]:
						base = pre_name[:index-1]
					else:
						base = pre_name[:index]
					break
			else:
				bone.name = pre_name
				continue
			if base:
				bone.name = base + self.separation + new_suffix
		if self.is_all:
			bpy.ops.pose.select_all(action='DESELECT')
			for b in pre_selects:
				context.active_object.data.bones[b.name].select = True
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class RenameBoneNameEndJapanese(bpy.types.Operator):
	bl_idname = "pose.rename_bone_name_end_japanese"
	bl_label = "日本語の接尾辞に変更"
	bl_description = "「.R/L」と「_R/L」を「左/右」に変換します"
	bl_options = {'REGISTER', 'UNDO'}

	is_all : BoolProperty(name="Apply to All Bones", default=False)
	reverse : BoolProperty(name="日本語 → 英語", default=False)

	@classmethod
	def poll(cls, context):
		obj = bpy.context.active_object
		if obj:
			if obj.type == 'ARMATURE' and obj.mode == 'POSE':
				if context.selected_pose_bones:
					return True
		return False

	def execute(self, context):
		if not self.is_all:
			targets = context.selected_pose_bones[:]
		else:
			targets = context.active_object.data.bones[:]
		for bone in targets:
			if not self.reverse:
				if re.search(r'[\._][rR]$', bone.name):
					bone.name = chr(21491) + bone.name[:-2]
				if re.search(r'[\._][lL]$', bone.name):
					bone.name = chr(24038) + bone.name[:-2]
			else:
				if re.search(r"^右", bone.name):
					bone.name = bone.name[1:] + "_R"
				if re.search(r"^左", bone.name):
					bone.name = bone.name[1:] + "_L"
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class TogglePosePosition(bpy.types.Operator):
	bl_idname = "pose.toggle_pose_position"
	bl_label = "Switch Position"
	bl_description = "Switch pose / rest position of armature"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if bpy.context.active_object:
			if bpy.context.active_object.type == 'ARMATURE':
				return True
		return False

	def execute(self, context):
		if context.object.data.pose_position == 'POSE':
			context.object.data.pose_position = 'REST'
			self.report(type={'INFO'}, message="Rest Position")
		else:
			context.object.data.pose_position = 'POSE'
			self.report(type={'INFO'}, message="Pose Position")
		return {'FINISHED'}

class CopyConstraintsMirror(bpy.types.Operator):
	bl_idname = "pose.copy_constraints_mirror"
	bl_label = "Copy Constraints to Flipped-Name Bones"
	bl_description = "Copy selected bones' constraints to bones which have left-right-flipped name"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			if len(context.active_pose_bone.constraints) > 0:
				return True
		return False

	def execute(self, context):
		arma_bones = context.active_object.data.bones
		pre_active = arma_bones.active
		selected = context.selected_pose_bones[:]
		pre_names = [b.name for b in selected]
		bpy.ops.pose.flip_names(do_strip_numbers=False)
		for bone, pre_name in zip(selected, pre_names):
			bpy.ops.pose.select_all(action='DESELECT')
			if len(bone.name) > len(pre_name):
				if not re.search(r'([\._-]\d+?)$', bone.name):
					flipped_name = None
				else:
					flipped_name = re.search(r'(.+)([\._-]\d+?)$', bone.name).group(1)
			elif len(bone.name) == len(pre_name):
				if not re.search(r'([\._-]\d+?)$', bone.name):
					flipped_name = None
				else:
					diffs = [a==b for a, b in zip(pre_name, bone.name)]
					if (diffs[-1]==False) and (diffs[-2]==True):
						flipped_name = bone.name[:-1]+pre_name[-1]
					elif (diffs[-1]==False) and (diffs[-2]==False):
						flipped_name = bone.name[:-2]+pre_name[-2:]
					else:
						flipped_name = None
			else:
				flipped_name = None
			if not flipped_name:
				self.report(type={'WARNING'}, message="Ignored " + pre_name)
				bone.name = pre_name
				continue
			try:
				target_b = context.active_object.pose.bones[flipped_name]
				target_b.bone.select = True
				bone.bone.select = True
				arma_bones.active = bone.bone
				bpy.ops.pose.constraints_copy()
			except KeyError:
				self.report(type={'WARNING'}, message="Ignored " + pre_name)
			bone.name = pre_name
		bpy.ops.pose.select_all(action='DESELECT')
		for b in selected:
			b.bone.select = True
		arma_bones.active = pre_active
		pre_mode = context.mode
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class RemoveBoneNameSerialNumbers(bpy.types.Operator):
	bl_idname = "pose.remove_bone_name_serial_numbers"
	bl_label = "Remove Dot-Number from Names"
	bl_description = "Try to remove right-most dot-number from select bones' names"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False

	def execute(self, context):
		for bone in context.selected_pose_bones:
			bone.name = re.sub(r'\.\d+$', "", bone.name)
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SetRigidBodyBone(bpy.types.Operator):
	bl_idname = "pose.set_rigid_body_bone"
	bl_label = "Create Chain-like Rigid Body Objects"
	bl_description = "Create rigid body objects from selected bones, and make these bones follow the objects"
	bl_options = {'REGISTER', 'UNDO'}

	shape_size : FloatProperty(name="Size", default=0.1, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	shape_level : IntProperty(name="Number of Subdivisions", default=3, min=1, max=6, soft_min=1, soft_max=6)
	constraints_size : FloatProperty(name="Size", default=0.1, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	items = [(it.identifier, it.name, it.description, idx)
		for idx, it in enumerate( bpy.ops.object.empty_add.get_rna_type().properties["type"].enum_items)]
	empty_display_type : EnumProperty(items=items, name="Shape", default='SPHERE')
	is_parent_shape : BoolProperty(name="Follow objects", default=False)
	rot_limit : FloatProperty(name="Limit Rotation", default=90, min=0, max=360, soft_min=0, soft_max=360, step=1, precision=3)
	linear_damping : FloatProperty(name="Translation", default=0.04, min=0, max=1, soft_min=0, soft_max=1, step=1, precision=3)
	angular_damping : FloatProperty(name="Rotation", default=0.1, min=0, max=1, soft_min=0, soft_max=1, step=1, precision=3)

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		box = self.layout.box()
		box.label(text="Rigid Body Object")
		row = box.row()
		row.label(text="Size")
		row.prop(self, 'shape_size', text="")
		row.label(text="Subdivisions")
		row.prop(self, 'shape_level', text="")
		row = box.row()
		row.label(text="Damping")
		row.label(text="Translation")
		row.prop(self, 'linear_damping', text="")
		row.label(text="Rotation")
		row.prop(self, 'angular_damping', text="")
		box = self.layout.box()
		box.label(text="Rigid Body Constraint")
		row = box.split(factor=0.5)
		row.prop(self, 'empty_display_type', text="")
		row.label(text="Size")
		row.prop(self, 'constraints_size')
		sp = box.split(factor=0.5)
		row = sp.row()
		row.label(text="Limit Rotation")
		row.prop(self, 'rot_limit')
		sp.prop(self, 'is_parent_shape')

	def set_sphere(self, context, p_bone, arma_obj, is_base=False):
		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=self.shape_level, radius=1, align='WORLD', enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
		sphere_obj = context.active_object
		bpy.ops.rigidbody.object_add()
		rg_setting = sphere_obj.rigid_body
		if is_base:
			rg_setting.enabled = False
			rg_setting.kinematic = True
		rg_setting.linear_damping = self.linear_damping
		rg_setting.angular_damping = self.angular_damping
		const = sphere_obj.constraints.new('COPY_TRANSFORMS')
		const.target = arma_obj
		if p_bone:
			const.subtarget = p_bone.name
		const.head_tail = 0.5
		bpy.ops.object.select_all(action='DESELECT')
		sphere_obj.select_set(True)
		bpy.ops.object.visual_transform_apply()
		sphere_obj.constraints.remove(const)
		if p_bone:
			bone = p_bone.bone
			sphere_obj.scale.y = (bone.head_local - bone.tail_local).length * 0.5
			sphere_obj.scale.x = sphere_obj.scale.z = self.shape_size
		else:
			sphere_obj.scale.x = sphere_obj.scale.y = sphere_obj.scale.z = self.shape_size
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		sphere_obj.display_type = 'WIRE'
		return sphere_obj

	def execute(self, context):
		pre_active_obj = context.active_object
		pre_mode = pre_active_obj.mode
		pre_cursor_location = context.scene.cursor.location[:]
		arm_obj = pre_active_obj
		arm = arm_obj.data
		no_parent_count = 0
		selected = context.selected_pose_bones[:]
		bones = []
		for bone in selected:
			if bone.parent:
				if not bone.parent in selected:
					base_bone = bone.parent
					no_parent_count += 1
			else:
				no_parent_count += 1
			bones.append(bone)
		if no_parent_count != 1:
			self.report(type={'ERROR'}, message="Please execute with connected bones")
			return {'CANCELLED'}
		bpy.ops.object.mode_set(mode='OBJECT')
		if base_bone:
			base_sphere = self.set_sphere(context, base_bone, arm_obj, is_base=True)
		else:
			base_sphere = self.set_sphere(context, None, arm_obj, is_base=True)
		base_sphere.select_set(True)
		arm_obj.select_set(True)
		bpy.context.view_layer.objects.active = arm_obj
		if base_bone:
			arm.bones.active = bone.bone
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.object.parent_set(type='BONE')
		else:
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
		bpy.ops.object.mode_set(mode='OBJECT')
		base_sphere.name = "Rigid Origin"
		pairs = []
		for bone in bones:
			sphere = self.set_sphere(context, bone, arm_obj, is_base=False)
			const = bone.constraints.new('DAMPED_TRACK')
			const.target = sphere
			sphere.name = "RigidBody"
			bpy.ops.object.empty_add(type=self.empty_display_type, radius=1, align='WORLD', location=(0, 0, 0))
			empty_obj = context.active_object
			const = empty_obj.constraints.new('COPY_TRANSFORMS')
			const.target = arm_obj
			const.subtarget = bone.name
			bpy.ops.object.select_all(action='DESELECT')
			empty_obj.select_set(True)
			bpy.ops.object.visual_transform_apply()
			empty_obj.constraints.remove(const)
			empty_obj.scale = (self.constraints_size, self.constraints_size, self.constraints_size)
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			empty_obj.name = "Rigid Constraints"
			bpy.ops.rigidbody.constraint_add()
			rg_c_setting = empty_obj.rigid_body_constraint
			rg_c_setting.type = 'GENERIC'
			for ax in ['x', 'y', 'z']:
				exec(f"rg_c_setting.use_limit_lin_{ax} = True")
				exec(f"rg_c_setting.limit_lin_{ax}_lower = 0")
				exec(f"rg_c_setting.limit_lin_{ax}_upper = 0")
				exec(f"rg_c_setting.use_limit_ang_{ax} = True")
				exec(f"rg_c_setting.limit_ang_{ax}_lower = math.radians({self.rot_limit}) * -1")
				exec(f"rg_c_setting.limit_ang_{ax}_upper = math.radians({self.rot_limit})")
			rg_c_setting.limit_ang_y_lower = rg_c_setting.limit_ang_y_upper = 0
			pairs.append((bone, sphere, empty_obj))
		for bone, shape, const in pairs:
			const.rigid_body_constraint.object1 = shape
			bpy.ops.object.select_all(action='DESELECT')
			const.select_set(True)
			arm_obj.select_set(True)
			bpy.context.view_layer.objects.active = arm_obj
			if bone.parent:
				if bone.parent in selected:
					for a, b, c in pairs:
						if bone.parent == a:
							const.rigid_body_constraint.object2 = b
							arm.bones.active = bone.parent.bone
							break
				else:
					const.rigid_body_constraint.object2 = base_sphere
			else:
				const.rigid_body_constraint.object2 = base_sphere
			if self.is_parent_shape:
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.object.parent_set(type='BONE')
				bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		pre_active_obj.select_set(True)
		bpy.context.view_layer.objects.active = pre_active_obj
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SetIKRotationLimitByPose(bpy.types.Operator):
	bl_idname = "pose.set_ik_rotation_limit_by_pose"
	bl_label = "Convert Current Rotation to Limit"
	bl_description = "Create limit rotation constraint or set IK's rotation limit based on selected bones' current rotation"
	bl_options = {'REGISTER', 'UNDO'}

	mode : EnumProperty(name="Limit Rotation", items=[('CONST', "Constraint", "", 2),('IK', "IK", "", 1)])
	other_side : EnumProperty(name="Limit of opposite direction", items=[
		('SYMMETRY', "Symmetrized", "", 1),('LIMIT_180', "No Limit", "", 2),('LIMIT_0', "Limit All", "", 3)])
	use_x : BoolProperty(name="X Axis", default=True)
	use_y : BoolProperty(name="Y Axis", default=True)
	use_z : BoolProperty(name="Z Axis", default=True)
	is_clear_rot : BoolProperty(name="Reset Bones Rotation", default=True)

	@classmethod
	def poll(cls, context):
		if context.selected_pose_bones:
			return True
		return False
	def draw(self, context):
		self.layout.prop(self, 'mode')
		box = self.layout.box()
		row = box.row()
		row.label(text="Limit")
		for p in ['use_x','use_y','use_z']:
			row.prop(self, p)
		row = box.split(factor=0.6)
		row.label(text="Limit of opposite direction")
		row.prop(self, 'other_side', text="")
		self.layout.prop(self, 'is_clear_rot')

	def execute(self, context):
		pre_active_obj = context.active_object
		pre_mode = pre_active_obj.mode
		for bone in context.selected_pose_bones:
			pre_rotation_mode = bone.rotation_mode
			bone.rotation_mode = 'ZYX'
			rot = bone.rotation_euler.copy()
			bone.rotation_mode = pre_rotation_mode
			if self.mode == 'IK':
				if self.use_x:
					bone.use_ik_limit_x = True
					rot.x = round(rot.x, 2)
					if 0 <= rot.x:
						bone.ik_max_x = rot.x
						if self.other_side == "SYMMETRY": bone.ik_min_x = -rot.x
						elif self.other_side == "LIMIT_180": bone.ik_min_x = -3.14159
						elif self.other_side == "LIMIT_0": bone.ik_min_x = 0
					else:
						bone.ik_min_x = rot.x
						if self.other_side == "SYMMETRY": bone.ik_max_x = -rot.x
						elif self.other_side == "LIMIT_180": bone.ik_max_x = 3.14159
						elif self.other_side == "LIMIT_0": bone.ik_max_x = 0
				if self.use_y:
					bone.use_ik_limit_y = True
					rot.y = round(rot.y, 2)
					if 0 <= rot.y:
						bone.ik_max_y = rot.y
						if self.other_side == "SYMMETRY": bone.ik_min_y = -rot.y
						elif self.other_side == "LIMIT_180": bone.ik_min_y = -3.14159
						elif self.other_side == "LIMIT_0": bone.ik_min_y = 0
					else:
						bone.ik_min_y = rot.y
						if self.other_side == "SYMMETRY": bone.ik_max_y = -rot.y
						elif self.other_side == "LIMIT_180": bone.ik_max_y = 3.14159
						elif self.other_side == "LIMIT_0": bone.ik_max_y = 0
				if self.use_z:
					bone.use_ik_limit_z = True
					rot.z = round(rot.z, 2)
					if 0 <= rot.z:
						bone.ik_max_z = rot.z
						if self.other_side == "SYMMETRY": bone.ik_min_z = -rot.z
						elif self.other_side == "LIMIT_180": bone.ik_min_z = -3.14159
						elif self.other_side == "LIMIT_0": bone.ik_min_z = 0
					else:
						bone.ik_min_z = rot.z
						if self.other_side == "SYMMETRY": bone.ik_max_z = -rot.z
						elif self.other_side == "LIMIT_180": bone.ik_max_z = 3.14159
						elif self.other_side == "LIMIT_0": bone.ik_max_z = 0
			elif self.mode == 'CONST':
				rot_const = None
				for const in bone.constraints:
					if const.type == 'LIMIT_ROTATION':
						rot_const = const
				if not rot_const:
					rot_const = bone.constraints.new('LIMIT_ROTATION')
				rot_const.owner_space = 'LOCAL'
				if self.use_x:
					rot_const.use_limit_x = True
					rot.x = round(rot.x, 2)
					if 0 <= rot.x:
						rot_const.max_x = rot.x
						if self.other_side == "SYMMETRY": rot_const.min_x = -rot.x
						elif self.other_side == "LIMIT_180": rot_const.min_x = -3.14159
						elif self.other_side == "LIMIT_0": rot_const.min_x = 0
					else:
						rot_const.min_x = rot.x
						if self.other_side == "SYMMETRY": rot_const.max_x = -rot.x
						elif self.other_side == "LIMIT_180": rot_const.max_x = 3.14159
						elif self.other_side == "LIMIT_0": rot_const.max_x = 0
				if self.use_y:
					rot_const.use_limit_y = True
					rot.y = round(rot.y, 2)
					if 0 <= rot.y:
						rot_const.max_y = rot.y
						if self.other_side == "SYMMETRY": rot_const.min_y = -rot.y
						elif self.other_side == "LIMIT_180": rot_const.min_y = -3.14159
						elif self.other_side == "LIMIT_0": rot_const.min_y = 0
					else:
						rot_const.min_y = rot.y
						if self.other_side == "SYMMETRY": rot_const.max_y = -rot.y
						elif self.other_side == "LIMIT_180": rot_const.max_y = 3.14159
						elif self.other_side == "LIMIT_0": rot_const.max_y = 0
				if self.use_z:
					rot_const.use_limit_z = True
					rot.z = round(rot.z, 2)
					if 0 <= rot.z:
						rot_const.max_z = rot.z
						if self.other_side == "SYMMETRY": rot_const.min_z = -rot.z
						elif self.other_side == "LIMIT_180": rot_const.min_z = -3.14159
						elif self.other_side == "LIMIT_0": rot_const.min_z = 0
					else:
						rot_const.min_z = rot.z
						if self.other_side == "SYMMETRY": rot_const.max_z = -rot.z
						elif self.other_side == "LIMIT_180": rot_const.max_z = 3.14159
						elif self.other_side == "LIMIT_0": rot_const.max_z = 0
		if self.is_clear_rot:
			bpy.ops.pose.rot_clear()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# サブメニュー #
################

class BoneNameMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_pose_specials_bone_name"
	bl_label = "Change Bone Name"

	def draw(self, context):
		self.layout.operator(RemoveBoneNameSerialNumbers.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator('armature.rename_bone_regular_expression', icon="PLUGIN")#VIEW3D_MT_armature_special で定義
		self.layout.operator(RenameBoneNameEnd.bl_idname, icon="PLUGIN")
		if context.preferences.view.language == 'ja_JP':
			self.layout.operator(RenameBoneNameEndJapanese.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator('object.copy_bone_name', icon='PLUGIN')#BONE_PT_context_bone で定義

class SpecialsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_pose_specials_specials"
	bl_label = "Advanced Manipulation"

	def draw(self, context):
		self.layout.operator(SplineAnnotation.bl_idname, icon="PLUGIN")
		self.layout.operator(SetRigidBodyBone.bl_idname, icon="PLUGIN")
		self.layout.operator(CreateCustomShape.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SetSlowParentBone.bl_idname, icon="PLUGIN")
		self.layout.operator(SetIKRotationLimitByPose.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreateWeightCopyMesh.bl_idname, icon="PLUGIN")

def gp_object_poll(self, object):
    return object.type == 'GPENCIL'
################
# クラスの登録 #
################

classes = [
	CreateCustomShape,
	CreateWeightCopyMesh,
	SplineAnnotation,
	SetSlowParentBone,
	RenameBoneNameEnd,
	RenameBoneNameEndJapanese,
	TogglePosePosition,
	CopyConstraintsMirror,
	RemoveBoneNameSerialNumbers,
	SetRigidBodyBone,
	SetIKRotationLimitByPose,
	BoneNameMenu,
	SpecialsMenu
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.scramble_addon_gp_object = bpy.props.PointerProperty(
	type=bpy.types.Object,
	poll=gp_object_poll
	)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.scramble_addon_gp_object

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
		self.layout.operator(CopyConstraintsMirror.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(SpecialsMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(BoneNameMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		if (context.object.data.pose_position == 'POSE'):
			self.layout.operator(TogglePosePosition.bl_idname, text="Switch Position (Current: Pose)", icon="PLUGIN")
		else:
			self.layout.operator(TogglePosePosition.bl_idname, text="Switch Position (Current: Rest)", icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
