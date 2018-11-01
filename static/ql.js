//script for displaying question details
var e=0;
function qdetails(event)
{
	if(e!=0)
	{
		e.target.style.backgroundColor="white";
	}
	var dets=document.getElementById("qdisplay");
	dets.style.display="inline-block";
	dets.style.width="5000px";
	var statement=document.getElementById("froala-editor");
	if(event.target.innerHTML !="ADD QUESTION")
	{
		statement.value=event.target.innerHTML;
		event.target.style.backgroundColor="#F8BDED";
	}
	else {
		statement.value="";
	}
	//var submit=document.getElementById("editq");
	e=event;
	//submit.onclick=addq(tar);
}
//script to add questions(To be completed)
function addq()
{
	console.log(e.target.innerHTML);
	if(e.target.style.color=="green")
	{
		var qs=document.getElementById("Qs");
		var question=document.createElement("div");
		question.className="question";
		question.onclick=qdetails;
		question.id="focusme";
		//question.style.backgroundColor="#F8BDED";
		question.innerHTML=document.getElementById("froala-editor").value;
		qs.appendChild(question);
		//var scrollPos =  $("#focusme").offset().top;
		//$("#Qs").scrollTop(scrollPos);
		//$('#Qs').animate({'scrollTop' : $("#focusme").position().top});
		question.scrollIntoView(true);
		$("#focusme").trigger("click");
		question.id="";
		//question.scrollto(1000);
	}
	else {
		e.target.innerHTML=document.getElementById("froala-editor").value;
	}
	//document.getElementById("frm").submit();
}
function removecase(event)
{
	li=document.getElementById("case"+event.target.id);
	li.parentNode.removeChild(li);
}

n_cases=1

function testcase()
{
	current_case=document.getElementById("case"+n_cases);
	button=current_case.querySelector("input[type='button']");
	button.value="Remove TestCase";
	button.id=n_cases;
	button.onclick=removecase;
	n_cases+=1
	cases=document.getElementById("testcases");
	li=document.createElement("li");
	li.style.border="2px solid grey";
	li.id="case"+n_cases;
	cases.appendChild(li);
	lab=document.createElement("label");
	lab.style.color="white";
	lab.innerHTML="Input File";
	inp=document.createElement("input");
	inp.id="input";
	inp.type="file";
	inp.name="input"+(n_cases);
	inp.style.color="white";
	li.appendChild(lab);
	li.appendChild(inp);
	lab=document.createElement("label");
	lab.style.color="white";
	lab.innerHTML="Output File";
	out=document.createElement("input");
	out.id="output";
	out.type="file";
	out.name="output"+(n_cases);
	out.style.color="white";
	li.appendChild(lab);
	li.appendChild(out);
	sub=document.createElement("input");
	sub.id="editq";
	sub.type="button";
	sub.value="Add TestCase";
	sub.onclick=testcase;
	li.appendChild(sub);
}
