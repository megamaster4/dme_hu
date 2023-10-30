from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class Burgstaat(Base):
    __tablename__ = "burgstaat"

    burgst_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    burgerlijkestaat: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "Key": "burgst_key",
            "Title": "burgerlijkestaat",
            "Description": "description",
            "CategoryGroupID": "categorygroupid",
        }


class CategoryGroup(Base):
    __tablename__ = "categorygroup"

    catgroup_key: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    dimensionkey: Mapped[str] = mapped_column(nullable=False)
    catgroup: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    parentid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "ID": "catgroup_key",
            "DimensionKey": "dimensionkey",
            "Title": "catgroup",
            "Description": "description",
            "ParentID": "parentid",
        }


class Leeftijd(Base):
    __tablename__ = "leeftijd"

    leeftijd_key: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    leeftijd: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(
        ForeignKey("categorygroup.catgroup_key"), nullable=True
    )
    categorygroup: Mapped[list["CategoryGroup"]] = relationship("CategoryGroup")

    def __resp_keys__() -> dict[str, str]:
        return {
            "Key": "leeftijd_key",
            "Title": "leeftijd",
            "Description": "description",
            "CategoryGroupID": "categorygroupid",
        }


class Geslacht(Base):
    __tablename__ = "geslacht"

    geslacht_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    geslacht: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "Key": "geslacht_key",
            "Title": "geslacht",
            "Description": "description",
            "CategoryGroupID": "categorygroupid",
        }


class Perioden(Base):
    __tablename__ = "perioden"

    datum_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    jaar: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "Key": "datum_key",
            "Title": "jaar",
            "Description": "description",
            "Status": "status",
        }


class Regios(Base):
    __tablename__ = "regios"

    regio_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    regio: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "Key": "regio_key",
            "Title": "regio",
            "Description": "description",
            "CategoryGroupID": "categorygroupid",
        }


class Bevolking(Base):
    __tablename__ = "bevolking"
    __url__ = "https://opendata.cbs.nl/ODataFeed/odata/03759ned/TypedDataSet"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    geslacht_key: Mapped[str] = mapped_column(
        ForeignKey("geslacht.geslacht_key"), nullable=False
    )
    leeftijd_key: Mapped[int] = mapped_column(
        ForeignKey("leeftijd.leeftijd_key"), nullable=False
    )
    burgst_key: Mapped[str] = mapped_column(
        ForeignKey("burgstaat.burgst_key"), nullable=False
    )
    regio_key: Mapped[str] = mapped_column(
        ForeignKey("regios.regio_key"), nullable=False
    )
    datum_key: Mapped[str] = mapped_column(
        ForeignKey("perioden.datum_key"), nullable=False
    )
    bevolking_1_januari: Mapped[int] = mapped_column(nullable=True)
    gemiddelde_bevolking: Mapped[float] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "ID": "id",
            "Geslacht": "geslacht_key",
            "Leeftijd": "leeftijd_key",
            "BurgerlijkeStaat": "burgst_key",
            "RegioS": "regio_key",
            "Perioden": "datum_key",
            "BevolkingOp1Januari_1": "bevolking_1_januari",
            "GemiddeldeBevolking_2": "gemiddelde_bevolking",
        }


