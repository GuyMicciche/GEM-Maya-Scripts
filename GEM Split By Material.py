# coding=utf-8

"""
Description:
    This script provides utilities for working with shading groups in Autodesk Maya.
    It allows for separating materials on a given object and creating individual objects for each material.

Author:
    Guy Micciche

Functions:
    - getSGs: Returns the shading groups associated with a given object.
    - sepMat: Separates materials on an object, creating individual objects for each material.
    - runScript: Main execution function that processes selected objects in Maya.
"""

from maya import cmds

def getSGs(in_obj_name):
    """
    Get shading groups associated with a given object.
    
    Args:
        in_obj_name (str): Name of the object to retrieve shading groups for.
    
    Returns:
        list[str]: List of shading groups associated with the object.
    """
    
    # Check if the object exists in the scene
    if not cmds.objExists(in_obj_name): 
        return []
    
    shadingEngines = set()  # Initialize an empty set to store shading engines
    
    # Get shape nodes of the object
    ShapeNodes = cmds.listRelatives(in_obj_name, shapes=1, children=1) or []
    if not ShapeNodes:
        return []
    
    # Loop through each shape node and find its connected shading engines
    for shape in ShapeNodes:
        dest = cmds.listConnections(shape, source=False, plugs=False, destination=True, type="shadingEngine")
        if not dest:
            continue
        shadingEngines.update(dest)
        
    return list(shadingEngines)

def sepMat(objectName, suffixName="_Splitted"):
    """
    Separate materials on an object and create individual objects for each material.
    
    Args:
        objectName (str): Name of the object to process.
        suffixName (str, optional): Suffix to append to the parent node of the created objects. Defaults to "_Splitted".
    """
    
    shadingGroups = getSGs(objectName)
    
    # If there's only one shading group, no need to separate
    if len(shadingGroups) <= 1:
        return

    nodeParentName = objectName + suffixName
    
    # If a node with the desired name doesn't exist, create a new group node
    if not cmds.objExists(nodeParentName): 
        nodeParentName = cmds.group(empty=1, n=nodeParentName)
    
    # Loop through each shading group and create a separate object for it
    for i in range(len(shadingGroups)):
        curMatSg = shadingGroups[i]
        
        cloneObjName = objectName + "_" + curMatSg
        cloneObjName = cmds.duplicate(objectName, n=cloneObjName)[0]
        cloneObjName = cmds.parent(cloneObjName, nodeParentName)[0]
        
        polyFacesSet = cmds.sets(cloneObjName + '.f[0:]')
        sgFacesSet = cmds.sets(cmds.sets(curMatSg, un=polyFacesSet))
        
        # Delete unnecessary faces and sets
        cmds.delete(cmds.sets(polyFacesSet, subtract=sgFacesSet), polyFacesSet, sgFacesSet)
    else:
        cmds.delete(objectName)

def runScript(*args, **kw):
    """
    Main execution function. Processes selected objects in Maya.
    """
    
    # Get the current selection in Maya
    selection = cmds.ls(sl=True, objectsOnly=True, noIntermediate=True)
    
    # Loop through each selected object and try to separate its materials
    for sel in selection:
        try:
            sepMat(sel)
        except:
            continue
        
    # Clear the selection
    cmds.select(cl=True)

if __name__ == "__main__":
    runScript()
