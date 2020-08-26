# 「プロパティ」エリア > 「アーマチュアデータ」タブ > 「ボーングループ」パネル
# "Propaties" Area > "Armature" Tab > "Bone Groups" Panel

import bpy

################
# オペレーター #
################

class BoneGroupOnlyShow(bpy.types.Operator):
	bl_idname = "pose.bone_group_only_show"
	bl_label = "Show only bone in this bones group"
	bl_description = "Group active on bones and bones of other hide"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="Invert", default=False)
	
	@classmethod
	def poll(cls, context):
		if (context.active_object):
			if (context.active_object.type == 'ARMATURE'):
				if (len(context.active_object.pose.bone_groups)):
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		for pbone in obj.pose.bones:
			bone = arm.bones[pbone.name]
			for i in range(len(arm.layers)):
				if (arm.layers[i] and bone.layers[i]):
					if (not pbone.bone_group):
						if (not self.reverse):
							bone.hide = True
						else:
							bone.hide = False
						break
					if (obj.pose.bone_groups.active.name == pbone.bone_group.name):
						if (not self.reverse):
							bone.hide = False
						else:
							bone.hide = True
					else:
						if (not self.reverse):
							bone.hide = True
						else:
							bone.hide = False
					break
		return {'FINISHED'}

class BoneGroupShow(bpy.types.Operator):
	bl_idname = "pose.bone_group_show"
	bl_label = "Show bone in bone group"
	bl_description = "Active bone group show or hide"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="Invert", default=False)
	
	@classmethod
	def poll(cls, context):
		if (context.active_object):
			if (context.active_object.type == 'ARMATURE'):
				if (len(context.active_object.pose.bone_groups)):
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		arm = obj.data
		for pbone in obj.pose.bones:
			bone = arm.bones[pbone.name]
			for i in range(len(arm.layers)):
				if (arm.layers[i] and bone.layers[i]):
					if (pbone.bone_group):
						if (obj.pose.bone_groups.active.name == pbone.bone_group.name):
							if (not self.reverse):
								bone.hide = False
							else:
								bone.hide = True
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	BoneGroupOnlyShow,
	BoneGroupShow
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
	for id in bpy.context.preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row()
		sub = row.row(align=True)
		sub.operator(BoneGroupShow.bl_idname, icon='RESTRICT_VIEW_OFF', text="Show").reverse = False
		sub.operator(BoneGroupShow.bl_idname, icon='RESTRICT_VIEW_ON', text="Hide").reverse = True
		sub = row.row(align=True)
		sub.operator(BoneGroupOnlyShow.bl_idname, icon='RESTRICT_VIEW_OFF', text="Only Show").reverse = False
		sub.operator(BoneGroupOnlyShow.bl_idname, icon='RESTRICT_VIEW_ON', text="Only Hide").reverse = True
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
