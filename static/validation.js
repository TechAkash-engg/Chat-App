var password = document.getElementById("password");
var confirm_password = document.getElementById("re_pass");

function validatePassword(){
  if(password.value != re_pass.value) {
    re_pass.setCustomValidity("Passwords Don't Match");
  } else {
    re_pass.setCustomValidity('');
  }
}

password.onchange = validatePassword;
re_pass.onkeyup = validatePassword;

