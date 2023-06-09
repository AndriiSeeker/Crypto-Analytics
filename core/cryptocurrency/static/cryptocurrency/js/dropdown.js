function myFunction() {
  document.getElementById("myDropdown").classList.toggle("show");
}


window.onclick = function(e){
console.log(e)
  var divToHide = document.getElementById('myDropdown');
    if(e.target.parentNode.id !== 'dropbtn'){
      divToHide.classList.remove('show');
    }
};