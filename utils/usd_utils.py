from pxr import Usd, UsdGeom, Sdf, Gf, UsdShade

class UsdUtils:
    @staticmethod
    def create_usd_file(file_path, ascii=True):
        # USD 파일을 ASCII(.usda)로 저장하지만 확장자는 .usd
        if ascii:
            args = {"format": "usda"}
        else:
            args = {"format": "usdc"}
        layer = Sdf.Layer.CreateNew(file_path, args)
        # USD Stage 생성 (ASCII 모드)
        stage = Usd.Stage.Open(layer)
        # USD 파일 저장
        stage.GetRootLayer().Save()
        return stage
    
    @staticmethod
    def set_default_prim(stage, prim):
        stage.SetDefaultPrim(prim)
    
    @staticmethod
    def get_stage(file_path):
        try:
            stage = Usd.Stage.Open(file_path)
            return stage
        except:
            return None
    
    @staticmethod
    def create_stage(file_path):
        return Usd.Stage.CreateNew(file_path)
    
    @staticmethod
    def get_prim(stage, path):
        return stage.GetPrimAtPath(path)

    @staticmethod
    def create_xform(stage, path = "/Root", parent_prim = None):
        xform = UsdGeom.Xform.Define(stage, path)
        
        defaltPrim = stage.GetDefaultPrim()
        if not defaltPrim:
            UsdUtils.set_default_prim(stage, xform.GetPrim())

        stage.GetRootLayer().Save()
        return xform.GetPrim()
        
    @staticmethod
    def create_scope(stage, path = "/Root", parent_prim = None):
        scope = UsdGeom.Scope.Define(stage, path)
        
        defaltPrim = stage.GetDefaultPrim()
        if not defaltPrim:
            UsdUtils.set_default_prim(stage, scope.GetPrim())
        stage.GetRootLayer().Save()
        return scope.GetPrim()
    
    @staticmethod
    def add_reference(prim, path):
        stage = prim.GetStage()
        prim.GetReferences().AddReference(path)
        stage.GetRootLayer().Save()
    
    @staticmethod
    def create_variants_set(xform, variant_set_name: str):
        stage = xform.GetStage()
        # Variant Set 생성
        variant_set = xform.GetVariantSets().AddVariantSet(variant_set_name)
        stage.GetRootLayer().Save()
        return variant_set
    @staticmethod
    def add_reference_to_variant_set(prim, variant_set_name, variants : dict, set_default = True):
        variant_set = prim.GetVariantSets().GetVariantSet(variant_set_name)

        if not variant_set:
            raise ValueError(f"Variant set '{variant_set_name}' not found.")

        current_variant = variant_set.GetVariantSelection()

        for variant_name, variant_value in variants.items():
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)
            with variant_set.GetVariantEditContext():
                prim.GetReferences().AddReference(variant_value)

        if not set_default:
            variant_set.SetVariantSelection(current_variant)

        stage = prim.GetStage()
        stage.GetRootLayer().Save()

    @staticmethod
    def set_transform(prim, translate=None, rotate=None, scale=None):
        """
        prim의 변환(이동, 회전, 스케일)을 설정하는 함수
        """
        xform = UsdGeom.Xform(prim)

        if translate:
            translate_op = xform.GetTranslateOp()
            if not translate_op:
                translate_op = xform.AddTranslateOp()
            translate_op.Set(Gf.Vec3f(*translate))

        if rotate:
            rotate_xyz_op = xform.GetRotateXYZOp()
            if not rotate_xyz_op:
                rotate_xyz_op = xform.AddRotateXYZOp()
            rotate_xyz_op.Set(Gf.Vec3f(*rotate))

        if scale:
            scale_op = xform.GetScaleOp()
            if not scale_op:
                scale_op = xform.AddScaleOp()
            scale_op.Set(Gf.Vec3f(*scale))

        prim.GetStage().GetRootLayer().Save()

    
    @staticmethod
    def add_sublayer(stage, path):
        com_layer = UsdUtils.get_stage(path).GetRootLayer()
        if com_layer not in stage.GetLayerStack():
            stage.GetRootLayer().subLayerPaths.append(path)
        stage.GetRootLayer().Save()

    @staticmethod
    def get_prim_path(prim):
        return prim.GetPath()
    
    @staticmethod
    def usd_to_dict(prim):
        """USD의 계층구조를 dict로 변환"""
        return {
            "name": prim.GetName(),
            "type": prim.GetTypeName(),
            "children": {child.GetName(): UsdUtils.usd_to_dict(child) for child in prim.GetChildren()}
        }
    @staticmethod
    def find_prim_paths_by_type_recursion(usd_dict, prim_type, parent_path=""):
        paths = []
        current_path = f"{parent_path}/{usd_dict['name']}" if parent_path else f"/{usd_dict['name']}"

        # 현재 Prim이 찾는 타입과 일치하면 경로 추가
        if usd_dict["type"] == prim_type:
            paths.append(current_path)

        # 하위 노드 탐색 (재귀 호출)
        for child_name, child_dict in usd_dict["children"].items():
            paths.extend(UsdUtils.find_prim_paths_by_type_recursion(child_dict, prim_type, current_path))

        return paths
    def find_prim_paths_by_type(usd_dict, prim_type):
        lists = UsdUtils.find_prim_paths_by_type_recursion(usd_dict, prim_type)
        for n, i in enumerate(lists):
            lists[n] = i
        return lists
            

    @staticmethod
    def bind_material(prim, material_path):
        stage = prim.GetStage()
        material = UsdShade.Material.Get(stage, material_path)
        UsdShade.MaterialBindingAPI(prim).Bind(material)
        stage.GetRootLayer().Save()

