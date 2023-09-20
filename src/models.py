from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

Base = declarative_base()


class Burgstaat(Base):
    __tablename__ = 'burgstaat'

    burgst_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    burgerlijkestaat: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {'Key': 'burgst_key', 'Title': 'burgerlijkestaat', 'Description': 'description', 'CategoryGroupID': 'categorygroupid'}


class CategoryGroup(Base):
    __tablename__ = 'categorygroup'

    catgroup_key: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    dimensionkey: Mapped[str] = mapped_column(nullable=False)
    catgroup: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    parentid: Mapped[int] = mapped_column(nullable=True)
    leeftijdgroup: Mapped["Leeftijd"] = relationship(back_populates="categorygroup")

    def __resp_keys__() -> dict[str, str]:
        return {'ID': 'catgroup_key', 'DimensionKey': 'dimensionkey', 'Title': 'catgroup', 'Description': 'description', 'ParentID': 'parentid'}


class Leeftijd(Base):
    __tablename__ = 'leeftijd'

    leeftijd_key: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    leeftijd: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(ForeignKey('categorygroup.catgroup_key'), nullable=True)
    categorygroup: Mapped["CategoryGroup"] = relationship(back_populates="leeftijdgroup")

    def __resp_keys__() -> dict[str, str]:
        return {'Key': 'leeftijd_key', 'Title': 'leeftijd', 'Description': 'description', 'CategoryGroupID': 'categorygroupid'}


class Geslacht(Base):
    __tablename__ = 'geslacht'

    geslacht_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    geslacht: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {'Key': 'geslacht_key', 'Title': 'geslacht', 'Description': 'description', 'CategoryGroupID': 'categorygroupid'}


class Perioden(Base):
    __tablename__ = 'perioden'

    datum_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    jaar: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {'Key': 'datum_key', 'Title': 'jaar', 'Description': 'description', 'Status': 'status'}


class Regios(Base):
    __tablename__ = 'regios'

    regio_key: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    regio: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    categorygroupid: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {'Key': 'regio_key', 'Title': 'regio', 'Description': 'description', 'CategoryGroupID': 'categorygroupid'}


class Bevolking(Base):
    __tablename__ = 'bevolking'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    geslacht_key: Mapped[str] = mapped_column(ForeignKey('geslacht.geslacht_key'), nullable=False)
    leeftijd_key: Mapped[int] = mapped_column(ForeignKey('leeftijd.leeftijd_key'), nullable=False)
    burgst_key: Mapped[str] = mapped_column(ForeignKey('burgstaat.burgst_key'), nullable=False)
    regio_key: Mapped[str] = mapped_column(ForeignKey('regios.regio_key'), nullable=False)
    datum_key: Mapped[str] = mapped_column(ForeignKey('perioden.datum_key'), nullable=False)
    bevolking_1_januari: Mapped[int] = mapped_column(nullable=True)
    gemiddelde_bevolking: Mapped[int] = mapped_column(nullable=True)

    def __resp_keys__() -> dict[str, str]:
        return {'ID': 'id', 'Geslacht': 'geslacht_key', 'Leeftijd': 'leeftijd_key', 'BurgerlijkeStaat': 'burgst_key',
                'RegioS': 'regio_key', 'Perioden': 'datum_key', 'BevolkingOp1Januari_1': 'bevolking_1_januari', 'GemiddeldeBevolking_2': 'gemiddelde_bevolking'}
