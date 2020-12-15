# 「プロパティ」エリア > 「シーン」タブ > 「剛体ワールド」パネル
# "Propaties" Area > "Scene" Tab > "Rigid Body World" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class WorldReset(bpy.types.Operator):
	bl_idname = "rigidbody.world_reset"
	bl_label = "Re-create Rigid Body World"
	bl_description = "Re-create rigid body world with same settings"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if (not context.scene.rigidbody_world):
			return False
		return context.scene.rigidbody_world.enabled
	def execute(self, context):
		collection = context.scene.rigidbody_world.collection
		constraints = context.scene.rigidbody_world.constraints
		time_scale = context.scene.rigidbody_world.time_scale
		steps_per_second = context.scene.rigidbody_world.steps_per_second
		use_split_impulse = context.scene.rigidbody_world.use_split_impulse
		solver_iterations = context.scene.rigidbody_world.solver_iterations
		frame_start = context.scene.rigidbody_world.point_cache.frame_start
		frame_end = context.scene.rigidbody_world.point_cache.frame_end

		bpy.ops.rigidbody.world_remove()
		bpy.ops.rigidbody.world_add()

		context.scene.rigidbody_world.collection = collection
		context.scene.rigidbody_world.constraints = constraints
		context.scene.rigidbody_world.time_scale = time_scale
		context.scene.rigidbody_world.steps_per_second = steps_per_second
		context.scene.rigidbody_world.use_split_impulse = use_split_impulse
		context.scene.rigidbody_world.solver_iterations = solver_iterations
		context.scene.rigidbody_world.point_cache.frame_start = frame_start
		context.scene.rigidbody_world.point_cache.frame_end = frame_end
		return {'FINISHED'}

class SyncFrames(bpy.types.Operator):
	bl_idname = "rigidbody.sync_frames"
	bl_label = "Match Rigid Body World's Start/End to Rendering's ones"
	bl_description = "Change rigid body world's start / end frames to the rendering's start / end frames"
	bl_options = {'REGISTER', 'UNDO'}

	startOffset : IntProperty(name="Start Offset", default=0, step=1)
	endOffset : IntProperty(name="End Offset", default=0, step=1)

	@classmethod
	def poll(cls, context):
		if context.scene.rigidbody_world:
			if context.scene.rigidbody_world.point_cache:
				return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		box = self.layout.box()
		sp = box.split(factor=0.55)
		row = sp.row()
		row.label(text="Start Frame")
		row.label(text=f":  {context.scene.frame_start} + {self.startOffset}")
		sp.prop(self, 'startOffset')
		sp = box.split(factor=0.55)
		row = sp.row()
		row.label(text="End Frame")
		row.label(text=f":  {context.scene.frame_end} + {self.endOffset}")
		sp.prop(self, 'endOffset')

	def execute(self, context):
		rigidbody_world = context.scene.rigidbody_world
		point_cache = rigidbody_world.point_cache
		point_cache.frame_start = context.scene.frame_start + self.startOffset
		point_cache.frame_end = context.scene.frame_end + self.endOffset
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	WorldReset,
	SyncFrames
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
		row.operator(WorldReset.bl_idname, icon='PLUGIN', text="Re-create")
		if context.scene.rigidbody_world:
			if context.scene.rigidbody_world.point_cache:
				row_item = row.row(align=True)
				row_item.prop(context.scene.rigidbody_world.point_cache, 'frame_start')
				row_item.prop(context.scene.rigidbody_world.point_cache, 'frame_end')
				row_item.operator(SyncFrames.bl_idname, icon='LINKED', text="")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
