# WIP: Python Store Inventory Management App

Demo console application written in Python using SQLAlchemy and SQLite.

This app uses my knowledge of CSV, File I/O, database ORMs, and statistics to create a product management inventory system that allows users to interact with product data. The data is cleaned from the CSV file before it is added to an SQLite database. All interactions with the records use ORM methods for viewing records, creating records, and exporting a new CSV backup.

Statistical calculations are performed on the data to provide the user with information about products in the database. Stats include:

- Total products
- Most expensive
- Least expensive
- Most common brand
- Least common brand
- Oldest product
- Newest product
- Highest quantity
- Lowest quantity
- Average price (mean)
- Mode price (most occurring value)
- Median price (sorted middle value)
- Variance of prices (for entire population)
- Standard Deviation of prices (for entire population)
- Quartiles:
  - Q1 (lower half price median)
  - Q2 (median)
  - Q3 (upper half price median)
- Interquartile range (IQR)

---

## Technology Used

- [Python](https://www.python.org/) Programming language that lets you work quickly
and integrate systems more effectively. ([docs](https://docs.python.org/3/))
- [Python Mathematical statistics module](https://docs.python.org/3/library/statistics.html) Functions used for calculating mathematical statistics of numeric data.
- [SQLAlchemy](https://www.sqlalchemy.org/) The Python SQL Toolkit and Object Relational Mapper ([docs](https://docs.sqlalchemy.org/en/latest/))
- [SQLite](https://www.sqlite.org/) The most used database engine in the world. ([docs](https://www.sqlite.org/docs.html))
- [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file format used for storing imported and exported data in a human-readable including a header row of field names.

---

## Run the app

Clone this repo then `cd python-store-inventory-management-app`.

Assuming you have Python3 installed on a MacOS, run these commands (or something similar):

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python app.py
```

When done running the app, you can deactivate the virtual environment by running `deactivate`.

---

## Screenshot

![Screen Shot 2022-09-13 at 10 35 27 PM](https://user-images.githubusercontent.com/764270/190053899-1be9711b-a029-49f3-9f79-0f2be02f951f.png)

