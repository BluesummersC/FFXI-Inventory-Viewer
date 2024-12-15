# FFXI-Inventory-Viewer  

This project has 3 major components:  
  FFXI Windower with the findAll mod (required) and the armory mod (optional, but highly suggested).  
  A MySQL database loaded with the master list of item information. Sourced from ffxiah.com/dev  
  A Flask frontend with a WSGI server.  
  
Using FindAll, you must export an inventory file, which contains all storage locations with the item ids of the items residing in those locations. Items that are not in a storage get lumped into a "key items" storage, not to be confused with actual 
Key Items.

The Flask frontend will consume this exported file and crossreference it with the master list to expand the item ids into thhe full item information, then store these into the database tagged with a user-generated Name and a random-generated Passkey. 
Querying the database with the Name and Passkey will serve the entry to the Datatable on teh website, which then allows many options for searching, filtering and sorting.
