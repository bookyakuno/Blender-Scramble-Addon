bl_info = {
    "name": "Mirror Mirror Tool",
    "author": "Robert Fornof & MX",
    "version": (1, 4),
    "blender": (2, 71, 0),
    "location": "View3D > Tool_Tab> Mirror",
    "description": "Set mirror",
    "warning": "",
    "wiki_url": "",
    "category": "Object"}

import bpy
from bpy.app.handlers import persistent


#------------------- FUNCTIONS------------------------------

# Do the Basic Union, Difference and Intersection Operations
def Operation(context,_operation):
#         ''' select the object, then select what you want it's mirror object to be '''
        #select 2 context object
    
        try:
            # select objects
     
            if(len(bpy.context.selected_objects)) == 1 : # one is selected , add mirror mod immediately to that object#
                modifier_ob = bpy.context.active_object         
                print("one is selected")
                mirror_mod = modifier_ob.modifiers.new("mirror_mirror","MIRROR")
          
            #   if modifier_ob.type !='MESH' and modifier_ob.type !="CURVE":
          #      mirror_ob = modifier_ob # set to mirror_ob , hope the other one is a mesh
           #     mirror_ob.select = False
            #    modifier_ob = bpy.context.selected_objects[0]
            else:
                #mirror_ob
                mirror_ob = bpy.context.active_object         # last ob selected
                mirror_ob.select = False # pop modifier_ob from sel_stack
                print("popped")
                
                #modifier_ob
                modifier_ob = bpy.context.selected_objects[0]
                print("Modifier object:" +str(modifier_ob.name))
                

      
                #modifier_ob.select=1
                
                print("mirror_ob",mirror_ob)
                print("modifier_ob",modifier_ob)
           
            # put mirror modifier on modifier_ob 
            
                mirror_mod = modifier_ob.modifiers.new("mirror_mirror","MIRROR")
            
            # set mirror object to mirror_ob
                mirror_mod.mirror_object = mirror_ob
                
            if _operation == "MIRROR_X":
                mirror_mod.use_x = True
                mirror_mod.use_y = False
                mirror_mod.use_z = False
            elif _operation == "MIRROR_Y":
                mirror_mod.use_x = False
                mirror_mod.use_y = True
                mirror_mod.use_z = False
            elif _operation == "MIRROR_Z":
                mirror_mod.use_x = False
                mirror_mod.use_y = False
                mirror_mod.use_z = True
            
                #selection at the end -add back the deselected mirror modifier object
            mirror_ob.select= 1
            modifier_ob.select=1
            bpy.bpy.context.view_layer.objects.active = modifier_ob
            print("Selected" + str(modifier_ob)) # modifier ob is the active ob
                #mirror_ob.select = 0
            #one = bpy.context.selected_objects[0]
            #bpy.data.objects[one.name].select = 1
        except: 
                print("please select exactly two objects, the last one gets the modifier unless its not a mesh")
           
#------------------- OPERATOR CLASSES ------------------------------                
# Mirror Tool                 



class MirrorX(bpy.types.Operator):
    """This adds an X mirror to the selected object"""
    bl_idname = "object.mirror_mirror_x"
    bl_label = "Mirror X"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        Operation(context,"MIRROR_X")
        return {'FINISHED'}
    
    
class MirrorY(bpy.types.Operator):
#     """This  adds a Y mirror modifier"""
    bl_idname = "object.mirror_mirror_y"
    bl_label = "Mirror Y"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        Operation(context,"MIRROR_Y")
        return {'FINISHED'}

class MirrorZ(bpy.types.Operator):
    """This  add a Z mirror modifier"""
    bl_idname = "object.mirror_mirror_z"
    bl_label = "Mirror Z"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        Operation(context,"MIRROR_Z")
        return {'FINISHED'}


class off_mirror_miller(bpy.types.Operator):
    """This  add a Z mirror modifier"""
    bl_idname = "object.off_mirror_miller"
    bl_label = "off_mirror_miller"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
#         Operation(context,"MIRROR_Z")
        if bpy.context.object.modifiers["Miller"].show_viewport == True:
            bpy.context.object.modifiers["Miller"].show_viewport = False
#         elif:
#             bpy.context.object.modifiers["Miller"].show_viewport = True
        return {'FINISHED'}








#------------------- MENU CLASSES ------------------------------  

class MirrorMenu(bpy.types.Menu):
    bl_label = "Mirror_Mirror_Tool"
    bl_idname = "OBJECT_MT_mirror"
    def draw(self, context):
        layout = self.layout

        self.layout.operator(MirrorTool.bl_idname,icon = "ZOOMIN")
       
class MirrorTab(bpy.types.Panel):
    "[note]: Add a mirror on the x, y , or z axis using : ALT+SHIFT+X , ALT+SHIFT+Y, ALT+SHIFT+Z in object mode"
    bl_label = "Mirror"
    bl_idname = "Mirror_Mirror_Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
#     bl_category = "Mirror"
    bl_context = "objectmode"
    bl_category = "Create"

    
    def draw(self,context):
        self.layout.label("Mirror Axis:",icon = "MODIFIER")    
        self.layout.operator(MirrorX.bl_idname ,icon = "ZOOMIN")
        self.layout.operator(MirrorY.bl_idname ,icon = "ZOOMIN")
        self.layout.operator(MirrorZ.bl_idname ,icon = "ZOOMIN")
        #self.layout.operator(MirrorX.bl_idname ,icon = "ZOOMOUT")
      
        self.layout.separator()  
    #---------- Tree Viewer--------------
def VIEW3D_MirrorMenu(self, context):
    self.layout.menu(MirrorMenu.bl_idname)
    
#------------------- REGISTER ------------------------------      
addon_keymaps = []
# 
# def register():
# 
#     
#     # Operators
# 
#     bpy.utils.register_class(MirrorX)
#     bpy.utils.register_class(MirrorY)
#     bpy.utils.register_class(MirrorZ)
#     #Append 3DVIEW Menu
#     #bpy.utils.register_class(MirrorMenu)
#     #bpy.types.VIEW3D_MT_object.append(VIEW3D_MirrorMenu)
#     
#     # Append 3DVIEW Tab
#     bpy.utils.register_class(MirrorTab)
#     


def register():
	
    bpy.utils.register_module(__name__)
	

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(MirrorX.bl_idname, 'FOUR', 'PRESS', ctrl=True, oskey = True)
    addon_keymaps.append((km, kmi))

    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(MirrorY.bl_idname, 'Y', 'PRESS', alt=True, shift = True)
    addon_keymaps.append((km, kmi))

    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(MirrorZ.bl_idname, 'Z', 'PRESS', alt=True, shift = True)
    addon_keymaps.append((km, kmi))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(off_mirror_miller.bl_idname, 'F', 'PRESS', alt=True, shift = True)
    addon_keymaps.append((km, kmi))
    
    
    
    
    
    
# 
# def unregister():
#     
#     #bpy.utils.unregister_class(MirrorMenu)
#     bpy.utils.unregister_class(MirrorTab)
#     #bpy.types.VIEW3D_MT_object.remove(VIEW3D_MirrorMenu)
#         
#     #Operators
#     bpy.utils.unregister_class(MirrorX)
#     bpy.utils.unregister_class(MirrorY)
#     bpy.utils.unregister_class(MirrorZ)
#             
def unregister():
	
    bpy.utils.unregister_module(__name__)
	


   # bpy.app.handlers.scene_update_post.remove(HandleScene)
    #bpy.types.VIEW3D_MT_object.remove(VIEW3D_MirrorMenu)
    
    # Keymapping
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    

if __name__ == "__main__":
    register()


