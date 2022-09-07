"""Python Store Inventory Management App"""

import csv
import time
from datetime import datetime
from statistics import mean, median, mode, pstdev, pvariance, quantiles

from sqlalchemy import func

from models import Base, Brand, Product, engine, session


def main_menu():
    """Display the main menu and get user input."""
    while True:
        print()
        print('Store Inventory Management App'.center(50))
        print('='*50)
        print('MAIN MENU'.center(50))
        print('='*50)
        print('''
            \rN) New Product
            \rV) View a Product by ID
            \rA) View Product Analysis
            \rB) Backup the Database
            \rL) List All Products
            \rR) List All Brands
            \rQ) Quit the Application''')
        choice = input("\nWhat would you like to do? ").strip().lower()
        # Validate users choice
        if choice in ['n', 'v', 'a', 'b', 'l', 'r', 'q']:
            return choice
        else:
            input('''
                \rPlease choose one of the options above.
                \rPress enter to try again.''')


def product_menu():
    """Display the product sub menu and get user input."""
    while True:
        print('''
            e - edit product
            d - delete product
            q - return to main menu''')
        choice = input("\nWhat would you like to do? ").strip().lower()
        # Validate users choice
        if choice in ['e', 'd', 'q']:
            return choice
        else:
            input('''
            Please choose one of the options above.
            Press enter to try again.''')


def clean_date(date_str):
    """Clean date string from user input.

    Split date values from format mm/dd/yyyy into separate variables,
    then convert to datetime object format year, month, day

    Args:
        date_str (str): String to interpret as a date.

    Returns:
        datetime.datetime: Date in datetime object format.
    """
    split_date = date_str.split('/')
    date = datetime(int(split_date[2]), int(split_date[0]), int(split_date[1]))
    return date


def humanize_date(date):
    """Convert datetime object to human friendly format.

    Args:
        date (datetime.date): Date to convert.

    Returns:
        datetime.date: Date in human friendly format.
    """
    return date.strftime('%B %d, %Y')


def clean_price(price_str):
    """Clean price string from user input.

    Args:
        price_str (str): String to interpret as a price.

    Returns:
        int: Price in cents
    """
    try:
        price_float = float(price_str.lstrip('$'))
    except ValueError:
        input('''
              \n***** PRICE ERROR *****
              \rThe price format should be a number without a currency symbol.
              \rEx: 12.99
              \rPress enter to try again.''')
        return
    else:
        return int(price_float * 100)


def humanize_price(price):
    """Convert price to human friendly format.

    Args:
        price (int): Price in cents.

    Returns:
        str: Price in human friendly format.
    """
    return f'${price / 100:.2f}'


def check_id(id_str, id_options):
    """Clean id string from user input.

    Used to check product id and brand id.

    Check if id entered is a number and if it is in the list of valid ids.

    Args:
        id_str (str): String to interpret as an id.
        id_options (list): List of valid id numbers.
    """
    try:
        item_id = int(id_str)
    except ValueError:
        input('''***** ID ERROR *****
              \rThe id should be a number.
              \rExample: 1
              \rPress enter to try again.''')
        return
    else:
        if item_id in id_options:
            return item_id
        else:
            input(f'''***** ID ERROR *****
              \rOptions are: {', '.join(map(str, id_options))}
              \rPress enter to try again.''')
            return


def check_quantity(qty):
    """Check if quantity is an integer.

    Args:
        qty (_type_): The value to check.
    """
    try:
        qty_int = int(qty)
    except ValueError:
        input('''
              \n***** QUANTITY ERROR *****
              \rThe quantity should be a number.
              \rExample: 100
              \rPress enter to try again.''')
        return
    else:
        return qty_int


def get_brand_name(brand_id):
    """Get brand name from brand id.

    Args:
        brand_id (int): The brand id to lookup.
    """
    brand = session.query(Brand).filter_by(brand_id=brand_id).first()
    if brand:
        return brand.brand_name
    else:
        return 'None'


