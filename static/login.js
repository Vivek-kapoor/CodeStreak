function check(form)
{
 usn=document.getElementById("usn");
 pwd=document.getElementById("pwd");
 
 if(usn.value==""){
	 alert("enter the usn");
 }
 else if(pwd.value==""){
	 alert("enter the password");
 }

else if(usn.value == "usn" && pwd.value == "pwd")
  {
    window.open('target.html')
  }
 else
 {
   alert("Error Password or Username")
  }
}
