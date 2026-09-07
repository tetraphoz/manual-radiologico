#!/usr/bin/env bash
# Recreate the reviewed line-art assets extracted from source/pages/*.png.
# Run from the repository root.  The page PNGs are the visual source archive.
set -euo pipefail

mkdir -p assets/figures

# Rasterize the vector logo for reliable inclusion with pdfLaTeX.
magick -background white -density 300 assets/figures/logo.svg -alpha remove assets/figures/logo-title.png

crop() {
  local source=$1 geometry=$2 target=$3
  magick "$source" -crop "$geometry" +repage -threshold 82% "$target"
}

# Emergency procedures, source pages 073--079 and 087--089.
crop source/pages/img-073.png '1000x320+170+470' assets/figures/jaleContenedor.png
crop source/pages/img-073.png '500x175+350+1260' assets/figures/estrangulamientoManeral.png
crop source/pages/img-074.png '1000x270+180+500' assets/figures/jaleCable.png
crop source/pages/img-074.png '500x145+350+900' assets/figures/estrangulamiento_posicionadora.png
crop source/pages/img-079.png '1100x300+130+1340' assets/figures/jale_maneral_fuente.png
crop source/pages/img-087.png '1050x470+170+1140' assets/figures/recuperacion_pertiga.png
crop source/pages/img-089.png '1100x400+130+900' assets/figures/retraccion_fuente.png
# Remove the scan's clipped lower text/border from the 7.4 drawing.
magick assets/figures/jale_maneral_fuente.png -crop '1100x260+0+35' +repage assets/figures/jale_maneral_fuente.png

# Gammagraphy equipment and operation drawings, source pages 107--112
# (printed source pages 105--110).
crop source/pages/img-107.png '1050x650+100+400' assets/figures/conector_fuente.png
crop source/pages/img-108.png '850x850+250+350' assets/figures/chapa_seguridad_contenedor.png
crop source/pages/img-109.png '1140x1050+70+170' assets/figures/manipulador_reel.png
crop source/pages/img-110.png '1180x1170+40+250' assets/figures/detalle_conector_reel.png
crop source/pages/img-111.png '1130x1280+100+230' assets/figures/operacion_radiografica.png
crop source/pages/img-112.png '1150x1050+80+350' assets/figures/exposicion_fuente.png
