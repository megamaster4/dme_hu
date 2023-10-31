CREATE TABLE public.perioden (
      datum_key varchar NOT NULL,
      jaar int4 NOT NULL,
      description varchar NULL,
      status varchar NOT NULL,
      CONSTRAINT "datum_key_pkey" PRIMARY KEY (datum_key)
);
CREATE TABLE public.regios (
      regio_key varchar NOT NULL,
      regio varchar NOT NULL,
      description varchar NULL,
      categorygroupid int4 NULL,
      CONSTRAINT "regio_key_pkey" PRIMARY KEY (regio_key)
);
CREATE TABLE public.burgstaat (
      burgst_key varchar NOT NULL,
      burgerlijkestaat varchar NOT NULL,
      description varchar NULL,
      categorygroupid int4 NULL,
      CONSTRAINT "burgst_key_pkey" PRIMARY KEY (burgst_key)
);
CREATE TABLE public.geslacht (
      geslacht_key varchar NOT NULL,
      geslacht varchar NOT NULL,
      description varchar NULL,
      categorygroupid int4 NULL,
      CONSTRAINT "geslacht_key_pkey" PRIMARY KEY (geslacht_key)
);
CREATE TABLE public.categorygroup (
      catgroup_key int NOT NULL,
      dimensionkey varchar NOT NULL,
      catgroup varchar NOT NULL,
      description varchar NULL,
      parentid int4 NULL,
      CONSTRAINT "catgroup_key_pkey" PRIMARY KEY (catgroup_key)
);
CREATE TABLE public.leeftijd (
      leeftijd_key int NOT NULL,
      leeftijd varchar NOT NULL,
      description varchar NULL,
      categorygroupid int4 NULL,
      CONSTRAINT "leeftijd_key_pkey" PRIMARY KEY (leeftijd_key),
      CONSTRAINT "categorygroup_fkey" FOREIGN KEY (categorygroupid) REFERENCES categorygroup (catgroup_key)
);
CREATE TABLE public.bevolking (
    id INTEGER NOT NULL,
    geslacht_key varchar NOT NULL,
    leeftijd_key int NOT NULL,
    burgst_key varchar NOT NULL,
    regio_key varchar NOT NULL,
    datum_key varchar NOT NULL,
    bevolking_1_januari int NULL,
    gemiddelde_bevolking numeric NULL,
    CONSTRAINT "bevolking_pkey" PRIMARY KEY (id),
    CONSTRAINT "geslacht_fkey" FOREIGN KEY (geslacht_key) REFERENCES geslacht (geslacht_key),
    CONSTRAINT "leeftijd_fkey" FOREIGN KEY (leeftijd_key) REFERENCES leeftijd (leeftijd_key),
    CONSTRAINT "burgstaat_fkey" FOREIGN KEY (burgst_key) REFERENCES burgstaat (burgst_key),
    CONSTRAINT "regio_fkey" FOREIGN KEY (regio_key) REFERENCES regios (regio_key),
    CONSTRAINT "datum_fkey" FOREIGN KEY (datum_key) REFERENCES perioden (datum_key)
);
CREATE TABLE public.bodemgebruik (
    id INTEGER NOT NULL,
    regio_key TEXT NOT NULL,
    datum_key TEXT NOT NULL,
    totale_oppervlakte INTEGER NULL,
    totaal_verkeersterrein INTEGER NULL,
    spoorterrein INTEGER NULL,
    wegverkeersterrein INTEGER NULL,
    vliegveld INTEGER NULL,
    totaal_bebouwd_terrein INTEGER NULL,
    woonterrein INTEGER NULL,
    terrein_voor_detailhandel_en_horeca INTEGER NULL,
    terrein_voor_openbare_voorzieningen INTEGER NULL,
    terrein_voor_sociaal_culturele_voorz INTEGER NULL,
    bedrijventerrein INTEGER NULL,
    totaal_semi_bebouwd_terrein INTEGER NULL,
    stortplaats INTEGER NULL,
    wrakkenopslagplaats INTEGER NULL,
    begraafplaats INTEGER NULL,
    delfstofwinplaats INTEGER NULL,
    bouwterrein INTEGER NULL,
    semi_verhard_overig_terrein INTEGER NULL,
    totaal_recreatieterrein INTEGER NULL,
    park_en_plantsoen INTEGER NULL,
    sportterrein INTEGER NULL,
    volkstuin INTEGER NULL,
    dagrecreatief_terrein INTEGER NULL,
    verblijfsrecreatief_terrein INTEGER NULL,
    totaal_agrarisch_terrein INTEGER NULL,
    terrein_voor_glastuinbouw INTEGER NULL,
    overig_agrarisch_terrein INTEGER NULL,
    totaal_bos_en_open_natuurlijk_terrein INTEGER NULL,
    bos INTEGER NULL,
    open_droog_natuurlijk_terrein INTEGER NULL,
    open_nat_natuurlijk_terrein INTEGER NULL,
    totaal_binnenwater INTEGER NULL,
    ijsselmeer_markermeer INTEGER NULL,
    afgesloten_zeearm INTEGER NULL,
    rijn_en_maas INTEGER NULL,
    randmeer INTEGER NULL,
    spaarbekken INTEGER NULL,
    recreatief_binnenwater INTEGER NULL,
    binnenwater_voor_delfstofwinning INTEGER NULL,
    vloei_en_of_slibveld INTEGER NULL,
    overig_binnenwater INTEGER NULL,
    totaal_buitenwater INTEGER NULL,
    waddenzee_eems_dollard INTEGER NULL,
    oosterschelde INTEGER NULL,
    westerschelde INTEGER NULL,
    noordzee INTEGER NULL,
    CONSTRAINT "bodemgebruik_pkey" PRIMARY KEY (id),
    CONSTRAINT "regio_fkey" FOREIGN KEY (regio_key) REFERENCES regios(regio_key),
    CONSTRAINT "datum_fkey" FOREIGN KEY (datum_key) REFERENCES perioden(datum_key)
);
CREATE index idx_bevolking_regio_key ON bevolking(regio_key);
CREATE index idx_bodemgebruik_regio_key ON bodemgebruik(regio_key);
CREATE index idx_bevolking_datum_key ON bevolking(datum_key);
CREATE index idx_bodemgebruik_datum_key ON bodemgebruik(datum_key);
CREATE index idx_bevolking_leeftijd_key ON bevolking(leeftijd_key);