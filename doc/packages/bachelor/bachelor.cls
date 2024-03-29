\RequirePackage{expl3}
\ProvidesExplClass{bachelor}{2022/06/07}{1.0.0}{Class to unify the style requirements for this bachelor thesis}

% loaded early to make sure to override the standard commands
\LoadClass[
12pt,
titlepage
]{article}

% load early to make csquotes happy
\RequirePackage{fvextra}

% create commands for the formalia

\cs_new_nopar:cpn {
	__jensheinrich_bachelor
_create_tl_with_defaults_and_description
\tl_use:N \c_colon_str
nnnn
}
 #1% name
 #2% description
 #3% default
 #4% prefix
 {

	 % create tling variable
	 \tl_new:c {%
		 l% local
		 #4 % prefix
		 _
		 #1 % name
		 _tl % type
	 }

	 % create default
	 \tl_const:cn {%
		 c %constant
		 #4 % prefix
		 _
		 #1 % name
		 _tl % type
		 _default % suffix to mark default values
	 }
	 {#3}

	 % create description
	 \tl_const:cn {%
		 c %constant
		 #4 % prefix
		 _
		 #1 % name
		 _tl % type
		 _description % suffix to mark description values
	 } {#2}

	 % set default value
	 \tl_set_eq:cc
	 {
		 l% local
		 #4 % prefix
		 _
		 #1 % name
		 _tl % type
	 }
	 {
		 c %constant
		 #4 % prefix
		 _
		 #1 % name
		 _tl % type
		 _default % suffix to mark default values
	 }
 }

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{email}
	{Mail adress}
	{SomeOne@SomeDomain.TLD}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{date}
	{Date}
	{\today}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{author}
	{Author name}
	{An Assigned Author}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{company}
	{Company name}
	{ACME Corp.}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{title}
	{title}
	{A weird title}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{matrikelnr}
	{matrikelno}
	{123~456~789}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{primary_supervisor}
	{Primary Supervisor}
	{Dr. P. Supervisor}
	{__jensheinrich_bachelor}

\__jensheinrich_bachelor_create_tl_with_defaults_and_description:nnnn
	{secondary_supervisor}
	{Secondary Supervisor}
	{Prof. Dr. S. Supervisor}
	{__jensheinrich_bachelor}


% Create the commands to set the values
%
\DeclareDocumentCommand{\email}{%
	m% mail address
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_email_tl {#1}
}
%
\DeclareDocumentCommand{\company}{%
	m% company name
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_company_tl {#1}
}

\DeclareDocumentCommand{\author}{%
	m% author name
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_author_tl {#1}
	% legacy option
	\gdef\@author{#1}
	% pagestyle
	\writer{#1}
}

\DeclareDocumentCommand{\title}{%
	m% title
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_title_tl {#1}
	% legacy option
	\gdef\@title{#1}
}

\DeclareDocumentCommand{\date}{%
	m% date
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_date_tl {#1}
	% legacy option
	\gdef\@date{#1}
}

\DeclareDocumentCommand{\matrikelnr}{%
	m% student matrikelno
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_matrikelnr_tl {#1}
}

\DeclareDocumentCommand{\primarysupervisor}{%
	m% student matrikelno
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_primary_supervisor_tl {#1}
}

\DeclareDocumentCommand{\secondarysupervisor}{%
	m% student matrikelno
}{%
	\tl_set:Nn \l__jensheinrich_bachelor_secondary_supervisor_tl {#1}
}


% helper

\cs_new:Npn \__jensheinrich_bachelor_check_before_use_tl:n
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

% Require packages after all options have been passed to them
\RequirePackage{hyperref}
\RequirePackage{amsthm}
\RequirePackage{amsmath}
\RequirePackage{cleveref}
\RequirePackage{biblatex}

\RequirePackage{bachelor_format}
\RequirePackage{bachelor_title}
\RequirePackage{bachelor_declaration}


