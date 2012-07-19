
var SagePad = SagePad || {};


SagePad.script_root = '';
SagePad.evaluate_url = '/eval';
SagePad.save_url = '/save';
SagePad.editor = null;
SagePad.output_css_id = '#output';

SagePad.dom_editor = null;
SagePad.dom_output = null;
SagePad.dom_window = jQuery(window)
SagePad.dom_body = jQuery('body')


SagePad.setScriptRoot = function(script_root) {
    var self = SagePad;
    self.script_root = script_root;
    self.evaluate_url = script_root + '/eval'
}

SagePad.initOutput = function(output) {
    var self = SagePad;
    self.output_css_id = '#' + output;
    self.dom_output = jQuery(self.output_css_id)
    self.setLayout(self.current_layout)
}

SagePad.LAYOUT_ONLY_EDITOR = 1
SagePad.LAYOUT_OUTPUT = 2
SagePad.LAYOUT_EDIT = 3

SagePad.current_layout = SagePad.LAYOUT_ONLY_EDITOR

SagePad.outputHeight = function() {
    var self = SagePad
    if (self.dom_output == null) 
	return 0;
    var old_css = {
	'overflow' : self.dom_output.css('overflow'),
	'visibility' : self.dom_output.css('visibility')
    };
    self.dom_output.css({'visibility':'hidden','height':'100%','overflow':'auto'})
    var h = self.dom_output.outerHeight(true)
    self.dom_output.css(old_css)
    return h
}

SagePad.setLayout = function(layout) {
    var self = SagePad
    self.dom_window.scrollTop(0);
    self.dom_window.scrollLeft(0);
    self.current_layout = layout
    var h_menu   = self.dom_editor.offset().top
    var h_window = self.dom_window.outerHeight(true);
    var h_body   = self.dom_body.outerHeight(true);
    var h_avail    = h_window - h_menu - 1;
	// self.dom_editor.outerHeight(true) - h_body + h_window;  // fit perfectly the browser height
    switch (layout) {
    case self.LAYOUT_ONLY_EDITOR: 
	h = h_avail;
	self.dom_editor.unbind('click', self.setLayoutEdit);
	if (self.dom_output != null) self.dom_output.hide()
	break;
    case self.LAYOUT_OUTPUT:
	if (self.dom_output != null) {
	    self.dom_output.show()
	    self.dom_output.bind('click', self.setLayoutInitial);
	}
	h = Math.max(h_window/4, h_avail - self.outputHeight());
	self.dom_editor.bind('click', self.setLayoutEdit);
	break;
    case self.LAYOUT_EDIT:
	if (self.dom_output != null) self.dom_output.show()
	h = Math.max(3*h_window/4, h_avail - self.outputHeight());
	break;
    }
    self.dom_editor.height(h);
    self.editor.resize();
    if (self.dom_output != null) {
	var margin = self.dom_output.outerWidth(true) - self.dom_output.width();
	self.dom_output.width( self.dom_editor.outerWidth() - margin );
	self.dom_output.height( h_window - h_menu - h - margin - 2);
    }
    return h;
}

SagePad.setLayoutEdit = function() {
    var self = SagePad
    if (self.current_layout == self.LAYOUT_OUTPUT) {
	self.setLayout(self.LAYOUT_EDIT);
    }
    return true;
}

SagePad.setLayoutInitial = function() {
    var self = SagePad;
    self.setLayout(self.LAYOUT_ONLY_EDITOR);
}

SagePad.initEditor = function(editor_id) {
    var self = SagePad;
    self.editor_id = editor_id;
    var editor_css_id = self.editor_css_id = '#' + editor_id;
    self.dom_editor = jQuery(editor_css_id)
    var e = self.editor = ace.edit('editor');
    e.setTheme('ace/theme/eclipse');
    e.session.setMode('ace/mode/python');
    e.getSession().setUseSoftTabs(true);
    e.renderer.setHScrollBarAlwaysVisible(true); 

    e.onCursorChange(self.setLayoutEdit);

    e.commands.addCommand({
	name: 'myEvaluateCommand',
	bindKey: {win: 'Ctrl-Return',  mac: 'Command-Return'},
	exec: self.evaluate
    });
    jQuery('a#evaluate').bind('click', self.evaluate);
    jQuery('a#menu_save').bind('click', self.save);

    self.setLayout(self.LAYOUT_ONLY_EDITOR);
    jQuery(window).unload(SagePad.unload);
}

SagePad.resize = function() {
    var self = SagePad;
    if (self.editor != null) {
	self.setLayout(self.current_layout)
    };
}

SagePad.evaluate = function() {
    var self = SagePad;
    self.setOutput('Please wait, computing...');
    jQuery.post(self.evaluate_url, { 
	code: self.editor.getValue(),
    }, self.evaluate_callback);
}

SagePad.save = function() {
    var self = SagePad;
    jQuery.post(self.save_url, { 
	code: self.editor.getValue(),
    });
}

SagePad.unload = function() {
    var self = SagePad;
    jQuery.ajaxSetup({async:false});
    self.save();
}

SagePad.evaluate_callback = function(data) {
    var self = SagePad;
    var output = data.output;
    self.setOutput(output+output+output);
}


SagePad.setOutput = function(output) {
    var self = SagePad;
    self.dom_output.text(output);
    self.setLayout(self.LAYOUT_OUTPUT);
}

SagePad.initSettings = function(settings_id) {
    var self = SagePad;
    self.settings_id = settings_id;
    var settings_css_id = self.settings_css_id = '#' + settings_id;
    jQuery(settings_css_id).dialog({
	autoOpen: false,
	// height: 300,
	// width: 350,
	modal: true,
	buttons: {
	    "Create an account": function() {
		var bValid = true;
		allFields.removeClass( "ui-state-error" );
		
		bValid = bValid && checkLength( name, "username", 3, 16 );
		bValid = bValid && checkLength( email, "email", 6, 80 );
		bValid = bValid && checkLength( password, "password", 5, 16 );
		
		bValid = bValid && checkRegexp( name, /^[a-z]([0-9a-z_])+$/i, "Username may consist of a-z, 0-9, underscores, begin with a letter." );
		// From jquery.validate.js (by joern), contributed by Scott Gonzalez: http://projects.scottsplayground.com/email_address_validation/
		bValid = bValid && checkRegexp( email, /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i, "eg. ui@jquery.com" );
		bValid = bValid && checkRegexp( password, /^([0-9a-zA-Z])+$/, "Password field only allow : a-z 0-9" );
		
		if ( bValid ) {
		    $( "#users tbody" ).append( "<tr>" +
						"<td>" + name.val() + "</td>" + 
						"<td>" + email.val() + "</td>" + 
						"<td>" + password.val() + "</td>" +
						"</tr>" ); 
		    $( this ).dialog( "close" );
		}
	    },
	    Cancel: function() {
		$( this ).dialog( "close" );
	    }
	},
	close: function() {
				allFields.val( "" ).removeClass( "ui-state-error" );
	}
    });
    jQuery('a#menu_settings').bind('click', self.showSettings);
}

SagePad.showSettings = function() {
    var self = SagePad;
    jQuery(self.settings_css_id).dialog('open');
}

jQuery(window).resize(SagePad.resize);
