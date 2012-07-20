
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

SagePad.setFontSize = function(fontsize) {
    var self = SagePad;
    self._font_size = fontsize;
    self.dom_editor.css('font-size', fontsize);
}

SagePad.getFontSize = function() {
    var self = SagePad;
    return self._font_size;
}

SagePad.setFolding = function(folding) {
    var self = SagePad;
    self._folding = folding;
    self.editor.session.setFoldStyle(folding);
}

SagePad.getFolding = function() {
    var self = SagePad;
    return self._folding;
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
    self.setFolding('manual');
    self.setFontSize('medium');

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
	// autoOpen: false,
	modal: true
    });
    jQuery('a#menu_settings').bind('click', self.showSettings);
    jQuery('#settings_theme').change(SagePad.settingsThemeCallback);
    jQuery('#settings_theme option[value="' + self.editor.getTheme() + '"]').attr('selected', 'selected');
    jQuery('#settings_fontsize').change(SagePad.settingsFontSizeCallback);
    jQuery('#settings_fontsize option[value="' + self.getFontSize() + '"]').attr('selected', 'selected');
    jQuery('#settings_folding').change(SagePad.settingsFoldingCallback);
    jQuery('#settings_folding option[value="' + self.getFolding() + '"]').attr('selected', 'selected');
}

SagePad.showSettings = function() {
    var self = SagePad;
    jQuery(self.settings_css_id).dialog('open');
}

SagePad.settingsThemeCallback = function() {
    var self = SagePad;
    var theme = jQuery('#settings_theme option:selected').val();
    self.editor.setTheme(theme);
}

SagePad.settingsFontSizeCallback = function() {
    var self = SagePad;
    var fontsize = jQuery('#settings_fontsize option:selected').val();
    self.setFontSize(fontsize);
}

SagePad.settingsFoldingCallback = function() {
    var self = SagePad;
    var folding = jQuery('#settings_folding option:selected').val();
    self.setFolding(folding);
}


jQuery(window).resize(SagePad.resize);

