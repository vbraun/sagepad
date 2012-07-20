
var Menu = Menu || {};


Menu.timeout    = 500;
Menu.closetimer = null;
Menu.item = null;
    

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
    
Menu.open = function () { 
    var self = Menu;
    self.canceltimer();
    self.close();
    self.item = jQuery(this).find('ul').css('visibility', 'visible');
};

Menu.register = function(css_id) {
    var self = Menu;
    self.css_id = css_id;
    jQuery(css_id + ' > li').bind('mouseover', self.open);
    jQuery(css_id + ' > li').bind('mouseout',  self.canceltimer);
    jQuery(document).bind('click', self.close);
};



