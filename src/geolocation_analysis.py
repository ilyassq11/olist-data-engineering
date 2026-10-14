import pandas as pd 
df = pd.read_csv("C:/Users/ilyas/Desktop/olist-data-engineering/data/olist_geolocation_dataset.csv")

import unicodedata

def normalizza_testo(testo):
    testo = str(testo).lower().strip()
    testo = ''.join(
        c for c in unicodedata.normalize('NFD', testo)
        if unicodedata.category(c) != 'Mn'
    )
    return testo

df["geolocation_city_normalized"] = df["geolocation_city"].apply(normalizza_testo)


ris = df[
    (df["geolocation_zip_code_prefix"] == 1307) &
    (df["geolocation_lat"].round(6) == -23.556812) &
    (df["geolocation_lng"].round(6) == -46.657135)
]

print(ris)


anomalie = (
    df.groupby(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    )["geolocation_city_normalized"]
    .nunique()
)

print("Numero di coordinate con più città:", (anomalie > 1).sum())

# Troviamo le coordinate associate a più di una città
anomalie = (
    df.groupby(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    )["geolocation_city_normalized"]
    .nunique()
)

# Teniamo solo le coordinate problematiche
anomalie = anomalie[anomalie > 1]

print("Coordinate problematiche:", len(anomalie))

# Prendiamo solo le righe del DataFrame che hanno
# una delle coordinate problematiche
righe_anomale = df[
    df.set_index(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    ).index.isin(anomalie.index)
].copy()

print("Righe coinvolte:", len(righe_anomale))

# Raggruppiamo le città associate a ogni coordinata
combinazioni = (
    righe_anomale
    .groupby(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    )["geolocation_city_normalized"]
    .agg(lambda x: " / ".join(sorted(x.unique())))
)

print(combinazioni.value_counts().head(20))

df["geolocation_city_normalized_2"] = (
    df["geolocation_city_normalized"]
    .str.replace("-", " ", regex=False)
    .str.replace("'", " ", regex=False)
    .str.replace("  ", " ", regex=False)
    .str.strip()
)

print(df["geolocation_city_normalized_2"].value_counts().head(30))


# Troviamo le coordinate associate a più di una città
anomalie_2 = (
    df.groupby(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    )["geolocation_city_normalized_2"]
    .nunique()
)

# Teniamo solo le coordinate problematiche
anomalie_2 = anomalie_2[anomalie_2 > 1]

print("Coordinate problematiche:", len(anomalie_2))


# Prendiamo le righe appartenenti alle 249 coordinate problematiche

righe_anomale_2 = df[
    df.set_index(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    ).index.isin(anomalie_2.index)
].copy()


# Per ogni coordinata vediamo quali città sono associate

combinazioni_2 = (
    righe_anomale_2
    .groupby(
        ["geolocation_zip_code_prefix",
         "geolocation_lat",
         "geolocation_lng"]
    )["geolocation_city_normalized_2"]
    .agg(lambda x: " / ".join(sorted(x.unique())))
)


# Vediamo le combinazioni che compaiono più spesso

print(combinazioni_2.value_counts().head(20))

print("Città mancanti:", df["geolocation_city"].isna().sum())
print("Totale righe:", len(df))

print("Stati mancanti:", df["geolocation_state"].isna().sum())
print("Stati diversi:", df["geolocation_state"].nunique())

print(df["geolocation_state"].value_counts())

print("Latitudini mancanti:", df["geolocation_lat"].isna().sum())
print("Longitudini mancanti:", df["geolocation_lng"].isna().sum())

print("Latitudine minima:", df["geolocation_lat"].min())
print("Latitudine massima:", df["geolocation_lat"].max())

print("Longitudine minima:", df["geolocation_lng"].min())
print("Longitudine massima:", df["geolocation_lng"].max())



# Controlliamo quali righe hanno coordinate molto probabilmente fuori dal Brasile

coordinate_sospette = df[
    (df["geolocation_lat"] > 10) |
    (df["geolocation_lat"] < -35) |
    (df["geolocation_lng"] > -30) |
    (df["geolocation_lng"] < -75)
]

print("Coordinate sospette:", len(coordinate_sospette))

