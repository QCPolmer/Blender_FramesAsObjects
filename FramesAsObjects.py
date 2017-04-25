##################################
################  notes:
####

#https://docs.blender.org/api/blender_python_api_2_65_5/info_tutorial_addon.html
# Outline Copied from animation_animall.py (search blender files)
# HELP
# https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Interface
#This is the right way to copy object instances here
                #http://blender.stackexchange.com/questions/45099/duplicating-a-mesh-object
                '''
                bpy.context.scene.objects[tmpObs[i].CustAnim_FramePool].select = True;
                tmpSelect = True;
                for c_o in bpy.context.scene.objects[tmpObs[i].CustAnim_FramePool].children:
                    if c_o.hide == False:
                       if c_o.select == True:
                           tmpSelect = False;
                for c in bpy.context.scene.objects[tmpObs[i].CustAnim_FramePool].children:
                    if c.hide == False :
                        c.select = tmpSelect; 
                        '''
                '''        
                bpy.context.scene.frame_set(  c_frame );
                                SiblingLerp( o, o, c, 1, 2, 2)
                                # https://docs.blender.org/api/blender_python_api_2_65_9/info_quickstart.html#animation
                                # https://docs.blender.org/api/blender_python_api_2_77a_release/bpy.types.bpy_struct.html?highlight=keyframe_insert#bpy.types.bpy_struct.keyframe_insert
                                
                                o.keyframe_insert("location", frame = bpy.context.scene.frame_current)
                                o.keyframe_insert("scale", frame = bpy.context.scene.frame_current)
                                o.keyframe_insert("rotation_euler", frame = bpy.context.scene.frame_current)        
                 '''
                        
# end notes
#################
#############################           


###########################################################                        
#Copyright (c) 2017 Harrison Mansolf
#This code is open source under the MIT license.
############################################################
'''
    About this pluggin:
        
    - This was conceived and coded to create a simpler 
        animation system that could coexist with 
        the built-in animation system
    - Currently works with: Loc/Rot/Scale keyframes 
        and armature poses
    - It works by creating a specially named 
        animation object in the scene once a frame is added
        (the animation object is an empty)
        then adding the frames to the animation object as 
        child objects with the frames in the frame-objects'
        name.
        ( the naming format is 'FRAME_NUMBER@ObjName' 
            EG: 00023@Cube.001 )
        once the frames are added, they can be manipulated
        or deleted like any other object,
        meaning all frames of a object can be manipulated 
        from a single frame of animation. 
    - Optional one button convert to and from 
        standard animations.
    - This pluggin also includes a tab to select various 
        frame-objects, or make them visible/invisible 
        based on their location in the timeline. 
        
    How to use: 
        
    - Install FramesAsObjects.py as an addon
        https://blender.stackexchange.com/questions/1688/installing-an-addon  
    - Select an object or armature in object mode 
        (RECOMMENDED: duplicate the object, and use the duplicate)
    - Go to the Animation tab-> FramesAsObjects_ForObject
    - Turn on 'FramesAsObjects ON' AND 'F.A.O. Animate this Object'
        (both can be turned off at any time without loosing anything)
    - Type in a name of the animation
    - Click 'Make Frame-Object' to add frame
        (frame will be added at current frame)
        (WARNING: DUPLICATE AN OBJECT IF IT ALREADY HAS AN ANIMATION 
           AND CLICK: "clear standard anim"!!)
       A Frame-Object, which is a instance of the selected object
        will be created at the objects location.
        the frame-object can be moved, rotated, resized or deleted. 
    - At any time, select the animated-object
        and click 'Bake FramesAsObjs Anim'
        to convert the object-Frames into an actual action
        (WARNING: this may overwrite an action by the same name)
    - ALTERNATIVELY:
         Select an object with a standard animation
         Type an animation name into the 
            Animation tab-> FramesAsObjects_ForObject
         panel, 
         and click 'Make F.A.O. from Frames'
         then an FramesAsObjects animation will be generated
         from whatever action is active on on object
         (WARNING: DOING THIS REMOVES AN OBJECTS STANDARD ANIMATION
            IT IS RECOMMENDED TO DUPLICATE AN OBJECT BEFORE DOING THIS)

'''
                        
