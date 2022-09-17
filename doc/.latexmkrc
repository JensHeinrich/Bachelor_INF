# Docs: https://mg.readthedocs.io/latexmk.html
# Only compile this list
@default_files = qw(
  bachelor.tex
);


# https://tex.stackexchange.com/questions/617226/latexmk-build-in-another-directory-and-move-back-file-once-its-compiled-avoid
$emulate_aux = 1;
$aux_dir = 'build';
%out_dir = 'output';

#$pdf_mode = 1;    # tex -> pdf
# https://ftp.fau.de/ctan/support/latexmk/example_rcfiles/lualatex_latexmkrc
# This shows how to use lualatex (http://en.wikipedia.org/wiki/LuaTeX)
# with latexmk.
#
#   WARNING: The method shown here is suitable only for ver. 4.51 and
#            later of latexmk, not for earlier versions.
#
$pdf_mode        = 4;
$postscript_mode = $dvi_mode = 0;

$out_dir = "./build";    # keep the temporary files away from the tree

$cleanup_includes_cusdep_generated = 1;    # remove generated files
$cleanup_includes_generated = 1;    # remove generated files


$max_repeat = 10;                          # maximum number of runs

# enable shell escape
$latex = 'latex  %O  --shell-escape %S';

#$pdflatex = 'lualatex  %O  --shell-escape %S';
$pdflatex = 'pdflatex  %O  --shell-escape %P';

#$lualatex = 'lualatex  %O  --shell-escape %P';
$lualatex = 'lualatex  %O  --shell-escape %P';

sub ensure_both {

    # Usage: ensure_both(values)
    # adds values to BIBINPUTS and TEXINPUTS
    foreach (@_) {
        my $val = $_;
        foreach ( 'BIBINPUTS', 'TEXINPUTS' ) {
            ensure_path( $_, $val );
        }
    }
}

# https://tex.stackexchange.com/questions/474756/how-to-suitably-configure-the-texinputs-variable-in-latexmkrc-for-detecting-the
ensure_path( 'TEXINPUTS', 'ub_beamer/' );

process_rc_file('packages/.latexmkrc');
process_rc_file('bibliographies/.latexmkrc');
process_rc_file('glossaries/.latexmkrc');

# glossaries
ensure_path( 'TEXINPUTS', 'glossaries/' );

ensure_path( 'TEXINPUTS', $out_dir );

#add_cus_dep( 'plantuml', 'latex', 0, 'run_plantuml_to_latex %S %D %O' );
add_cus_dep( 'plantuml', 'latex', 0, 'run_plantuml_to_latex' );

#add_cus_dep('plantuml', 'latex', 0, 'plantuml2latex');

@plantuml_flags = qw(
  -tlatex:nopreamble
  -verbose
);

# https://tex.stackexchange.com/questions/573256/why-the-specify-output-dir-compile-failed-using-latexmk
# $plantuml2latex = 'internal run_plantuml_to_latex %S %D %O';
#
sub run_plantuml_to_latex {
  my $return = 999;
  my $source = shift;
  my ( $source_base, $source_path ) = fileparse( $source );
  # Paths for source and dest should have been made the same.
  # That's the way latexmk works.

    use Cwd qw(realpath);
my $full_source = realpath($source).".plantuml";
my $full_out_dir = realpath($out_dir . "/" . $source_path) ;

pushd($out_dir);
  my @cmd_line = ('plantuml',
'-tlatex:nopreamble',
'-o', $full_out_dir, $full_source );
  print "$My_name: Running external command '@cmd_line'\n";
  $return = system( @cmd_line );
popd();

  return $return;
}


sub run_plantuml {
    my ( $base, $path ) = fileparse( $_[0] );
    local @plantuml_flags = @plantuml_flags;
    local $plantuml       = "plantuml ";
    if ($silent) {
        push @plantuml_flags, "-quiet";
    }
    use Cwd qw(realpath);

    #my $abs_path_out_dir = realpath($out_dir);
    my $abs_path_source = realpath( $_[0] );
    if ($out_dir) {
        pushd($out_dir);
        #push @plantuml_flags, "-output $path";
        push @plantuml_flags, "-output ./" . $path;

     #  		# push @plantuml_flags, "-output %Z";
     #  	    push @plantuml_flags, "-output " . $abs_path_out_dir . "/" . $path;
    }
    push @plantuml_flags, "$abs_path_source" . ".plantuml";

    #push @plantuml_flags, "$path" . "$base" . ".plantuml";
    $plantuml = join( ' ', "plantuml", @plantuml_flags );
    print( $plantuml . "\n" );
    my $ret = system($plantuml);
    print($ret);

    #my $ret = Run_subst($plantuml);
    # https://alvinalexander.com/blog/post/perl/how-move-rename-file-perl/
    if ($out_dir) {
        popd();

        #  	make_path("$out_dir" ."/" . "$path");
        #  	copy(
        #  			"$path" . "$base" . ".latex",
        #  			"$out_dir" . "/" ."$path" . "$base" . ".latex",
        #  	    ) or die "Error moving $!";
        #
    }
    else {
        # push @plantuml_flags, "-output " . $path ;
    }
    return $ret;
}