def get_quantity_input(current_value):
    """Get quantity from user input."""
    quantity_error = True
    quantity_checked = None
    while quantity_error:
        if current_value:
            # If there's a current value, we're updating and existing product
            quantity = input(
                'Current quantity is {}.\nPlease enter the new quantity: '
                .format(
                    current_value
                )).strip()
        else:
            # If no current value, we must be creating a new product
            quantity = input('Quantity: ').strip()
        quantity_checked = check_quantity(quantity)
        # Use isinstance(obj, int) instead of type(obj) == int for performance
        # REF: https://switowski.com/blog/type-vs-isinstance
        if isinstance(quantity_checked, int):
            quantity_error = False
    return quantity_checked


def get_price_input(current_value):
    """Get price from user input."""
    price_error = True
    price_cleaned = None
    while price_error:
        if current_value:
            # If there's a current value, we're updating and existing product
            price = input(
                'Current price is {}.\nPlease enter the new price (Ex: 12.99): '
                .format(
                    humanize_price(current_value)
                )).strip()
        else:
            # If no current value, we must be creating a new product
            price = input('Price (Ex: 12.99): ').strip()
        price_cleaned = clean_price(price)
        if isinstance(price_cleaned, int):
            price_error = False
    return price_cleaned


def get_brand_input(current_value):
    """Get brand from user input."""
    id_error = True
    id_cleaned = None
    while id_error:
        # List brand ids with brand names
        id_options = []
        print("Brand options list:")
        for brand in session.query(Brand).order_by(Brand.brand_id):
            id_options.append(brand.brand_id)
            print(f'{brand.brand_id}) {brand.brand_name}')
        if current_value:
            # If there's a current value, we're updating and existing product
            id_str = input(
                "Current brand ID is {}: {}.\nPlease enter the new brand's ID ({}-{}) or 'X' if the brand is not listed: "
                .format(
                    current_value,
                    get_brand_name(current_value),
                    id_options[0],
                    id_options[-1]
                )).strip()
        else:
            # If no current value, we must be creating a new product
            id_str = input(
                "Enter a brand's ID ({}-{}) or 'X' if the brand is not listed: "
                .format(
                    id_options[0],
                    id_options[-1]
                )).strip()

        if id_str.lower() == 'x':
            id_error = False
        else:
            id_cleaned = check_id(id_str, id_options)
            id_error = False
    return id_cleaned


def confirm_product_info(name, quantity, price, brand_name):
    """Confirm product info with user before committing to database."""
    print(f'''
      \rProduct Name: {name}
      \rQuantity: {quantity}
      \rPrice: {price}
      \rBrand: {brand_name}
      ''')
    return input('Is this correct? (y/N): ').strip().lower()


def print_section_header(txt):
    """Template to use when printing section headers."""
    print('-'*50)
    print(txt.center(50))
    print('-'*50)


def add_product():
    """Add a new product to the database."""
    print_section_header('ADD NEW PRODUCT')
    # Get input values
    name = input('Name: ').strip()
    quantity_input = get_quantity_input(None)
    price_input = get_price_input(None)
    brand_input = get_brand_input(None)
    # Check for duplicate product names
    # If duplicate product names are found while attempting to add a new
    # product, get the most recently updated and save to that existing product.
    duplicate_product_names_in_db = session.query(Product).filter_by(product_name=name).order_by(Product.date_updated.desc())
    if duplicate_product_names_in_db.count() > 0:
        # Let the user know how many duplicate product names already exist
        print('\nNOTE: {} duplicate product(s) found with the same name: {}'
              .format(
                  duplicate_product_names_in_db.count(),
                  name)
              )
        # Since results are ordered by date_updated, the first result is the
        # most recently updated product.
        product = duplicate_product_names_in_db[0]
        print(f'The most recently edited version will be updated (product ID {product.product_id})')
        product.product_quantity = quantity_input
        product.product_price = price_input
        product.brand_id = brand_input
        product.date_updated = datetime.now()
        # Confirm input
        confirm = confirm_product_info(
            name,
            quantity_input,
            humanize_price(price_input),
            get_brand_name(brand_input)
        )
        if confirm == 'y':
            session.commit()
            print(f'\nProduct ID {product.product_id} has been updated in the database.')
        else:
            print('\nProduct not updated.')
    else:
        # Confirm input
        confirm = confirm_product_info(
            name,
            quantity_input,
            humanize_price(price_input),
            get_brand_name(brand_input)
        )
        if confirm == 'y':
            new_product = Product(product_name=name,
                                  product_quantity=quantity_input,
                                  product_price=price_input,
                                  brand_id=brand_input,
                                  date_updated=datetime.now())
            session.add(new_product)
            session.commit()
            print(f'\n{name} has been added to the database.')
        else:
            print('\nProduct not added.')
    time.sleep(1.5)


