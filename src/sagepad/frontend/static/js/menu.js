
var Menu = Menu || {};

Menu.setScriptRoot = function(script_root) {
    var self = Menu;
    self.script_root = script_root;
    self.menu_url = script_root + '/_menu'
}
    
Menu.setScriptRoot('');

Menu.timeout    = 500;
Menu.closetimer = null;
Menu.item = null;
Menu.css_id = null;


Menu.close = function() {
    var self = Menu;
    if (self.item != null) 
	self.item.css('visibility', 'hidden');
};
    
Menu.canceltimer = function () { 
    var self = Menu;
    if (self.closetimer) {  
	window.clearTimeout(self.closetimer);
	self.closetimer = null;
    }
};
    
Menu.mouseover = function () { 
    var self = Menu;
    self.canceltimer();
    self.close();
    self.item = jQuery(this).find('ul').css('visibility', 'visible');
};

Menu.mouseout = function () {
    var self = Menu;
    self.closetimer = window.setTimeout(self.close, self.timeout);
}

Menu.evaluate_link = function () {
    var self = Menu;
    var evaluate_link = jQuery(self.css_id + ' .evaluate_link');
    for (var i = 0; i < evaluate_link.length; i++) {
	var link = evaluate_link[i];
	var check = (link === this);
	var radio = link.children[0];
	radio.checked = ('checked', check);
	if (check) {
	    var value = radio.getAttribute('value');
	    jQuery.getJSON(self.menu_url, {eval_mode:value}, Menu.callback);
	}
    }
}


Menu.callback = function (data) {
    var self = Menu;
    self.setEvaluateRadio(data['eval_mode'])
}


Menu.setEvaluateRadio = function (eval_mode) {
    var self = Menu;
    var evaluate_link = jQuery(self.css_id + ' .evaluate_link');
    for (var i = 0; i < evaluate_link.length; i++) {
	var link = evaluate_link[i];
	var radio = link.children[0];
	var check = (radio.getAttribute('value') == eval_mode);
	radio.checked = ('checked', check);
    }
}

Menu.register = function(css_id) {
    var self = Menu;
    self.css_id = css_id;
    jQuery(css_id + ' > li').bind('mouseover', self.mouseover);
    jQuery(css_id + ' > li').bind('mouseout',  self.mouseout);
    jQuery(css_id + ' .evaluate_link').bind('click', self.evaluate_link);
    jQuery(document).bind('click', self.close);
};



