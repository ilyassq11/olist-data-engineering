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

## analisi tabella order_item

order_items = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_order_items_dataset.csv"
)

print(order_items.head())
print()
order_items.info()

# 1. Controlliamo la chiave composta
duplicati_item = order_items.duplicated(
    subset=["order_id", "order_item_id"]
).sum()

print("Duplicati order_id + order_item_id:", duplicati_item)


# 2. Controlliamo che tutti gli order_id esistano nella tabella orders
ordini_mancanti = ~order_items["order_id"].isin(orders["order_id"])

print("Order ID presenti in order_items ma non in orders:",
      ordini_mancanti.sum())


# 3. Controlliamo i valori di order_item_id
print("\nValori order_item_id:")
print(order_items["order_item_id"].value_counts().sort_index())


# 4. Controlliamo prezzi e costi di spedizione anomali
print("\nPrezzi <= 0:", (order_items["price"] <= 0).sum())
print("Freight <= 0:", (order_items["freight_value"] <= 0).sum())


# 5. Controlliamo le date di spedizione
order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"]
)

print("\nDate shipping_limit_date convertite.")
print(order_items["shipping_limit_date"].describe())

print("Freight = 0:", (order_items["freight_value"] == 0).sum())
print("Freight < 0:", (order_items["freight_value"] < 0).sum())

print("\nValori freight negativi:")
print(
    order_items.loc[
        order_items["freight_value"] < 0,
        ["order_id", "order_item_id", "price", "freight_value"]
    ]
)


## analisi tabella products

products = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_products_dataset.csv"
)

print(products.head())
print()
products.info()


# 1. Product ID: deve essere unico
print("\nProduct ID duplicati:", products["product_id"].duplicated().sum())


# 2. Valori mancanti
print("\nValori mancanti:")
print(products.isna().sum())


# 3. Valori impossibili o sospetti
colonne_numeriche = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("\nValori <= 0:")
for colonna in colonne_numeriche:
    print(colonna, ":", (products[colonna] <= 0).sum())


# 4. Product ID usati negli ordini ma assenti da products
product_mancanti = ~order_items["product_id"].isin(products["product_id"])

print(
    "\nProduct ID presenti in order_items ma non in products:",
    product_mancanti.sum()
)

print(
    products.loc[
        products["product_weight_g"] <= 0,
        ["product_id", "product_category_name", "product_weight_g"]
    ]
)


## analisi tabella customers

customers = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_customers_dataset.csv"
)

print(customers.head())
print()
customers.info()

# 1. Customer ID: deve essere unico
print(
    "\ncustomer_id duplicati:",
    customers["customer_id"].duplicated().sum()
)

# 2. Customer unique ID: controlliamo quanti clienti reali
print(
    "customer_unique_id distinti:",
    customers["customer_unique_id"].nunique()
)

print(
    "customer_unique_id duplicati:",
    customers["customer_unique_id"].duplicated().sum()
)

# 3. Controlliamo che tutti i customer_id usati negli ordini
#    esistano nella tabella customers
customer_mancanti = ~orders["customer_id"].isin(
    customers["customer_id"]
)

print(
    "\nCustomer ID presenti in orders ma non in customers:",
    customer_mancanti.sum()
)

# 4. Controlliamo gli stati
print("\nStati:")
print(customers["customer_state"].value_counts().sort_index())

## analisi tabella sellers

sellers = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_sellers_dataset.csv"
)

print("\n Tabella sellers")
print(sellers.head())
print()
sellers.info()

# 1. Seller ID: deve essere unico
print(
    "seller_id duplicati:",
    sellers["seller_id"].duplicated().sum()
)

# 2. Controlliamo che tutti i seller_id presenti negli ordini
#    esistano nella tabella sellers
seller_mancanti = ~order_items["seller_id"].isin(
    sellers["seller_id"]
)

print(
    "Seller ID presenti in order_items ma non in sellers:",
    seller_mancanti.sum()
)

# 3. Controlliamo gli stati
print("\nStati:")
print(sellers["seller_state"].value_counts().sort_index())

## Analisi tabella order_payments

order_payments = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_order_payments_dataset.csv"
)

print("\n Tabella order_payments")
print(order_payments.head())
print()
order_payments.info()

