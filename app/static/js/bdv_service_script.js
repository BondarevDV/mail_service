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