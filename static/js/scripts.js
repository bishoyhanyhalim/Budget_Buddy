let newval = document.querySelectorAll(".form-control");

console.log("wellcome this is newval" ,newval);
var regex ={
  userNameR: /^[a-zA-Z0-9_-]{3,}$/,
  emailR: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  passwordR: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$%*?&]{8,16}$/
  ,
}

function validate(element){
  var inputType = element.name;
  var inputValue = element.value;
console.log(inputValue);
  if (inputType === 'username'){
    if (regex.userNameR.test(inputValue)){
      element.classList.add("is-valid");
      element.classList.remove("is-invalid");
      console.log("valid");

    }
    else
    {
      element.classList.remove("is-valid");
      element.classList.add("is-invalid");  console.log("invalid")
    }
  }

  if (inputType === "email"){
    if (regex.emailR.test(inputValue)){
      element.classList.add("is-valid");
      element.classList.remove("is-invalid");
      console.log("valid");
    }
    else
{
  element.classList.remove("is-valid");
  element.classList.add("is-invalid");  console.log("invalid")
}
  }
  if (inputType === "password"){
    if (regex.passwordR.test(inputValue)){
      var temp = inputValue;
      element.classList.add("is-valid");
      element.classList.remove("is-invalid");
      console.log("valid");
    }
    else
{
  element.classList.remove("is-valid");
  element.classList.add("is-invalid");  console.log("invalid")
}
  }

  if (inputType === "confirmPassword"){


    if (inputValue === password.value){
      console.log(password.value);
      element.classList.add("is-valid");
      element.classList.remove("is-invalid");
      console.log("valid");
    }
    else
{
  element.classList.remove("is-valid");
  element.classList.add("is-invalid");  console.log("invalid")
}
  }

}


newval.forEach((element)=>{

  element.addEventListener("input", function(){

   validate(element);
})})
