 #!/bin/bash
 #You need lingua and gettext installed to run this
 
 echo "Updating arche_m2m.pot"
 pot-create -d arche_m2m -o src/arche_m2m/arche_m2m/locale/arche_m2m.pot src/arche_m2m/arche_m2m
 #pot-create -d arche_m2m_user -o src/arche_m2m/arche_m2m/locale/arche_m2m_user.pot src/arche_m2m/arche_m2m
 
 echo "Merging Swedish localisation"
 msgmerge --update  src/arche_m2m/arche_m2m/locale/sv/LC_MESSAGES/arche_m2m.po  src/arche_m2m/arche_m2m/locale/arche_m2m.pot
 echo "Updated locale files"
