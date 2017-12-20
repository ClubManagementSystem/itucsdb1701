Parts Implemented by Beste
================================
In **club.py,** there are club management functions besides with main club functions.

- **Social Media:** You can add social media accounts while registering the club but additionally you can manage them in
club management like deleting or adding a new one.

  .. code-block:: python
    :caption: club.py - Add a social media account

    @link2.route('/addsocmed/<int:cid>', methods = ['GET', 'POST'])
    @login_required
    def addsocmed(cid):
        if request.method == 'POST':
            typesoc = request.form['typesoc']
            link = request.form['link']
            with dbapi2._connect(current_app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = """INSERT INTO SOCMED(CLUBID,TYPESOC,LINK) VALUES (%s,%s,%s)"""
                    cursor.execute(query,(cid,typesoc,link))
                    connection.commit()
                    return redirect(url_for('link2.socmed', cid=cid))

- **Balance:** In balance, the finance data of the club is holded. You can add positive/negative numbers for income/expense
respectively. Only board members of the club can acess this page and the social media page.

- **Inventory:** In inventory, Clava features an improved item store system that can shows who has the item right now.
While only board members can add items to the inventory, only chairman can delete one. Moreover, all registered users can
access the inventory page and apply for an item as well as release an item which he/she got.

  .. code-block:: python
      :caption: club.py - Release/Apply an item

      @link2.route('/releaseitem/<int:cid>/<int:id>', methods = ['GET', 'POST'])
      def releaseitem(cid,id):
          if request.method == "POST":
              with dbapi2._connect(current_app.config['dsn']) as connection:
                  cursor = connection.cursor()
                  query  = """UPDATE INVENTORY SET AVAILABLE=0 WHERE (ID = %s)  """
                  cursor.execute(query,(id,))
                  connection.commit()
                  return redirect(url_for('link2.clubInventory',clubId=cid))

      @link2.route('/inventoryapp/<int:cid>/<int:id>', methods = ['GET', 'POST'])
      def apply_inventory(cid,id):
          if request.method == "POST":
              uid = current_user.get_id()
              with dbapi2._connect(current_app.config['dsn']) as connection:
                  cursor = connection.cursor()
                  query  = """UPDATE INVENTORY SET AVAILABLE=1,USERNAMEID=%s WHERE (ID = %s)  """
                  cursor.execute(query,(uid,id,))
                  connection.commit()
                  return redirect(url_for('link2.clubInventory',clubId=cid))

- **Member List:** There is a member list entity that only accessible by the board members. The chairman can use this for removing
a user from the club.
