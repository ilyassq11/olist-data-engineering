import os
import pandas as pd

cartella_data = r"C:\Users\ilyas\Desktop\olist-data-engineering\data"

file_csv = [
    file
    for file in os.listdir(cartella_data)
    if file.endswith(".csv")
]

print("File CSV trovati:")
for file in sorted(file_csv):
    print("-", file)


orders = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_orders_dataset.csv"
)

print(orders.head())
print()
print(orders.info())    

duplicati_order_id = orders["order_id"].duplicated().sum()

print("Order ID duplicati:", duplicati_order_id)
print("Order ID unici:", orders["order_id"].nunique())
print("Righe totali:", len(orders))

print("\n")

print("Customer ID mancanti:", orders["customer_id"].isna().sum())
print("Customer ID distinti:", orders["customer_id"].nunique())
print("Righe totali:", len(orders))

print("\n")

ordini_per_cliente = orders["customer_id"].value_counts()

print("Clienti con più di un ordine:", (ordini_per_cliente > 1).sum())
print("Numero massimo di ordini per customer_id:", ordini_per_cliente.max())

print("\n")

print(
    orders.groupby("order_status")[
        [
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].apply(lambda x: x.isna().sum())
)

colonne_date = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for colonna in colonne_date:
    orders[colonna] = pd.to_datetime(orders[colonna])

orders.info()

print("\n")

approvazione_prima_acquisto = (
    orders["order_approved_at"] < orders["order_purchase_timestamp"]
).sum()

print("Approvazione prima dell'acquisto:", approvazione_prima_acquisto)

consegna_corriere_prima_approvazione = (
    orders["order_delivered_carrier_date"] < orders["order_approved_at"]
).sum()

print(
    "Consegna al corriere prima dell'approvazione:",
    consegna_corriere_prima_approvazione
)

differenza_approvazione_corriere = (
    orders["order_delivered_carrier_date"]
    - orders["order_approved_at"]
)

casi_anomali = differenza_approvazione_corriere < pd.Timedelta(0)

print("Casi:", casi_anomali.sum())
print(
    "Differenza minima:",
    differenza_approvazione_corriere[casi_anomali].min()
)
print(
    "Differenza massima:",
    differenza_approvazione_corriere[casi_anomali].max()
)

ordini_anomali = orders[
    orders["order_delivered_carrier_date"] < orders["order_approved_at"]
]

print(
    ordini_anomali["order_status"].value_counts()
)

print(
    ordini_anomali[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].head(10).to_string(index=False)
)

caso_estremo = ordini_anomali.loc[
    differenza_approvazione_corriere.idxmin()
]

print(caso_estremo.to_string())

corriere_prima_acquisto = (
    orders["order_delivered_carrier_date"]
    < orders["order_purchase_timestamp"]
).sum()

print(
    "Consegna al corriere prima dell'acquisto:",
    corriere_prima_acquisto
)

orders["data_corriere_anomala"] = (
    orders["order_delivered_carrier_date"]
    < orders["order_purchase_timestamp"]
)

print(
    orders["data_corriere_anomala"].value_counts()
)

orders["data_consegna_cliente_anomala"] = (
    orders["order_delivered_customer_date"]
    < orders["order_purchase_timestamp"]
)

print(orders["data_consegna_cliente_anomala"].value_counts())

orders["consegna_in_ritardo"] = (
    orders["order_delivered_customer_date"]
    > orders["order_estimated_delivery_date"]
)

print(orders["consegna_in_ritardo"].value_counts())

print(orders["order_status"].value_counts())