def edit_product(product_id):
    """Edit a product in the database."""
    product = session.query(Product).filter_by(product_id=product_id).one()
    print('-'*50)
    print(f'Editing {product.product_name}')
    # Get input values
    quantity_input = get_quantity_input(product.product_quantity)
    price_input = get_price_input(product.product_price)
    brand_input = get_brand_input(product.brand_id)
    # Confirm input
    confirm = confirm_product_info(
        product.product_name,
        quantity_input,
        humanize_price(price_input),
        get_brand_name(brand_input)
    )
    if confirm == 'y':
        product.product_quantity = quantity_input
        product.product_price = price_input
        product.brand_id = brand_input
        product.date_updated = datetime.now()
        session.commit()
        print(f'\n{product.product_name} has been updated in the database.')
    else:
        print('\nProduct not updated.')
    time.sleep(1.5)


def view_product():
    """View a product by id."""
    print_section_header('VIEW PRODUCT BY ID')
    id_options = []
    id_cleaned = None
    for product in session.query(Product).order_by(Product.product_id):
        id_options.append(product.product_id)
    id_error = True
    while id_error:
        id_str = input(
            f"Enter a product's ID number ({id_options[0]}-{id_options[-1]}): ").strip()
        id_cleaned = check_id(id_str, id_options)
        id_error = False
    the_product = session.query(Product).filter_by(product_id=id_cleaned).one_or_none()
    print('*'*50)
    print(f'''*** {the_product.product_name} ***
          \rPrice: {humanize_price(the_product.product_price)}
          \rQuantity: {the_product.product_quantity}
          \rBrand: {get_brand_name(the_product.brand_id)}
          \rDate Updated: {humanize_date(the_product.date_updated)}''')
    print('*'*50)
    product_choice = product_menu()
    if product_choice == 'e':
        edit_product(the_product.product_id)
    elif product_choice == "d":
        confirm = input(f'Are you sure you want to delete {the_product.product_name}? (y/N): ').strip().lower()
        if confirm == 'y':
            session.delete(the_product)
            session.commit()
            print(f'{the_product.product_name} has been deleted.')
        else:
            print(f'{the_product.product_name} has not been deleted.')
        time.sleep(1.5)
    else:
        return


def backup_db():
    """Backup the database."""
    print_section_header('BACKUP DATABASE')
    print("Backing up data...")
    time.sleep(1.5)
    with open('inventory-backup.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['product_id',
                         'product_name',
                         'product_quantity',
                         'product_price',
                         'brand_id',
                         'date_updated'])
        for product in session.query(Product).order_by(Product.product_id):
            writer.writerow([product.product_id,
                             product.product_name,
                             product.product_quantity,
                             product.product_price,
                             product.brand_id,
                             product.date_updated])
    print("Product data has been backed-up to the file 'inventory_backup.csv'.")


def list_products():
    """List all products in the database."""
    print_section_header('LIST ALL PRODUCTS')
    for product in session.query(Product).order_by(Product.product_id):
        print('{}: {}, Qty: {}, Price: {}, Brand: {}, Updated: {}'
              .format(
                  product.product_id,
                  product.product_name,
                  product.product_quantity,
                  humanize_price(product.product_price),
                  get_brand_name(product.brand_id),
                  humanize_date(product.date_updated)
                  )
              )
    input('\nPress enter to return to the main menu.')


def list_brands():
    """List all brands in the database."""
    print_section_header('LIST ALL BRANDS')
    for brand in session.query(Brand).order_by(Brand.brand_id):
        # Get the number of products associated with the brand
        product_count = session.query(Product).filter_by(brand_id=brand.brand_id).count()
        print(f'{brand.brand_id}: {brand.brand_name}, Number of Products: {product_count}')
    input('\nPress enter to return to the main menu.')


