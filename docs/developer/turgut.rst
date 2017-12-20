Parts Implemented by Turgut
================================

In **classes.py,** the basic user methods are implemented as well as class structure of it. The users' clubs are added to it
in favor of adding them to the navigation bar. The methods are coded accorded to *flask-login*. There is also *UserList* class
for storing users.

  .. code-block:: python
    :caption: classes.py - User Class

    class User(UserMixin):
        def __init__(self, name,rname, number, email, psw):
            self.name = name
            self.rname = rname
            self.number = number
            self.email = email
            self.psw = psw
            with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT LEVEL FROM USERDB WHERE(NAME = %s) """
                cursor.execute(query,(self.name,))
                lvl = cursor.fetchone()
                if lvl:
                    self.level = lvl[0]
                else:
                    self.level = 0

                query = """SELECT CLUBID,CLUBDB.NAME FROM CLUBMEM,USERDB,CLUBDB WHERE(USERDB.ID = USERID AND USERDB.NAME = %s AND CLUBDB.ID = CLUBID)"""
                cursor.execute(query,(self.name,))
                arr = cursor.fetchall()
                for a in range(len(arr)):
                    arr[a] = list(arr[a])
                    arr[a][1] = arr[a][1].replace(' Kulubu','')
                    arr[a][1] = arr[a][1].replace(' Club','')
                    arr[a] = tuple(arr[a])
                self.clubs = arr





In **admin.py,** there are operations related with club application confirmation and clubs such as decline, accept club
application, set an active club to passive.
With *suspendclub* method, Admin can set a club invinsible to the users while keeping their all data in the database.
Admin also can *acceptApp* which makes the club active. On the other hand, he/she can delete a club with its' all data with
using *declineApp* method.

.. code-block:: python
  :caption: admin.py - Decline Application

      @link4.route('/declineApp/<int:id>/', methods = ['GET', 'POST'])
      def declineApp(id):
          if current_user.level == 1:
              with dbapi2.connect(current_app.config['dsn']) as connection:
                  cursor = connection.cursor()
                  query = """DELETE FROM CLUBDB WHERE (ID = %s)"""
                  cursor.execute(query,(id,))
                  connection.commit()
              return redirect(url_for('link4.admin_home'))
          else:
              flash("Permission Denied")
              return redirect(url_for('link3.userProfile'))

In **user.py,** there are main user methods such as *edit profile* as well as the html connections like the other py files.

.. code-block:: python
  :caption: user.py - Edit Profile

      @link3.route('/edit_profile',methods=['GET', 'POST'])
      @login_required
      def updateProfile():
          if request.method == "POST":
              userpsw0 = request.form['psw']
              userpwd1 = request.form['psw-repeat']
              useremail = request.form['email']
              if userpsw0 != None:
                  if userpsw0 != userpwd1:
                      flash('Passwords do not match!')
                      return redirect(url_for('link3.editProfile'))
                  else:
                      userpsw = pwd_context.encrypt(userpsw0)
                      userid=current_user.get_id()
                      with dbapi2._connect(current_app.config['dsn']) as connection:
                          cursor = connection.cursor()
                          query = """UPDATE USERDB SET PSW=%s WHERE(ID=%s)"""
                          cursor.execute(query,(userpsw,userid,))
                          connection.commit()
              if useremail!= None:
                  userid=current_user.get_id()
                  with dbapi2._connect(current_app.config['dsn']) as connection:
                      cursor = connection.cursor()
                      query = """UPDATE USERDB SET EMAIL=%s WHERE(ID=%s)"""
                      cursor.execute(query,(useremail,userid,))
                      connection.commit()
              else:
                  return redirect(url_for('link3.userProfile'))
          return redirect(url_for('link3.userProfile'))


In **event.py,** there are event and notice functions alognside with their *render_template* calls. Differently from other
similar select/add/delete/update functions, there is a *cleanevent* method which checks event times and deletes the
past ones. It is called whenever a event listing function is called.

.. code-block:: python
  :caption: event.py - Clean Event

    def cleanevents():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            now = datetime.datetime.now()
            cursor = connection.cursor()
            query = """DELETE FROM EVENT WHERE(DATE < %s)"""
            cursor.execute(query,(now,))


In **home.py,** there are basic functions that is the foundation of the application such as *sign up, login, logout*.
There is also a function for club searching.

  .. code-block:: python
    :caption: home.py - Search for Clubs

      @link1.route("/search", methods = ['GET', 'POST'])
      def search():
          if request.method == "POST":
              keyword = request.form['keyword']
              arr = get_clubs() # 0 -> id, 1 -> name, 2 -> type
              result = [s for s in arr if keyword.lower() in s[1].lower()]
              return render_template('search.html',keyword = keyword, result = result)
          else:
              flash("Unauthorized Access")
              return redirect(url_for('link1.home_page'))