# 1. Chiave composta
print(
    "Duplicati order_id + payment_sequential:",
    order_payments.duplicated(
        subset=["order_id", "payment_sequential"]
    ).sum()
)

# 2. Integrità referenziale con orders
ordini_mancanti = ~order_payments["order_id"].isin(
    orders["order_id"]
)

print(
    "Order ID presenti nei pagamenti ma non in orders:",
    ordini_mancanti.sum()
)

# 3. Controlliamo i tipi di pagamento
print("\nTipi di pagamento:")
print(order_payments["payment_type"].value_counts())

# 4. Valori anomali
print(
    "\nPayment value <= 0:",
    (order_payments["payment_value"] <= 0).sum()
)

print(
    "Installments <= 0:",
    (order_payments["payment_installments"] <= 0).sum()
)


print("\n=== PAYMENT VALUE <= 0 ===")
print(
    order_payments.loc[
        order_payments["payment_value"] <= 0
    ]
)

print("\n=== INSTALLMENTS <= 0 ===")
print(
    order_payments.loc[
        order_payments["payment_installments"] <= 0
    ]
)

print("\n=== NOT_DEFINED ===")
print(
    order_payments.loc[
        order_payments["payment_type"] == "not_defined"
    ]
)

## Analisi tabella order_reviews

order_reviews = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_order_reviews_dataset.csv"
)

print("\n Tabella order_reviews")
print(order_reviews.head())
print()
order_reviews.info()

# 1. review_id dovrebbe essere unico
print(
    "review_id duplicati:",
    order_reviews["review_id"].duplicated().sum()
)

# 2. Tutti gli ordini recensiti devono esistere in orders
ordini_mancanti = ~order_reviews["order_id"].isin(
    orders["order_id"]
)

print(
    "Order ID presenti nelle recensioni ma non in orders:",
    ordini_mancanti.sum()
)

# 3. Controlliamo il range dei punteggi
print("\nReview score:")
print(order_reviews["review_score"].value_counts().sort_index())

# 4. Controlliamo le date
order_reviews["review_creation_date"] = pd.to_datetime(
    order_reviews["review_creation_date"]
)

order_reviews["review_answer_timestamp"] = pd.to_datetime(
    order_reviews["review_answer_timestamp"]
)

print("\nDate convertite.")

# 5. Risposte precedenti alla creazione della recensione
print(
    "Risposte prima della creazione:",
    (
        order_reviews["review_answer_timestamp"]
        < order_reviews["review_creation_date"]
    ).sum()
)


duplicati_review = order_reviews[
    order_reviews["review_id"].duplicated(keep=False)
].sort_values("review_id")

print(
    "Review ID duplicati associati a più order_id:",
    duplicati_review.groupby("review_id")["order_id"].nunique().gt(1).sum()
)

print("\nEsempi:")
print(duplicati_review.head(20))


print(
    "Duplicati review_id con contenuto diverso:"
)

print(
    order_reviews.groupby("review_id")
    .nunique()
    .max(axis=1)
    .gt(1)
    .sum()
)


duplicati_review = order_reviews[
    order_reviews["review_id"].duplicated(keep=False)
]

print(
    duplicati_review.groupby("review_id")[
        [
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp"
        ]
    ].nunique().max().sort_values(ascending=False)
)

## Analisi tabella product_category_name_translation

category_translation = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\product_category_name_translation.csv"
)

print(category_translation.head())
print()
category_translation.info()


# 1. Controlliamo che la categoria portoghese sia unica
print(
    "Categorie portoghesi duplicate:",
    category_translation["product_category_name"].duplicated().sum()
)

# 2. Controlliamo che anche la traduzione inglese sia unica
print(
    "Categorie inglesi duplicate:",
    category_translation["product_category_name_english"].duplicated().sum()
)

# 3. Categorie presenti nei prodotti ma assenti nella tabella di traduzione
categorie_mancanti = ~products["product_category_name"].dropna().isin(
    category_translation["product_category_name"]
)

print(
    "Categorie dei prodotti senza traduzione:",
    categorie_mancanti.sum()
)

categorie_senza_traduzione = (
    products.loc[
        products["product_category_name"].notna()
        & ~products["product_category_name"].isin(
            category_translation["product_category_name"]
        ),
        "product_category_name"
    ]
    .unique()
)

print("Categorie senza traduzione:", len(categorie_senza_traduzione))
print(categorie_senza_traduzione)