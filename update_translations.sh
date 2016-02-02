 #!/bin/bash
 #You need lingua and gettext installed to run this
 
 echo "Updating arche_m2m.pot"
 pot-create -d arche_m2m -o arche_m2m/locale/arche_m2m.pot arche_m2m

 echo "Merging Swedish localisation"
 msgmerge --update  arche_m2m/locale/sv/LC_MESSAGES/arche_m2m.po  arche_m2m/locale/arche_m2m.pot
 echo "Updated locale files"
