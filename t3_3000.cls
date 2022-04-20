\RequirePackage{expl3}
\ProvidesExplClass{t3_3000}{2022/04/13}{1.0.0}{Class to create a document matching the requirements of the tthree_threethousand for DHBW mannheim's informatics courses}

% \debug_on:n {all}

% loaded early to make sure to override the standard commands
\LoadClass[
twocolumn,
10pt,
]{article}

\msg_new:nnnn {t3_3000} {debug} {#1 #2 #3 } {}

\str_const:Nn \c__jensheinrich_tthree_threethousand_prefix {__jensheinrich_tthree_threethousand}

\cs_new_nopar:cpn {
	__jensheinrich_tthree_threethousand
_create_str_with_defaults_and_description
\str_use:N \c_colon_str
nnnn
}
 #1% name
 #2% description
 #3% default
 {

	 % create string variable
	 \str_new:c {%
		 l% local
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _str % type
	 }

	 % create default
	 \str_const:cn {%
		 c %constant
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _str % type
		 _default % suffix to mark default values
	 }
	 {#3}

	 % create description
	 \str_const:cn {%
		 c %constant
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _str % type
		 _description % suffix to mark description values
	 } {#2}

	 % set default value
	 \str_set_eq:cc
	 {
		 l% local
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _str % type
	 }
	 {
		 c %constant
		 \c__jensheinrich_tthree_threethousand_prefix % prefix
		 _
		 #1 % name
		 _str % type
		 _default % suffix to mark default values
	 }
 }


\__jensheinrich_tthree_threethousand_create_str_with_defaults_and_description:nnnn
	{email}
	{Mail adress}
	{SomeOne@SomeDomain.TLD}

\__jensheinrich_tthree_threethousand_create_str_with_defaults_and_description:nnnn
	{author}
	{Author name}
	{An Assigned Author}

\__jensheinrich_tthree_threethousand_create_str_with_defaults_and_description:nnnn
	{company}
	{company name}
	{ACME Corp.}

\__jensheinrich_tthree_threethousand_create_str_with_defaults_and_description:nnnn
	{title}
	{title}
	{A weird title}

\__jensheinrich_tthree_threethousand_create_str_with_defaults_and_description:nnnn
	{matrikelnr}
	{matrikelno}
	{123 456 789}

% create variables
%\str_new:N \l__jensheinrich_tthree_threethousand_email_str
%\str_new:N \l__jensheinrich_tthree_threethousand_company_str
%\str_new:N \l__jensheinrich_tthree_threethousand_author_str
%\str_new:N \l__jensheinrich_tthree_threethousand_title_str
%\str_new:N \l__jensheinrich_tthree_threethousand_matrikelnr_str

% create default values
%\str_const:Nn \l__jensheinrich_tthree_threethousand_email_str_default {SomeOne@SomeDomain.TLD}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_company_str_default {ACME Corp.}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_author_str_default {An Assigned Author}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_title_str_default {A weird title}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_str_default {123 456 789}

% assign default values
% \str_set_eq:NN \l__jensheinrich_tthree_threethousand_email_str \l__jensheinrich_tthree_threethousand_email_str_default
% \str_set_eq:NN \l__jensheinrich_tthree_threethousand_company_str \l__jensheinrich_tthree_threethousand_company_str_default
% \str_set_eq:NN \l__jensheinrich_tthree_threethousand_author_str \l__jensheinrich_tthree_threethousand_author_str_default
% \str_set_eq:NN \l__jensheinrich_tthree_threethousand_title_str \l__jensheinrich_tthree_threethousand_title_str_default
% \str_set_eq:NN \l__jensheinrich_tthree_threethousand_matrikelnr_str \l__jensheinrich_tthree_threethousand_matrikelnr_str_default
%
% assign command names
\str_const:Nn \l__jensheinrich_tthree_threethousand_email_str_cmd {email}
\str_const:Nn \l__jensheinrich_tthree_threethousand_company_str_cmd {company}
\str_const:Nn \l__jensheinrich_tthree_threethousand_author_str_cmd {author}
\str_const:Nn \l__jensheinrich_tthree_threethousand_title_str_cmd {title}
\str_const:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_str_cmd {matrikelnr}

% assign descriptions
%\str_const:Nn \l__jensheinrich_tthree_threethousand_email_str_description {email}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_company_str_description {company}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_author_str_description {author}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_title_str_description {title}
% \str_const:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_str_description {matrikelnr}



% create messages
\msg_new:nnnn
	{t3_3000} % module
	{undefined} % message name
{#1~has~not~been~defined.~Please~set~it~using~\str_use:N \c_backslash_str #2} % main message
	{The~default~value~of~\use:c{#1}~will~be~used~for~#1} % additional text

%
\DeclareDocumentCommand{\email}{%
	m% mail address
}{%
	\str_set:Nn \l__jensheinrich_tthree_threethousand_email_str {#1}
}
%
\DeclareDocumentCommand{\company}{%
	m% company name
}{%
	\str_set:Nn \l__jensheinrich_tthree_threethousand_company_str {#1}
}

\DeclareDocumentCommand{\author}{%
	m% author name
}{%
	\str_set:Nn \l__jensheinrich_tthree_threethousand_author_str {#1}
}

\DeclareDocumentCommand{\title}{%
	m% title
}{%
	\str_set:Nn \l__jensheinrich_tthree_threethousand_title_str {#1}
}

\DeclareDocumentCommand{\matrikelnr}{%
	m% student matrikelno
}{%
	\str_set:Nn \l__jensheinrich_tthree_threethousand_matrikelnr_str {#1}
}

% helper

\cs_new:Npn \__jensheinrich_tthree_threethousand_check_before_use_str:n
#1% string command to check
{%

\str_set:Nn \l_tmpa_str {\cs_to_str:N #1 _default }

	\str_replace_once:Nnn
		\l_tmpa_str
		{l}
		{c}

	\str_if_eq:cNT {#1} \l_tmpa_str
	{% True
		\msg_warning:nnxx
			{t3_3000}
			{undefined}
			{\use:c { \cs_to_str:N #1 _description}}
			{\use:c { \cs_to_str:N #1 _cmd}}
	}

	\str_use:N #1
}

\RequirePackage{t3_3000_title}

\RequirePackage[
left=0.75in,
right=0.75in,
bottom=0.64in,
top=0in,
twocolumn,
nomarginpar,
]{geometry}



\RequirePackage[
]{fancyhdr}

\setlength{\headsep}{0.71in}

%\setlength{\columnsep}{\dimexpr(3.313in-3.688in)}

\RequirePackage{biblatex}
% set the required citation style
\PassOptionsToPackage{
	authoryear,
}{biblatex}