def analyze_products():
    """Analyze products in the database."""
    print_section_header('PRODUCT ANALYSIS')

    product_query = session.query(Product)

    # Get the total number of products
    total_products = product_query.count()

    # Get most expensive and least expensive products
    most_expensive = product_query.order_by(
        Product.product_price.desc()).first()
    least_expensive = product_query.order_by(
        Product.product_price.asc()).first()

    # Get oldest and newest products
    oldest_product = product_query.order_by(
        Product.date_updated.asc()).first()
    newest_product = product_query.order_by(
        Product.date_updated.desc()).first()

    # Create list of all product prices
    product_prices = []
    for product in product_query:
        product_prices.append(product.product_price)
    mean_price = mean(product_prices)
    mode_price = mode(product_prices)
    median_price = median(product_prices)

    # Get highest and lowest quantity products
    large_qty = product_query.order_by(
        Product.product_quantity.desc()).first()
    low_qty = session.query(Product).order_by(
        Product.product_quantity.asc()).first()

    # Get brands with the most and least products
    # This query returns a list of tuples containing each brand_id and the
    # count of products associated with it.
    # NOTE: I'm filtering out Null (None) brand_ids because I don't want to
    # count them as an actual brand.
    products_grouped_by_brand = session.query(
        Product.brand_id,
        func.count(Product.product_id)
    ).group_by(Product.brand_id).filter(Product.brand_id != 0)
    # Since there doesn't seem to be an easy way to get the last row of a
    # query, I'm creating asc and desc lists and then getting the first()
    # item from each list.
    brands_ordered_by_product_count_desc = products_grouped_by_brand.order_by(
        func.count(Product.brand_id).desc()
    )
    brands_ordered_by_product_count_asc = products_grouped_by_brand.order_by(
        func.count(Product.brand_id).asc()
    )
    # These return a single tuple like (brand_id, product_count)
    most_common_brand = brands_ordered_by_product_count_desc.first()
    least_common_brand = brands_ordered_by_product_count_asc.first()
    # Get the brand_name value based on each brand_id
    most_common_brand_in_db = session.query(Brand).filter_by(
                brand_id=most_common_brand[0]).one_or_none()
    least_common_brand_in_db = session.query(Brand).filter_by(
                brand_id=least_common_brand[0]).one_or_none()

    # Variance
    # DEF: pvariance() is a measure of the variability (spread or dispersion)
    # of an entire population of data. Note variance() is a measure of the
    # variability of a sample of data (not the entire population of values).
    # It's the average of each point from the mean.
    #
    # Useful since an average (mean) is not always a good indication of the
    # tentative value (or expected price).
    # https://qr.ae/pvODEn
    #
    # A small variance indicates values are clustered closely around the mean.
    # If this value is less than the mean, it means that on average, product
    # prices have a low difference with the mean (close to the mean).
    #
    # A large variance indicates that the data is spread out.
    # If this value is higher than the mean, there are a lot of extreme values,
    # and the mean is a poor estimate of the actual prices.
    #
    # REF: https://docs.python.org/3/library/statistics.html#statistics.pvariance
    # I'm dividing the result by 100 here to get a dollar-friendly number.
    pv = round(pvariance(product_prices) / 100)

    # Standard Deviation
    # DEF: The standard deviation is a measure of how spread out numbers are.
    # It's the square root of the population variance.
    #
    # Standard deviation is expressed in the same units as the original values
    # (e.g., minutes or meters).
    #
    # A low standard deviation indicates that the values tend to be close to the mean.
    # A high standard deviation indicates that the values are spread out over a wider range.
    #
    # Using Standard Deviation, we have a "standard" way of knowing what is
    # a normal range, and thus we can find extremely large or small values.
    # https://www.mathsisfun.com/data/standard-deviation.html
    #
    # REF: https://docs.python.org/3/library/statistics.html#statistics.pstdev
    psd = pstdev(product_prices)

    # Quartiles
    # DEF: The IQR is the difference between the 75th percentile and the 25th
    # percentile, which is the middle 50% of the data.
    # The IQR is a more robust measure of price spread than simply using
    # highest-price - lowest-price as the range because the IQR is less
    # sensitive to outliers (very high or very low values).
    #
    # A quartile is a type of quantile.
    # https://www.geeksforgeeks.org/interquartile-range-and-quartile-deviation-using-numpy-and-scipy/
    #
    # REF: https://docs.python.org/3/library/statistics.html#statistics.quantiles
    q1 = quantiles(product_prices)[0]
    q2 = quantiles(product_prices)[1]
    q3 = quantiles(product_prices)[2]
    iqr = q3 - q1

    time.sleep(1.5)
    print(f'''
          \rTotal products: {total_products}
          \rMost expensive: {humanize_price(most_expensive.product_price)}: {most_expensive.product_name}
          \rLeast expensive: {humanize_price(least_expensive.product_price)}: {least_expensive.product_name}
          \rMost common brand: {most_common_brand_in_db.brand_name}, Product count: {most_common_brand[1]}
          \rLeast common brand: {least_common_brand_in_db.brand_name}, Product count: {least_common_brand[1]}
          \rOldest product: {humanize_date(oldest_product.date_updated)}: {oldest_product.product_name}
          \rNewest product: {humanize_date(newest_product.date_updated)}: {newest_product.product_name}
          \rHighest quantity: {large_qty.product_quantity} {large_qty.product_name}
          \rLowest quantity: {low_qty.product_quantity} {low_qty.product_name}
          \rAverage price (mean): {humanize_price(mean_price)}
          \rMode price (most occurring value): {humanize_price(mode_price)}
          \rMedian price (sorted middle value): {humanize_price(median_price)}
          \rPrice variance: {humanize_price(pv)}
          \rPrice standard deviation: {humanize_price(psd)}
          \rQuartiles:
          \r- Q1 (lower half price median): {humanize_price(q1)}
          \r- Q2 (median): {humanize_price(q2)}
          \r- Q3 (upper half price median): {humanize_price(q3)}
          \rInterquartile range (IQR): {humanize_price(iqr)}''')
    input('\nPress enter to return to the main menu.')