add_cus_dep( 'eps', 'pdf', 0, 'run_eps2pdf' );
@eps2pdf_flags = qw(
  --restricted
);

sub run_eps2pdf {
    my ( $base, $path ) = fileparse( $_[0] );
    local @eps2pdf_flags = @eps2pdf_flags;
    local $eps2pdf       = "epstopdf ";
    if ($out_dir) {
        push @eps2pdf_flags, "--outfile=" . $path . $base . ".pdf";
    }
    else {
        push @eps2pdf_flags, "--outfile=" . $path . $base . ".pdf";
    }
    if ($silent) {
        push @eps2pdf_flags, "--quiet";
    }
    push @eps2pdf_flags, "$path" . "$base" . ".eps";
    $eps2pdf = join( ' ', "epstopdf", @eps2pdf_flags );
    my $ret = Run_subst($eps2pdf);
    return $ret;
}

# https://tex.stackexchange.com/questions/400325/latexmkrc-for-bib2gls
add_cus_dep( 'aux', 'glstex', 0, 'run_bib2gls' );
push @generated_exts, 'glstex', 'glg';
@bib2gls_flags = qw(
  --group
  --warn-non-bib-fields
  --warn-unknown-entry-types
  --force-cross-resource-refs
  --mfirstuc-math-protection
  --record-count
  --record-count-unit
  --trim-fields
  --provide-glossaries
);

sub run_bib2gls {
    my ( $base, $path ) = fileparse( $_[0] );
    local @bib2gls_flags = @bib2gls_flags;
    local $bib2gls       = "bib2gls ";
    if ($out_dir) {
        push @bib2gls_flags, "--dir %Y";
    }
    if ($silent) {
        push @bib2gls_flags, "--silent";
    }
    push @bib2gls_flags, "$base";
    $bib2gls = join( ' ', "bib2gls", @bib2gls_flags );
    my $ret = Run_subst($bib2gls);

    # Analyze log file.
    local *LOG;
    $LOG = "$base.glg";
    if ( !$ret && -e $LOG ) {
        open LOG, "<$LOG";
        while (<LOG>) {
            if (/^Reading (.*\.bib)\s$/) {
                rdb_ensure_file( $rule, $1 );
            }
            # https://tex.stackexchange.com/questions/420107/latexmk-clean-multiple-files-created-by-custom-dependency
            if (/^Writing (.*\.glstex)\s$/) {
                rdb_add_generated($rule, $1);
                print( "Created " . $1);
            }
        }
        close LOG;
    }
    return $ret;
}

# https://ftp.fau.de/ctan/support/latexmk/example_rcfiles/minted_latexmkrc
# For the minted package (which does nice formatting of source code):
#
# 1. Need to use -shell-escape on *latex command.
# 2. Need to arrange passing of the output dir (actually aux dir if it
#    differs from out dir) to minted.  Then this directory information does
#    not have to be specified  in the .tex file itself.
# 3. In some cases, latexmk does an extra run of *latex than is
#    needed.  This is solved by getting latexmk to ignore certain lines in
#    the aux file when latexmk looks for changes.  These lines are written
#    by minted and are irrelevant to the output file from *latex.
#
#    The reason for the extra run of *latex that may happen is because
#    after minted runs pygmentize to make the nicely formatted source code,
#    minted saves cached information about the run(s) of pygmentize. This
#    information is  put in the aux file. So latexmk sees the changed aux
#    file, and knows that may affect the output of *latex, which it
#    therefore reruns. However the minted-written lines do not affect the
#    output of *latex.
#
# The method works if the aux dir's name contains a string of MORE than one
# space That's a problem in minted's calls to pygmentize.
# Single spaces in the name are OK.
# Generally it helps to  use only aux_dir and out_dir names  without spaces,
# to avoid trouble.

$pre_tex_code = "\\PassOptionsToPackage{outputdir={build}}{minted}";

#&alt_tex_cmds;
#&set_tex_cmds( '--shell-escape %O %P');
# &set_tex_cmds( '-shell-escape %O '
#         . '\'\PassOptionsToPackage{outputdir={%Y}}{minted}\input{%S}\''
#         );
# (Here the outer level of single quotes is for Perl.  The dot is for
# Perl's string concatenation. The \' tell Perl to put actual single
# quotes in the string (given to the shell).  In Unix, the shell is sh (or
# equivalent), so the string inside the single quotes is a single argument
# to the command is not changed at all.)
#
$hash_calc_ignore_pattern{aux} =
    '^\\\\gdef\\\\minted@oldcachelist\{,'
  . '|^\s*default\.pygstyle,'
  . '|^\s*[[:xdigit:]]+\.pygtex';