print("\nPrime 20 coordinate sospette:")
print(
    coordinate_sospette[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].head(20)
)




print(
    coordinate_sospette[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].to_string(index=False)
)



print(
    coordinate_sospette[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].value_counts().to_string()
)



zip_sospetti = coordinate_sospette["geolocation_zip_code_prefix"].unique()

df_zip_sospetti = df[
    df["geolocation_zip_code_prefix"].isin(zip_sospetti)
].copy()

print(
    df_zip_sospetti[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].sort_values(
        ["geolocation_zip_code_prefix", "geolocation_lat"]
    ).to_string(index=False)
)



print("Righe totali:", len(df))
print("Colonne:", df.columns.tolist())


df["coordinate_sospette"] = (
    (df["geolocation_lat"] > 10) |
    (df["geolocation_lat"] < -35) |
    (df["geolocation_lng"] > -30) |
    (df["geolocation_lng"] < -75)
)

print(df["coordinate_sospette"].value_counts())


duplicati = df.duplicated(
    subset=[
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ]
)

print("Righe duplicate:", duplicati.sum())
print("Righe uniche:", (~duplicati).sum())


frequenza_righe = (
    df[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ]
    .value_counts()
)

print("Numero di combinazioni uniche:", len(frequenza_righe))

print("\nPrime 20 combinazioni più frequenti:")
print(frequenza_righe.head(20))



distribuzione_duplicati = frequenza_righe.value_counts().sort_index()

print(distribuzione_duplicati.head(20))


duplicati_coordinate = (
    df.groupby(
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng"
        ]
    )
    .agg(
        citta_diverse=("geolocation_city_normalized_2", "nunique"),
        stati_diversi=("geolocation_state", "nunique")
    )
)

print("Coordinate associate a più città:", 
      (duplicati_coordinate["citta_diverse"] > 1).sum())

print("Coordinate associate a più stati:", 
      (duplicati_coordinate["stati_diversi"] > 1).sum())

coordinate_multi_stato = duplicati_coordinate[
    duplicati_coordinate["stati_diversi"] > 1
]

print(coordinate_multi_stato)


righe_multi_stato = df[
    df.set_index(
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng"
        ]
    ).index.isin(coordinate_multi_stato.index)
]

print(
    righe_multi_stato[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ]
    ].to_string(index=False)
)




df["stato_incoerente"] = (
    df.set_index(
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng"
        ]
    ).index.isin(coordinate_multi_stato.index)
)

print(df["stato_incoerente"].value_counts())




stato_principale = (
    df.groupby(
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng"
        ]
    )["geolocation_state"]
    .agg(lambda x: x.mode()[0])
)

indice_coordinate = pd.MultiIndex.from_frame(
    df[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng"
        ]
    ]
)

df["stato_incoerente"] = (
    df["geolocation_state"].values
    != indice_coordinate.map(stato_principale).values
)

print(df["stato_incoerente"].value_counts())


coordinate_per_zip = (
    df.groupby("geolocation_zip_code_prefix")
    .agg(
        lat_min=("geolocation_lat", "min"),
        lat_max=("geolocation_lat", "max"),
        lng_min=("geolocation_lng", "min"),
        lng_max=("geolocation_lng", "max")
    )
)

coordinate_per_zip["lat_diff"] = (
    coordinate_per_zip["lat_max"] - coordinate_per_zip["lat_min"]
)

coordinate_per_zip["lng_diff"] = (
    coordinate_per_zip["lng_max"] - coordinate_per_zip["lng_min"]
)

print(coordinate_per_zip.sort_values(
    "lat_diff",
    ascending=False
).head(20))


print("\n")


coordinate_per_zip_pulito = (
    df[df["coordinate_sospette"] == False]
    .groupby("geolocation_zip_code_prefix")
    .agg(
        lat_min=("geolocation_lat", "min"),
        lat_max=("geolocation_lat", "max"),
        lng_min=("geolocation_lng", "min"),
        lng_max=("geolocation_lng", "max")
    )
)

coordinate_per_zip_pulito["lat_diff"] = (
    coordinate_per_zip_pulito["lat_max"]
    - coordinate_per_zip_pulito["lat_min"]
)