bl_info = {
    'name': 'FramesAsObjects',
    'author': 'Harrison Mansolf <harrisonMansolf@gmail.com>',
    'version': (0, .1),
    "blender": (2, 69, 7),
    'location': 'Tool bar > Animation tab > FramesAsObjects',
    'description': 'Allows objects to be used as animation frames',
    'warning': 'ALPHA ADDON, USE AT YOUR OWN RISK!!!',
    "support": "TESTING",
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Animation/AnimAll',
    'tracker_url': 'https://developer.blender.org/T24874',
    'category': 'Animation'}


import bpy
from bpy.props import *



ZERO_PADDING_FOR_FRAMES = 6

class View3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    bl_label = 'FramesAsObjects'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


def initSceneProperties():
    bpy.types.Scene.MoveFrames= IntProperty(
        name = "Shift this many frames:", default = 0)
    bpy.types.Scene.ShowThisManyFrames= IntProperty(
        name = "By this many frames", default = 0)
    bpy.types.Scene.Cust_Anim_SYSTEM_ON= BoolProperty(
        name = "FramesAsObjects ON", default = True)
    return
initSceneProperties()

class MoveFrames(bpy.types.Operator):
    bl_idname = "mesh.cust_anim_move_frame" #NAME HERE
    bl_label = "Shift frame-object time:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            if( not tmpObs[i].name.split("@")[0].lstrip('-').isdigit() ):
                tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Frames-Objects Selected!");
        else:
            for o in tmpObs :
                o.name = str( int( int( o.name.split("@")[0] ) + \
                   bpy.context.scene.MoveFrames ) ).zfill(ZERO_PADDING_FOR_FRAMES) + "@" + o.name.split("@")[1] 
            
        return {"FINISHED"}
bpy.utils.register_class(MoveFrames)

def recursiveFullCopyAnimObject( o):
    
    clonedObj = o.copy()
    #clonedObj.data = o.data.copy() #include this if whole copy is needed
    #clonedObj.animation_data_clear()
    bpy.context.scene.objects.link( clonedObj )
    clonedObj.location = o.location
    
    #clonedObj["CustAnim_FramePool"] = "";
    #clonedObj["CustAnim_Obj_On"] = False;
    #clonedObj.hide_render = True;
    if o.parent:
        clonedObj.parent =  o.parent;
        clonedObj.matrix_parent_inverse = o.parent.matrix_world.inverted()
    #clonedObj.name = str( bpy.context.scene.frame_current \
     #  ).zfill(ZERO_PADDING_FOR_FRAMES) + "@" + o.name
       
    for c in o.children:
        c_copy = recursiveFullCopyAnimObject( c);
        c_copy.parent = clonedObj
        c_copy.matrix_parent_inverse = clonedObj.matrix_world.inverted()
    if not bpy.context.scene.objects.find(o.CustAnim_FramePool) == -1:
        tmpPool = recursiveFullCopyAnimObject(\
            bpy.context.scene.objects[o.CustAnim_FramePool]);
        o.CustAnim_FramePool = tmpPool.name;
    return clonedObj
