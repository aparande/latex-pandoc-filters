import os
import shutil
import sys

from tempfile import mkdtemp
from subprocess import call
from typing import Tuple

from pandocfilters import get_filename4code, get_extension

def tex2image(tex_src: str, filetype:str, outfile:str, header_file:str) -> None:
  """
  Compile LaTeX src to an image.  The LaTeX is copied to a standalone article
  file and compiled to a pdf.  If the output type is an image, then ImageMagick
  is used to convert the PDF to png and trim away extra white space.

  Based on https://github.com/jgm/pandocfilters/blob/master/examples/tikz.py
  """
  tmpdir = mkdtemp()
  olddir = os.getcwd()

  headerfile_name = os.path.basename(header_file)
  shutil.copyfile(f"{header_file}", tmpdir+f"/{headerfile_name}")
  os.chdir(tmpdir)

  with open('standalone_tex.tex', 'w') as f:
    f.write("\\documentclass[]{article}")
    f.write("\n\\input{" + headerfile_name + "}")
    f.write("\\begin{document}")
    f.write("\\thispagestyle{empty}")
    f.write(tex_src)
    f.write("\n\\end{document}\n")

  call(["pdflatex", 'standalone_tex.tex'], stdout=sys.stderr)
  os.chdir(olddir)
  if filetype == 'pdf':
    shutil.copyfile(tmpdir + '/standalone_tex.pdf', outfile + '.pdf')
  else:
    call(["convert", tmpdir + '/standalone_tex.pdf', \
        "-density", "500", "-strip", "-fuzz", "50%", \
        "-trim", "+repage", outfile + '.' + filetype])
  shutil.rmtree(tmpdir)

def convert_to_image(fmt:str, code:str, header_file:str = "header.tex",
    dir_prefix:str="tex") -> Tuple[str, str]:
  """
  Convert latex source into an image and save it to a directory.
  Based on https://github.com/jgm/pandocfilters/blob/master/examples/tikz.py

  dir_prefix is the prefix of the image directory the code will be saved to
  """
  outfile = get_filename4code(dir_prefix, code)
  filename = outfile.split("/")[1]
  filetype = get_extension(fmt, "png", html="png", latex="png")
  src = outfile + '.' + filetype
  if not os.path.isfile(src):
    tex2image(code, filetype, outfile, header_file)
    sys.stderr.write('Created image ' + src + '\n')

  return filename, filetype

