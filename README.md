# THANK YOU FOR USING TEXTSPITTER!! #

I created this little app to help me process documents from folder sets and batches.  Instead of trying to determine each file type and process accordingly, I thought it would be more prudent to read file names and then route text extraction functions accordingly.  Also, I was having a really difficult time getting textract/pdftotext to work **because of damn Poppler**.  So instead of troubleshooting that whole process after 6+ hours, I figured this was more time-efficient.

This is my first python module, so I hope I did this well!

## Directions ##
This module is designed to run as simply as possible.  Just provide the file location string data into the argument, and get your text returned to you.

```
from TextSpitter import WordLoader as WL
import sqlite3


folder_loc = 'foo/bar/'

doc_file = folder_loc + 'file_thing.doc'
docx_file = folder_loc + 'file_thing.docx'
pdf_file = folder_loc + 'file_thing.pdf'
text_file = folder_loc + 'file_thing.txt'

doc_tup = (doc_file, docx_file, pdf_file, text_file)

# SQL code to write to database
conn = sqlite3.connect('example_db')
c= conn.cursor()

STMNT = 'INSERT INTO doc_contents VALUE %s'

# For Loop code to insert doc content into db
for ele in doc_tup:
	text = WL.file_load(ele)
	c.executemany(STMNT, text)
	print('Done!  Wrote the following to db: %s', (text[:25]))
```

## TO DOs ##
* [x] push to github
* [ ] spruce up documentation
* [ ] solicit feedback
* [ ] expand functionality to other file types
* [ ] TDB

## WANT TO CONTRIBUTE!? ##
_*OH MY GOD, PLEASE DO.*_

Just make a pull request and add whatever you want (or fix whatever you want).  I'll review and approve if everything seems good.  

Thanks, everyone!