class DuplicateCustAnimObj(bpy.types.Operator):
    bl_idname = "mesh.cust_anim_duplicate_obj" #NAME HERE
    bl_label = "Duplicate:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
            if bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1:
                if tmpObs[i].CustAnim_FramePool.strip() != "":
                #add object if not existing
                    emptyOb = bpy.data.objects.new( "empty", None );
                    emptyOb.name = tmpObs[i].CustAnim_FramePool;
                    bpy.context.scene.objects.link( emptyOb );
                    if tmpObs[i].parent: emptyOb.parent = tmpObs[i].parent
                        
                else:
                    tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Objects With 'F.A.O. animate this object' on, and a animation name selected!");
        else:
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                recursiveFullCopyAnimObject( o)
                   
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpObs : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(DuplicateCustAnimObj)
class SelectVisibleFramesCustAnimObj(bpy.types.Operator):
    bl_idname = "mesh.cust_anim_select_visible_frames" #NAME HERE
    bl_label = "Toggle Select Frames-Objects:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
            if bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1:
                tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Objects With 'F.A.O. animate this object' on, and a animation name selected!");
        else:
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                bpy.context.scene.objects[tmpObs[i].CustAnim_FramePool].select = True;
                tmpSelect = True;
                for c_o in bpy.context.scene.objects[tmpObs[i].CustAnim_FramePool].children:
                    if c_o.hide == False:
                       if c_o.select == True:
                           tmpSelect = False;
                for c in bpy.context.scene.objects[tmpObs[i].CustAnim_FramePool].children:
                    if c.hide == False :
                        c.select = tmpSelect;   
                
                   
        return {"FINISHED"}
bpy.utils.register_class(SelectVisibleFramesCustAnimObj)
#######
## Try End
####
#

def AddFrame_BASE_FUNCTION(o, frame):
    clonedObj = o.copy()
    clonedObj.animation_data_clear()
    #clonedObj.data = o.data.copy() #include this if whole copy is needed
    
    bpy.context.scene.objects.link( clonedObj )
    clonedObj["CustAnim_FramePool"] = "";
    clonedObj["CustAnim_Obj_On"] = False;
    clonedObj.hide_render = True;
    parentObj = bpy.context.scene.objects[ o["CustAnim_FramePool"] ];
    clonedObj.parent =  parentObj;
    clonedObj.matrix_parent_inverse = parentObj.matrix_world.inverted()
    clonedObj.name = str( frame \
       ).zfill(ZERO_PADDING_FOR_FRAMES) + "@" + o.name

class AddFrame(bpy.types.Operator):
    bl_idname = "mesh.cust_anim_make_frame" #NAME HERE
    bl_label = "Make Frame-Object (Selected ):" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
            if bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1:
                if tmpObs[i].CustAnim_FramePool.strip() != "":
                #add object if not existing
                    emptyOb = bpy.data.objects.new( "empty", None );
                    emptyOb.name = tmpObs[i].CustAnim_FramePool;
                    bpy.context.scene.objects.link( emptyOb );
                    if tmpObs[i].parent: emptyOb.parent = tmpObs[i].parent
                        
                else:
                    tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Objects With 'F.A.O. animate this object' on, and a animation name selected!");
        else:
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                AddFrame_BASE_FUNCTION(o, bpy.context.scene.frame_current)
                o.animation_data_clear()
                '''
                clonedObj = o.copy()
                #clonedObj.data = o.data.copy() #include this if whole copy is needed
                clonedObj.animation_data_clear()
                bpy.context.scene.objects.link( clonedObj )
                
  
                clonedObj["CustAnim_FramePool"] = "";
                clonedObj["CustAnim_Obj_On"] = False;
                clonedObj.hide_render = True;
                parentObj = bpy.context.scene.objects[ o["CustAnim_FramePool"] ];
                clonedObj.parent =  parentObj;
                clonedObj.matrix_parent_inverse = parentObj.matrix_world.inverted()
                clonedObj.name = str( bpy.context.scene.frame_current \
                   ).zfill(ZERO_PADDING_FOR_FRAMES) + "@" + o.name
                '''  
                   
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpObs : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(AddFrame)