class Bodemgebruik(Base):
    __tablename__ = "bodemgebruik"
    __url__ = "https://opendata.cbs.nl/ODataFeed/odata/70262ned/TypedDataSet"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    regio_key: Mapped[str] = mapped_column(
        ForeignKey("regios.regio_key"), nullable=False
    )
    datum_key: Mapped[str] = mapped_column(
        ForeignKey("perioden.datum_key"), nullable=False
    )
    totale_oppervlakte: Mapped[int] = mapped_column(nullable=True)
    totaal_verkeersterrein: Mapped[int] = mapped_column(nullable=True)
    spoorterrein: Mapped[int] = mapped_column(nullable=True)
    wegverkeersterrein: Mapped[int] = mapped_column(nullable=True)
    vliegveld: Mapped[int] = mapped_column(nullable=True)
    totaal_bebouwd_terrein: Mapped[int] = mapped_column(nullable=True)
    woonterrein: Mapped[int] = mapped_column(nullable=True)
    terrein_voor_detailhandel_en_horeca: Mapped[int] = mapped_column(nullable=True)
    terrein_voor_openbare_voorzieningen: Mapped[int] = mapped_column(nullable=True)
    terrein_voor_sociaal_culturele_voorz: Mapped[int] = mapped_column(nullable=True)
    bedrijventerrein: Mapped[int] = mapped_column(nullable=True)
    totaal_semi_bebouwd_terrein: Mapped[int] = mapped_column(nullable=True)
    stortplaats: Mapped[int] = mapped_column(nullable=True)
    wrakkenopslagplaats: Mapped[int] = mapped_column(nullable=True)
    begraafplaats: Mapped[int] = mapped_column(nullable=True)
    delfstofwinplaats: Mapped[int] = mapped_column(nullable=True)
    bouwterrein: Mapped[int] = mapped_column(nullable=True)
    semi_verhard_overig_terrein: Mapped[int] = mapped_column(nullable=True)
    totaal_recreatieterrein: Mapped[int] = mapped_column(nullable=True)
    park_en_plantsoen: Mapped[int] = mapped_column(nullable=True)
    sportterrein: Mapped[int] = mapped_column(nullable=True)
    volkstuin: Mapped[int] = mapped_column(nullable=True)
    dagrecreatief_terrein: Mapped[int] = mapped_column(nullable=True)
    verblijfsrecreatief_terrein: Mapped[int] = mapped_column(nullable=True)
    totaal_agrarisch_terrein: Mapped[int] = mapped_column(nullable=True)
    terrein_voor_glastuinbouw: Mapped[int] = mapped_column(nullable=True)
    overig_agrarisch_terrein: Mapped[int] = mapped_column(nullable=True)
    totaal_bos_en_open_natuurlijk_terrein: Mapped[int] = mapped_column(nullable=True)
    bos: Mapped[int] = mapped_column(nullable=True)
    open_droog_natuurlijk_terrein: Mapped[int] = mapped_column(nullable=True)
    open_nat_natuurlijk_terrein: Mapped[int] = mapped_column(nullable=True)
    totaal_binnenwater: Mapped[int] = mapped_column(nullable=True)
    ijsselmeer_markermeer: Mapped[int] = mapped_column(nullable=True)
    afgesloten_zeearm: Mapped[int] = mapped_column(nullable=True)
    rijn_en_maas: Mapped[int] = mapped_column(nullable=True)
    randmeer: Mapped[int] = mapped_column(nullable=True)
    spaarbekken: Mapped[int] = mapped_column(nullable=True)
    recreatief_binnenwater: Mapped[int] = mapped_column(nullable=True)
    binnenwater_voor_delfstofwinning: Mapped[int] = mapped_column(nullable=True)
    vloei_en_of_slibveld: Mapped[int] = mapped_column(nullable=True)
    overig_binnenwater: Mapped[int] = mapped_column(nullable=True)
    totaal_buitenwater: Mapped[int] = mapped_column(nullable=True)
    waddenzee_eems_dollard: Mapped[int] = mapped_column(nullable=True)
    oosterschelde: Mapped[int] = mapped_column(nullable=True)
    westerschelde: Mapped[int] = mapped_column(nullable=True)
    noordzee: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {
            "ID": "id",
            "RegioS": "regio_key",
            "Perioden": "datum_key",
            "TotaleOppervlakte_1": "totale_oppervlakte",
            "TotaalVerkeersterrein_2": "totaal_verkeersterrein",
            "Spoorterrein_3": "spoorterrein",
            "Wegverkeersterrein_4": "wegverkeersterrein",
            "Vliegveld_5": "vliegveld",
            "TotaalBebouwdTerrein_6": "totaal_bebouwd_terrein",
            "Woonterrein_7": "woonterrein",
            "TerreinVoorDetailhandelEnHoreca_8": "terrein_voor_detailhandel_en_horeca",
            "TerreinVoorOpenbareVoorzieningen_9": "terrein_voor_openbare_voorzieningen",
            "TerreinVoorSociaalCultureleVoorz_10": "terrein_voor_sociaal_culturele_voorz",
            "Bedrijventerrein_11": "bedrijventerrein",
            "TotaalSemiBebouwdTerrein_12": "totaal_semi_bebouwd_terrein",
            "Stortplaats_13": "stortplaats",
            "Wrakkenopslagplaats_14": "wrakkenopslagplaats",
            "Begraafplaats_15": "begraafplaats",
            "Delfstofwinplaats_16": "delfstofwinplaats",
            "Bouwterrein_17": "bouwterrein",
            "SemiVerhardOverigTerrein_18": "semi_verhard_overig_terrein",
            "TotaalRecreatieterrein_19": "totaal_recreatieterrein",
            "ParkEnPlantsoen_20": "park_en_plantsoen",
            "Sportterrein_21": "sportterrein",
            "Volkstuin_22": "volkstuin",
            "DagrecreatiefTerrein_23": "dagrecreatief_terrein",
            "VerblijfsrecreatiefTerrein_24": "verblijfsrecreatief_terrein",
            "TotaalAgrarischTerrein_25": "totaal_agrarisch_terrein",
            "TerreinVoorGlastuinbouw_26": "terrein_voor_glastuinbouw",
            "OverigAgrarischTerrein_27": "overig_agrarisch_terrein",
            "TotaalBosEnOpenNatuurlijkTerrein_28": "totaal_bos_en_open_natuurlijk_terrein",
            "Bos_29": "bos",
            "OpenDroogNatuurlijkTerrein_30": "open_droog_natuurlijk_terrein",
            "OpenNatNatuurlijkTerrein_31": "open_nat_natuurlijk_terrein",
            "TotaalBinnenwater_32": "totaal_binnenwater",
            "IJsselmeerMarkermeer_33": "ijsselmeer_markermeer",
            "AfgeslotenZeearm_34": "afgesloten_zeearm",
            "RijnEnMaas_35": "rijn_en_maas",
            "Randmeer_36": "randmeer",
            "Spaarbekken_37": "spaarbekken",
            "RecreatiefBinnenwater_38": "recreatief_binnenwater",
            "BinnenwaterVoorDelfstofwinning_39": "binnenwater_voor_delfstofwinning",
            "VloeiEnOfSlibveld_40": "vloei_en_of_slibveld",
            "OverigBinnenwater_41": "overig_binnenwater",
            "TotaalBuitenwater_42": "totaal_buitenwater",
            "WaddenzeeEemsDollard_43": "waddenzee_eems_dollard",
            "Oosterschelde_44": "oosterschelde",
            "Westerschelde_45": "westerschelde",
            "Noordzee_46": "noordzee",
        }
