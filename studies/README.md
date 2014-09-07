# structuredproducts

## This application provides a study and implementation of the Structured Product concepts presented in the book, "Options as a Strategic Investment", by Lawrence G McMillan. See chapter 32 for more information.                          

Observe tests.py to study the behavior of the structured products responding to changes in inputs.

The tests execute the examples outlined in the book in order to assert the accuracy of the code implementation.

Note: To date, this code base implements and tests concepts relating to the Index Product.

## To run tests:

1. create mysql.cnf with following

```
[client]
database = DATABASE
user = USER
password = PASSWORD
default-character-set = utf8
```

2. create database
3. pip install requirements.txt
4. python manage.py test studies.tests