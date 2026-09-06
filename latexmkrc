# latexmk configuration for the BYN manual conversion project.

$pdf_mode = 1;
$out_dir = 'build';
$aux_dir = 'build';

# Keep diagnostics useful and stop on the first real LaTeX error.
$pdflatex = 'pdflatex -file-line-error -halt-on-error -interaction=nonstopmode %O %S';

# Also remove common generated files from the build directory during cleanup.
@generated_exts = (@generated_exts, 'synctex.gz', 'run.xml', 'bcf');