class ShowFramesAfterNBefore(bpy.types.Operator):
    bl_idname = "mesh.frames_before_n_after" #NAME HERE
    bl_label = "Select Frame-Objs:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
            if bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1:
                tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Objects With 'F.A.O. animate this object' on, and a animation name selected!");
        else:
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                curframe = bpy.context.scene.frame_current;
                makeFramesBetween_TimeOneAndTwo_Visible( \
                    o, curframe - bpy.context.scene.ShowThisManyFrames,  \
                    curframe + bpy.context.scene.ShowThisManyFrames)
                
                
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpObs : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(ShowFramesAfterNBefore)

class UnbakeCustmAnimation(bpy.types.Operator):
    bl_idname = "mesh.unbake_custom_anim" #NAME HERE
    bl_label = "Make F.A.O. From Frames:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
            if not hasattr(tmpObs[i].animation_data, "action"):
                tmpObs.remove(tmpObs[i])
            else:
                if bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1:
                    if tmpObs[i].CustAnim_FramePool.strip() != "":
                    #add object if not existing
                        emptyOb = bpy.data.objects.new( "empty", None );
                        emptyOb.name = tmpObs[i].CustAnim_FramePool;
                        bpy.context.scene.objects.link( emptyOb );
                        if tmpObs[i].parent: emptyOb.parent = tmpObs[i].parent
                            
                    else:
                        tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Objects With 'F.A.O. animate this object' on, and a animation name (and any frames) selected!");
        else:
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                curframe = bpy.context.scene.frame_current;
                allFrame = {}
                for f in o.animation_data.action.fcurves:
                    for k in f.keyframe_points:
                        allFrame[k.co[0] ] = True
                for i in allFrame.keys():
                    bpy.context.scene.frame_set(  int(i) );
                    AddFrame_BASE_FUNCTION(o, bpy.context.scene.frame_current)   
                o.animation_data_clear()
                o.CustAnim_Obj_On = True;
                
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpObs : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(UnbakeCustmAnimation)

class BakeCustomAnim(bpy.types.Operator):
    bl_idname = "mesh.bake_custom_anim" #NAME HERE
    bl_label = "Bake FramesAsObjs Anim:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            if (bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1):
                tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Objects With 'F.A.O. animate this object' on, and a animation name (and no standard animation action) selected!");
        else:
            tmpSelect_After_For_Loop = [];
            Obj_Names_To_remove_after_This = {};
            for o in tmpObs:
                o_cust_anim = bpy.context.scene.objects[o.CustAnim_FramePool]
                for c in o_cust_anim.children:
                    # this, for some reason, needs to be here...
                    # I think too many loops  
                    c_frame = int( c.name.split("@")[0] )
                    if not bpy.context.scene.objects.find([c.name]) == -1:
                        ooo= ""; # in case I need something here
                    else:
                        if c.name.split("@")[0].lstrip('-').isdigit(): 
                            Obj_Names_To_remove_after_This[c.name] = True;
                            if not bpy.context.scene.objects.find( c.name ) == -1:
                                # SiblingLerp( subjectA, objA, objB, startFrame, endFrame, curFrame)
                               
                                bpy.context.scene.frame_set(  c_frame );
                                SiblingLerp( o, o, c, 1, 2, 2)
                                o.keyframe_insert("location", frame = bpy.context.scene.frame_current)
                                o.keyframe_insert("scale", frame = bpy.context.scene.frame_current)
                                o.keyframe_insert("rotation_euler", frame = bpy.context.scene.frame_current)
                                
                                # For Armatures
                                if hasattr(o.pose, 'bones'):
                                    for b in o.pose.bones: 
                                        b.keyframe_insert("location", frame = bpy.context.scene.frame_current)
                                        b.keyframe_insert("rotation_quaternion", frame = bpy.context.scene.frame_current)
                                        b.keyframe_insert("scale", frame = bpy.context.scene.frame_current)
                                       
                                # bpy.context.scene.objects.unlink( bpy.data.objects[c.name])
                                # bpy.data.objects.remove( bpy.data.objects[c.name])  
                Obj_Names_To_remove_after_This[o_cust_anim.name] = True;
                # bpy.context.scene.objects.unlink( bpy.data.objects[o_cust_anim.name])
                # bpy.data.objects.remove( bpy.data.objects[o_cust_anim.name])
                 
            for i in Obj_Names_To_remove_after_This:
                bpy.context.scene.objects.unlink( bpy.data.objects[i])
                bpy.data.objects.remove( bpy.data.objects[i])
                        
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpObs : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(BakeCustomAnim)

