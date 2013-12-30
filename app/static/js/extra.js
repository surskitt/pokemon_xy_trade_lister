function set_openid(openid, pr)
{
	u = openid.search('<username>')
	if (u != -1) {
			// openid requires username
			user = prompt('Enter your ' + pr + ' username:')
			openid = openid.replace('<username>', user)
	}
	form = document.forms['login'];
	form.elements['openid'].value = openid
}

function toggleAboutEdit()
{
	$("#userInfo").toggle()
	$("#userInfoEdit").toggle()
}