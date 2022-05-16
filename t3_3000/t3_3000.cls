\RequirePackage{expl3}
\ProvidesExplClass{t3_3000}{2022/04/25}{1.0.2}{Class to create a document matching the requirements of the tthree_threethousand for DHBW mannheim's informatics courses}

% \debug_on:n {all}

% loaded early to make sure to override the standard commands
\LoadClass[
twocolumn,
10pt,
]{article}

\RequirePackage{stix}
%\usepackage{unicode-math}
\RequirePackage{emoji}
% https://tex.stackexchange.com/questions/458627/how-do-i-display-unicode-characters-with-minted

\RequirePackage{newunicodechar}

% \defaultfontfeatures{Scale = MatchLowercase}
% \setmainfont{CMU Serif}[Scale = 1.0]
% \setsansfont{CMU Sans Serif}
% \setmonofont{CMU Typewriter Text}
%\setmathfont{Latin Modern Math}

% https://tex.stackexchange.com/questions/503431/minted-unicode-characters-in-listing
\usepackage{fontspec}
%\setmonofont{DejaVu Sans Mono}
\setmonofont{Ubuntu Mono Regular}


\msg_new:nnnn {t3_3000} {debug} {#1 #2 #3 } {}

\bool_new:N \l__jensheinrich_tthree_threethousand_draft_bool
\keys_define:nn {jensheinrich_tthree_threethousand} {
	draft .bool_set:N = \l__jensheinrich_tthree_threethousand_draft_bool,
}

\tl_const:Nn \c__jensheinrich_tthree_threethousand_prefix {__jensheinrich_tthree_threethousand}

\cs_new_nopar:cpn {
	__jensheinrich_tthree_threethousand
_create_tl_with_defaults_and_description
\tl_use:N \c_colon_str
nnnn
}
 #1% name
 #2% description
 #3% default
 {

	 % create tling variable
	 \tl_new:c {%
		 l% local
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _tl % type
	 }

	 % create default
	 \tl_const:cn {%
		 c %constant
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _tl % type
		 _default % suffix to mark default values
	 }
	 {#3}

	 % create description
	 \tl_const:cn {%
		 c %constant
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _tl % type
		 _description % suffix to mark description values
	 } {#2}

	 % set default value
	 \tl_set_eq:cc
	 {
		 l% local
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _tl % type
	 }
	 {
		 c %constant
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _tl % type
		 _default % suffix to mark default values
	 }
 }


\__jensheinrich_tthree_threethousand_create_tl_with_defaults_and_description:nnnn
	{email}
	{Mail adress}
	{SomeOne@SomeDomain.TLD}

\__jensheinrich_tthree_threethousand_create_tl_with_defaults_and_description:nnnn
	{author}
	{Author name}
	{An Assigned Author}

\__jensheinrich_tthree_threethousand_create_tl_with_defaults_and_description:nnnn
	{company}
	{company name}
	{ACME Corp.}

\__jensheinrich_tthree_threethousand_create_tl_with_defaults_and_description:nnnn
	{title}
	{title}
	{A weird title}

\__jensheinrich_tthree_threethousand_create_tl_with_defaults_and_description:nnnn
	{matrikelnr}
	{matrikelno}
	{123~456~789}

% create variables
%\tl_new:N \l__jensheinrich_tthree_threethousand_email_tl
%\tl_new:N \l__jensheinrich_tthree_threethousand_company_tl
%\tl_new:N \l__jensheinrich_tthree_threethousand_author_tl
%\tl_new:N \l__jensheinrich_tthree_threethousand_title_tl
%\tl_new:N \l__jensheinrich_tthree_threethousand_matrikelnr_tl

% create default values
%\tl_const:Nn \l__jensheinrich_tthree_threethousand_email_tl_default {SomeOne@SomeDomain.TLD}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_company_tl_default {ACME Corp.}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_author_tl_default {An Assigned Author}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_title_tl_default {A weird title}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_tl_default {123 456 789}

% assign default values
% \tl_set_eq:NN \l__jensheinrich_tthree_threethousand_email_tl \l__jensheinrich_tthree_threethousand_email_tl_default
% \tl_set_eq:NN \l__jensheinrich_tthree_threethousand_company_tl \l__jensheinrich_tthree_threethousand_company_tl_default
% \tl_set_eq:NN \l__jensheinrich_tthree_threethousand_author_tl \l__jensheinrich_tthree_threethousand_author_tl_default
% \tl_set_eq:NN \l__jensheinrich_tthree_threethousand_title_tl \l__jensheinrich_tthree_threethousand_title_tl_default
% \tl_set_eq:NN \l__jensheinrich_tthree_threethousand_matrikelnr_tl \l__jensheinrich_tthree_threethousand_matrikelnr_tl_default
%
% assign command names
\tl_const:Nn \l__jensheinrich_tthree_threethousand_email_tl_cmd {email}
\tl_const:Nn \l__jensheinrich_tthree_threethousand_company_tl_cmd {company}
\tl_const:Nn \l__jensheinrich_tthree_threethousand_author_tl_cmd {author}
\tl_const:Nn \l__jensheinrich_tthree_threethousand_title_tl_cmd {title}
\tl_const:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_tl_cmd {matrikelnr}

% assign descriptions
%\tl_const:Nn \l__jensheinrich_tthree_threethousand_email_tl_description {email}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_company_tl_description {company}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_author_tl_description {author}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_title_tl_description {title}
% \tl_const:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_tl_description {matrikelnr}



% create messages
\msg_new:nnnn
	{t3_3000} % module
	{undefined} % message name
{#1~has~not~been~defined.~Please~set~it~using~\tl_use:N \c_backslash_tl #2} % main message
	{The~default~value~of~\use:c{#1}~will~be~used~for~#1} % additional text

%
\DeclareDocumentCommand{\email}{%
	m% mail address
}{%
	\tl_set:Nn \l__jensheinrich_tthree_threethousand_email_tl {#1}
}
%
\DeclareDocumentCommand{\company}{%
	m% company name
}{%
	\tl_set:Nn \l__jensheinrich_tthree_threethousand_company_tl {#1}
}

\DeclareDocumentCommand{\author}{%
	m% author name
}{%
	\tl_set:Nn \l__jensheinrich_tthree_threethousand_author_tl {#1}
}

\DeclareDocumentCommand{\title}{%
	m% title
}{%
	\tl_set:Nn \l__jensheinrich_tthree_threethousand_title_tl {#1}
}

\DeclareDocumentCommand{\matrikelnr}{%
	m% student matrikelno
}{%
	\tl_set:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_tl {#1}
}

% helper

\cs_new:Npn \__jensheinrich_tthree_threethousand_check_before_use_tl:n
#1% tling command to check
{%

\tl_set:Nn \l_tmpa_tl {\cs_to_tl:N #1 _default }

	\tl_replace_once:Nnn
		\l_tmpa_tl
		{l}
		{c}

	\tl_if_eq:cNT {#1} \l_tmpa_tl
	{% True
		\msg_warning:nnxx
			{t3_3000}
			{undefined}
			{\use:c { \cs_to_tl:N #1 _description}}
			{\use:c { \cs_to_tl:N #1 _cmd}}
	}

	\tl_use:N #1
}

\RequirePackage{t3_3000_title}
\RequirePackage{t3_3000_declaration}
\RequirePackage{t3_3000_pagestyle}

% set the required citation style
\PassOptionsToPackage{
	style=alphabetic,
}{biblatex}

\RequirePackage{biblatex}