class SelectCustamAnim_FromFrame(bpy.types.Operator):
    bl_idname = "mesh.select_cust_anim_from_frames" #NAME HERE
    bl_label = "Select Anim From Frame-Obj" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
           # if  hasattr(tmpObs[i].animation_data, "action"):
            #    tmpObs.remove(tmpObs[i])
            #else:
            #if (bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1):
            #   tmpObs.remove(tmpObs[i])
            if not tmpObs[i].name.split("@")[0].lstrip('-').isdigit():
                tmpObs.remove( tmpObs[i] )
            else: 
                if not tmpObs[i].parent:
                    tmpObs.remove( tmpObs[i] )
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Frame-objects with a object to animate selected");
        else:
            tmpObs_CustAnimObjs = bpy.context.scene.objects;
            tmpObs_CustAnimObjs_Names = {}
            i2 = len( tmpObs_CustAnimObjs )-1
            while i2 >= 0:
                if not bpy.context.scene.objects.find(tmpObs_CustAnimObjs[i2].CustAnim_FramePool) == -1:
                    tmpObs_CustAnimObjs_Names[ tmpObs_CustAnimObjs[i2].CustAnim_FramePool] = \
                        tmpObs_CustAnimObjs[i2].name
                i2 -=1;
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                if o.parent.name in tmpObs_CustAnimObjs_Names :
                    tmpSelect_After_For_Loop.append(bpy.context.scene.objects[\
                        tmpObs_CustAnimObjs_Names[o.parent.name]])
                
                        
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpSelect_After_For_Loop : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(SelectCustamAnim_FromFrame)

class SelectVisFrams_FromCustAnim(bpy.types.Operator):
    bl_idname = "mesh.select_visible_frames_from_custom_anim" #NAME HERE
    bl_label = "Select All frame-obs From Anim" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            if (bpy.context.scene.objects.find(tmpObs[i].CustAnim_FramePool) == -1):
                tmpObs.remove(tmpObs[i])
            i -= 1;
        if( len(tmpObs) == 0 ): self.report({'ERROR'},"No Frame objects with custom anim objects selected");
        else:
            tmpSelect_After_For_Loop = [];
            for o in tmpObs:
                for c in bpy.context.scene.objects[o.CustAnim_FramePool].children:
                    if c.hide == False:
                        tmpSelect_After_For_Loop.append(c);
                
            bpy.ops.object.select_all(action='DESELECT');
            for o in tmpSelect_After_For_Loop : 
               o.select = True;
        return {"FINISHED"}
bpy.utils.register_class(SelectVisFrams_FromCustAnim)


class Clear_NonCustomAnim(bpy.types.Operator):
    bl_idname = "mesh.clear_noncustom_anim" #NAME HERE
    bl_label = "Clear Standard Anim:" #Text here
    
    def invoke(self, context, event):
        tmpObs = bpy.context.selected_objects;
        
        i= len(bpy.context.selected_objects)-1; 
        while( i >= 0 ):
            #if( not tmpObs[i].CustAnim_Obj_On == True ):
            #    tmpObs.remove(tmpObs[i])
           # if  hasattr(tmpObs[i].animation_data, "action"):
            #    tmpObs.remove(tmpObs[i])
            #else:
            tmpObs[i].animation_data_clear()
            i -=1;
        return {"FINISHED"}
bpy.utils.register_class(Clear_NonCustomAnim)

