# FFXI-Inventory-Viewer  
This consists of 3 major systems:  
  Windower with the findAll mod.  
  A MySQL database loaded with all item information.  
  A Flask frontend.  

You must have Windower and the plugin called findAll (was Organizer). This plugin will output your inventory into a static file via the Windower command line.
Load the webpage and upload the .lua file and the site will create an organized list of item_ids, query the database for all info related to each item_id, and serve it up in a jquery datatable!

If findall has been updated or removed, this won't work until a new solution is made.
