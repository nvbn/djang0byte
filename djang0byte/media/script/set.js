// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
// Html tags
// http://en.wikipedia.org/wiki/html
// ----------------------------------------------------------------------------
// Basic set. Feel free to add more tags
// ----------------------------------------------------------------------------
function color(color) {
    return "<span style='color:"+color+";'>";
}

mySettings = {
	onTab:			{keepDefault:false, openWith:'	 '},
	markupSet: [
		{name:'Heading 3', key:'3', openWith:'<h3(!( class="[![Class]!]")!)>', closeWith:'</h3>', placeHolder:'Заголовок' },
		{name:'Bold', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)' },
		{name:'Italic', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)' },
		{name:'Stroke through', key:'S', openWith:'<del>', closeWith:'</del>' },
        {
            name:'Colors',
			className:'colors',
			openWith:color('[![Color]!]'),
			closeWith:'</span>',
				dropMenu: [
					{name:'Yellow',	openWith: color('yellow'), 	closeWith:'</span>', className:"col1-1" },
					{name:'Orange',	openWith: color('orange'), 	closeWith:'</span>', className:"col1-2" },
					{name:'Red', 	openWith: color('red'), 	closeWith:'</span>', className:"col1-3" },

					{name:'Blue', 	openWith: color('blue'), 	closeWith:'</span>', className:"col2-1" },
					{name:'Purple', openWith: color('purple'), 	closeWith:'</span>', className:"col2-2" },
					{name:'Green', 	openWith: color('green'), 	closeWith:'</span>', className:"col2-3" },

					{name:'White', 	openWith: color('white'), 	closeWith:'</span>', className:"col3-1" },
					{name:'Gray', 	openWith: color('gray'), 	closeWith:'</span>', className:"col3-2" },
					{name:'Black',	openWith: color('black'), 	closeWith:'</span>', className:"col3-3" }
				]
		},
        {name:'Size', key:'S', openWith:'<span style="size: [![Text size]!]px">', closeWith:'</span>',
            dropMenu :[
                {name:'9', openWith:'<span style="size:9px">', closeWith:'</span>' },
                {name:'12', openWith:'<span style="size:12px">', closeWith:'</span>' },
                {name:'14', openWith:'<span style="size:14px">', closeWith:'</span>' },
                {name:'16', openWith:'<span style="size:16px">', closeWith:'</span>' },
                {name:'18', openWith:'<span style="size:18px">', closeWith:'</span>' },
                {name:'20', openWith:'<span style="size:20px">', closeWith:'</span>' },
                {name:'22', openWith:'<span style="size:22px">', closeWith:'</span>' }
		]},
		{name:'Ul', openWith:'<ul>\n', closeWith:'</ul>\n' },
		{name:'Ol', openWith:'<ol>\n', closeWith:'</ol>\n' },
		{name:'Li', openWith:'<li>', closeWith:'</li>' },
		{name:'Picture', key:'P', replaceWith:'<img src="[![Адрес:!:http://]!]" alt="[![Alternative text]!]" />' },
		{name:'Link', key:'L', openWith:'<a href="[![Адрес:!:http://]!]"(!( title="[![Title]!]")!)>', closeWith:'</a>', placeHolder:'Текст ссылки' },
        {name:'Code', key:'P', openWith:'<code lang="[![Язык]!]">',  closeWith:'</code>'},
        {name:'User', key:'P', openWith:'<user>',  closeWith:'</user>'},
        {name:'Cut', key:'S', replaceWith:'<cut>',
            dropMenu :[
                {name:'cut', replaceWith:'<cut>' },
                {name:'fcut', replaceWith:'<fcut>' }
		]},
        {name:'Spoiler', openWith:'<spoiler>',  closeWith:'</spoiler>'},
        {name:'Quote', openWith:'<quote>',  closeWith:'</quote>'}
	]
}