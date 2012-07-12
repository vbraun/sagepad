
var SagePad = SagePad || {};


SagePad.script_root = '';
SagePad.evaluate_url = '/eval';
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

SagePad.setLayout = function(layout) {
    var self = SagePad
    self.current_layout = layout
    var h_window = self.dom_window.outerHeight();
    var h_body   = self.dom_body.outerHeight();
    var h_fit    = self.dom_editor.outerHeight() - h_body + h_window;  // fit perfectly the browser height
    var h = h_fit;
    switch (layout) {
    case self.LAYOUT_ONLY_EDITOR:
	if (self.dom_output != null) {
	    h = h + self.dom_output.outerHeight()
	    self.dom_editor.unbind('click', self.setLayoutEdit);
	}
	break;
    case self.LAYOUT_OUTPUT:
	h = Math.max(h_window/4, h_fit);
	self.dom_editor.bind('click', self.setLayoutEdit);
	break;
    case self.LAYOUT_EDIT:
	h = Math.max(3*h_window/4, h_fit);
	break;
    }
    self.dom_editor.height(h);
    self.editor.resize();
    return h;
}

SagePad.setLayoutEdit = function() {
    var self = SagePad
    self.dom_output.text('setLayoutEdit ' + Date());
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

    self.setLayout(self.LAYOUT_ONLY_EDITOR);
}

SagePad.resize = function() {
    var self = SagePad;
    if (self.editor != null) {
	self.setLayout(self.current_layout)
    };
}

jQuery(window).resize(SagePad.resize);

SagePad.evaluate = function() {
    var self = SagePad;
    self.setOutput('Please wait, computing...');
    jQuery.getJSON(self.evaluate_url, { 
	code: self.editor.getValue(),
    }, self.evaluate_callback);
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
