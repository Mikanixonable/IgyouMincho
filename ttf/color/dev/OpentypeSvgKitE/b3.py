import os
import glob
import b
# fontname = "test"

text = "nanoemoji --family \"{}\" --color_format glyf_colr_1"

svgs = glob.glob("./SVGs/*.svg")
svgnames = ""
for svg in svgs:
    svgnames += " " + svg

# command = text.format(b.fontname)
command = text.format(b.fontname)+svgnames
print(command)
os.system(command)