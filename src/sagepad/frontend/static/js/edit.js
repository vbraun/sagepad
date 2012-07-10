
var editor = ace.edit('editor');
editor.setTheme('ace/theme/eclipse');
editor.session.setMode('ace/mode/python');
editor.getSession().setUseSoftTabs(true);
editor.renderer.setHScrollBarAlwaysVisible(true); 

// Initial size
jQuery('#editor').height(jQuery(window).height());


jQuery(window).resize(function() {
    jQuery('#editor').height(jQuery(window).height() - 200);
});

editor.commands.addCommand({
    name: 'myEvalCommand',
    bindKey: {win: 'Ctrl-Return',  mac: 'Command-Return'},
    exec: function(editor) {
	jQuery('#editor').height(jQuery(window).height()/4); 
	editor.resize();
    }
});


$(function() {
    $('a#calculate').bind('click', function() {
	$.getJSON($SAGEPAD_SCRIPT_ROOT + '/eval', {
            a: $('input[name="a"]').val(),
            b: $('input[name="b"]').val(),
            code: editor.getValue() 
      }, function(data) {
          $("#output").text(data.output);
          $("#result").text(data.result);
      });
      return false;
    });
});