class PanelOne(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_1"
    bl_category = "Animation"
    bl_label = 'FramesAsObjects_ForFrames'

    def draw(self, context):
        #self.layout.label("Small Class")
        layout = self.layout
        
        
        box = layout.box()
        box.label("Frame-Object Operators")
        row = box.row()
        row.operator("mesh.cust_anim_move_frame") 
        row2 = box.row()
        row2.prop( bpy.context.scene, "MoveFrames")
        
        
        
        
        #scn = k
        


#MAKE CUSTOM OBJECT VARS USABLE LIKE THIS!!!
bpy.types.Object.CustAnim_FramePool = StringProperty(
    name = "Name:", default = "")
bpy.types.Object.CustAnim_Obj_On = BoolProperty(
    name = "F.A.O. Animate This Object", default = False)
 

class PanelTwo(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_2"
    bl_category = "Animation"
    bl_label = 'FramesAsObjects_ForObject'

    def draw(self, context):
        #self.layout.label("Also Small Class")
        layout = self.layout
    
        obj = context.object
        #row = layout.row()
        #row.prop(obj, "hide_select")
        #row.prop(obj, "hide_render")
    
        
        
        box2 = layout.box()
        box2.label("Object to animate operations")
       #bpy.context.object["AnAbnormalyOddName"] = "not in observer"
        row21 = box2.row()
        row21.prop( bpy.context.scene, "Cust_Anim_SYSTEM_ON")
        
        row3 = box2.row()
        row3.prop( bpy.context.object, "CustAnim_Obj_On")
        row5_1 = box2.row()
        row5_1.label("Name of animation:")
        row5 = box2.row()
        row5.prop( bpy.context.object, "CustAnim_FramePool")
        row5_1 = box2.row()
        row5_1.operator(  "mesh.cust_anim_select_visible_frames")
        row6 = box2.row()
        row6.operator("mesh.cust_anim_make_frame") 
        row6_1 = box2.row()
        row6_1.label( "Full Duplicate Obj+Anim" )
        row7 = box2.row()
        row7.operator("mesh.cust_anim_duplicate_obj")
        
        row8_1 = box2.row()
        row8_1.label( "Bake/Unbake Cust Animation" )
        row8 = box2.row()
        row8.operator("mesh.unbake_custom_anim")
        row9 = box2.row()
        row9.operator("mesh.bake_custom_anim")
        row10 = box2.row()
        row11_1 = box2.row()
        row11_1.label( "Clear Anim:" )
        row11 = box2.row()
        row11.operator("mesh.clear_noncustom_anim")

class PanelThree(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_3"
    bl_category = "Animation"
    bl_label = 'FramesAsObjects_Select'

    def draw(self, context):
        #self.layout.label("Also Small Class")
        layout = self.layout
    
        obj = context.object
        #row = layout.row()
        #row.prop(obj, "hide_select")
        #row.prop(obj, "hide_render")
    
        
        
        box2 = layout.box()
        box2.label("Select Frame-Objs OR Animation:")
       #bpy.context.object["AnAbnormalyOddName"] = "not in observer"
        
        row25 = box2.row()
        row25.operator(  "mesh.select_cust_anim_from_frames")
        row23_1 = box2.row()
        row23_1.label( "Select frame-objs before ")
        row23_2 = box2.row()
        row23_2.label( "and after current frame:")
        row23 = box2.row()
        row23.operator( "mesh.frames_before_n_after")
        row24 = box2.row()
        row24.prop( bpy.context.scene, "ShowThisManyFrames")
        row26 = box2.row()
        row26.operator(  "mesh.select_visible_frames_from_custom_anim")
        
             
        
'''
bpy.utils.register_class(PanelThree)
bpy.utils.register_class(PanelTwo)
bpy.utils.register_class(PanelOne)
'''

def makeFramesBetween_TimeOneAndTwo_Visible( targetObj, startTime, endTime): 
    parentObj = bpy.context.scene.objects[targetObj["CustAnim_FramePool"]];
    tmpList=  []; 
    for d in parentObj.children:  
        #pulls first digits out of name
        if d.name.split("@")[0].lstrip('-').isdigit(): 
            d.hide = True;
            if int(d.name.split("@")[0]) > startTime:
                if int(d.name.split("@")[0]) < endTime:
                    d.hide = False;

def SiblingLerp_OneMove(target, objA, objB, partObjAtoB):
    if hasattr(target, 'matrix'):
        #if not objA.matrix_basis == objB.matrix_basis:
        if not target.matrix_basis == objB.matrix_basis:
            target.matrix_basis = objA.matrix_basis.lerp(objB.matrix_basis, partObjAtoB);
    else:
        #if not objA.matrix_world == objB.matrix_world:
        if not target.matrix_world == objB.matrix_world:
            target.matrix_world = objA.matrix_world.lerp( objB.matrix_world, partObjAtoB)
        

def SiblingLerp( subjectA, objA, objB, startFrame, endFrame, curFrame):
    target = subjectA;
    if not target.is_visible(bpy.context.scene):
       return
    if (endFrame - startFrame) == 0: partObjAtoB = 0        
    else: partObjAtoB = (curFrame - startFrame) / (endFrame - startFrame);
    SiblingLerp_OneMove(target, objA, objB, partObjAtoB)
    cldNames = {};
    # Run this script for all objects chidren
    for d in subjectA.children:  
        if hasattr( objA.children, d.name) and hasattr( objB.children, d.name):
            SiblingLerp( d, objA.children[d.name], objB.children[d.name], startFrame, endFrame, curFrame)
    # check for bones too see if children are armatures
    if hasattr(objA.pose, 'bones') and hasattr(objB.pose, 'bones'):
        if hasattr(target.pose, 'bones'):
            bnNames = {}
            for i in subjectA.pose.bones: 
                 bnNames[i.name] = i.name
            for i in bnNames: 
                 tmpBnSubA = target.pose.bones[i];
                 tmpBnA = objA.pose.bones[i]; tmpBnB = objB.pose.bones[i];
                 # Run this script for all armatureBone chidren
                 for d in tmpBnSubA.children:  
                    if hasattr( tmpBnA.children, d.name) and hasattr( tmpBnB.children, d.name):
                        SiblingLerp( d, tmpBnA.children[d.name], tmpBnB.children[d.name], startFrame, endFrame, curFrame)
                
                 SiblingLerp_OneMove(tmpBnSubA, tmpBnA, tmpBnB, partObjAtoB)


def getChildBeforeAndAfterCurrentFrame( parentObj, curFrame):
    return makeList_GetHiLow( parentObj, makeFrameList( parentObj), curFrame)

def makeFrameList_Struct( targetObj): 
    parentObj = bpy.context.scene.objects[targetObj["CustAnim_FramePool"]];
    tmpList=  []; 
    for d in parentObj.children:  
        #pulls first digits out of name
        if d.name.split("@")[0].lstrip('-').isdigit(): 
            tmpList.append( {'frame':int( d.name.split("@")[0] ), 'name':d.name } )   
    return sorted(tmpList, key=lambda frame: frame['frame']) 
def makeFramesList_GetHiLow( objToMove, getMakeFramesList, curFrame):
    i = 0;
    if len(getMakeFramesList) < 2: # if only 1, no animation
        return { "hiObj":objToMove.name, "lowObj":objToMove.name,\
                    "hiFrame":10000, "lowFrame":0 } 
    while i < len(getMakeFramesList):
        if getMakeFramesList[i]["frame"] >= curFrame:
            if i == 0:
                return { "hiObj":getMakeFramesList[i]['name'], "lowObj":getMakeFramesList[i]['name'],\
                    "hiFrame":getMakeFramesList[i]["frame"], "lowFrame":getMakeFramesList[i]["frame"] } 
            else:
                return { "hiObj":getMakeFramesList[i]['name'], "lowObj":getMakeFramesList[i-1]['name'],\
                    "hiFrame":getMakeFramesList[i]["frame"], "lowFrame":getMakeFramesList[i - 1]["frame"] }  
        i += 1;
    i -= 1;
    return { "hiObj":getMakeFramesList[i]['name'], "lowObj":getMakeFramesList[i]['name'],\
                    "hiFrame":getMakeFramesList[i]["frame"], "lowFrame":getMakeFramesList[i]["frame"] }  


def Sibling_complete_lerp( targetObj, getFramesList):
    curframe = bpy.context.scene.frame_current;
    f = getFramesList;
    # Should have this as a list, 
    # then I can iterate through them
    SiblingLerp( targetObj, \
        bpy.context.scene.objects[f['lowObj']], \
        bpy.context.scene.objects[f['hiObj']],\
         f['lowFrame'], f['hiFrame'], curframe);


'''
    OBJDATA:
        TargetObject: 
            CustAnim_Obj_On,
            CustAnim_FramePool,
            _CustAnim_FrameObj,
            _CustAnim_FramesList
     FRAMELIST:
         [
            {'frame':3, 'name':'Hello'},
            {'frame':3, 'name':'Hello'}
         ]

''' 
def Optimize_Skip_Recalc(i, curframe):
    #   I never made this for lack of outside interest!
    #
    #  But if I had, Here is what I would do
    #
    # can check if curframe is out of range of hi/lo frame,
    # and check if numb frames == numb of child objects in 
    # frame animation
    #
    # return False if either was false
    return True;
 
def FrameChangeHandler(scene):
    if not bpy.context.scene.Cust_Anim_SYSTEM_ON: return
    
    curframe = bpy.context.scene.frame_current;
    sceneObserverPool = [];
    for i in bpy.context.scene.objects:
        if i.is_visible(bpy.context.scene):
            if i.CustAnim_Obj_On == True:
                if not bpy.context.scene.objects.find(i.CustAnim_FramePool) == -1:
                    #Optimize goes here
                    if( Optimize_Skip_Recalc(i, curframe)):
                        i["_CustAnim_FramesList"] =  makeFrameList_Struct( i );
                        i["_CustAnim_HiLoFrames"] = makeFramesList_GetHiLow( i, \
                            i["_CustAnim_FramesList"], curframe);
                    #End Optimize
                    sceneObserverPool.append(i);
    for i in sceneObserverPool:
        Sibling_complete_lerp( i, i["_CustAnim_HiLoFrames"])       
  
  

#Register as from script
     
def register():
    for i in range( (bpy.app.handlers.frame_change_pre.__len__()-1), -1, -1):
        if bpy.app.handlers.frame_change_pre[i].__name__ == FrameChangeHandler.__name__:
            bpy.app.handlers.frame_change_pre.remove( bpy.app.handlers.frame_change_pre[i]);
    bpy.app.handlers.frame_change_pre.append(FrameChangeHandler)   
    
    bpy.utils.register_class(PanelThree)
    bpy.utils.register_class(PanelTwo)
    bpy.utils.register_class(PanelOne)
    
def unregister():
    for i in range( (bpy.app.handlers.frame_change_pre.__len__()-1), -1, -1):
        if bpy.app.handlers.frame_change_pre[i].__name__ == FrameChangeHandler.__name__:
            bpy.app.handlers.frame_change_pre.remove( bpy.app.handlers.frame_change_pre[i]);
    
    bpy.utils.unregister_class(PanelThree)
    bpy.utils.unregister_class(PanelTwo)
    bpy.utils.unregister_class(PanelOne)
    
    #bpy.app.handlers.frame_change_pre.remove(FrameChangeHandler)   
    
#For script
# UnComment below out if running as script
#register()
 