coordinate_per_zip_pulito["lng_diff"] = (
    coordinate_per_zip_pulito["lng_max"]
    - coordinate_per_zip_pulito["lng_min"]
)

print(
    coordinate_per_zip_pulito
    .sort_values("lat_diff", ascending=False)
    .head(20)
)     

print("\n")

controllo_zip = (
    df[df["geolocation_zip_code_prefix"] == 68985]
    .groupby(
        [
            "geolocation_lat",
            "geolocation_lng"
        ]
    )
    .size()
    .sort_values(ascending=False)
)

print(controllo_zip.head(20))


print("\n")



coordinate_principali = (
    df[df["coordinate_sospette"] == False]
    .groupby(
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng"
        ]
    )
    .size()
    .reset_index(name="numero_righe")
)

coordinate_principali = (
    coordinate_principali
    .sort_values(
        [
            "geolocation_zip_code_prefix",
            "numero_righe"
        ],
        ascending=[True, False]
    )
)

coordinate_principali["posizione"] = (
    coordinate_principali
    .groupby("geolocation_zip_code_prefix")
    .cumcount()
)

print(
    coordinate_principali[
        coordinate_principali["posizione"] == 0
    ].head(20)
)


# Numero totale di righe per ogni ZIP
righe_per_zip = (
    df[df["coordinate_sospette"] == False]
    .groupby("geolocation_zip_code_prefix")
    .size()
    .rename("righe_totali")
)

# Uniamo il numero totale alla coordinata principale
controllo_zip = coordinate_principali[
    coordinate_principali["posizione"] == 0
].copy()

controllo_zip = controllo_zip.merge(
    righe_per_zip,
    on="geolocation_zip_code_prefix"
)

# Percentuale di righe rappresentate dalla coordinata principale
controllo_zip["percentuale_principale"] = (
    controllo_zip["numero_righe"]
    / controllo_zip["righe_totali"]
    * 100
)

print(
    controllo_zip.sort_values(
        "percentuale_principale"
    ).head(20)
)

print("\n")


stati_per_zip = (
    df.groupby("geolocation_zip_code_prefix")["geolocation_state"]
    .nunique()
)

zip_multi_stato = stati_per_zip[stati_per_zip > 1]

print("ZIP associati a più stati:", len(zip_multi_stato))
print(zip_multi_stato)


zip_multi_stato_dettaglio = (
    df[
        df["geolocation_zip_code_prefix"].isin(zip_multi_stato.index)
    ]
    .groupby(
        [
            "geolocation_zip_code_prefix",
            "geolocation_state",
            "geolocation_city_normalized_2"
        ]
    )
    .size()
    .reset_index(name="numero_righe")
    .sort_values(
        [
            "geolocation_zip_code_prefix",
            "numero_righe"
        ],
        ascending=[True, False]
    )
)

print(zip_multi_stato_dettaglio.to_string(index=False))

print("\n")

righe_zip_stato_sospette = df[
    df["geolocation_zip_code_prefix"].isin(zip_multi_stato.index)
].copy()

stato_principale_zip = (
    righe_zip_stato_sospette
    .groupby("geolocation_zip_code_prefix")["geolocation_state"]
    .agg(lambda x: x.mode()[0])
)

righe_zip_stato_sospette["stato_principale_zip"] = (
    righe_zip_stato_sospette["geolocation_zip_code_prefix"]
    .map(stato_principale_zip)
)

righe_zip_stato_sospette = righe_zip_stato_sospette[
    righe_zip_stato_sospette["geolocation_state"]
    != righe_zip_stato_sospette["stato_principale_zip"]
]

print(
    righe_zip_stato_sospette[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
            "stato_principale_zip"
        ]
    ].to_string(index=False)
)

print("\n")

stato_principale_zip = (
    df.groupby("geolocation_zip_code_prefix")["geolocation_state"]
    .agg(lambda x: x.mode()[0])
)

df["stato_incoerente_zip"] = (
    df["geolocation_state"]
    != df["geolocation_zip_code_prefix"].map(stato_principale_zip)
)

print(df["stato_incoerente_zip"].value_counts())

print("\n")

print(df.dtypes)
df.info()