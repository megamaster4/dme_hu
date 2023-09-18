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
      catgroup_key int32 NOT NULL,
      dimensionkey varchar NOT NULL,
      catgroup varchar NOT NULL,
      description varchar NULL,
      parentid int4 NULL,
      CONSTRAINT "catgroup_key_pkey" PRIMARY KEY (catgroup_key)
);
CREATE TABLE public.leeftijd (
      leeftijd_key varchar NOT NULL,
      leeftijd varchar NOT NULL,
      description varchar NULL,
      categorygroupid int4 NULL,
      CONSTRAINT "leeftijd_key_pkey" PRIMARY KEY (leeftijd_key)
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

