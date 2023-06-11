
function validatePasswords() {
    
    let p1 = document.getElementById("password").value
    let p2 = document.getElementById("password_again").value
    if(p1 == p2 && p1 != "") {
        let form = document.getElementById("password_form")
        form.submit();
    } else {
        let error = document.getElementById("error")
        error.classList.remove("hidden")
    }
}