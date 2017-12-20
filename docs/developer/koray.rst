Parts Implemented by Koray
================================

In **club.py,** all methods for clubs such as club register, register to a club, member confirmation,
board member configuration, club management. They are secured with user level confirmation to prevent
unauthorized access.

.. code-block:: python
  :caption: club.py - Accept an application for membership of a club

    @link2.route('/welcomeApply/<int:clubId>/<int:userId>', methods = ['GET', 'POST'])
    @login_required
    def welcomeApply(clubId, userId):
        if request.method == 'POST':
            with dbapi2._connect(current_app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = """DELETE FROM APPTAB WHERE(CLUBID = %s AND USERID = %s)"""
                    cursor.execute(query,(clubId, userId,))

                    query = """INSERT INTO CLUBMEM (CLUBID, USERID, LEVEL) VALUES (%s, %s, 0)"""
                    cursor.execute(query,(clubId, userId,))
                    connection.commit()
        else:
            flash("Unaccepted Method.")
        return redirect(url_for('link2.clubProfile', id = clubId))

In **message.py,** we implemented a message system that provides communication between the users and the clubs that user
is registered to. All functions of the message system is in this file such as create conversation, send messages, delete messages.

.. code-block:: python
    :caption: message.py - Send a message

    @link6.route('/sendMessages/<int:furom>/<int:tu>/<int:role>/', methods = ['POST', 'GET'])
    def sendMessages(furom, role, tu):
    	if request.method == 'POST':
    		message = request.form['message']
    		with dbapi2.connect(current_app.config['dsn']) as connection:
    			cursor = connection.cursor()
    			if role == 1:
    				query = """INSERT INTO MESSAGE(USERID, CLUBID, DATE, MSG, DIR) VALUES(%s, %s, %s, %s, true)"""
    				cursor.execute(query, (furom, tu, datetime.datetime.now(), message,))
    			else:
    				query = """INSERT INTO MESSAGE(USERID, CLUBID, DATE, MSG, DIR) VALUES(%s, %s, %s, %s, false)"""
    				cursor.execute(query, (tu, furom, datetime.datetime.now(), message,))
    			connection.commit()
    		return redirect(url_for('link6.getMessages', furom = furom, role = role, ti = tu))
    	else:
    		return "sendmessage method fault"
