# THANK YOU FOR USING TEXTSPITTER!! #

I created this little app to help me process documents from folder sets and batches.  Instead of trying to determine each file type and process accordingly, I thought it would be more prudent to read file names and then route text extraction functions accordingly.  Also, I was having a really difficult time getting textract/pdftotext to work **because of damn Poppler**.  So instead of troubleshooting that whole process after 6+ hours, I figured this was more time-efficient.

This is my first python module, so I hope I did this well!

## Installation ##
* Type `pip install TextSpitter`
* **OPTIONAL** type `pip install PyMuPDF` to install the Python-MuPDF engine for better fidelity with text extraction (i.e.: maintaining correct White Spacing)
	* You will need to follow instructions to ensure that PyMuPDF's dependencies install to your system.  There are wheels and binaries available for Windows, Linux, and MacOSX, though if you're on something weird like NetBSD/FreeBSD/specialty linux distros, you may e SOL.  Fortunately, CLI options like Yum, Pkgin, Apt-Get and so forth will have packages available straight from the terminal.
	* For detailed instructions, please visit here: https://github.com/rk700/PyMuPDF and maybe give those guys some kudos, because they worked their tails off.

## Directions ##
This module is designed to run as simply as possible.  Just provide the file location string data into the argument, and get your text returned to you.

```
from TextSpitter import TextSpitter as TS
folder_loc = 'foo/bar/'

docx_file = folder_loc + 'file_thing.docx'
pdf_file = folder_loc + 'file_thing.pdf'
text_file = folder_loc + 'file_thing.txt'

doc_tup = (docx_file, pdf_file, text_file)

raw_text_payload = [TS(filename=ele) for ele in doc_tup]
text = '\n'.join(raw_text_payload)
return text
```

## TO DOs ##
* [x] spruce up documentation
* [X] Add stream functionality for s3-based file reading
* [ ] expand functionality to other file types
* [ ] TDB

## WANT TO CONTRIBUTE!? ##
_*OH MY GOD, PLEASE DO.*_

Just make a pull request and add whatever you want (or fix whatever you want).  I'll review and approve if everything seems good.

Thanks, everyone!
