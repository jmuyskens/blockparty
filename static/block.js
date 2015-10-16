var saves = document.getElementsByClassName('save');
Array.prototype.forEach.call(saves, function(el) {
	el.addEventListener('click', function(ev) {
		ev.preventDefault();
		console.log('hey');
		var xhr = new XMLHttpRequest();
		xhr.open('POST', el.href);
		xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		var textarea = el.parentElement.getElementsByTagName('textarea')[0];
		console.log(textarea);
		xhr.send(JSON.stringify({'content': textarea.value}));
	})
});

var codes = document.getElementsByClassName('code');
Array.prototype.forEach.call(codes, function(el) {
	var editor = CodeMirror.fromTextArea(el, {
		lineNumbers: true,
		mode: 'htmlmixed',
        tabMode: "indent",
        viewportMargin: Infinity,
        stylesheet: "static/node_modules/codemirror/theme/solarized.css"
    });
	editor.on('change', function(e) {
		e.save();
		console.log('changed', e);
		console.log(e.getTextArea());
	})
    editor.on('blur', function(e){
    	e.save();
    })
});