def add_brands_csv():
    """Add brands from a csv file."""
    with open('brands.csv') as csvfile:
        # Using csv.DictReader to read the csv file and use the first row
        # as fieldnames and as the dictionary keys used to assign values with.
        # REF: https://docs.python.org/3.8/library/csv.html#csv.DictReader
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if brand already exists in the database
            brand_in_db = session.query(Brand).filter_by(
                brand_name=row['brand_name']).one_or_none()
            if brand_in_db is None:
                new_brand = Brand(
                    # Use the dictionary keys to assign values to the
                    # corresponding columns in the database.
                    brand_name=row['brand_name'])
                session.add(new_brand)
        session.commit()


def add_products_csv():
    """Add products from a csv file."""
    with open('inventory.csv') as csvfile:
        # Using csv.DictReader to read the csv file and use the first row
        # as fieldnames and as the dictionary keys used to assign values with.
        # REF: https://docs.python.org/3.8/library/csv.html#csv.DictReader
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if product already exists in the database
            duplicate_products_in_db = session.query(Product).filter_by(
                product_name=row['product_name'])
            if duplicate_products_in_db.count() == 0:
                new_product = Product(
                    # Use the dictionary keys to assign values to the
                    # corresponding columns in the database.
                    product_name=row['product_name'],
                    product_quantity=int(row['product_quantity']),
                    product_price=clean_price(row['product_price']),
                    date_updated=clean_date(row['date_updated']),
                    # Run a query to get the brand_id from the brand_name
                    brand_id=session.query(Brand).filter_by(
                        brand_name=row['brand_name']).one().brand_id)
                session.add(new_product)
        session.commit()


def app():
    """Run the app."""
    app_running = True
    while app_running:
        choice = main_menu()
        if choice == 'v':
            view_product()
        elif choice == 'n':
            add_product()
        elif choice == 'a':
            analyze_products()
        elif choice == 'b':
            backup_db()
        elif choice == 'l':
            list_products()
        elif choice == 'r':
            list_brands()
        else:
            app_running = False
            print('\nClosing App. Goodbye!\n')


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_products_csv()
    app()
