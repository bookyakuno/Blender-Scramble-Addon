# 「3Dビュー」エリア > プロパティ >     レイヤーボタンがあるパネル
# "3D View" Area > Propaties > Layer Buttons Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class CollectionShowHide(bpy.types.Operator): #
	bl_idname = "view3d.collection_show_hide"
	bl_label = "Toggle Show/Hide Collections"
	bl_description = "Shows or hides collection"
	bl_options = {'REGISTER'}

	name : StringProperty(name="Collection Name")
	parent_names : StringProperty(name="Parent-Collections\' Names")
	exclusive : BoolProperty(name="Hide Others", default=False)
	wire : BoolProperty(name="Wireframe", default=False)

	def execute(self, context):
		par_names = [x for x in self.parent_names.split(",") if not len(x) == 0]
		if not par_names:
			coll = context.view_layer.layer_collection.children[self.name]
			if (self.exclusive):
				for col in context.view_layer.layer_collection.children:
					if col.name != self.name: col.hide_viewport = True
		else:
			par = context.view_layer.layer_collection.children[par_names[0]]
			if (self.exclusive):
				for col in context.view_layer.layer_collection.children:
					if col.name != par_names[0]: col.hide_viewport = True
			try:
				for name in par_names[1:]:
					if (self.exclusive):
						for col in par.children:
							if col.name != name: col.hide_viewport = True
					par = par.children[name]
			except IndexError:
				pass		
			coll = par.children[self.name]
		if (self.exclusive):
			coll.hide_viewport = False
			return {'FINISHED'}
		if (self.wire):
			for obj in coll.collection.objects:
				obj.show_all_edges = True
				if obj.display_type != 'WIRE':
					obj.display_type = 'WIRE'
				else:
					obj.display_type = 'TEXTURED'
		else:
			coll.hide_viewport = not coll.hide_viewport
		return {'FINISHED'}
	def invoke(self, context, event):
		if (event.shift):
			self.exclusive = False
			self.wire = True
		return self.execute(context)

def flatten(layer_collection, parent_name=""):
	flat = []
	for coll in layer_collection.children:
		if len(coll.children) > 0:
			flat.append((coll, f"{parent_name},{layer_collection.name}"))
			flat += flatten(coll, f"{parent_name},{layer_collection.name}")
		else:
			flat.append((coll, f"{parent_name},{layer_collection.name}"))
			flat.append((None, None))
	return flat

def GetIcon(layer_collection):
	if layer_collection.hide_viewport:
		return "HIDE_ON"
	for obj in layer_collection.collection.objects[:5]:
		if (obj.display_type != 'WIRE'):
			return "HIDE_OFF"
	else:
		return 'SHADING_WIRE'


################
# クラスの登録 #
################

classes = [
	CollectionShowHide
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
		#coll_dic = {c.name:  for }
		if (context.object):
			if (context.object.type == 'ARMATURE'):
				self.layout.label(text="Bone Layer")
				col = self.layout.column()
				col.scale_y = 0.7
				col.prop(context.object.data, 'layers', text="")
		self.layout.separator(factor=1.0)
		if context.active_object:
			obj_par_collection = context.active_object.users_collection[0].name
		else:
			obj_par_collection = ""
		for col in context.view_layer.layer_collection.children:
			row = self.layout.row()
			if col.name == obj_par_collection:
				row.label(icon='KEYTYPE_KEYFRAME_VEC')
			else:
				row.label(icon='HANDLETYPE_AUTO_VEC')
			op1 = row.operator(CollectionShowHide.bl_idname, text=f"{col.name}", icon='NONE', emboss=False)
			op1.name, op1.parent_names = [col.name, ""]
			op1.exclusive, op1.wire = [True, False]
			op2 = row.operator(CollectionShowHide.bl_idname, text="", icon=GetIcon(col), emboss=False)
			op2.name, op2.parent_names = [col.name, ""]
			op2.exclusive, op2.wire = [False, False]
			flatten_nest = flatten(col)[:-1]
			for coll in flatten_nest:
				if coll[0] == None:
					self.layout.separator(factor=0.3)
				else:
					row = self.layout.row()
					if coll[0].name == obj_par_collection:
						row.label(icon='KEYTYPE_KEYFRAME_VEC')
					else:
						row.label(icon='HANDLETYPE_AUTO_VEC')				
					op1 = row.operator(CollectionShowHide.bl_idname, text=f"{coll[0].name}", icon='NONE', emboss=False)
					op1.name, op1.parent_names = [coll[0].name, coll[1]]
					op1.exclusive, op1.wire = [True, False]
					op2 = row.operator(CollectionShowHide.bl_idname, text="", icon=GetIcon(coll[0]), emboss=False)
					op2.name, op2.parent_names = [coll[0].name, coll[1]]
					op2.exclusive, op2.wire = [False, False]
			self.layout.separator(factor=1.0)
		self.layout.label(text="(shift: Toggle Wireframe)")

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
