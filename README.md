# Blender_FramesAsObjects
A blender3d script ( a addon ) that allows objects to be used as animation frames.

Tested in blender 2.70


# About this pluggin:
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
        
# How to use: 
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
         from whatever action is active on object
         (WARNING: DOING THIS REMOVES AN OBJECTS STANDARD ANIMATION
            IT IS RECOMMENDED TO DUPLICATE AN OBJECT BEFORE DOING THIS)
