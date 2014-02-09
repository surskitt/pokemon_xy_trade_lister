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

function tradeFormToggle()
{
	$("#addTradeForm").toggle()
	$("#addTradeCsvForm").toggle()
}

toastr.options = {
			"closeButton": true,
			"debug": false,
			"positionClass": "toast-bottom-right",
			"onclick": null,
			"showDuration": "300",
			"hideDuration": "1000",
			"timeOut": "5000",
			"extendedTimeOut": "1000",
			"showEasing": "swing",
			"hideEasing": "linear",
			"showMethod": "fadeIn",
			"hideMethod": "fadeOut"
		}