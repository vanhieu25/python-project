Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\src\views\cars\car_list_view.py", line 390, in add_car
dialog = CarDialog(self.db_helper, parent=self)
File "C:\Users\hieuc\Documents\final-project\python-project\src\views\cars\car_list_view.py", line 37, in **init**
self.setup_ui()
~~~~~~~~~~~~~^^
File "C:\Users\hieuc\Documents\final-project\python-project\src\views\cars\car_list_view.py", line 94, in setup_ui
self.status_combo.addItems([
~~~~~~~~~~~~~~~~~~~~~~~~~~^^
("available", "C≥n hαng"),
^^^^^^^^^^^^^^^^^^^^^^^^^^
...<2 lines>...
("maintenance", "B?o du?ng")
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
])
^^
TypeError: index 0 has type 'tuple' but 'str' is expected