if __name__ == "__main__":

    # root_stage = UsdUtils.create_usd_file("/home/rapa/NA_Spirit/root.usd", ascii=True)
    root_stage = UsdUtils.get_stage("/home/rapa/NA_Spirit/root.usd")
    root_prim = UsdUtils.get_prim(root_stage, "/Root")
    # root_prim = UsdUtils.create_scope(root_stage, "/Root")
    # geo_prim = UsdUtils.create_scope(root_stage, "/Root/geo")
    # mat_prim = UsdUtils.create_scope(root_stage, "/Root/mat")

    # UsdUtils.add_reference(geo_prim, "/home/rapa/NA_Spirit/Mat_MDL.v005.usd")
    # UsdUtils.add_reference(mat_prim, "/home/rapa/NA_Spirit/material_test.usd")
    import pprint
    root_dict = UsdUtils.usd_to_dict(root_prim)
    pprint.pprint(root_dict)
    geo_paths = UsdUtils.find_prim_paths_by_type(root_dict, "Mesh")
    print(geo_paths)
    mat_paths = UsdUtils.find_prim_paths_by_type(root_dict, "Material")
    print(mat_paths)

    geo_prim = UsdUtils.get_prim(root_stage, geo_paths[0])
    UsdUtils.bind_material(geo_prim, mat_paths[0])





    
# mesh export
#file -force -options ";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=0;defaultMeshScheme=catmullClark;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=48;frameStride=1;frameSample=0.0;defaultUSDFormat=usda;rootPrim=;rootPrimType=xform;defaultPrim=geo;exportMaterials=0;shadingMode=useRegistry;convertMaterialsTo=[UsdPreviewSurface];exportAssignedMaterials=1;exportRelativeTextures=automatic;exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;includeEmptyTransforms=1;stripNamespaces=0;worldspace=0;exportStagesAsRefs=1;excludeExportTypes=[];legacyMaterialScope=0" -typ "USD Export" -pr -es "/home/rapa/NA_Spirit/geo.usd";
    
# material export
# file -force -options ";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=0;defaultMeshScheme=catmullClark;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=48;frameStride=1;frameSample=0.0;defaultUSDFormat=usda;rootPrim=;rootPrimType=xform;defaultPrim=geo;exportMaterials=1;shadingMode=useRegistry;convertMaterialsTo=[MaterialX];exportAssignedMaterials=1;exportRelativeTextures=automatic;exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;includeEmptyTransforms=1;stripNamespaces=1;worldspace=0;exportStagesAsRefs=1;excludeExportTypes=[Meshes];legacyMaterialScope=0" -typ "USD Export" -pr -es "/home/rapa/NA_Spirit/tex.usd";


    
# mesh export
#file -force -options ";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=0;defaultMeshScheme=catmullClark;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=48;frameStride=1;frameSample=0.0;defaultUSDFormat=usda;rootPrim=;rootPrimType=xform;defaultPrim=geo;exportMaterials=0;shadingMode=useRegistry;convertMaterialsTo=[UsdPreviewSurface];exportAssignedMaterials=1;exportRelativeTextures=automatic;exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;includeEmptyTransforms=1;stripNamespaces=0;worldspace=0;exportStagesAsRefs=1;excludeExportTypes=[];legacyMaterialScope=0" -typ "USD Export" -pr -es "/home/rapa/NA_Spirit/geo.usd";
    
# material export
# file -force -options ";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=0;defaultMeshScheme=catmullClark;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=48;frameStride=1;frameSample=0.0;defaultUSDFormat=usda;rootPrim=;rootPrimType=xform;defaultPrim=geo;exportMaterials=1;shadingMode=useRegistry;convertMaterialsTo=[MaterialX];exportAssignedMaterials=1;exportRelativeTextures=automatic;exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;includeEmptyTransforms=1;stripNamespaces=1;worldspace=0;exportStagesAsRefs=1;excludeExportTypes=[Meshes];legacyMaterialScope=0" -typ "USD Export" -pr -es "/home/rapa/NA_Spirit/tex.usd";




