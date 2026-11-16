# Proyek Analisis Data: E-Commerce Public Dataset ✨

Analisis pesanan e-commerce (Olist, Brasil) periode Januari 2017 - Agustus 2018 untuk menjawab:
1. Kategori produk apa yang masuk 10 besar revenue dan berapa kontribusinya?
2. State mana yang paling sering terlambat dan seberapa besar dampaknya ke review score?

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   └── products_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
cd submission
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```
cd dashboard
streamlit run dashboard.py
```
Dashboard terbuka di http://localhost:8501

## Menjalankan Ulang Notebook (opsional)
```
pip install jupyter
jupyter notebook notebook.ipynb
```
Jalankan seluruh sel. Sel terakhir akan menghasilkan ulang `dashboard/main_data.csv`.
