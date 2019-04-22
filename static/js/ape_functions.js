function run(process_id){
	var run_buttons = document.querySelectorAll('*[id^="run_"],*[id^="edit_"],*[id^="results_"], *[id="add_btn"]');
	for (var i=0; i<run_buttons.length;i++){
		if(run_buttons[i].id != process_id){
			run_buttons[i].disabled = true;
		}else{
			run_buttons[i].style.display = "none";
		}
	}
	document.getElementById("loader_" + process_id).hidden = false;
	id_num = process_id.split('_').pop()
	document.getElementById("passrate_" + id_num).innerHTML = "";
	document.getElementById("lastrun_" + id_num).innerHTML = "";
	status_cell = document.getElementById("status_" + id_num)
	status_cell.innerHTML = "running..";
	status_cell.style.color = 'black';
	status_cell.style.fontWeight = 'bold';
	status_cell.parentElement.style.backgroundColor = "gray";
	document.getElementById("added_" + id_num).innerHTML = "";
}