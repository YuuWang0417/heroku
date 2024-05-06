from sqlite3 import connect

from package.data import handsign


class HandSignDecetion():

    def __init__(self, database_path):
        self.database_path = database_path

    # def select_all_book(self) -> list[Book]:

    #     res = []
    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = '''
    #             SELECT * FROM book
    #         '''
    #         cursor.execute(query)
    #         temp = cursor.fetchall()

    #         for i in temp:
    #             book = Book(bid=i[0], isbn=i[1], name=i[2], lang=i[3], publisher=i[4], author=i[5],
    #                         price=i[6],  inventory=i[7], book_cover=f"uploads/{i[8]}")
    #             res.append(book)
    #         cursor.close()
    #         conn.commit()

    #     return res

    # def select_book_limit(self, start, count):

    #     res = []
    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = '''
    #             SELECT * FROM book WHERE invetory > 0 LIMIT ?, ?
    #         '''
    #         cursor.execute(query, (start, count))
    #         temp = cursor.fetchall()

    #         for i in temp:
    #             book = Book(bid=i[0], isbn=i[1], name=i[2], lang=i[3], publisher=i[4], author=i[5],
    #                         price=i[6], inventory=i[7], book_cover=f"uploads/{i[8]}")
    #             res.append(book)
    #         cursor.close()
    #         conn.commit()
    #     return res

    def select_sign_from_keyword(self, keyword: str):
        res = []
        with connect(self.database_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM handsign WHERE english = ?
            '''
            cursor.execute(query, (keyword, ))
            temp = cursor.fetchall()

            for i in temp:
                book = handsign(MID = i[0], english=i[1], chinese=i[2])
                res.append(book.chinese)
            cursor.close()
            # conn.commit()
        return res

    # def insert_book_by_request(self, request, session):
    #     title = request.form['title']
    #     isbn = request.form['isbn']
    #     author = request.form['author']
    #     publisher = request.form['publisher']
    #     price = request.form['price']
    #     num = request.form['num']
    #     language = request.form['language']
    #     filename = session.get('book_cover')

    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = "INSERT INTO book (isbn, bname, language, pname, author, price, invetory, book_cover) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    #         cursor.execute(query, (isbn, title, language,
    #                                publisher, author, price, num, filename))
    #         cursor.close()
    #         conn.commit()

    # def select_member_from_account(self, account, password):
    #     member = None
    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = "SELECT * FROM member WHERE account=? AND pwd=?"
    #         cursor.execute(query, (account, password))
    #         res = cursor.fetchone()
    #         member = Member(*res)
    #         print(member)
    #         cursor.close()

    #     return member

    # def insert_member_by_request(self, request):
    #     name = request.form['name']
    #     email = request.form['email']
    #     phone = request.form['phone']
    #     address = request.form['address']
    #     account = request.form['account']
    #     pwd = request.form['password']

    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = '''INSERT INTO member (name, mail, tel, addr, account, pwd)
    #         VALUES (?, ?, ?, ?, ?, ?)'''
    #         cursor.execute(query, (name, email, phone, address, account, pwd))
    #         conn.commit()

    # def select_book_from_bid(self, bid):
    #     book = None
    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = '''
    #             SELECT * FROM book WHERE bid=?
    #         '''
    #         cursor.execute(query, (str(bid),))
    #         temp = cursor.fetchone()

    #         book = Book(bid=temp[0], isbn=temp[1], name=temp[2], lang=temp[3], publisher=temp[4], author=temp[5],
    #                     price=temp[6], inventory=temp[7], book_cover=f"uploads/{temp[8]}")

    #         cursor.close()
    #         conn.commit()
    #     return book

    # def selec_order_from_buyer_id(self, buyer_id):
    #     orders = []
    #     with connect(self.database_path) as conn:

    #         cursor = conn.cursor()
    #         query = "SELECT * FROM `order` WHERE buyer_id=?"
    #         cursor.execute(query, str(buyer_id))
    #         res = cursor.fetchall()

    #         for i in res:
    #             order = Order(oid=i[0], isbn=i[1], name=i[2],
    #                           quantity=i[3], second_price=i[4], uid=[5])
    #             orders.append(order)
    #         cursor.close()
    #         conn.commit()

    #     return orders

    # def insert_order(self, book:Book, uid):
    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = '''INSERT INTO `order` (isbn, pname, quantity, secondhand, buyer_id)
    #         VALUES ( ?, ?, ?, ?, ?)'''
    #         cursor.execute(query, (book.isbn, book.name, book.inventory, book.price, uid))
    #         conn.commit()

    # def updata_book(self, book:Book, buy_inventory:int):
    #     with connect(self.database_path) as conn:
    #         cursor = conn.cursor()
    #         query = '''
    #             UPDATE book SET invetory = ? WHERE bid=?
    #         '''
    #         new_inventory = (book.inventory - int(buy_inventory))
    #         cursor.execute(query, (new_inventory, book.bid, ))
    #         conn.commit()
