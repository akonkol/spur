SyntaxHighlighter.brushes.Cisco = function()
{
	var interface =	'interface FastEthernet';
	var keywords =	'ip snmp-server tacacs-server ntp line logging'+
			'boot hostname banner end clock udld power ';
	var security =	'crypto';

	this.regexList = [
		{ regex: new RegExp('description.*$', 'gm'),			css: 'comments' }, 
		{ regex: new RegExp('!.*$', 'gm'),			css: 'comments' }, 
		{ regex: new RegExp('^( no|no).*$', 'gm'),			css: 'comments' }, 
		{ regex: new RegExp('^version.*$', 'gm'),			css: 'color2' }, 
		{ regex: new RegExp('^service.*$', 'gm'),			css: 'color2' }, 
		{ regex: new RegExp('^aaa.*$', 'gm'),			css: 'color3' }, 
		{ regex: new RegExp('^interface.*$', 'gm'),			css: 'color2' }, 
		{ regex: new RegExp('^access-list.*$', 'gm'),			css: 'color3' }, 
		{ regex: new RegExp('^username.*$', 'gm'),			css: 'color2' }, 
		{ regex: new RegExp('^enable.*$', 'gm'),			css: 'color2' }, 
		{ regex: SyntaxHighlighter.regexLib.multiLineCComments,		css: 'comments' },			// multiline comments
		{ regex: SyntaxHighlighter.regexLib.doubleQuotedString,		css: 'string' },			// strings
		{ regex: SyntaxHighlighter.regexLib.singleQuotedString,		css: 'string' },			// strings
		{ regex: /^\s*#.*/gm,										css: 'preprocessor' },
		{ regex: new RegExp(this.getKeywords(keywords), 'gm'),		css: 'color1' },			// c# keyword
		{ regex: new RegExp(this.getKeywords(interface),'gm'),		css: 'color2' },			// c# keyword
		{ regex: new RegExp(this.getKeywords(security), 'gm'),		css: 'color3' }			// c# keyword
		];
		
	this.forHtmlScript(SyntaxHighlighter.regexLib.aspScriptTags);
};

SyntaxHighlighter.brushes.Cisco.prototype	= new SyntaxHighlighter.Highlighter();
SyntaxHighlighter.brushes.Cisco.aliases	= ['cisco','network'];

