var deleteAs = document.getElementsByClassName('delete');
console.log(deleteAs[0]);
Array.prototype.forEach.call(deleteAs, function(el) {
	el.addEventListener('click', function(e) {
		e.preventDefault();
		xhr = new XMLHttpRequest();
		xhr.open('DELETE', el.href);
		xhr.send();
		document.location.reload();
	});
})