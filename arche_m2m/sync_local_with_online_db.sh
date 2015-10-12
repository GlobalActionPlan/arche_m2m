#!/bin/bash
rsync --progress -z m2m@m2m-staging.globalactionplan.com:~/m2m_staging/var/Data.fs var/Data.fs
rsync --progress -zr m2m@m2m-staging.globalactionplan.com:~/m2m_staging/var/blob var/.
