chgrp http . -R
chgrp afg .git -R
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod 755 manage.py
chmod 775 database/ media/
chmod 664 database/db.sqlite3
