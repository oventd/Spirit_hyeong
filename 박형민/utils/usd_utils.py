from pxr import Usd, UsdGeom, Sdf, Gf, UsdShade

class UsdUtils:
    @staticmethod
    def create_usd_file(file_path, ascii=True):
        """
        USD 파일을 ASCII(.usda)로 저장하지만 확장자는 .usd
        """
        if ascii:
            args = {"format": "usda"}
        else:
            args = {"format": "usdc"}
        layer = Sdf.Layer.CreateNew(file_path, args)
        # USD Stage 생성
        stage = Usd.Stage.Open(layer)
        # USD 파일 저장
        stage.GetRootLayer().Save()
        return stage
    
    @staticmethod
    def set_default_prim(stage, prim):
        """
        입력받은 prim을 default prim로 설정

        :param stage: USD Stage
        :param prim: USD Prim
        """
        stage.SetDefaultPrim(prim)
    
    @staticmethod
    def get_stage(file_path):
        """
        입력받은 패스의 Stage를 가져오는 메서드

        :param file_path: usd file path
        """
        try:
            stage = Usd.Stage.Open(file_path)
            return stage
        except:
            return None
    
    @staticmethod
    def create_stage(file_path):
        """
        usd 패스에 stage를 만드는 메서드

        :param file_path: usd file path
        """
        return Usd.Stage.CreateNew(file_path)
    
    @staticmethod
    def get_prim(stage, path):
        """
        stage의 path에 맞는 Prim를 가져오는 메서드

        :param stage: USD Stage
        :param path: USD Prim Path
        """
        return stage.GetPrimAtPath(path)

    @staticmethod
    def create_xform(stage, path = "/Root"):
        """
        xform 노드를 생성

        :param stage: USD Stage
        :param path: USD Prim Path
        """
        xform = UsdGeom.Xform.Define(stage, path)
        
        defaltPrim = stage.GetDefaultPrim()
        if not defaltPrim:
            UsdUtils.set_default_prim(stage, xform.GetPrim())

        stage.GetRootLayer().Save()
        return xform.GetPrim()
        
    @staticmethod
    def create_scope(stage, path = "/Root"):
        """
        scope 노드를 생성

        :param stage: USD Stage
        :param path: USD Prim Path
        """
        scope = UsdGeom.Scope.Define(stage, path)
        
        defaltPrim = stage.GetDefaultPrim()
        if not defaltPrim:
            UsdUtils.set_default_prim(stage, scope.GetPrim())
        stage.GetRootLayer().Save()
        return scope.GetPrim()
    
    @staticmethod
    def add_reference(prim, path):
        """
        prim에 path를 reference로 추가

        :param prim: USD Prim
        :param path: USD Prim Path
        """
        stage = prim.GetStage()
        prim.GetReferences().AddReference(path)
        stage.GetRootLayer().Save()
    
    @staticmethod
    def create_variants_set(prim, variant_set_name: str):
        """
        prim에 variant set를 생성

        :param prim: USD Prim
        :param variant_set_name: variant set name
        """
        stage = prim.GetStage()
        
        variant_set = prim.GetVariantSets().AddVariantSet(variant_set_name)
        stage.GetRootLayer().Save()
        return variant_set
    @staticmethod
    def add_reference_to_variant_set(prim, variant_set_name, variants : dict, set_default = True):
        """
        variant set에 reference를 추가
        
        :param prim: USD Prim
        :param variant_set_name: variant set name
        :param variants: variant name, reference path
        :param set_default: set default variant, varient set으로 적용
        """
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
    def set_transform(prim, translate: tuple=None, rotate: tuple=None, scale: tuple=None):
        """
        prim의 이동, 회전, 스케일을 설정하는 함수

        :param prim: USD Prim
        :param translate: 이동 (x, y, z)
        :param rotate: 회전 (x, y, z)
        :param scale: 스케일 (x, y, z)
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
        """
        stage에 sublayer를 추가

        :param stage: USD Stage
        :param path: 서브레이어 USD Path
        """
        com_layer = UsdUtils.get_stage(path).GetRootLayer()
        if com_layer not in stage.GetLayerStack():
            stage.GetRootLayer().subLayerPaths.append(path)
        stage.GetRootLayer().Save()

    @staticmethod
    def get_prim_path(prim)->str:
        """
        prim의 패스를 반환

        :param prim: USD Prim
        """
        return prim.GetPath()
    
    @staticmethod
    def usd_to_dict(prim) -> dict:
        """
        prim의 하위 hierarchy를 dict로 변환

        :param prim: USD Prim
        """
        return {
            "name": prim.GetName(),
            "type": prim.GetTypeName(),
            "children": {child.GetName(): UsdUtils.usd_to_dict(child) for child in prim.GetChildren()}
        }
    @staticmethod
    def find_prim_paths_by_type_recursion(usd_dict, prim_type, parent_path=""):
        """
        재귀를 통해 타입에 맞는_prim_path를 찾는 메서드

        :param usd_dict: USD Dict
        :param prim_type: 타입
        :param parent_path: 부모 패스
        """
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
        """
        재귀를 통해 타입에 맞는_prim_path를 찾는 메서드
        재귀함수를 실행함

        :param usd_dict: USD Dict
        :param prim_type: 타입
        """
        lists = UsdUtils.find_prim_paths_by_type_recursion(usd_dict, prim_type)
        for n, i in enumerate(lists):
            lists[n] = i
        return lists
            

    @staticmethod
    def bind_material(prim, material_path):
        """
        prim에 material path의 material를 bind하는 메서드

        :param prim: USD Prim
        :param material_path: material path
        """
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



