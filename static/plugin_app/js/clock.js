// JavaScript Document

/**

Clock

*/

function showClock(){
	var CurentDate = new Date();
	var CaseDay = CurentDate.getDay();
	var CaseMonth = CurentDate.getMonth();
	var strYear = CurentDate.getFullYear();
	var strDay = CurentDate.getDate();
	var hours = CurentDate.getHours()    
	var minutes = CurentDate.getMinutes()
	var seconds = CurentDate.getSeconds()
	var dn="PM",strDay1,strMonth;
	if(CaseDay == 0){strDay1 = "Chủ Nhật";}
	else if(CaseDay == 1){strDay1 = "Thứ Hai";}
	else if(CaseDay == 2){strDay1 = "Thứ Ba";}
	else if(CaseDay == 3){strDay1 = "Thứ Tư";}
	else if(CaseDay == 4){strDay1 = "Thứ Năm";}
	else if(CaseDay == 5){strDay1 = "Thứ Sáu";}
	else if(CaseDay == 6){strDay1 = "Thứ Bảy";}
	if(CaseMonth == 0){strMonth = "1";}
	else if(CaseMonth ==1){strMonth = "2";}
	else if(CaseMonth ==2){strMonth = "3";}
	else if(CaseMonth ==3){strMonth = "4";}
	else if(CaseMonth ==4){strMonth = "5";}
	else if(CaseMonth ==5){strMonth = "6";}
	else if(CaseMonth ==6){strMonth = "7";}
	else if(CaseMonth ==7){strMonth = "8";}
	else if(CaseMonth ==8){strMonth = "9";}
	else if(CaseMonth ==9){strMonth = "10";}
	else if(CaseMonth ==10){strMonth = "11";}
	else if(CaseMonth ==11){strMonth = "12";}
	if (hours<12){dn="AM";hours=hours+12;}
    if (hours>12){dn="PM";hours=hours-12;}
	if (hours==0){hours=12;dn="AM"}
	if (minutes<=9){minutes="0"+minutes;}
	if (seconds<=9){seconds="0"+seconds;}
    var myclock = strDay1 + ", Ngày " + strDay + " / " + strMonth + " / " + strYear + " - lúc " +hours+":"+minutes+":" +seconds+" "+dn;
    var idShow = document.getElementById('liveClock');
    if (idShow){
        idShow.innerHTML=myclock;
        setTimeout("showClock()",1000)
    }
}


//addLoadEvent(func);
function addLoadEvent(func){	
	var oldonload = window.onload;
	if (typeof window.onload != 'function'){
	    	window.onload = func;
	} else {
		window.onload = function(){
			oldonload();
			func();
		}
	}
}

addLoadEvent(showClock);