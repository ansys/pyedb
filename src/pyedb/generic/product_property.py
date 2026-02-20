import re
from pydantic import BaseModel


class EMProperties(BaseModel):
    class EMPropertiesInner(BaseModel):
        general: str = ""
        modeled: bool = True
        union: bool = True
        use_precedence: bool = False
        precedence_value: int = 1
        planar_em: str = ""
        refined: bool = True
        refine_factor: int = 1
        no_edge_mesh: bool = False
        hfss: str = ""
        solve_inside: bool = False
        siwave: str = ""
        dcir_equipotential_region: bool = False

    type: str = "Mesh"
    data_id: str = "EM properties1"
    properties: EMPropertiesInner = EMPropertiesInner()

    @classmethod
    def from_em_string(cls, em_string: str) -> "EMProperties":
        """Parse EM properties string."""
        def extract(pattern: str) -> str:
            match = re.search(pattern, em_string)
            if match:
                return match.group(1)
            else:
                raise ValueError(f"Pattern '{pattern}' not found in EM properties string.")

        def to_bool(val: str) -> bool:
            return val.lower() == "true"

        inner = cls.EMPropertiesInner(
            modeled=to_bool(extract(r"Modeled='([^']+)'")),
            union=to_bool(extract(r"Union='([^']+)'")),
            use_precedence=to_bool(extract(r"'Use Precedence'='([^']+)'")),
            precedence_value=int(extract(r"'Precedence Value'='([^']+)'")),
            planar_em=extract(r"PlanarEM='([^']*)'"),
            refined=to_bool(extract(r"Refined='([^']+)'")),
            refine_factor=int(extract(r"RefineFactor='([^']+)'")),
            no_edge_mesh=to_bool(extract(r"NoEdgeMesh='([^']+)'")),
            hfss=extract(r"HFSS='([^']*)'"),
            solve_inside=to_bool(extract(r"'Solve Inside'='([^']+)'")),
            siwave=extract(r"SIwave='([^']*)'"),
            dcir_equipotential_region=to_bool(extract(r"'DCIR Equipotential Region'='([^']+)'")),
        )

        return cls(
            type=extract(r"Type\('([^']+)'\)"),
            data_id=extract(r"DataId='([^']+)'"),
            properties=inner,
        )

    def to_em_string(self) -> str:
        """Convert back to EM properties string."""
        p = self.properties
        return (
            r"$begin 'EM properties'\n"
            rf"\tType('{self.type}')\n"
            rf"\tDataId='{self.data_id}'\n"
            r"\t$begin 'Properties'\n"
            rf"\t\tGeneral='{p.general}'\n"
            rf"\t\tModeled='{str(p.modeled).lower()}'\n"
            rf"\t\tUnion='{str(p.union).lower()}'\n"
            rf"\t\t'Use Precedence'='{str(p.use_precedence).lower()}'\n"
            rf"\t\t'Precedence Value'='{p.precedence_value}'\n"
            rf"\t\tPlanarEM='{p.planar_em}'\n"
            rf"\t\tRefined='{str(p.refined).lower()}'\n"
            rf"\t\tRefineFactor='{p.refine_factor}'\n"
            rf"\t\tNoEdgeMesh='{str(p.no_edge_mesh).lower()}'\n"
            rf"\t\tHFSS='{p.hfss}'\n"
            rf"\t\t'Solve Inside'='{str(p.solve_inside).lower()}'\n"
            rf"\t\tSIwave='{p.siwave}'\n"
            rf"\t\t'DCIR Equipotential Region'='{str(p.dcir_equipotential_region).lower()}'\n"
            r"\t$end 'Properties'\n"
            r"$end 'EM properties'\n"
        )
