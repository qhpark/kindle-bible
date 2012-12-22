kindle-bible
============

A python script that builds a kindle-readable book with navpoints support from the contents available from web.

`kindle_bible.py` generates :
- {cover, toc, body}.html
- $proj.ncx for navpoints (if nav points are enabled)
- $proj.opf for mobipocket creator.

Usage:
- Install mobipocket creator from http://www.mobipocket.com/en/downloadsoft/DownloadCreator.asp
- Open $proj.opf and generate.

NOTE
----
- written for personal use, not quite ready for public release
- some polishing changes may come.. someday.. hopefully.
