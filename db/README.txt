load_ffxiah.py, and the xml file are here for archiving! The remote server only needs the .sql file we create.

To save on remote processing usage, it is easier to create and populate the table locally and the export/import it.

To Create the table in a local MySql database:
Get the full Item Data XML file from https://www.ffxiah.com/dev
Run: python load_ffxiah.py -f {XML file}

To export from the local MySql:
Navigate to C:\Program Files\MySQL\MySQL Server 8.0\bin\
Run: .\mysqldump.exe -u root -p {db name} {table name} > D:/ffxi_inventory/db/ffxiah.sql

To import:
upload the output sql file from above to the remote server.
Open MySql Shell on remote server.
Run: use {full database name}; source {full path to sql file};