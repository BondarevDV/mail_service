        let email_select = document.getElementById('email');
        let folder_select = document.getElementById('folder');

        email_select.onchange = function() {
            email = email_select.value;
            alert(email);
            fetch('/folders/' + email).then(function(response){
                response.json().then(function(data) {
                    let optionHTML = '';
                    for(let folder of data.folders){
                        optionHTML += '<option value="' + folder.id + '">' + folder.name + '</option>';
                    }
                    folder_select.innerHTML = optionHTML;
                 });
             });

        }




const list_items = document.querySelectorAll('.card');
const lists = document.querySelectorAll('.container');

let draggedItem = null;

for (let i = 0; i < list_items.length; i++) {
	const item = list_items[i];

	item.addEventListener('dragstart', function () {
		draggedItem = item;
		setTimeout(function () {
			item.style.display = 'none';
		}, 0)
	});

	item.addEventListener('dragend', function () {
		setTimeout(function () {
			draggedItem.style.display = 'block';
			draggedItem = null;
		}, 0);
	})

	for (let j = 0; j < lists.length; j ++) {
		const list = lists[j];

		list.addEventListener('dragover', function (e) {
			e.preventDefault();
		});

		list.addEventListener('dragenter', function (e) {
			e.preventDefault();
			this.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
		});

		list.addEventListener('dragleave', function (e) {
			this.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
		});

		list.addEventListener('drop', function (e) {
			console.log('drop');
			this.append(draggedItem);
			this.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
		});
	}
}